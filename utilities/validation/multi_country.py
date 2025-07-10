"""
Multi-country validation logic.

This module handles the complete workflow for validating models across
multiple countries, including parallel job submission and analytics generation.
"""

import time
from pathlib import Path
from typing import Dict, Any, List

# Configuration
MAX_INSTANCES = 100  # Maximum number of concurrent AWS Batch jobs

from .country_utils import load_countries_list, create_country_scenario, get_country_display_list
from . import (
    validate_json_files, ensure_tmp_directory, cleanup_tmp_directory,
    apply_scenario_to_model, test_api_health
)
from .api_client import submit_simulation_job, get_job_status
from .analytics import process_job_analytics


def count_active_jobs(job_results: Dict[str, Dict[str, Any]]) -> int:
    """
    Count the number of jobs that are currently active (submitted but not completed).
    
    Args:
        job_results: Dictionary mapping country ISO3 to job info
        
    Returns:
        int: Number of active jobs
    """
    active_count = 0
    for job_info in job_results.values():
        if job_info.get('submitted') and not job_info.get('completed', False):
            # Check if job is still running
            job_id = job_info.get('job_id')
            if job_id:
                status_data = get_job_status(job_id)
                if status_data:
                    job_status = status_data.get('jobStatus', 'UNKNOWN')
                    # Count as active if not in terminal state
                    if job_status not in ['SUCCEEDED', 'FAILED']:
                        active_count += 1
                    elif job_status in ['SUCCEEDED', 'FAILED']:
                        # Mark as completed to avoid checking again
                        job_info['completed'] = True
    return active_count


def wait_for_instance_availability(
    job_results: Dict[str, Dict[str, Any]], 
    max_instances: int = MAX_INSTANCES,
    verbose: bool = True,
    check_interval: int = 10
) -> None:
    """
    Wait until there are fewer than max_instances active jobs.
    
    Args:
        job_results: Dictionary mapping country ISO3 to job info
        max_instances: Maximum number of concurrent instances
        verbose: Whether to print waiting messages
        check_interval: How often to check job status (seconds)
    """
    while True:
        active_count = count_active_jobs(job_results)
        if active_count < max_instances:
            break
        
        if verbose:
            print(f"⏳ {active_count}/{max_instances} instances active, waiting {check_interval}s...")
        time.sleep(check_interval)


def prepare_country_models(
    country_scenarios: Dict[str, Dict[str, Any]],
    model_path: str,
    tmp_dir,
    verbose: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Prepare model files for all countries by applying scenarios.
    
    Args:
        country_scenarios: Dictionary mapping ISO3 to country info
        model_path: Path to base model file
        tmp_dir: Temporary directory for model files
        verbose: Whether to print progress
        
    Returns:
        Dictionary mapping ISO3 to prepared model info
    """
    prepared_models = {}
    
    if verbose:
        print(f"📋 Preparing {len(country_scenarios)} model files...")
    
    for iso3, country_info in country_scenarios.items():
        # Apply scenario to model for this country
        country_model_path = tmp_dir / f"model_{iso3}.json"
        
        if verbose:
            print(f"🔧 Preparing model for {country_info['name']} ({iso3})")
        
        if apply_scenario_to_model(model_path, country_info['scenario_path'], str(country_model_path)):
            prepared_models[iso3] = {
                'name': country_info['name'],
                'model_path': str(country_model_path),
                'ready': True
            }
            if verbose:
                print(f"✅ Model prepared for {country_info['name']}")
        else:
            prepared_models[iso3] = {
                'name': country_info['name'],
                'ready': False,
                'error': 'Failed to apply scenario'
            }
            if verbose:
                print(f"❌ Failed to prepare model for {country_info['name']} ({iso3})")
    
    ready_count = len([m for m in prepared_models.values() if m.get('ready')])
    if verbose:
        print(f"📊 Model preparation complete: {ready_count}/{len(country_scenarios)} models ready")
    
    return prepared_models


def submit_jobs_with_throttling(
    prepared_models: Dict[str, Dict[str, Any]],
    environment: str,
    max_instances: int = MAX_INSTANCES,
    verbose: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Submit jobs for all prepared models with throttling to respect max_instances limit.
    
    Args:
        prepared_models: Dictionary mapping ISO3 to prepared model info
        environment: API environment
        max_instances: Maximum number of concurrent instances
        verbose: Whether to print progress
        
    Returns:
        Dictionary mapping ISO3 to job submission results
    """
    job_results = {}
    ready_models = {iso3: info for iso3, info in prepared_models.items() if info.get('ready')}
    
    if verbose:
        print(f"🚀 Starting batch job submission for {len(ready_models)} models...")
    
    submitted_count = 0
    
    for iso3, model_info in ready_models.items():
        # Only check for throttling after we've submitted max_instances jobs
        if submitted_count >= max_instances:
            if verbose:
                print(f"🎯 Reached {max_instances} submissions, starting throttling...")
            wait_for_instance_availability(job_results, max_instances, verbose)
        
        # Submit job
        if verbose:
            if submitted_count < max_instances:
                print(f"🚀 Submitting job for {model_info['name']} ({iso3}) [{submitted_count+1}/{max_instances}]")
            else:
                active_count = count_active_jobs(job_results)
                print(f"🚀 Submitting job for {model_info['name']} ({iso3}) [{active_count}/{max_instances} active]")
        
        job_result = submit_simulation_job(model_info['model_path'], environment)
        
        if job_result and 'jobId' in job_result:
            job_results[iso3] = {
                'name': model_info['name'],
                'job_id': job_result['jobId'],
                'job_name': job_result.get('jobName'),
                'submitted': True,
                'completed': False
            }
            submitted_count += 1
            if verbose:
                print(f"✅ Job submitted for {model_info['name']}: {job_result['jobId']}")
        else:
            job_results[iso3] = {
                'name': model_info['name'],
                'submitted': False,
                'error': 'Job submission failed'
            }
            if verbose:
                print(f"❌ Job submission failed for {model_info['name']}")
    
    # Add failed models to results
    for iso3, model_info in prepared_models.items():
        if not model_info.get('ready') and iso3 not in job_results:
            job_results[iso3] = {
                'name': model_info['name'],
                'submitted': False,
                'error': model_info.get('error', 'Model preparation failed')
            }
    
    if verbose:
        successful_submissions = len([j for j in job_results.values() if j.get('submitted')])
        print(f"📊 Batch submission complete: {successful_submissions}/{len(prepared_models)} jobs submitted")
    
    return job_results


def poll_multiple_jobs(
    job_results: Dict[str, Dict[str, Any]], 
    poll_interval: int, 
    max_wait_time: int, 
    verbose: bool
) -> Dict[str, Dict[str, Any]]:
    """
    Poll multiple jobs until completion or timeout.
    
    Args:
        job_results: Dictionary mapping country ISO3 to job info
        poll_interval: Polling interval in seconds
        max_wait_time: Maximum wait time for all jobs
        verbose: Whether to print progress
        
    Returns:
        Dictionary of completed jobs with their final status
    """
    # Only poll jobs that were successfully submitted
    active_jobs = {iso3: info for iso3, info in job_results.items() if info.get('submitted')}
    completed_jobs = {}
    
    if not active_jobs:
        return {}
    
    if verbose:
        print(f"⏳ Polling {len(active_jobs)} jobs for completion")
        print("=" * 60)
    
    start_time = time.time()
    
    while active_jobs and (time.time() - start_time) < max_wait_time:
        elapsed_time = time.time() - start_time
        elapsed_minutes = int(elapsed_time // 60)
        elapsed_seconds = int(elapsed_time % 60)
        
        jobs_to_remove = []
        
        for iso3, job_info in active_jobs.items():
            job_id = job_info['job_id']
            status_data = get_job_status(job_id)
            
            if status_data is None:
                if verbose:
                    print(f"❌ [{elapsed_minutes:02d}:{elapsed_seconds:02d}] {job_info['name']}: Status check failed")
                jobs_to_remove.append(iso3)
                completed_jobs[iso3] = {
                    **job_info,
                    'success': False,
                    'error': 'Status check failed'
                }
                continue
            
            job_status = status_data.get("jobStatus", "UNKNOWN")
            
            if verbose:
                print(f"📊 [{elapsed_minutes:02d}:{elapsed_seconds:02d}] {job_info['name']}: {job_status}")
            
            # Terminal states
            if job_status == "SUCCEEDED":
                jobs_to_remove.append(iso3)
                completed_jobs[iso3] = {
                    **job_info,
                    'success': True,
                    'job_name': status_data.get('jobName')
                }
                if verbose:
                    print(f"✅ {job_info['name']} completed successfully!")
            
            elif job_status == "FAILED":
                jobs_to_remove.append(iso3)
                completed_jobs[iso3] = {
                    **job_info,
                    'success': False,
                    'error': f"Job failed: {status_data.get('statusReason', 'Unknown')}"
                }
                if verbose:
                    print(f"❌ {job_info['name']} failed!")
        
        # Remove completed jobs from active polling
        for iso3 in jobs_to_remove:
            del active_jobs[iso3]
        
        # Sleep before next poll if there are still active jobs
        if active_jobs:
            time.sleep(poll_interval)
    
    # Handle any remaining jobs that timed out
    for iso3, job_info in active_jobs.items():
        completed_jobs[iso3] = {
            **job_info,
            'success': False,
            'error': f'Job timed out after {max_wait_time} seconds'
        }
        if verbose:
            print(f"⏰ {job_info['name']} timed out")
    
    if verbose:
        successful = len([j for j in completed_jobs.values() if j.get('success')])
        print(f"\n📊 Polling complete: {successful}/{len(completed_jobs)} jobs succeeded")
    
    return completed_jobs


def validate_multiple_countries(
    model_path: str,
    scenario_path: str,
    countries_path: str,
    environment: str,
    poll_interval: int,
    max_wait_time: int,
    skip_api_test: bool,
    no_cleanup: bool,
    verbose: bool,
    generate_analytics: bool,
    max_instances: int = MAX_INSTANCES
) -> bool:
    """
    Validate model changes across multiple countries.
    
    This function runs the complete validation pipeline for each country
    in the countries list, submitting jobs in parallel and collecting
    analytics for each country separately.
    """
    from . import print_header, print_step
    
    if verbose:
        print_header("Multi-Country Validation")
    
    try:
        # Step 1: Load countries list
        if verbose:
            print_step("1", "Loading countries list")
        countries = load_countries_list(countries_path)
        
        if verbose:
            print(f"📊 Found {len(countries)} countries to validate:")
            print(get_country_display_list(countries))
        
        # Step 2: Validate JSON format (base files)
        if verbose:
            print_step("2", "Validating base JSON format")
        if not validate_json_files(model_path, scenario_path):
            return False
        
        # Step 3: Create temporary scenarios for each country
        if verbose:
            print_step("3", "Creating country-specific scenarios")
        
        tmp_dir = ensure_tmp_directory()
        country_scenarios = {}
        
        for country in countries:
            iso3 = country['iso3']
            country_scenario_path = tmp_dir / f"scenario_{iso3}.json"
            
            if create_country_scenario(scenario_path, iso3, str(country_scenario_path)):
                country_scenarios[iso3] = {
                    'name': country['name'],
                    'scenario_path': str(country_scenario_path)
                }
                if verbose:
                    print(f"✅ Created scenario for {country['name']} ({iso3})")
            else:
                if verbose:
                    print(f"❌ Failed to create scenario for {country['name']} ({iso3})")
                if not no_cleanup:
                    cleanup_tmp_directory()
                return False
        
        # Step 4: Submit jobs in parallel (if not skipping API test)
        job_results = {}
        completed_jobs = {}
        if not skip_api_test:
            if verbose:
                print_step("4", "Testing API connectivity")
            if not test_api_health():
                if verbose:
                    print("💡 Tip: Use skip_api_test=True for offline validation")
                if not no_cleanup:
                    cleanup_tmp_directory()
                return False
            
            if verbose:
                print_step("5", "Preparing model files for all countries")
                print(f"📊 Total countries: {len(country_scenarios)}")
            
            # Phase 1: Prepare all model files
            prepared_models = prepare_country_models(
                country_scenarios=country_scenarios,
                model_path=model_path,
                tmp_dir=tmp_dir,
                verbose=verbose
            )
            
            if verbose:
                print_step("6", f"Submitting jobs with throttling (max {max_instances} concurrent)")
                print(f"🎯 Throttling limit: {max_instances} concurrent instances")
            
            # Phase 2: Submit all jobs with throttling
            job_results = submit_jobs_with_throttling(
                prepared_models=prepared_models,
                environment=environment,
                max_instances=max_instances,
                verbose=verbose
            )
            
            # Step 7: Poll all jobs for completion
            if verbose:
                print_step("7", f"Polling {len([j for j in job_results.values() if j.get('submitted')])} jobs for completion")
            
            completed_jobs = poll_multiple_jobs(job_results, poll_interval, max_wait_time, verbose)
            
            # Debug: Check what's in completed_jobs
            if verbose:
                print(f"\n🔍 Debug - Number of completed jobs: {len(completed_jobs)}")
                for iso3, job_info in completed_jobs.items():
                    print(f"  {iso3}: success={job_info.get('success')}, job_name={job_info.get('job_name')}")
            
            # Step 8: Generate analytics for successful jobs
            if generate_analytics and completed_jobs:
                if verbose:
                    print_step("8", "Generating analytics for completed jobs")
                
                model_basename = Path(model_path).stem
                scenario_basename = Path(scenario_path).stem
                
                analytics_success = 0
                for iso3, job_info in completed_jobs.items():
                    if job_info.get('success') and job_info.get('job_name'):
                        try:
                            analytics_result = process_job_analytics(
                                job_name=job_info['job_name'],
                                model_name=f"{model_basename}_{iso3}",
                                scenario_name=scenario_basename,
                                environment=environment,
                                preview=False  # Don't preview for batch
                            )
                            if analytics_result['success']:
                                analytics_success += 1
                                if verbose:
                                    print(f"✅ Analytics generated for {job_info['name']}: {analytics_result['data_records']} records")
                            else:
                                if verbose:
                                    print(f"⚠️  Analytics failed for {job_info['name']}: {analytics_result.get('error')}")
                        except Exception as e:
                            if verbose:
                                print(f"⚠️  Analytics error for {job_info['name']}: {e}")
                
                if verbose:
                    print(f"📊 Analytics generated for {analytics_success}/{len(completed_jobs)} completed jobs")
        
        else:
            if verbose:
                print_step("4", "Skipping API test (offline mode)")
        
        # Step 9: Cleanup
        if not no_cleanup:
            cleanup_tmp_directory()
        elif verbose:
            print(f"\n📁 Temporary files preserved in: {tmp_dir}")
        
        # Success summary
        if not skip_api_test:
            successful_jobs = len([j for j in job_results.values() if j.get('submitted')])
            
            # Debug: print completed_jobs to understand the issue
            if verbose:
                print(f"\n📊 Debug - completed_jobs: {completed_jobs}")
            
            completed_jobs_count = len([j for j in completed_jobs.values() if j.get('success')])
            
            if verbose:
                print_header("Multi-Country Validation Complete")
                print(f"🗺️  Countries processed: {len(countries)}")
                print(f"🚀 Jobs submitted: {successful_jobs}")
                print(f"✅ Jobs completed successfully: {completed_jobs_count}")
                
                if completed_jobs_count == len(countries):
                    print("\n💚 All countries validated successfully!")
                elif completed_jobs_count > 0:
                    print(f"\n⚠️  {len(countries) - completed_jobs_count} countries had issues")
                else:
                    print("\n❌ No countries completed successfully")
            
            return completed_jobs_count == len(countries)
        else:
            if verbose:
                print_header("Multi-Country Validation Complete")
                print(f"🗺️  Countries processed: {len(countries)} (offline mode)")
                print("\n💚 All countries scenarios created successfully!")
            return True
        
    except Exception as e:
        if verbose:
            print(f"\n❌ Multi-country validation error: {e}")
        if not no_cleanup:
            cleanup_tmp_directory()
        return False