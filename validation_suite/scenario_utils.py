"""
Scenario application and validation utilities.
"""
import json
import sys
from typing import Dict, Any
from pathlib import Path

try:
    from jsonpath_ng.ext import parse
except ImportError:
    print("Error: jsonpath-ng is required. Install with: pip install jsonpath-ng", file=sys.stderr)
    sys.exit(1)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Loads and parses a JSON file, exiting on error."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"L Error reading or parsing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def save_json_file(data: Dict[str, Any], file_path: str):
    """Saves data to a JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"L Error writing to {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def apply_scenario_to_model_data(model: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Applies scenario parameters to a model data dictionary."""
    if 'parameters' not in scenario:
        print("L Error: Scenario file must contain a 'parameters' section", file=sys.stderr)
        return model

    for param_name, param_config in scenario['parameters'].items():
        if 'paths' not in param_config or 'value' not in param_config:
            continue
        
        value = param_config['value']
        for path_str in param_config['paths']:
            jsonpath_expr = parse(path_str)
            jsonpath_expr.update(model, value)
    return model
    
def apply_scenario_to_model(model_path: str, scenario_path: str, output_path: str) -> bool:
    """Loads model and scenario, applies changes, and saves the result."""
    model = load_json_file(model_path)
    scenario = load_json_file(scenario_path)
    updated_model = apply_scenario_to_model_data(model, scenario)
    save_json_file(updated_model, output_path)
    return True

def validate_json_files(model_path: str, scenario_path: str) -> bool:
    """Validates that JSON files are well-formed."""
    try:
        load_json_file(model_path)
        load_json_file(scenario_path)
        return True
    except SystemExit: # load_json_file calls sys.exit on error
        return False