"""
Utilities package for botech-demographic-model.

This package provides tools for model validation, scenario application,
remote API testing, and result analytics.

Main Functions:
    validate_model_changes: Complete pre-commit validation pipeline
    apply_scenario: Apply scenario parameters to a model
    test_remote_api: Test model against remote API
    cleanup_workspace: Clean temporary files

Configuration:
    DEFAULT_MODEL: Default model file path
    DEFAULT_SCENARIO: Default scenario file path  
    DEFAULT_ENVIRONMENT: Default API environment
"""

from pathlib import Path

from .file_utils import (
    validate_file_exists,
    load_json_file,
    save_json_file,
    validate_json_files,
)
from .scenario import (
    apply_scenario_to_model,
    apply_scenario_to_model_data,
)
from .api_client import (
    test_api_health,
    submit_and_poll_job,
)
from .cleanup import (
    cleanup_tmp_directory,
    ensure_tmp_directory,
)

from .analytics import (
    # ULID parsing
    extract_ulid_from_job_name,
    
    # Analytics API
    fetch_analytics_data,
    
    # CSV conversion
    convert_to_csv,
    save_analytics_csv,
    
    # Main processor
    process_job_analytics,
)

from .multi_country import validate_multiple_countries

# Configuration constants
DEFAULT_MODEL = "model.json"
DEFAULT_SCENARIO = "scenarios/default_scenario.json"
DEFAULT_ENVIRONMENT = "standard"


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")


def print_step(step: str, description: str) -> None:
    """Print a formatted step."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)


def validate_model_changes(
    model_path: str = DEFAULT_MODEL,
    scenario_path: str = DEFAULT_SCENARIO,
    environment: str = DEFAULT_ENVIRONMENT,
    poll_interval: int = 3,
    max_wait_time: int = 3600,
    skip_api_test: bool = False,
    no_cleanup: bool = False,
    verbose: bool = True,
    generate_analytics: bool = True,
    countries_path: str = None,
    max_instances: int = 100
) -> bool:
    """
    Complete validation pipeline for model changes.
    
    Args:
        model_path: Path to the model JSON file
        scenario_path: Path to the scenario JSON file  
        environment: API environment to test against
        poll_interval: Polling interval in seconds
        max_wait_time: Maximum wait time for job completion
        skip_api_test: Skip remote API testing
        no_cleanup: Skip cleanup of temporary files
        verbose: Print detailed progress information
        generate_analytics: Generate analytics CSV from completed job
        countries_path: Path to JSON file with list of countries to test
        max_instances: Maximum number of concurrent AWS Batch instances
        
    Returns:
        bool: True if validation passed, False otherwise
    """
    if verbose:
        print_header("Model Change Validation")
        print(f"🎯 Target: Pre-commit validation for {model_path}")
        print(f"📋 Scenario: {scenario_path}")
        print(f"🌐 Environment: {environment}")
        if countries_path:
            print(f"🗺️  Countries: {countries_path}")
    
    try:
        # Step 1: Validate input files
        if verbose:
            print_step("1", "Validating input files")
        validate_file_exists(model_path, "Model")
        validate_file_exists(scenario_path, "Scenario")
        
        # Validate countries file if provided
        if countries_path:
            validate_file_exists(countries_path, "Countries")
            
        # If countries are specified, use multi-country workflow
        if countries_path:
            return validate_multiple_countries(
                model_path=model_path,
                scenario_path=scenario_path,
                countries_path=countries_path,
                environment=environment,
                poll_interval=poll_interval,
                max_wait_time=max_wait_time,
                skip_api_test=skip_api_test,
                no_cleanup=no_cleanup,
                verbose=verbose,
                generate_analytics=generate_analytics,
                max_instances=max_instances
            )
        
        # Single-country validation workflow
        return _validate_single_country(
            model_path=model_path,
            scenario_path=scenario_path,
            environment=environment,
            poll_interval=poll_interval,
            max_wait_time=max_wait_time,
            skip_api_test=skip_api_test,
            no_cleanup=no_cleanup,
            verbose=verbose,
            generate_analytics=generate_analytics
        )
        
    except KeyboardInterrupt:
        if verbose:
            print("\n\n⏹️  Validation interrupted by user")
        if not no_cleanup:
            cleanup_tmp_directory()
        return False
    except Exception as e:
        if verbose:
            print(f"\n❌ Unexpected error: {e}")
        if not no_cleanup:
            cleanup_tmp_directory()
        return False


def _validate_single_country(
    model_path: str,
    scenario_path: str,
    environment: str,
    poll_interval: int,
    max_wait_time: int,
    skip_api_test: bool,
    no_cleanup: bool,
    verbose: bool,
    generate_analytics: bool
) -> bool:
    """Single-country validation workflow (original logic)."""
    
    # Step 2: Validate JSON format
    if verbose:
        print_step("2", "Validating JSON format")
    if not validate_json_files(model_path, scenario_path):
        if not no_cleanup:
            cleanup_tmp_directory()
        return False
    
    # Step 3: Apply scenario to model
    if verbose:
        print_step("3", "Applying scenario to model")
    tmp_dir = ensure_tmp_directory()
    tmp_model_path = tmp_dir / "validation_model.json"
    
    if not apply_scenario_to_model(model_path, scenario_path, str(tmp_model_path)):
        if verbose:
            print("❌ Failed to apply scenario to model")
        if not no_cleanup:
            cleanup_tmp_directory()
        return False
    
    # Step 4: API testing (optional)
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
            print_step("5", "Submitting job and polling for completion")
        job_result = submit_and_poll_job(str(tmp_model_path), environment, poll_interval, max_wait_time)
        if job_result is None:
            if verbose:
                print("❌ Remote API testing failed")
            if not no_cleanup:
                cleanup_tmp_directory()
            return False
        
        # Step 6: Generate analytics (optional)
        if generate_analytics and job_result.get('jobName'):
            if verbose:
                print_step("6", "Generating analytics data")
            try:
                # Extract clean names for directory structure
                model_basename = Path(model_path).stem
                scenario_basename = Path(scenario_path).stem
                
                analytics_result = process_job_analytics(
                    job_name=job_result['jobName'],
                    model_name=model_basename,
                    scenario_name=scenario_basename,
                    environment=environment,
                    preview=verbose
                )
                if analytics_result['success']:
                    if verbose:
                        print(f"✅ Analytics generated: {analytics_result['data_records']} records")
                        if analytics_result.get('csv_path'):
                            print(f"📄 CSV saved: {analytics_result['csv_path']}")
                else:
                    if verbose:
                        print(f"⚠️  Analytics generation failed: {analytics_result.get('error', 'Unknown error')}")
            except Exception as e:
                if verbose:
                    print(f"⚠️  Analytics generation error: {e}")
        elif generate_analytics:
            if verbose:
                print_step("6", "Skipping analytics (no job name available)")
    else:
        if verbose:
            print_step("4", "Skipping API test (offline mode)")
    
    # Step 7: Cleanup
    if not no_cleanup:
        cleanup_tmp_directory()
    elif verbose:
        print(f"\n📁 Temporary files preserved in: {tmp_dir}")
    
    # Success summary
    if verbose:
        print_header("Validation Complete")
        print("🎉 All validation checks passed successfully!")
        print(f"✅ Model: {model_path}")
        print(f"✅ Scenario: {scenario_path}")
        print(f"✅ Environment: {environment}")
        if not skip_api_test:
            print("✅ Remote API integration test passed")
            if generate_analytics:
                print("✅ Analytics data generated")
        print("\n💚 Ready to commit to main branch!")
    
    return True


# Expose key functions for external use
__all__ = [
    # Main validation function
    'validate_model_changes',
    
    # Configuration
    'DEFAULT_MODEL',
    'DEFAULT_SCENARIO', 
    'DEFAULT_ENVIRONMENT',
    
    # Utility functions
    'print_header',
    'print_step',
    
    # File operations
    'validate_file_exists',
    'load_json_file',
    'save_json_file',
    'validate_json_files',
    
    # Scenario operations
    'apply_scenario_to_model',
    'apply_scenario_to_model_data',
    
    # API operations
    'test_api_health',
    'submit_and_poll_job',
    
    # Cleanup operations
    'cleanup_tmp_directory',
    'ensure_tmp_directory',
    
    # Analytics functions
    'extract_ulid_from_job_name',
    'fetch_analytics_data',
    'convert_to_csv',
    'save_analytics_csv',
    'process_job_analytics',
]