"""
Scenario application utilities for model validation.

This module handles applying scenario parameters to model JSON files using JSONPath expressions.
"""

import sys
from typing import Dict, Any

try:
    from jsonpath_ng import parse
    from jsonpath_ng.ext import parse as parse_ext
except ImportError:
    print("Error: jsonpath-ng is required. Install with: pip install jsonpath-ng", file=sys.stderr)
    sys.exit(1)

from .file_utils import load_json_file, save_json_file


def apply_jsonpath_value(model: Dict[str, Any], jsonpath_expr: str, value: Any) -> bool:
    """Apply a value to a model using a JSONPath expression."""
    try:
        # Try extended parser first for complex expressions
        try:
            jsonpath_parser = parse_ext(jsonpath_expr)
        except Exception:
            # Fall back to basic parser
            jsonpath_parser = parse(jsonpath_expr)
        
        # Find matches
        matches = jsonpath_parser.find(model)
        
        if not matches:
            print(f"⚠️  Warning: JSONPath '{jsonpath_expr}' found no matches")
            return False
        
        # Update all matches
        for match in matches:
            match.full_path.update(model, value)
        
        print(f"✅ Applied value {value} to {len(matches)} location(s) via '{jsonpath_expr}'")
        return True
        
    except Exception as e:
        print(f"❌ Error: Failed to apply JSONPath '{jsonpath_expr}': {e}")
        return False


def apply_scenario_to_model_data(model: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Apply scenario parameters to the model data."""
    if 'parameters' not in scenario:
        print("❌ Error: Scenario file must contain a 'parameters' section")
        sys.exit(1)
    
    applied_count = 0
    failed_count = 0
    
    for param_name, param_config in scenario['parameters'].items():
        if 'paths' not in param_config or 'value' not in param_config:
            print(f"⚠️  Warning: Parameter '{param_name}' missing 'paths' or 'value' field")
            continue
        
        value = param_config['value']
        paths = param_config['paths']
        
        if not isinstance(paths, list):
            print(f"⚠️  Warning: Parameter '{param_name}' paths must be a list")
            continue
        
        print(f"\n🔧 Applying parameter: {param_name}")
        print(f"   Value: {value}")
        
        param_applied = False
        for jsonpath_expr in paths:
            if apply_jsonpath_value(model, jsonpath_expr, value):
                param_applied = True
            else:
                failed_count += 1
        
        if param_applied:
            applied_count += 1
    
    print(f"\n📊 Summary: Applied {applied_count} parameters successfully")
    if failed_count > 0:
        print(f"⚠️  Warning: {failed_count} JSONPath expressions failed to find matches")
    
    return model


def apply_scenario_to_model(model_path: str, scenario_path: str, output_path: str) -> bool:
    """Apply scenario to model and save to output file."""
    try:
        print(f"📂 Loading model: {model_path}")
        model = load_json_file(model_path)
        
        print(f"📂 Loading scenario: {scenario_path}")
        scenario = load_json_file(scenario_path)
        
        print(f"\n🔄 Applying scenario '{scenario.get('metadata', {}).get('label', 'Unknown')}' to model...")
        updated_model = apply_scenario_to_model_data(model, scenario)
        
        print(f"\n💾 Saving updated model to: {output_path}")
        save_json_file(updated_model, output_path)
        
        print("✅ Scenario application completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying scenario: {e}")
        return False