### **Refactoring Plan**

**Goal:** Create a single, unified `validation_suite` package that contains all core logic. The TUI and CLI will be clean entry points into this package, and all validation runs will be recorded in the SQLite database.

**Strategy:** We will build the new, clean structure first, copy and modify the code to work within it, and only then delete the old, redundant files.

---

### **Phase 1: Create the New Directory Structure**

Execute these commands from your project's root directory.

```bash
# 1. Create the main package directory
mkdir -p validation_suite/analytics

# 2. Create the scripts directory if it doesn't exist
mkdir -p scripts
```

**Verification:** You should now have a `validation_suite/` directory with an `analytics/` subdirectory inside it.

---

### **Phase 2: Consolidate Code - Move and Rename Key Files**

This phase brings the *correct* versions of your files into the new structure.

```bash
# Move the core database logic
mv utilities/validation_db.py validation_suite/db.py

# Move the DB-aware multi-country runner
mv utilities/multi_country.py validation_suite/multi_country.py

# Move the central runner/orchestrator
mv utilities/run_all_validations.py validation_suite/runner.py

# Move the TUI
mv utilities/utilities.txt validation_suite/tui.py

# Move the new, unified CLI
mv utilities/validate_changes.py validation_suite/cli.py

# Move the single, correct version of country_utils
mv utilities/country_utils.py validation_suite/country_utils.py

# Consolidate scenario logic into a new file
# (We'll populate this in the next phase)
touch validation_suite/scenario_utils.py

# Consolidate API logic for the main simulation runs
mv utilities/validation/api_client.py validation_suite/api_client.py

# -- Analytics Files --
# Move the DB-aware analytics processor and rename it
mv utilities/analytics/database_processor.py validation_suite/analytics/processor.py

# Move the analytics API client
mv utilities/analytics/api_client.py validation_suite/analytics/api_client.py

# Move the ULID parser
mv utilities/analytics/ulid_parser.py validation_suite/analytics/ulid_parser.py

# -- Standalone Scripts --
# These are one-off tools, not part of the core library. They belong in `scripts/`.
mv utilities/apply_scenario.py scripts/
mv utilities/upload_project.py scripts/
mv utilities/create_country_scenarios.py scripts/
mv utilities/validate_scenario.py scripts/
mv utilities/create_economic_analyses.py scripts/
mv utilities/run_economic_analyses.py scripts/
```

**Verification:** Your `validation_suite/` directory should now contain the moved files. The old `utilities/` and `utilities/validation/` directories still exist but are now partially empty.

---

### **Phase 3: Code Modification - Update Files for the New Structure**

This is the most critical phase. For each file, **replace its entire contents** with the provided code block. This prevents any errors from partial edits.

#### **Step 3.1: Initialize Packages**

1.  **File:** `validation_suite/__init__.py` (Create this file)
    **Action:** Add the following content. This makes `validation_suite` a Python package.
    ```python
    # This file makes the validation_suite directory a Python package.
    ```
2.  **File:** `validation_suite/analytics/__init__.py` (Create this file)
    **Action:** Add the following content.
    ```python
    # This file makes the analytics directory a Python package.
    ```

#### **Step 3.2: Update Core Logic Files**

1.  **File:** `validation_suite/runner.py`
    **Action:** Replace the entire contents of the file. This version uses direct imports instead of `subprocess`.
    ```python
    #!/usr/bin/env python3
    """
    Enhanced Multi-Country Validation Runner

    This script orchestrates validation runs across all countries and scenarios,
    with database integration for tracking results and incremental execution.
    """
    import os
    import subprocess
    import json
    import logging
    from pathlib import Path
    from typing import Dict, Any, List, Tuple, Optional

    from .db import ValidationDatabase
    from .country_utils import load_countries_list
    from .multi_country import validate_multiple_countries

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


    class EnhancedValidationRunner:
        """
        Enhanced validation runner with database integration and incremental execution.
        """
        def __init__(self, db_path: str = "validation_results.db"):
            self.db = ValidationDatabase(db_path)
            self.db_path = db_path

        def get_git_commit(self) -> str:
            try:
                return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
            except subprocess.CalledProcessError:
                logger.warning("Could not get git commit hash")
                return "unknown"

        def discover_scenarios(self, scenario_templates_dir: str = "scenario-templates") -> List[str]:
            scenario_dir = Path(scenario_templates_dir)
            if not scenario_dir.exists():
                logger.error(f"Scenario templates directory not found: {scenario_dir}")
                return []
            scenarios = [str(f) for f in scenario_dir.glob("*.json")]
            logger.info(f"Discovered {len(scenarios)} scenario templates")
            return scenarios

        def load_countries(self, countries_file: str = "list_of_countries.json") -> List[Dict[str, str]]:
            try:
                countries = load_countries_list(countries_file)
                logger.info(f"Loaded {len(countries)} countries")
                return countries
            except Exception as e:
                logger.error(f"Failed to load countries: {e}")
                return []

        def generate_all_combinations(self, countries: List[Dict[str, str]], scenarios: List[str]) -> List[Tuple[str, str, str]]:
            combinations = []
            for country in countries:
                for scenario_path in scenarios:
                    scenario_name = Path(scenario_path).stem
                    combinations.append((country['iso3'], scenario_name, scenario_path))
            logger.info(f"Generated {len(combinations)} country/scenario combinations")
            return combinations

        def filter_combinations_needing_rerun(self, combinations: List[Tuple[str, str, str]], git_commit: str) -> List[Tuple[str, str, str]]:
            needed = [combo for combo in combinations if self.db.needs_rerun(combo[0], combo[1], git_commit)]
            logger.info(f"Found {len(needed)} combinations needing rerun")
            return needed

        def run_validation_for_scenario_group(self, model_path: str, scenario_path: str, countries_to_run: List[Dict[str, str]], environment: str, max_instances: int, **kwargs) -> bool:
            scenario_name = Path(scenario_path).stem
            logger.info(f"Running validation for scenario: {scenario_name} across {len(countries_to_run)} countries.")
            
            # Create a temporary file containing only the countries for this run
            temp_countries_path = f"temp_countries_{scenario_name}.json"
            with open(temp_countries_path, 'w') as f:
                json.dump({"countries": countries_to_run}, f)

            try:
                success = validate_multiple_countries(
                    model_path=model_path,
                    scenario_path=scenario_path,
                    countries_path=temp_countries_path,
                    environment=environment,
                    poll_interval=10,
                    max_wait_time=7200,
                    skip_api_test=False,
                    no_cleanup=False,
                    verbose=True,
                    generate_analytics=True,
                    max_instances=max_instances,
                    database_path=self.db_path,
                    **kwargs
                )
            finally:
                if os.path.exists(temp_countries_path):
                    os.remove(temp_countries_path)
            
            return success

        def run(self, model_path: str, countries_file: str, scenario_templates_dir: str, environment: str, max_instances: int, force_rerun: bool, specific_countries: Optional[List[str]], specific_scenarios: Optional[List[str]], **kwargs) -> Dict[str, Any]:
            logger.info("Starting enhanced validation run")
            git_commit = self.get_git_commit()
            logger.info(f"Current git commit: {git_commit}")

            all_scenarios = self.discover_scenarios(scenario_templates_dir)
            if not all_scenarios:
                return {"success": False, "error": "No scenarios found"}

            all_countries = self.load_countries(countries_file)
            if not all_countries:
                return {"success": False, "error": "No countries found"}

            # Filter based on specific requests
            scenarios_to_run = [s for s in all_scenarios if not specific_scenarios or Path(s).stem in specific_scenarios]
            countries_to_run = [c for c in all_countries if not specific_countries or c['iso3'] in specific_countries]
            
            logger.info(f"Targeting {len(scenarios_to_run)} scenarios and {len(countries_to_run)} countries.")

            # Group combinations by scenario for efficient processing
            scenario_groups = {}
            for scenario_path in scenarios_to_run:
                scenario_name = Path(scenario_path).stem
                combinations = self.generate_all_combinations(countries_to_run, [scenario_path])
                
                if not force_rerun:
                    combinations = self.filter_combinations_needing_rerun(combinations, git_commit)
                
                if combinations:
                    # Get the full country dicts for the combinations that need running
                    iso3_to_run = {combo[0] for combo in combinations}
                    countries_for_this_scenario = [c for c in countries_to_run if c['iso3'] in iso3_to_run]
                    scenario_groups[scenario_name] = {
                        "scenario_path": scenario_path,
                        "countries": countries_for_this_scenario
                    }

            if not scenario_groups:
                logger.info("All targeted combinations are up-to-date. Nothing to run.")
                return {"success": True, "message": "All combinations up to date"}

            total_jobs_to_run = sum(len(group['countries']) for group in scenario_groups.values())
            run_id = self.db.start_validation_run(git_commit, total_jobs_to_run)
            logger.info(f"Started validation run {run_id} with {total_jobs_to_run} jobs.")

            successful_runs = 0
            failed_runs = 0
            for scenario, group_info in scenario_groups.items():
                try:
                    # Pass the run_id to the validation function
                    kwargs_with_runid = {**kwargs, 'run_id': run_id}
                    success = self.run_validation_for_scenario_group(
                        model_path, group_info["scenario_path"], group_info["countries"], environment, max_instances, **kwargs_with_runid
                    )
                    if success:
                        successful_runs +=1
                        logger.info(f"✅ Scenario group {scenario} completed successfully.")
                    else:
                        failed_runs += 1
                        logger.error(f"❌ Scenario group {scenario} failed.")
                except Exception as e:
                    failed_runs += 1
                    logger.error(f"❌ Unhandled exception processing scenario {scenario}: {e}", exc_info=True)
            
            # This is tricky because job status is now recorded inside `validate_multiple_countries`. 
            # We will refetch counts from the DB for the final summary.
            with self.db.get_connection() as conn:
                res = conn.execute("SELECT successful_jobs, failed_jobs FROM validation_runs WHERE run_id = ?", (run_id,)).fetchone()
                final_successful, final_failed = res[0], res[1]

            final_status = "completed" if final_failed == 0 else "failed"
            self.db.update_run_status(run_id, final_status, final_successful, final_failed)

            return {
                "success": final_failed == 0,
                "run_id": run_id,
                "total_jobs": total_jobs_to_run,
                "successful_jobs": final_successful,
                "failed_jobs": final_failed
            }
    ```

2.  **File:** `validation_suite/multi_country.py`
    **Action:** Replace the entire contents of the file. This version has corrected relative imports and ensures DB integration.
    ```python
    """
    Multi-country validation logic.

    This module handles the complete workflow for validating models across
    multiple countries, including parallel job submission and analytics generation.
    Enhanced with database integration for tracking validation runs and results.
    """
    import time
    import subprocess
    from pathlib import Path
    from typing import Dict, Any, List, Optional
    from datetime import datetime
    import logging

    from .scenario_utils import apply_scenario_to_model, validate_json_files
    from .api_client import submit_simulation_job, get_job_status, test_api_health
    from .db import ValidationDatabase
    from .analytics.processor import DatabaseAnalyticsProcessor
    from .country_utils import get_country_display_list, create_country_scenario, load_countries_list
    
    logger = logging.getLogger(__name__)

    MAX_INSTANCES = 100

    def get_git_commit() -> str:
        try:
            return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def ensure_tmp_directory() -> Path:
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)
        return tmp_dir

    def cleanup_tmp_directory() -> None:
        # Simplified cleanup logic for this context
        pass

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
        max_instances: int = MAX_INSTANCES,
        database_path: str = "validation_results.db",
        run_id: Optional[int] = None # Expect a run_id from the orchestrator
    ) -> bool:
        """
        Validate model changes across multiple countries for a single scenario.
        """
        if verbose:
            print(f"\n--- Running: {Path(scenario_path).name} ---")

        db = ValidationDatabase(database_path)
        analytics_processor = DatabaseAnalyticsProcessor(database_path)

        if not run_id:
            logger.error("A valid run_id must be provided to validate_multiple_countries.")
            return False

        try:
            countries = load_countries_list(countries_path)
            if not countries:
                return False

            if not validate_json_files(model_path, scenario_path):
                return False

            tmp_dir = ensure_tmp_directory()
            
            if not test_api_health():
                return False

            # This simplified version applies the *same base scenario* to each country's model
            # The country is a parameter within the model itself
            
            # 1. Prepare country-specific models
            prepared_models = {}
            for country in countries:
                iso3 = country['iso3']
                country_model_path = tmp_dir / f"model_{iso3}_{Path(scenario_path).stem}.json"
                
                # Create a temporary scenario file for just this country's iso3 code
                country_scenario_path = tmp_dir / f"scenario_{iso3}_{Path(scenario_path).stem}.json"
                if not create_country_scenario(scenario_path, iso3, str(country_scenario_path)):
                    logger.error(f"Failed to create scenario for {iso3}")
                    continue

                if apply_scenario_to_model(model_path, str(country_scenario_path), str(country_model_path)):
                    prepared_models[iso3] = {'model_path': str(country_model_path), 'name': country['name']}
                else:
                    logger.error(f"Failed to prepare model for {iso3}")

            # 2. Submit jobs
            job_submissions = {}
            for iso3, info in prepared_models.items():
                logger.info(f"Submitting job for {info['name']} ({iso3})")
                job_result = submit_simulation_job(info['model_path'], environment)
                if job_result and 'jobId' in job_result:
                    job_submissions[iso3] = {'job_id': job_result['jobId'], 'job_name': job_result.get('jobName'), 'name': info['name']}
                    db.record_job_result(run_id, iso3, Path(scenario_path).stem, job_result.get('jobName', ''), 'submitted', datetime.now(), None)
                else:
                    db.record_job_result(run_id, iso3, Path(scenario_path).stem, '', 'failed_submission', datetime.now(), datetime.now())

            # 3. Poll for completion
            active_jobs = job_submissions.copy()
            completed_jobs = {}
            start_time = time.time()
            
            while active_jobs and (time.time() - start_time) < max_wait_time:
                jobs_to_remove = []
                for iso3, job_info in active_jobs.items():
                    status_data = get_job_status(job_info['job_id'])
                    if status_data:
                        job_status = status_data.get("jobStatus", "UNKNOWN")
                        if job_status in ["SUCCEEDED", "FAILED"]:
                            jobs_to_remove.append(iso3)
                            completed_jobs[iso3] = {**job_info, 'final_status': job_status, 'status_data': status_data}
                            logger.info(f"Job for {job_info['name']} finished with status: {job_status}")
                
                for iso3 in jobs_to_remove:
                    del active_jobs[iso3]
                
                if active_jobs:
                    time.sleep(poll_interval)
            
            # Handle timeouts
            for iso3, job_info in active_jobs.items():
                completed_jobs[iso3] = {**job_info, 'final_status': 'TIMEOUT'}
                logger.warning(f"Job for {job_info['name']} timed out.")

            # 4. Process analytics and update DB
            all_successful = True
            for iso3, job_info in completed_jobs.items():
                job_status = "success" if job_info['final_status'] == 'SUCCEEDED' else 'failed'
                job_name = job_info.get('job_name')
                
                # Update job result in DB
                db.record_job_result(run_id, iso3, Path(scenario_path).stem, job_name or '', job_status, None, datetime.now())

                if job_status == 'success' and generate_analytics and job_name:
                    analytics_result = analytics_processor.process_job_with_database(
                        job_name=job_name,
                        run_id=run_id,
                        country=iso3,
                        scenario=Path(scenario_path).stem,
                        model_name=Path(model_path).stem,
                        environment=environment,
                        save_csv=False # DB only
                    )
                    if not analytics_result['success']:
                        logger.error(f"Analytics processing failed for {iso3}: {analytics_result.get('error')}")
                
                if job_status != 'success':
                    all_successful = False

            return all_successful

        except Exception as e:
            logger.error(f"Unhandled error in multi-country validation for {scenario_path}: {e}", exc_info=True)
            return False
    ```

3.  **File:** `validation_suite/scenario_utils.py`
    **Action:** Replace the empty file's contents. This combines logic from `apply_scenario.py` and `validate_scenario.py`.
    ```python
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
            print(f"❌ Error reading or parsing {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    def save_json_file(data: Dict[str, Any], file_path: str):
        """Saves data to a JSON file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error writing to {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    def apply_scenario_to_model_data(model: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Applies scenario parameters to a model data dictionary."""
        if 'parameters' not in scenario:
            print("❌ Error: Scenario file must contain a 'parameters' section", file=sys.stderr)
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
    ```

4.  **File:** `validation_suite/analytics/processor.py`
    **Action:** Replace the entire contents of the file. This fixes its internal imports.
    ```python
    """
    Analytics Database Processor
    """
    import logging
    from typing import Dict, Any, List, Optional

    from ..db import ValidationDatabase
    from .api_client import fetch_analytics_data
    from .ulid_parser import extract_ulid_from_job_name, validate_ulid_format

    logger = logging.getLogger(__name__)

    class DatabaseAnalyticsProcessor:
        def __init__(self, db_path: str = "validation_results.db"):
            self.db = ValidationDatabase(db_path)

        def fetch_analytics_for_ulid(self, ulid: str, environment: str = "standard") -> Optional[List[Dict]]:
            try:
                return fetch_analytics_data(environment=environment, ulid=ulid)
            except Exception as e:
                logger.error(f"Failed to fetch analytics for ULID {ulid}: {e}")
                return None

        def process_job_with_database(self, job_name: str, run_id: int, country: str, scenario: str, model_name: str, environment: str, **kwargs) -> Dict[str, Any]:
            result = {"success": False, "ulid": None, "data_records": 0, "error": None}
            
            try:
                ulid = extract_ulid_from_job_name(job_name, environment)
                if not ulid or not validate_ulid_format(ulid):
                    result["error"] = f"Invalid ULID extracted from job name: {job_name}"
                    return result
                result["ulid"] = ulid
                
                analytics_data = self.fetch_analytics_for_ulid(ulid, environment)
                if analytics_data is None:
                    result["error"] = "Failed to fetch analytics data"
                    return result
                
                result["data_records"] = len(analytics_data)
                
                self.db.store_metrics(run_id, country, scenario, ulid, analytics_data)
                logger.info(f"Stored {len(analytics_data)} metrics in DB for {country}/{scenario}")
                
                result["success"] = True
                return result
            except Exception as e:
                result["error"] = str(e)
                logger.error(f"Processing error for {job_name}: {e}", exc_info=True)
                return result
    ```
    
5.  **File:** `validation_suite/tui.py`
    **Action:** Replace the entire contents of the file. This is the direct-integration version.
    ```python
    #!/usr/bin/env python3
    """
    Terminal User Interface (TUI) for Model Validation
    """
    import json
    import os
    import sys
    import glob
    from pathlib import Path
    from typing import List, Dict, Any

    from .runner import EnhancedValidationRunner

    def load_json_file(file_path: str) -> Any:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def get_model_files() -> List[str]:
        return sorted([p for p in glob.glob("*.json") + glob.glob("models/*.json") if "scenario" not in p and "list" not in p]) or ["model.json"]

    def get_scenario_files() -> List[str]:
        return sorted(glob.glob("scenario-templates/*.json")) or ["scenarios/default_scenario.json"]

    def get_country_files() -> List[str]:
        return sorted(glob.glob("list_of_*.json")) or []

    def get_environments() -> List[str]:
        return ["default", "standard", "appendix_3"]

    def print_header():
        print("=" * 60 + "\n" + "🔍 Model Validation TUI".center(60) + "\n" + "=" * 60 + "\n")

    def print_menu(title: str, options: List[str], current_selection: str = None) -> int:
        print(f"\n📋 {title}\n" + "-" * 40)
        for i, option in enumerate(options, 1):
            marker = "→" if option == current_selection else " "
            print(f"{marker} {i}. {option}")
        print(f"  {len(options) + 1}. Back/Skip\n")
        
        while True:
            try:
                choice = input("Select option (number): ").strip()
                if not choice: continue
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return choice_num - 1
                elif choice_num == len(options) + 1:
                    return -1
                else:
                    print(f"Please enter a number between 1 and {len(options) + 1}")
            except (ValueError, KeyboardInterrupt, EOFError):
                print("\n\n⏹️  Cancelled by user")
                sys.exit(0)

    def run_validation(selections: Dict[str, str]) -> None:
        """Run the validation using the integrated runner."""
        print("\n" + "=" * 60 + "\n🚀 Running Validation\n" + "=" * 60)
        try:
            runner = EnhancedValidationRunner()
            
            # The TUI runs a specific set of scenarios/countries, so we force it.
            # The runner is designed to work with groups, so we adapt.
            scenario_name = Path(selections["Scenario"]).stem
            country_iso_codes = None
            if selections["Countries"] != "all":
                country_data = load_json_file(selections["Countries"])
                if country_data:
                    country_iso_codes = [c['iso3'] for c in country_data.get('countries', [])]
            
            result = runner.run(
                model_path=selections["Model"],
                countries_file="list_of_countries.json",
                scenario_templates_dir=str(Path(selections["Scenario"]).parent),
                environment=selections["Environment"],
                max_instances=100,
                force_rerun=True, # TUI runs are explicit actions, so always run.
                specific_scenarios=[scenario_name],
                specific_countries=country_iso_codes
            )

            print("\n" + "=" * 60)
            if result.get("success"):
                print(f"✅ Validation completed successfully! Run ID: {result.get('run_id')}")
            else:
                print(f"❌ Validation failed: {result.get('error', 'Unknown error')}")
            print("=" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\n\n⏹️  Validation interrupted by user")
        except Exception as e:
            print(f"\n❌ Error running validation: {e}", exc_info=True)

    def main():
        print_header()
        selections = {
            "Model": "model.json",
            "Scenario": get_scenario_files()[0] if get_scenario_files() else "",
            "Environment": "standard",
            "Countries": "all"
        }
        
        while True:
            print("\n🎯 Current Selections:")
            for key, value in selections.items(): print(f"   {key:15}: {value}")
            
            print("\n📋 Main Menu\n" + "-" * 40)
            print("  1. Select Model\n  2. Select Scenario\n  3. Select Environment\n  4. Select Countries\n  5. Run Validation\n  6. Exit\n")
            
            try:
                choice = input("Select option (number): ").strip()
                if choice == "1":
                    files = get_model_files()
                    idx = print_menu("Select Model File", files, selections["Model"])
                    if idx >= 0: selections["Model"] = files[idx]
                elif choice == "2":
                    files = get_scenario_files()
                    idx = print_menu("Select Scenario File", files, selections["Scenario"])
                    if idx >= 0: selections["Scenario"] = files[idx]
                elif choice == "3":
                    envs = get_environments()
                    idx = print_menu("Select Environment", envs, selections["Environment"])
                    if idx >= 0: selections["Environment"] = envs[idx]
                elif choice == "4":
                    files = ["all"] + get_country_files()
                    idx = print_menu("Select Countries File ('all' for everything)", files, selections["Countries"])
                    if idx >= 0: selections["Countries"] = files[idx]
                elif choice == "5":
                    run_validation(selections)
                elif choice == "6":
                    print("\n👋 Goodbye!")
                    sys.exit(0)
                else:
                    print("Please enter a number between 1 and 6")
            except (KeyboardInterrupt, EOFError):
                print("\n\n⏹️  Cancelled by user")
                sys.exit(0)

    if __name__ == "__main__":
        main()
    ```
    
6. **File:** `validation_suite/cli.py`
   **Action:** Replace the entire contents of the file. This is the direct-integration CLI.
   ```python
   #!/usr/bin/env python3
   """
   Validate Changes CLI - Main entry point for the enhanced validation system.
   """
   import sys
   import argparse
   import logging
   from .runner import EnhancedValidationRunner
   from .db import ValidationDatabase
   
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   
   def main():
       parser = argparse.ArgumentParser(description="Unified Validation and Query CLI")
       # Add arguments...
       parser.add_argument("--countries", nargs="+", help="Specific countries to run (ISO3 codes)")
       parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run (stem names)")
       parser.add_argument("--force", action="store_true", help="Force re-run all combinations")
       parser.add_argument("--environment", default="standard", help="API environment")
       parser.add_argument("--max-instances", type=int, default=100, help="Maximum concurrent instances")
       parser.add_argument("--model", default="model.json", help="Path to model file")
       parser.add_argument("--countries-file", default="list_of_countries.json", help="Path to countries JSON file")
       parser.add_argument("--scenarios-dir", default="scenario-templates", help="Directory with scenario templates")
       parser.add_argument("--database", default="validation_results.db", help="Path to validation database")
       parser.add_argument("--status", action="store_true", help="Show recent run status")
       parser.add_argument("--verbose", action="store_true", help="Verbose output")
   
       args = parser.parse_args()
   
       if args.verbose:
           logging.getLogger().setLevel(logging.DEBUG)
   
       runner = EnhancedValidationRunner(args.database)
   
       if args.status:
           db = ValidationDatabase(args.database)
           summary = db.get_latest_run_summary()
           if not summary:
               print("No validation runs found.")
               return
           print(json.dumps(summary, indent=2))
           if summary.get('failed_jobs', 0) > 0:
               print("\nFailed jobs:")
               failed = db.get_failed_jobs(summary['run_id'])
               for country, scenario in failed:
                   print(f" - {country}/{scenario}")
           return
   
       # Default action: run validation
       runner.run(
           model_path=args.model,
           countries_file=args.countries_file,
           scenario_templates_dir=args.scenarios_dir,
           environment=args.environment,
           max_instances=args.max_instances,
           force_rerun=args.force,
           specific_countries=args.countries,
           specific_scenarios=args.scenarios
       )
   
   if __name__ == "__main__":
       main()
   ```

---

### **Phase 4: Cleanup - Delete Obsolete Files and Directories**

After confirming the new structure works, this step removes all the old, confusing code.

```bash
# !! DANGER !! Execute this only after you are sure the new structure works.
# This is a destructive action.

# Remove the old top-level package
rm -rf utilities/

# Remove all the individual old files that were moved to scripts/
rm -f apply_scenario.py
rm -f upload_project.py
rm -f create_country_scenarios.py
rm -f validate_scenario.py
rm -f create_economic_analyses.py
rm -f run_economic_analyses.py
rm -f validate_changes.py
rm -f run_all_validations.py
rm -f multi_country.py
rm -f query_results.py
rm -f country_utils.py
rm -f validate_model_changes.py
rm -f validation_db.py
```

---

### **Phase 5: How to Run the New System**

With the refactoring complete, here is how you interact with the system from your project root:

1.  **To run the Terminal User Interface (TUI):**
    ```bash
    python -m validation_suite.tui
    ```

2.  **To run validations from the Command Line Interface (CLI):**
    ```bash
    # Run all outdated combinations
    python -m validation_suite.cli

    # Force a run for specific countries and scenarios
    python -m validation_suite.cli --force --countries USA CAN --scenarios default_scenario

    # Check the status of the last run
    python -m validation_suite.cli --status
    ```

This explicit, step-by-step plan provides a clear path to a much cleaner, more reliable, and more maintainable validation system. An LLM agent should be able to follow these literal commands without deviation.
