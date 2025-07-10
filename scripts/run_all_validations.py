#!/usr/bin/env python3
"""
Enhanced Multi-Country Validation Runner

This script orchestrates validation runs across all countries and scenarios,
with database integration for tracking results and incremental execution.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utilities"))

from validation_db import ValidationDatabase
from analytics.database_processor import DatabaseAnalyticsProcessor
try:
    from country_utils import load_countries_list
except ImportError:
    # Fallback to direct import
    import json
    def load_countries_list(countries_path: str):
        with open(countries_path, 'r') as f:
            data = json.load(f)
        return data.get('countries', [])
from multi_country import validate_multiple_countries

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedValidationRunner:
    """
    Enhanced validation runner with database integration and incremental execution.
    """
    
    def __init__(self, db_path: str = "validation_results.db"):
        """
        Initialize runner with database connection.
        
        Args:
            db_path: Path to validation database
        """
        self.db = ValidationDatabase(db_path)
        self.analytics_processor = DatabaseAnalyticsProcessor(db_path)
        self.db_path = db_path
    
    def get_git_commit(self) -> str:
        """
        Get current git commit hash.
        
        Returns:
            str: Git commit hash
        """
        try:
            return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        except subprocess.CalledProcessError:
            logger.warning("Could not get git commit hash")
            return "unknown"
    
    def discover_scenarios(self, scenario_templates_dir: str = "scenario-templates") -> List[str]:
        """
        Discover available scenario templates.
        
        Args:
            scenario_templates_dir: Directory containing scenario templates
            
        Returns:
            List of scenario template paths
        """
        scenario_dir = Path(scenario_templates_dir)
        if not scenario_dir.exists():
            logger.error(f"Scenario templates directory not found: {scenario_dir}")
            return []
        
        scenarios = []
        for scenario_file in scenario_dir.glob("*.json"):
            scenarios.append(str(scenario_file))
        
        logger.info(f"Discovered {len(scenarios)} scenario templates")
        return scenarios
    
    def load_countries(self, countries_file: str = "list_of_countries.json") -> List[Dict[str, str]]:
        """
        Load list of countries for validation.
        
        Args:
            countries_file: Path to countries JSON file
            
        Returns:
            List of country dictionaries
        """
        try:
            countries = load_countries_list(countries_file)
            logger.info(f"Loaded {len(countries)} countries")
            return countries
        except Exception as e:
            logger.error(f"Failed to load countries: {e}")
            return []
    
    def generate_all_combinations(
        self, 
        countries: List[Dict[str, str]], 
        scenarios: List[str]
    ) -> List[Tuple[str, str, str]]:
        """
        Generate all country/scenario combinations.
        
        Args:
            countries: List of country dictionaries
            scenarios: List of scenario file paths
            
        Returns:
            List of (country_iso3, scenario_name, scenario_path) tuples
        """
        combinations = []
        
        for country in countries:
            for scenario_path in scenarios:
                scenario_name = Path(scenario_path).stem
                combinations.append((country['iso3'], scenario_name, scenario_path))
        
        logger.info(f"Generated {len(combinations)} country/scenario combinations")
        return combinations
    
    def filter_combinations_needing_rerun(
        self, 
        combinations: List[Tuple[str, str, str]], 
        git_commit: str
    ) -> List[Tuple[str, str, str]]:
        """
        Filter combinations that need to be rerun based on git commit changes.
        
        Args:
            combinations: List of (country, scenario, scenario_path) tuples
            git_commit: Current git commit hash
            
        Returns:
            List of combinations needing rerun
        """
        needed_combinations = []
        
        for country, scenario, scenario_path in combinations:
            if self.db.needs_rerun(country, scenario, git_commit):
                needed_combinations.append((country, scenario, scenario_path))
        
        logger.info(f"Found {len(needed_combinations)} combinations needing rerun")
        return needed_combinations
    
    def run_validation_for_scenario(
        self,
        model_path: str,
        scenario_path: str,
        countries: List[Dict[str, str]],
        environment: str,
        max_instances: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run validation for a specific scenario across all countries.
        
        Args:
            model_path: Path to model file
            scenario_path: Path to scenario file
            countries: List of country dictionaries
            environment: API environment
            max_instances: Maximum concurrent instances
            **kwargs: Additional parameters for validation
            
        Returns:
            Dict with validation results
        """
        scenario_name = Path(scenario_path).stem
        logger.info(f"Running validation for scenario: {scenario_name}")
        
        # Create temporary countries file for this scenario
        temp_countries_file = f"temp_countries_{scenario_name}.json"
        try:
            with open(temp_countries_file, 'w') as f:
                json.dump(countries, f)
            
            # Run validation using existing multi-country infrastructure
            success = validate_multiple_countries(
                model_path=model_path,
                scenario_path=scenario_path,
                countries_path=temp_countries_file,
                environment=environment,
                poll_interval=10,
                max_wait_time=3600,  # 1 hour
                skip_api_test=False,
                no_cleanup=False,
                verbose=True,
                generate_analytics=True,
                max_instances=max_instances,
                **kwargs
            )
            
            return {
                "success": success,
                "scenario": scenario_name,
                "countries_processed": len(countries)
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_countries_file):
                os.remove(temp_countries_file)
    
    def run_enhanced_validation(
        self,
        model_path: str = "model.json",
        countries_file: str = "list_of_countries.json",
        scenario_templates_dir: str = "scenario-templates",
        environment: str = "standard",
        max_instances: int = 100,
        force_rerun: bool = False,
        specific_countries: Optional[List[str]] = None,
        specific_scenarios: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run enhanced validation with database integration.
        
        Args:
            model_path: Path to model file
            countries_file: Path to countries JSON file
            scenario_templates_dir: Directory with scenario templates
            environment: API environment
            max_instances: Maximum concurrent instances
            force_rerun: Force rerun all combinations
            specific_countries: Optional list of specific countries to run
            specific_scenarios: Optional list of specific scenarios to run
            **kwargs: Additional parameters
            
        Returns:
            Dict with validation results
        """
        logger.info("Starting enhanced validation run")
        
        # Get current git commit
        git_commit = self.get_git_commit()
        logger.info(f"Current git commit: {git_commit}")
        
        # Discover scenarios
        scenarios = self.discover_scenarios(scenario_templates_dir)
        if not scenarios:
            return {"success": False, "error": "No scenarios found"}
        
        # Filter scenarios if specified
        if specific_scenarios:
            scenarios = [s for s in scenarios if Path(s).stem in specific_scenarios]
            logger.info(f"Filtered to {len(scenarios)} specific scenarios")
        
        # Load countries
        countries = self.load_countries(countries_file)
        if not countries:
            return {"success": False, "error": "No countries found"}
        
        # Filter countries if specified
        if specific_countries:
            countries = [c for c in countries if c['iso3'] in specific_countries]
            logger.info(f"Filtered to {len(countries)} specific countries")
        
        # Generate all combinations
        combinations = self.generate_all_combinations(countries, scenarios)
        
        # Filter combinations needing rerun (unless force_rerun is True)
        if not force_rerun:
            combinations = self.filter_combinations_needing_rerun(combinations, git_commit)
        
        if not combinations:
            logger.info("No combinations need to be rerun")
            return {"success": True, "message": "All combinations up to date"}
        
        # Start validation run in database
        total_jobs = len(combinations)
        run_id = self.db.start_validation_run(git_commit, total_jobs)
        logger.info(f"Started validation run {run_id} with {total_jobs} jobs")
        
        # Group combinations by scenario for efficient processing
        scenario_groups = {}
        for country, scenario, scenario_path in combinations:
            if scenario not in scenario_groups:
                scenario_groups[scenario] = {
                    "scenario_path": scenario_path,
                    "countries": []
                }
            scenario_groups[scenario]["countries"].append({
                "iso3": country,
                "name": next((c['name'] for c in countries if c['iso3'] == country), country)
            })
        
        # Process each scenario group
        successful_jobs = 0
        failed_jobs = 0
        
        for scenario, group_info in scenario_groups.items():
            logger.info(f"Processing scenario: {scenario}")
            
            try:
                result = self.run_validation_for_scenario(
                    model_path=model_path,
                    scenario_path=group_info["scenario_path"],
                    countries=group_info["countries"],
                    environment=environment,
                    max_instances=max_instances,
                    **kwargs
                )
                
                if result["success"]:
                    successful_jobs += len(group_info["countries"])
                    logger.info(f"✅ Scenario {scenario} completed successfully")
                else:
                    failed_jobs += len(group_info["countries"])
                    logger.error(f"❌ Scenario {scenario} failed")
                    
            except Exception as e:
                logger.error(f"❌ Error processing scenario {scenario}: {e}")
                failed_jobs += len(group_info["countries"])
        
        # Update run status
        final_status = "completed" if failed_jobs == 0 else ("failed" if successful_jobs == 0 else "completed")
        self.db.update_run_status(run_id, final_status, successful_jobs, failed_jobs)
        
        logger.info(f"Validation run {run_id} completed: {successful_jobs} successful, {failed_jobs} failed")
        
        return {
            "success": failed_jobs == 0,
            "run_id": run_id,
            "total_jobs": total_jobs,
            "successful_jobs": successful_jobs,
            "failed_jobs": failed_jobs,
            "git_commit": git_commit
        }


def main():
    """Main entry point for enhanced validation runner."""
    parser = argparse.ArgumentParser(description="Enhanced Multi-Country Validation Runner")
    
    # File paths
    parser.add_argument("--model", default="model.json", help="Path to model file")
    parser.add_argument("--countries", default="list_of_countries.json", help="Path to countries JSON file")
    parser.add_argument("--scenarios-dir", default="scenario-templates", help="Directory with scenario templates")
    parser.add_argument("--database", default="validation_results.db", help="Path to validation database")
    
    # Runtime parameters
    parser.add_argument("--environment", default="standard", help="API environment")
    parser.add_argument("--max-instances", type=int, default=100, help="Maximum concurrent instances")
    
    # Filtering options
    parser.add_argument("--force", action="store_true", help="Force rerun all combinations")
    parser.add_argument("--country", nargs="+", help="Specific countries to run (ISO3 codes)")
    parser.add_argument("--scenario", nargs="+", help="Specific scenarios to run")
    
    # Output options
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--status", action="store_true", help="Show recent run status and exit")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize runner
    runner = EnhancedValidationRunner(args.database)
    
    # Status check
    if args.status:
        summary = runner.db.get_latest_run_summary()
        if summary:
            print(f"Latest run ({summary['run_id']}): {summary['status']}")
            print(f"  Timestamp: {summary['timestamp']}")
            print(f"  Git commit: {summary['git_commit']}")
            print(f"  Jobs: {summary['successful_jobs']}/{summary['total_jobs']} successful")
            
            if summary['failed_jobs'] > 0:
                failed_jobs = runner.db.get_failed_jobs(summary['run_id'])
                print(f"  Failed jobs: {len(failed_jobs)}")
                for country, scenario in failed_jobs[:5]:  # Show first 5
                    print(f"    {country}/{scenario}")
                if len(failed_jobs) > 5:
                    print(f"    ... and {len(failed_jobs) - 5} more")
        else:
            print("No validation runs found")
        return
    
    # Run validation
    try:
        result = runner.run_enhanced_validation(
            model_path=args.model,
            countries_file=args.countries,
            scenario_templates_dir=args.scenarios_dir,
            environment=args.environment,
            max_instances=args.max_instances,
            force_rerun=args.force,
            specific_countries=args.country,
            specific_scenarios=args.scenario
        )
        
        if result["success"]:
            print(f"✅ Validation completed successfully!")
            print(f"   Run ID: {result['run_id']}")
            print(f"   Jobs: {result['successful_jobs']}/{result['total_jobs']} successful")
            sys.exit(0)
        else:
            print(f"❌ Validation failed: {result.get('error', 'Unknown error')}")
            if 'failed_jobs' in result:
                print(f"   Failed jobs: {result['failed_jobs']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()