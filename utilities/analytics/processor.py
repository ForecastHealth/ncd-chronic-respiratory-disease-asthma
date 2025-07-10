"""
Main analytics processor for handling complete analytics workflow.

This module provides the main entry point for processing job analytics
from ULID extraction through CSV generation.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .ulid_parser import extract_ulid_from_job_name, validate_ulid_format
from .api_client import fetch_and_save_analytics
from .csv_converter import save_analytics_csv, convert_json_file_to_csv, preview_csv_data


# Configuration
DEFAULT_VALIDATION_DIR = "validation"
DEFAULT_ENVIRONMENT = "standard"


def get_validation_output_dir(
    model_name: str, 
    scenario_name: str, 
    base_dir: str = None
) -> Path:
    """
    Get standardized validation output directory.
    
    Creates directory structure: validation/model_name/scenario_name/
    
    Args:
        model_name: Name of the model (e.g., "model")
        scenario_name: Name of the scenario (e.g., "default_scenario")
        base_dir: Base directory (defaults to current working directory)
        
    Returns:
        Path: Validation output directory path
    """
    if base_dir is None:
        base_dir = os.getcwd()
    
    # Clean names for directory structure
    clean_model = model_name.replace('.json', '').replace('/', '_')
    clean_scenario = scenario_name.replace('.json', '').replace('/', '_')
    
    validation_dir = Path(base_dir) / DEFAULT_VALIDATION_DIR / clean_model / clean_scenario
    validation_dir.mkdir(parents=True, exist_ok=True)
    
    return validation_dir


def generate_csv_filename(ulid: str) -> str:
    """
    Generate standardized CSV filename for analytics output.
    
    Args:
        ulid: The ULID identifier
        
    Returns:
        str: Standardized filename (just ULID.csv)
    """
    return f"{ulid}.csv"


def process_job_analytics(
    job_name: str,
    model_name: str,
    scenario_name: str,
    environment: str = DEFAULT_ENVIRONMENT,
    base_dir: str = None,
    preview: bool = True,
    **api_kwargs
) -> Dict[str, Any]:
    """
    Complete analytics processing pipeline for a completed job.
    
    Args:
        job_name: The completed job name containing ULID
        model_name: Name of the model for directory structure
        scenario_name: Name of the scenario for directory structure
        environment: API environment (default: 'standard')
        base_dir: Base directory (default: current working directory)
        preview: Whether to show data preview
        **api_kwargs: Additional parameters for API client
        
    Returns:
        Dict containing results and file paths
    """
    result = {
        "success": False,
        "ulid": None,
        "data_records": 0,
        "csv_path": None,
        "error": None
    }
    
    print(f"🔄 Processing analytics for job: {job_name}")
    
    try:
        # Step 1: Extract ULID from job name
        ulid = extract_ulid_from_job_name(job_name, environment)
        if not ulid:
            result["error"] = f"Could not extract ULID from job name: {job_name}"
            print(f"❌ {result['error']}")
            return result
        
        if not validate_ulid_format(ulid):
            result["error"] = f"Invalid ULID format: {ulid}"
            print(f"❌ {result['error']}")
            return result
        
        result["ulid"] = ulid
        print(f"✅ Extracted ULID: {ulid}")
        
        # Step 2: Setup output directory
        validation_dir = get_validation_output_dir(model_name, scenario_name, base_dir)
        print(f"📁 Output directory: {validation_dir}")
        
        # Step 3: Fetch analytics data (without saving JSON)
        print(f"🔍 Fetching analytics data...")
        from .api_client import fetch_analytics_data
        data = fetch_analytics_data(
            environment=environment,
            ulid=ulid,
            **api_kwargs
        )
        
        if data is None:
            result["error"] = "Failed to fetch analytics data from API"
            print(f"❌ {result['error']}")
            return result
        
        result["data_records"] = len(data)
        
        # Step 4: Save directly to CSV
        csv_filename = generate_csv_filename(ulid)
        csv_path = validation_dir / csv_filename
        
        print(f"📄 Converting to CSV...")
        if save_analytics_csv(data, str(csv_path)):
            result["csv_path"] = str(csv_path)
            print(f"✅ CSV saved: {csv_path}")
        else:
            print(f"⚠️  Failed to save CSV file")
        
        # Step 5: Preview data
        if preview and data:
            preview_csv_data(data)
        
        result["success"] = True
        print(f"🎉 Analytics processing complete!")
        print(f"📊 Records processed: {len(data)}")
        
        return result
        
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print(f"❌ {result['error']}")
        return result


def process_multiple_jobs(
    job_names: List[str],
    model_name: str,
    scenario_name: str,
    environment: str = DEFAULT_ENVIRONMENT,
    base_dir: str = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Process analytics for multiple jobs.
    
    Args:
        job_names: List of job names to process
        model_name: Name of the model for directory structure
        scenario_name: Name of the scenario for directory structure
        environment: API environment
        base_dir: Base directory
        **kwargs: Additional parameters for process_job_analytics
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    print(f"🔄 Processing analytics for {len(job_names)} jobs")
    print("=" * 60)
    
    for i, job_name in enumerate(job_names, 1):
        print(f"\n📋 Job {i}/{len(job_names)}")
        result = process_job_analytics(
            job_name=job_name,
            model_name=model_name,
            scenario_name=scenario_name,
            environment=environment,
            base_dir=base_dir,
            preview=False,  # Disable preview for batch processing
            **kwargs
        )
        results.append(result)
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print("\n" + "=" * 60)
    print(f"📊 Batch Processing Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {get_validation_output_dir(model_name, scenario_name, base_dir)}")
    
    return results