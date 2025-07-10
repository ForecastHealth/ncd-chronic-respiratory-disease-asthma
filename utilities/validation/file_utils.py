"""
File handling utilities for model validation.

This module provides functions for loading, saving, and validating JSON files.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def validate_file_exists(file_path: str, file_type: str) -> None:
    """Validate that a file exists."""
    if not Path(file_path).exists():
        print(f"❌ Error: {file_type} file does not exist: {file_path}")
        sys.exit(1)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: Failed to read {file_path}: {e}")
        sys.exit(1)


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Error: Failed to write {file_path}: {e}")
        sys.exit(1)


def validate_json_files(model_path: str, scenario_path: str) -> bool:
    """Validate that JSON files are properly formatted."""
    print("🔍 Validating JSON file formats...")
    
    try:
        # Validate model file
        model_data = load_json_file(model_path)
        print(f"✅ Model JSON is valid ({len(json.dumps(model_data))} characters)")
        
        # Validate scenario file
        scenario_data = load_json_file(scenario_path)
        print(f"✅ Scenario JSON is valid ({len(json.dumps(scenario_data))} characters)")
        
        # Check scenario structure
        if 'parameters' not in scenario_data:
            print("❌ Error: Scenario file missing 'parameters' section")
            return False
        
        print(f"✅ Scenario contains {len(scenario_data['parameters'])} parameters")
        return True
        
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False