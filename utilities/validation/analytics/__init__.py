"""
Analytics module for processing simulation results.

This module provides tools for extracting ULIDs from job names,
fetching analytics data from the API, and converting to CSV format.

Main Functions:
    extract_ulid_from_job_name: Extract ULID from completed job names
    fetch_analytics_data: Fetch analytics data from API
    convert_to_csv: Convert JSON analytics data to CSV format
    process_job_analytics: Complete pipeline for job analytics processing
"""

from .ulid_parser import extract_ulid_from_job_name, validate_ulid_format
from .api_client import fetch_analytics_data
from .csv_converter import convert_to_csv, save_analytics_csv
from .processor import process_job_analytics

__all__ = [
    'extract_ulid_from_job_name',
    'validate_ulid_format',
    'fetch_analytics_data', 
    'convert_to_csv',
    'save_analytics_csv',
    'process_job_analytics',
]