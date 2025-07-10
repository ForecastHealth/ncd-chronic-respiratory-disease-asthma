#!/usr/bin/env python3
"""
Validate Changes CLI

Simple command-line interface for maintainers to run validations and query results.
This is the main entry point for the enhanced validation system.
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utilities"))

from validation_db import ValidationDatabase
from analytics.database_processor import DatabaseAnalyticsProcessor

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_query(db_path: str, query: str) -> None:
    """
    Run a SQL query against the validation database.
    
    Args:
        db_path: Path to validation database
        query: SQL query to execute
    """
    db = ValidationDatabase(db_path)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                # Print column headers
                columns = [description[0] for description in cursor.description]
                print("\t".join(columns))
                print("-" * (len("\t".join(columns))))
                
                # Print results
                for row in results:
                    print("\t".join(str(value) for value in row))
                    
                print(f"\n{len(results)} rows returned")
            else:
                print("No results returned")
                
    except Exception as e:
        print(f"Query error: {e}")
        sys.exit(1)


def show_status(db_path: str) -> None:
    """
    Show recent validation run status.
    
    Args:
        db_path: Path to validation database
    """
    db = ValidationDatabase(db_path)
    
    try:
        summary = db.get_latest_run_summary()
        if not summary:
            print("No validation runs found")
            return
        
        print(f"Latest Validation Run (ID: {summary['run_id']})")
        print("=" * 50)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Git Commit: {summary['git_commit']}")
        print(f"Status: {summary['status']}")
        print(f"Total Jobs: {summary['total_jobs']}")
        print(f"Successful Jobs: {summary['successful_jobs']}")
        print(f"Failed Jobs: {summary['failed_jobs']}")
        
        if summary['failed_jobs'] > 0:
            print(f"\nFailed Jobs:")
            failed_jobs = db.get_failed_jobs(summary['run_id'])
            for country, scenario in failed_jobs:
                print(f"  {country}/{scenario}")
        
        # Show some recent metrics
        print(f"\nSample Metrics:")
        metrics = db.get_metrics_for_run(summary['run_id'])
        if metrics:
            print("Country\tScenario\tElement\tYear\tValue")
            print("-" * 50)
            for metric in metrics[:10]:  # Show first 10
                print(f"{metric['country']}\t{metric['scenario']}\t{metric['element_label']}\t{metric['timestamp_year']}\t{metric['value']}")
            
            if len(metrics) > 10:
                print(f"... and {len(metrics) - 10} more metrics")
        
    except Exception as e:
        print(f"Status error: {e}")
        sys.exit(1)


def show_common_queries(db_path: str) -> None:
    """
    Show common query examples.
    
    Args:
        db_path: Path to validation database
    """
    print("Common Query Examples:")
    print("=" * 50)
    print()
    
    queries = [
        ("Show all validation runs", "SELECT * FROM validation_runs ORDER BY timestamp DESC"),
        ("Show failed jobs from latest run", "SELECT jr.country, jr.scenario, jr.job_status FROM job_results jr JOIN validation_runs vr ON jr.run_id = vr.run_id WHERE vr.run_id = (SELECT MAX(run_id) FROM validation_runs) AND jr.job_status != 'success'"),
        ("Show metrics for specific country", "SELECT * FROM metrics WHERE country = 'USA' ORDER BY timestamp_year"),
        ("Show population metrics by country", "SELECT country, AVG(value) as avg_population FROM metrics WHERE element_label = 'population' GROUP BY country"),
        ("Show recent commits", "SELECT DISTINCT git_commit, timestamp FROM validation_runs ORDER BY timestamp DESC LIMIT 5"),
        ("Show success rate by scenario", "SELECT scenario, COUNT(*) as total, SUM(CASE WHEN job_status = 'success' THEN 1 ELSE 0 END) as successful FROM job_results GROUP BY scenario"),
    ]
    
    for i, (description, query) in enumerate(queries, 1):
        print(f"{i}. {description}")
        print(f"   {query}")
        print()


def export_results(db_path: str, run_id: int, output_dir: str) -> None:
    """
    Export validation results to CSV files.
    
    Args:
        db_path: Path to validation database
        run_id: Validation run ID to export
        output_dir: Output directory for CSV files
    """
    processor = DatabaseAnalyticsProcessor(db_path)
    
    try:
        result = processor.export_run_results(run_id, output_dir)
        
        if result["success"]:
            print(f"✅ Results exported successfully!")
            print(f"   Output directory: {result['output_dir']}")
            print(f"   Metrics file: {result['metrics_file']}")
            print(f"   Summary file: {result['summary_file']}")
        else:
            print(f"❌ Export failed: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Export error: {e}")
        sys.exit(1)


def main():
    """Main entry point for validate_changes CLI."""
    parser = argparse.ArgumentParser(
        description="Validate Changes CLI - Run validations and query results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run validation for all countries and scenarios
  python validate_changes.py

  # Run validation for specific countries
  python validate_changes.py --countries USA CAN MEX

  # Run validation for specific scenarios
  python validate_changes.py --scenarios asthma_cr1_scenario asthma_cr3_scenario

  # Force rerun all combinations
  python validate_changes.py --force

  # Show status of recent runs
  python validate_changes.py --status

  # Run SQL query
  python validate_changes.py --query "SELECT * FROM metrics WHERE country='USA'"

  # Export results
  python validate_changes.py --export-run 123 --output-dir results/
        """
    )
    
    # Validation parameters
    parser.add_argument("--countries", nargs="+", help="Specific countries to run (ISO3 codes)")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run")
    parser.add_argument("--force", action="store_true", help="Force re-run all combinations")
    parser.add_argument("--environment", default="standard", help="API environment")
    parser.add_argument("--max-instances", type=int, default=100, help="Maximum concurrent instances")
    
    # File paths
    parser.add_argument("--model", default="model.json", help="Path to model file")
    parser.add_argument("--countries-file", default="list_of_countries.json", help="Path to countries JSON file")
    parser.add_argument("--scenarios-dir", default="scenario-templates", help="Directory with scenario templates")
    parser.add_argument("--database", default="validation_results.db", help="Path to validation database")
    
    # Query and status options
    parser.add_argument("--query", help="Run SQL query on results")
    parser.add_argument("--status", action="store_true", help="Show recent run status")
    parser.add_argument("--examples", action="store_true", help="Show common query examples")
    
    # Export options
    parser.add_argument("--export-run", type=int, help="Export results for specific run ID")
    parser.add_argument("--output-dir", help="Output directory for exports")
    
    # General options
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle query examples
    if args.examples:
        show_common_queries(args.database)
        return
    
    # Handle SQL query
    if args.query:
        run_query(args.database, args.query)
        return
    
    # Handle status check
    if args.status:
        show_status(args.database)
        return
    
    # Handle export
    if args.export_run:
        if not args.output_dir:
            args.output_dir = f"validation_export_run_{args.export_run}"
        export_results(args.database, args.export_run, args.output_dir)
        return
    
    # Default action: run validation
    print("🚀 Starting validation run...")
    print(f"   Database: {args.database}")
    
    if args.countries:
        print(f"   Countries: {', '.join(args.countries)}")
    if args.scenarios:
        print(f"   Scenarios: {', '.join(args.scenarios)}")
    if args.force:
        print("   Mode: Force rerun all combinations")
    
    # Build command for run_all_validations.py
    cmd = [
        sys.executable,
        str(Path(__file__).parent / "run_all_validations.py"),
        "--model", args.model,
        "--countries", args.countries_file,
        "--scenarios-dir", args.scenarios_dir,
        "--database", args.database,
        "--environment", args.environment,
        "--max-instances", str(args.max_instances)
    ]
    
    if args.force:
        cmd.append("--force")
    
    if args.countries:
        cmd.extend(["--country"] + args.countries)
    
    if args.scenarios:
        cmd.extend(["--scenario"] + args.scenarios)
    
    if args.verbose:
        cmd.append("--verbose")
    
    try:
        # Run the validation
        result = subprocess.run(cmd, check=True)
        print("✅ Validation completed successfully!")
        
        # Show quick status
        print("\n📊 Quick Status:")
        show_status(args.database)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Validation failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()