"""
Analytics Database Processor

This module bridges the analytics API and database storage, extending
the existing analytics processing to store results in the validation database.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .processor import process_job_analytics, get_validation_output_dir
from .api_client import fetch_analytics_data
from .ulid_parser import extract_ulid_from_job_name, validate_ulid_format
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from validation_db import ValidationDatabase

import logging
logger = logging.getLogger(__name__)


class DatabaseAnalyticsProcessor:
    """
    Analytics processor with database integration.
    
    Extends existing analytics processing to store results in the
    validation database while maintaining CSV compatibility.
    """
    
    def __init__(self, db_path: str = "validation_results.db"):
        """
        Initialize processor with database connection.
        
        Args:
            db_path: Path to validation database
        """
        self.db = ValidationDatabase(db_path)
        self.db_path = db_path
    
    def fetch_analytics_for_ulid(self, ulid: str, environment: str = "standard") -> Optional[Dict]:
        """
        Fetch analytics data for a given ULID.
        
        Args:
            ulid: The ULID identifier
            environment: API environment
            
        Returns:
            Dict with analytics data or None if failed
        """
        try:
            data = fetch_analytics_data(environment=environment, ulid=ulid)
            return {
                "success": data is not None,
                "data": data,
                "ulid": ulid,
                "record_count": len(data) if data else 0
            }
        except Exception as e:
            logger.error(f"Failed to fetch analytics for ULID {ulid}: {e}")
            return None
    
    def parse_analytics_csv(self, csv_content: str) -> List[Dict]:
        """
        Parse analytics CSV content into normalized format.
        
        Args:
            csv_content: CSV content string
            
        Returns:
            List of metric dictionaries
        """
        return self.db.parse_csv_to_metrics(csv_content)
    
    def store_analytics_in_db(
        self, 
        run_id: int, 
        country: str, 
        scenario: str, 
        ulid: str, 
        analytics_data: List[Dict]
    ) -> bool:
        """
        Store analytics data in the validation database.
        
        Args:
            run_id: Validation run ID
            country: Country ISO3 code
            scenario: Scenario name
            ulid: Job ULID
            analytics_data: List of analytics metrics
            
        Returns:
            bool: True if successful
        """
        try:
            self.db.store_metrics(run_id, country, scenario, ulid, analytics_data)
            return True
        except Exception as e:
            logger.error(f"Failed to store analytics in database: {e}")
            return False
    
    def maintain_csv_compatibility(self, analytics_data: List[Dict]) -> str:
        """
        Convert analytics data to CSV format for backward compatibility.
        
        Args:
            analytics_data: List of metric dictionaries
            
        Returns:
            str: CSV formatted string
        """
        if not analytics_data:
            return "element_label,timestamp_year,value\n"
        
        lines = ["element_label,timestamp_year,value"]
        for metric in analytics_data:
            lines.append(f"{metric['element_label']},{metric['timestamp_year']},{metric['value']}")
        
        return "\n".join(lines)
    
    def process_job_with_database(
        self,
        job_name: str,
        run_id: int,
        country: str,
        scenario: str,
        model_name: str,
        environment: str = "standard",
        save_csv: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process job analytics with database storage.
        
        Args:
            job_name: Job name containing ULID
            run_id: Validation run ID
            country: Country ISO3 code
            scenario: Scenario name
            model_name: Model name for CSV directory structure
            environment: API environment
            save_csv: Whether to also save CSV file
            **kwargs: Additional parameters
            
        Returns:
            Dict with processing results
        """
        result = {
            "success": False,
            "ulid": None,
            "data_records": 0,
            "csv_path": None,
            "database_stored": False,
            "error": None
        }
        
        try:
            # Extract ULID from job name
            ulid = extract_ulid_from_job_name(job_name, environment)
            if not ulid or not validate_ulid_format(ulid):
                result["error"] = f"Invalid ULID extracted from job name: {job_name}"
                return result
            
            result["ulid"] = ulid
            
            # Fetch analytics data
            analytics_result = self.fetch_analytics_for_ulid(ulid, environment)
            if not analytics_result or not analytics_result["success"]:
                result["error"] = "Failed to fetch analytics data"
                return result
            
            analytics_data = analytics_result["data"]
            result["data_records"] = len(analytics_data)
            
            # Store in database
            if self.store_analytics_in_db(run_id, country, scenario, ulid, analytics_data):
                result["database_stored"] = True
                logger.info(f"Stored {len(analytics_data)} metrics in database for {country}/{scenario}")
            else:
                result["error"] = "Failed to store in database"
                return result
            
            # Optional CSV export for backward compatibility
            if save_csv:
                try:
                    csv_result = process_job_analytics(
                        job_name=job_name,
                        model_name=model_name,
                        scenario_name=scenario,
                        environment=environment,
                        preview=False,
                        **kwargs
                    )
                    if csv_result["success"]:
                        result["csv_path"] = csv_result["csv_path"]
                        logger.info(f"CSV saved for backward compatibility: {csv_result['csv_path']}")
                except Exception as e:
                    logger.warning(f"CSV export failed (continuing with database storage): {e}")
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"Processing error for {job_name}: {e}")
            return result
    
    def process_multiple_jobs_with_database(
        self,
        jobs: List[Dict[str, Any]],
        run_id: int,
        model_name: str,
        environment: str = "standard",
        save_csv: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple jobs with database storage.
        
        Args:
            jobs: List of job dictionaries with 'job_name', 'country', 'scenario'
            run_id: Validation run ID
            model_name: Model name
            environment: API environment
            save_csv: Whether to also save CSV files
            **kwargs: Additional parameters
            
        Returns:
            List of processing results
        """
        results = []
        
        logger.info(f"Processing {len(jobs)} jobs for database storage")
        
        for i, job in enumerate(jobs, 1):
            logger.info(f"Processing job {i}/{len(jobs)}: {job['job_name']}")
            
            result = self.process_job_with_database(
                job_name=job['job_name'],
                run_id=run_id,
                country=job['country'],
                scenario=job['scenario'],
                model_name=model_name,
                environment=environment,
                save_csv=save_csv,
                **kwargs
            )
            
            results.append({
                **result,
                "job_name": job['job_name'],
                "country": job['country'],
                "scenario": job['scenario']
            })
            
            if result["success"]:
                logger.info(f"✅ {job['country']}/{job['scenario']}: {result['data_records']} records")
            else:
                logger.error(f"❌ {job['country']}/{job['scenario']}: {result['error']}")
        
        # Summary
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        logger.info(f"Batch processing complete: {successful} successful, {failed} failed")
        
        return results
    
    def update_job_status_in_db(
        self,
        run_id: int,
        country: str,
        scenario: str,
        ulid: str,
        job_status: str,
        submitted_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> None:
        """
        Update job status in database.
        
        Args:
            run_id: Validation run ID
            country: Country ISO3 code
            scenario: Scenario name
            ulid: Job ULID
            job_status: Job status ('success', 'failed', 'timeout')
            submitted_at: Submission timestamp
            completed_at: Completion timestamp
        """
        try:
            self.db.record_job_result(
                run_id=run_id,
                country=country,
                scenario=scenario,
                ulid=ulid,
                job_status=job_status,
                submitted_at=submitted_at,
                completed_at=completed_at
            )
        except Exception as e:
            logger.error(f"Failed to update job status in database: {e}")
    
    def get_failed_jobs_for_rerun(self, run_id: int) -> List[Dict[str, str]]:
        """
        Get failed jobs that need to be rerun.
        
        Args:
            run_id: Validation run ID
            
        Returns:
            List of job dictionaries with 'country' and 'scenario'
        """
        try:
            failed_jobs = self.db.get_failed_jobs(run_id)
            return [{"country": country, "scenario": scenario} for country, scenario in failed_jobs]
        except Exception as e:
            logger.error(f"Failed to get failed jobs: {e}")
            return []
    
    def export_run_results(self, run_id: int, output_dir: str = None) -> Dict[str, Any]:
        """
        Export run results to CSV files.
        
        Args:
            run_id: Validation run ID
            output_dir: Output directory (defaults to validation/<run_id>)
            
        Returns:
            Dict with export results
        """
        try:
            if output_dir is None:
                output_dir = f"validation/run_{run_id}"
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Export main metrics
            metrics_file = output_path / "metrics.csv"
            success = self.db.export_run_csv(run_id, str(metrics_file))
            
            if success:
                # Export run summary
                summary = self.db.get_latest_run_summary()
                jobs = self.db.get_run_jobs(run_id)
                
                summary_file = output_path / "run_summary.txt"
                with open(summary_file, 'w') as f:
                    f.write(f"Validation Run {run_id} Summary\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Timestamp: {summary['timestamp']}\n")
                    f.write(f"Git Commit: {summary['git_commit']}\n")
                    f.write(f"Status: {summary['status']}\n")
                    f.write(f"Total Jobs: {summary['total_jobs']}\n")
                    f.write(f"Successful Jobs: {summary['successful_jobs']}\n")
                    f.write(f"Failed Jobs: {summary['failed_jobs']}\n\n")
                    
                    f.write("Job Details:\n")
                    for job in jobs:
                        f.write(f"  {job['country']}/{job['scenario']}: {job['job_status']}\n")
                
                return {
                    "success": True,
                    "metrics_file": str(metrics_file),
                    "summary_file": str(summary_file),
                    "output_dir": str(output_path)
                }
            
            return {"success": False, "error": "Failed to export metrics"}
            
        except Exception as e:
            logger.error(f"Failed to export run results: {e}")
            return {"success": False, "error": str(e)}