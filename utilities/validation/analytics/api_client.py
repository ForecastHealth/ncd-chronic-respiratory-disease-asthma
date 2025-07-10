"""
Analytics API client for fetching simulation results data.

This module provides functionality to fetch analytics data from the
forecast health analytics API.
"""

import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path


# Configuration
ANALYTICS_BASE_URL = "https://analytics.forecasthealth.org"


def fetch_analytics_data(
    environment: str, 
    ulid: str,
    event_type: str = "*",
    group_by: List[str] = None,
    group_by_date: str = "timestamp:year",
    aggregations: str = "value:last",
    timeout: int = 30
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch analytics data from the analytics API.
    
    Args:
        environment: The environment name (e.g., 'standard')
        ulid: The ULID identifier for the simulation
        event_type: Event type filter (default: '*' for all)
        group_by: List of fields to group by (default: ['element_label'])
        group_by_date: Date grouping specification (default: 'timestamp:year')
        aggregations: Aggregation specification (default: 'value:last')
        timeout: Request timeout in seconds
        
    Returns:
        List[Dict]: Analytics data as JSON array, None if error
    """
    if group_by is None:
        group_by = ["element_label"]
    
    # Build query parameters
    params = {
        "event_type": event_type,
        "group_by_date": group_by_date,
        "aggregations": aggregations
    }
    
    # Add multiple group_by parameters
    for field in group_by:
        if "group_by" not in params:
            params["group_by"] = field
        else:
            # Handle multiple group_by params - convert to list
            if isinstance(params["group_by"], str):
                params["group_by"] = [params["group_by"]]
            params["group_by"].append(field)
    
    url = f"{ANALYTICS_BASE_URL}/analytics/{environment}/{ulid}"
    
    print(f"🔍 Fetching analytics data from: {url}")
    print(f"📊 Environment: {environment}")
    print(f"🆔 ULID: {ulid}")
    print(f"📋 Parameters: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched {len(data)} records")
            return data
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to analytics API. Check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {timeout} seconds")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from analytics API")
        return None
    except Exception as e:
        print(f"❌ Unexpected error fetching analytics data: {e}")
        return None


def save_analytics_json(data: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Save analytics data to JSON file.
    
    Args:
        data: Analytics data to save
        output_path: Path to save the JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Analytics data saved to: {output_path}")
        print(f"📊 Records saved: {len(data)}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving analytics JSON: {e}")
        return False


def fetch_and_save_analytics(
    environment: str,
    ulid: str, 
    output_path: str,
    **kwargs
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch analytics data and save to JSON file.
    
    Args:
        environment: The environment name
        ulid: The ULID identifier
        output_path: Path to save the JSON file
        **kwargs: Additional parameters for fetch_analytics_data
        
    Returns:
        List[Dict]: The fetched data, None if error
    """
    data = fetch_analytics_data(environment, ulid, **kwargs)
    
    if data is not None:
        if save_analytics_json(data, output_path):
            return data
        else:
            return None
    
    return None