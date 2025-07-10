#!/usr/bin/env python3
"""
Terminal User Interface (TUI) for Model Validation

A simple TUI that allows users to select model, scenario, countries,
and environment options for running the validation script.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
import glob


def load_env_file(env_file_path: str = ".env.local") -> Dict[str, str]:
    """Load environment variables from .env.local file."""
    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def load_json_file(file_path: str) -> Any:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def get_model_files() -> List[str]:
    """Get list of available model files."""
    models = []
    # Check for model.json in root
    if os.path.exists("model.json"):
        models.append("model.json")
    
    # Check for any other JSON files that might be models
    for pattern in ["*.json", "models/*.json"]:
        for file in glob.glob(pattern):
            if file not in models and not file.startswith("list_") and "scenario" not in file:
                models.append(file)
    
    return sorted(models) if models else ["model.json"]


def get_scenario_files() -> List[str]:
    """Get list of available scenario files."""
    scenarios = []
    
    # Check scenario-templates directory
    template_dir = "scenario-templates"
    if os.path.exists(template_dir):
        for file in glob.glob(f"{template_dir}/*.json"):
            scenarios.append(file)
    
    # Check scenarios directory
    scenario_dir = "scenarios"
    if os.path.exists(scenario_dir):
        for file in glob.glob(f"{scenario_dir}/*.json"):
            scenarios.append(file)
    
    return sorted(scenarios) if scenarios else ["scenarios/default_scenario.json"]


def get_country_files() -> List[str]:
    """Get list of available country files."""
    country_files = []
    for pattern in ["list_of_*.json", "data/*countries*.json"]:
        for file in glob.glob(pattern):
            if "countries" in file.lower():
                country_files.append(file)
    
    return sorted(country_files) if country_files else []


def get_environments() -> List[str]:
    """Get list of available environments."""
    return ["default", "standard", "appendix_3"]


def print_header():
    """Print the TUI header."""
    print("=" * 60)
    print("🔍 Model Validation TUI")
    print("=" * 60)
    print()


def print_menu(title: str, options: List[str], current_selection: str = None) -> int:
    """Print a menu and get user selection."""
    print(f"\n📋 {title}")
    print("-" * 40)
    
    for i, option in enumerate(options, 1):
        marker = "→" if option == current_selection else " "
        print(f"{marker} {i}. {option}")
    
    print(f"  {len(options) + 1}. Back/Skip")
    print()
    
    while True:
        try:
            choice = input("Select option (number): ").strip()
            if choice == "":
                continue
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num - 1  # Return 0-based index
            elif choice_num == len(options) + 1:
                return -1  # Back/Skip
            else:
                print(f"Please enter a number between 1 and {len(options) + 1}")
        except ValueError:
            print("Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\n\n⏹️  Cancelled by user")
            sys.exit(0)


def confirm_selection(selections: Dict[str, str]) -> bool:
    """Show final selections and confirm."""
    print("\n" + "=" * 60)
    print("📋 Review Your Selections")
    print("=" * 60)
    
    for key, value in selections.items():
        print(f"{key:15}: {value}")
    
    print("\n" + "-" * 60)
    
    while True:
        try:
            confirm = input("Run validation with these settings? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
        except (KeyboardInterrupt, EOFError):
            print("\n\n⏹️  Cancelled by user")
            sys.exit(0)


def run_validation(selections: Dict[str, str]) -> None:
    """Run the validation script with selected parameters."""
    print("\n" + "=" * 60)
    print("🚀 Running Validation")
    print("=" * 60)
    
    # Build command for the enhanced validation system (SQLite database)
    cmd = ["python3", "scripts/validate_changes.py"]
    
    # Add required parameters
    cmd.extend(["--model", selections["Model"]])
    cmd.extend(["--environment", selections["Environment"]])
    
    # Add optional parameters  
    if selections.get("Countries") and selections["Countries"] != "None (single country)":
        cmd.extend(["--countries-file", selections["Countries"]])
        
    # For scenarios, we need to determine how to pass the scenario
    # The scripts/validate_changes.py expects scenarios to be in a scenarios directory
    # Let's add the scenarios directory parameter if it's a template
    scenario_path = selections["Scenario"]
    if "scenario-templates/" in scenario_path:
        cmd.extend(["--scenarios-dir", "scenario-templates"])
        scenario_name = Path(scenario_path).stem
        cmd.extend(["--scenarios", scenario_name])
    else:
        # If it's not a template, we may need to handle differently
        # For now, let's just use the scenarios directory approach
        scenario_dir = str(Path(scenario_path).parent)
        scenario_name = Path(scenario_path).stem
        cmd.extend(["--scenarios-dir", scenario_dir])
        cmd.extend(["--scenarios", scenario_name])
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        # Run the validation
        result = subprocess.run(cmd, check=False, cwd=Path.cwd())
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ Validation completed successfully!")
        else:
            print("❌ Validation failed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running validation: {e}")


def main():
    """Main TUI loop."""
    print_header()
    
    # Load environment defaults
    env_vars = load_env_file()
    default_env = env_vars.get("ENVIRONMENT", "appendix_3")
    
    # Initialize selections
    selections = {
        "Model": "model.json",
        "Scenario": "scenario-templates/default_scenario.json", 
        "Environment": default_env,
        "Countries": "None (single country)"
    }
    
    # Get available options
    model_files = get_model_files()
    scenario_files = get_scenario_files()
    country_files = ["None (single country)"] + get_country_files()
    environments = get_environments()
    
    # Main menu loop
    while True:
        print(f"\n🎯 Current Selections:")
        for key, value in selections.items():
            print(f"   {key:15}: {value}")
        
        print(f"\n📋 Main Menu")
        print("-" * 40)
        print("  1. Select Model")
        print("  2. Select Scenario") 
        print("  3. Select Environment")
        print("  4. Select Countries (optional)")
        print("  5. Run Validation")
        print("  6. Exit")
        print()
        
        try:
            choice = input("Select option (number): ").strip()
            
            if choice == "1":
                # Select model
                idx = print_menu("Select Model File", model_files, selections["Model"])
                if idx >= 0:
                    selections["Model"] = model_files[idx]
                    
            elif choice == "2":
                # Select scenario
                idx = print_menu("Select Scenario File", scenario_files, selections["Scenario"])
                if idx >= 0:
                    selections["Scenario"] = scenario_files[idx]
                    
            elif choice == "3":
                # Select environment
                idx = print_menu("Select Environment", environments, selections["Environment"])
                if idx >= 0:
                    selections["Environment"] = environments[idx]
                    
            elif choice == "4":
                # Select countries
                idx = print_menu("Select Countries File", country_files, selections["Countries"])
                if idx >= 0:
                    selections["Countries"] = country_files[idx]
                    
            elif choice == "5":
                # Run validation
                if confirm_selection(selections):
                    run_validation(selections)
                    
                    # Ask if user wants to run again
                    print("\n" + "-" * 60)
                    while True:
                        try:
                            again = input("Run another validation? (y/n): ").strip().lower()
                            if again in ['y', 'yes']:
                                break
                            elif again in ['n', 'no']:
                                print("\n👋 Goodbye!")
                                sys.exit(0)
                            else:
                                print("Please enter 'y' or 'n'")
                        except (KeyboardInterrupt, EOFError):
                            print("\n\n⏹️  Cancelled by user")
                            sys.exit(0)
                    
            elif choice == "6":
                print("\n👋 Goodbye!")
                sys.exit(0)
                
            else:
                print("Please enter a number between 1 and 6")
                
        except (KeyboardInterrupt, EOFError):
            print("\n\n⏹️  Cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()