"""
CSV conversion utilities for analytics data.

This module provides functionality to convert JSON analytics data
to CSV format for analysis and comparison.
"""

import csv
import json
from typing import Dict, Any, List, Optional, Set
from pathlib import Path


def extract_csv_headers(data: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all unique keys from analytics data to use as CSV headers.
    
    Args:
        data: List of analytics records
        
    Returns:
        List[str]: Sorted list of unique column names
    """
    headers: Set[str] = set()
    
    for record in data:
        headers.update(record.keys())
    
    # Sort headers for consistent output
    return sorted(headers)


def convert_to_csv(data: List[Dict[str, Any]]) -> str:
    """
    Convert JSON analytics data to CSV format.
    
    Args:
        data: List of analytics records
        
    Returns:
        str: CSV formatted string
    """
    if not data:
        return ""
    
    headers = extract_csv_headers(data)
    
    # Create CSV content
    csv_lines = []
    
    # Add header row
    csv_lines.append(','.join(f'"{header}"' for header in headers))
    
    # Add data rows
    for record in data:
        row = []
        for header in headers:
            value = record.get(header, "")
            # Handle different data types
            if value is None:
                row.append('""')
            elif isinstance(value, str):
                # Escape quotes in string values
                escaped_value = value.replace('"', '""')
                row.append(f'"{escaped_value}"')
            else:
                # Convert numbers and other types to string
                row.append(f'"{str(value)}"')
        
        csv_lines.append(','.join(row))
    
    return '\n'.join(csv_lines)


def save_analytics_csv(
    data: List[Dict[str, Any]], 
    output_path: str,
    include_metadata: bool = True
) -> bool:
    """
    Save analytics data to CSV file.
    
    Args:
        data: Analytics data to save
        output_path: Path to save the CSV file
        include_metadata: Whether to include metadata comment at top of file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            if include_metadata:
                f.write(f"# Analytics data export\n")
                f.write(f"# Records: {len(data)}\n")
                if data:
                    headers = extract_csv_headers(data)
                    f.write(f"# Columns: {len(headers)}\n")
                    f.write(f"# Headers: {', '.join(headers)}\n")
                f.write(f"#\n")
            
            csv_content = convert_to_csv(data)
            f.write(csv_content)
        
        print(f"💾 Analytics CSV saved to: {output_path}")
        print(f"📊 Records exported: {len(data)}")
        if data:
            headers = extract_csv_headers(data)
            print(f"📋 Columns: {len(headers)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving analytics CSV: {e}")
        return False


def convert_json_file_to_csv(
    json_path: str, 
    csv_path: str,
    include_metadata: bool = True
) -> bool:
    """
    Convert a JSON file containing analytics data to CSV.
    
    Args:
        json_path: Path to input JSON file
        csv_path: Path to output CSV file
        include_metadata: Whether to include metadata comments
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"❌ JSON file must contain an array of objects")
            return False
        
        # Convert and save
        return save_analytics_csv(data, csv_path, include_metadata)
        
    except FileNotFoundError:
        print(f"❌ JSON file not found: {json_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in file {json_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error converting JSON to CSV: {e}")
        return False


def preview_csv_data(data: List[Dict[str, Any]], max_rows: int = 5) -> None:
    """
    Print a preview of the CSV data.
    
    Args:
        data: Analytics data to preview
        max_rows: Maximum number of rows to show
    """
    if not data:
        print("📄 No data to preview")
        return
    
    headers = extract_csv_headers(data)
    
    print(f"📄 CSV Preview ({len(data)} total records):")
    print("-" * 60)
    
    # Print headers
    print(" | ".join(f"{header:15}" for header in headers[:4]))  # Show first 4 columns
    if len(headers) > 4:
        print(f" | ... ({len(headers)-4} more columns)")
    print("-" * 60)
    
    # Print sample rows
    for i, record in enumerate(data[:max_rows]):
        row_values = []
        for j, header in enumerate(headers[:4]):
            value = str(record.get(header, ""))[:15]  # Truncate long values
            row_values.append(f"{value:15}")
        
        print(" | ".join(row_values))
        if len(headers) > 4:
            print(" | ...")
    
    if len(data) > max_rows:
        print(f"... ({len(data) - max_rows} more rows)")
    
    print("-" * 60)