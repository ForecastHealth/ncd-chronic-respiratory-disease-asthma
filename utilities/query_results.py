"""
Query Results Interface

Convenient methods for analyzing stored validation results with
pandas integration for data analysis and visualization.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging

try:
    from .validation_db import ValidationDatabase
except ImportError:
    from validation_db import ValidationDatabase

logger = logging.getLogger(__name__)


class ResultsQuery:
    """
    Query interface for analyzing validation results.
    
    Provides convenient methods for common analysis patterns
    and data export functionality.
    """
    
    def __init__(self, db_path: str = "validation_results.db"):
        """
        Initialize query interface.
        
        Args:
            db_path: Path to validation database
        """
        self.db = ValidationDatabase(db_path)
        self.db_path = db_path
    
    def get_latest_run_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get summary of the latest validation run.
        
        Returns:
            Dict with run summary or None if no runs
        """
        return self.db.get_latest_run_summary()
    
    def get_runs_dataframe(self, limit: int = 10) -> pd.DataFrame:
        """
        Get validation runs as a pandas DataFrame.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            DataFrame with validation runs
        """
        with self.db.get_connection() as conn:
            query = """
            SELECT * FROM validation_runs 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def get_job_results_dataframe(self, run_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get job results as a pandas DataFrame.
        
        Args:
            run_id: Optional run ID filter (defaults to latest run)
            
        Returns:
            DataFrame with job results
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return pd.DataFrame()
            run_id = latest_run['run_id']
        
        with self.db.get_connection() as conn:
            query = """
            SELECT jr.*, vr.git_commit, vr.timestamp as run_timestamp
            FROM job_results jr
            JOIN validation_runs vr ON jr.run_id = vr.run_id
            WHERE jr.run_id = ?
            ORDER BY jr.country, jr.scenario
            """
            return pd.read_sql_query(query, conn, params=(run_id,))
    
    def get_metrics_dataframe(
        self, 
        run_id: Optional[int] = None,
        country: Optional[str] = None,
        scenario: Optional[str] = None,
        element_label: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get metrics as a pandas DataFrame.
        
        Args:
            run_id: Optional run ID filter (defaults to latest run)
            country: Optional country filter
            scenario: Optional scenario filter
            element_label: Optional element label filter
            
        Returns:
            DataFrame with metrics
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return pd.DataFrame()
            run_id = latest_run['run_id']
        
        # Build query with filters
        query = """
        SELECT m.*, vr.git_commit, vr.timestamp as run_timestamp
        FROM metrics m
        JOIN validation_runs vr ON m.run_id = vr.run_id
        WHERE m.run_id = ?
        """
        params = [run_id]
        
        if country:
            query += " AND m.country = ?"
            params.append(country)
        
        if scenario:
            query += " AND m.scenario = ?"
            params.append(scenario)
        
        if element_label:
            query += " AND m.element_label = ?"
            params.append(element_label)
        
        query += " ORDER BY m.country, m.scenario, m.element_label, m.timestamp_year"
        
        with self.db.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def compare_scenarios(
        self, 
        country: str, 
        scenario_a: str, 
        scenario_b: str,
        run_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Compare metrics between two scenarios for a specific country.
        
        Args:
            country: Country ISO3 code
            scenario_a: First scenario name
            scenario_b: Second scenario name
            run_id: Optional run ID (defaults to latest)
            
        Returns:
            DataFrame with comparison results
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return pd.DataFrame()
            run_id = latest_run['run_id']
        
        with self.db.get_connection() as conn:
            query = """
            SELECT 
                a.element_label,
                a.timestamp_year,
                a.value as value_a,
                b.value as value_b,
                (b.value - a.value) as difference,
                CASE 
                    WHEN a.value = 0 THEN NULL
                    ELSE ((b.value - a.value) / a.value) * 100
                END as percent_change
            FROM metrics a
            JOIN metrics b ON (
                a.run_id = b.run_id AND 
                a.country = b.country AND 
                a.element_label = b.element_label AND 
                a.timestamp_year = b.timestamp_year
            )
            WHERE a.run_id = ? AND a.country = ? 
                AND a.scenario = ? AND b.scenario = ?
            ORDER BY a.element_label, a.timestamp_year
            """
            return pd.read_sql_query(
                query, conn, 
                params=(run_id, country, scenario_a, scenario_b)
            )
    
    def get_failed_jobs(self, run_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get failed jobs with details.
        
        Args:
            run_id: Optional run ID (defaults to latest)
            
        Returns:
            List of failed job dictionaries
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return []
            run_id = latest_run['run_id']
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT jr.*, vr.git_commit, vr.timestamp as run_timestamp
                FROM job_results jr
                JOIN validation_runs vr ON jr.run_id = vr.run_id
                WHERE jr.run_id = ? AND jr.job_status != 'success'
                ORDER BY jr.country, jr.scenario
                """,
                (run_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_metric_trends(
        self, 
        element_label: str, 
        countries: Optional[List[str]] = None,
        scenarios: Optional[List[str]] = None,
        run_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get metric trends over time for specific element.
        
        Args:
            element_label: Element label to analyze
            countries: Optional list of countries to include
            scenarios: Optional list of scenarios to include
            run_id: Optional run ID (defaults to latest)
            
        Returns:
            DataFrame with trend data
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return pd.DataFrame()
            run_id = latest_run['run_id']
        
        # Build query with filters
        query = """
        SELECT country, scenario, timestamp_year, value
        FROM metrics
        WHERE run_id = ? AND element_label = ?
        """
        params = [run_id, element_label]
        
        if countries:
            placeholders = ','.join(['?' for _ in countries])
            query += f" AND country IN ({placeholders})"
            params.extend(countries)
        
        if scenarios:
            placeholders = ','.join(['?' for _ in scenarios])
            query += f" AND scenario IN ({placeholders})"
            params.extend(scenarios)
        
        query += " ORDER BY country, scenario, timestamp_year"
        
        with self.db.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def get_success_rates(self) -> pd.DataFrame:
        """
        Get success rates by country and scenario.
        
        Returns:
            DataFrame with success rate statistics
        """
        with self.db.get_connection() as conn:
            query = """
            SELECT 
                country,
                scenario,
                COUNT(*) as total_jobs,
                SUM(CASE WHEN job_status = 'success' THEN 1 ELSE 0 END) as successful_jobs,
                ROUND(
                    (SUM(CASE WHEN job_status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
                    2
                ) as success_rate
            FROM job_results
            GROUP BY country, scenario
            ORDER BY country, scenario
            """
            return pd.read_sql_query(query, conn)
    
    def get_git_commit_history(self, limit: int = 10) -> pd.DataFrame:
        """
        Get git commit history with validation results.
        
        Args:
            limit: Maximum number of commits to return
            
        Returns:
            DataFrame with commit history
        """
        with self.db.get_connection() as conn:
            query = """
            SELECT 
                git_commit,
                timestamp,
                status,
                total_jobs,
                successful_jobs,
                failed_jobs,
                ROUND((successful_jobs * 100.0 / total_jobs), 2) as success_rate
            FROM validation_runs
            ORDER BY timestamp DESC
            LIMIT ?
            """
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def export_results_csv(self, run_id: int, output_path: str) -> bool:
        """
        Export results to CSV file.
        
        Args:
            run_id: Run ID to export
            output_path: Output CSV file path
            
        Returns:
            bool: True if successful
        """
        return self.db.export_run_csv(run_id, output_path)
    
    def export_dataframe_csv(self, df: pd.DataFrame, output_path: str) -> bool:
        """
        Export DataFrame to CSV file.
        
        Args:
            df: DataFrame to export
            output_path: Output CSV file path
            
        Returns:
            bool: True if successful
        """
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(df)} rows to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export DataFrame: {e}")
            return False
    
    def create_summary_report(self, run_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create comprehensive summary report.
        
        Args:
            run_id: Optional run ID (defaults to latest)
            
        Returns:
            Dict with summary statistics
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return {"error": "No validation runs found"}
            run_id = latest_run['run_id']
        
        try:
            # Get basic run info
            run_info = self.db.get_latest_run_summary() if run_id is None else None
            jobs_df = self.get_job_results_dataframe(run_id)
            metrics_df = self.get_metrics_dataframe(run_id)
            
            # Calculate statistics
            summary = {
                "run_id": run_id,
                "total_jobs": len(jobs_df),
                "successful_jobs": len(jobs_df[jobs_df['job_status'] == 'success']),
                "failed_jobs": len(jobs_df[jobs_df['job_status'] != 'success']),
                "total_metrics": len(metrics_df),
                "unique_countries": metrics_df['country'].nunique() if len(metrics_df) > 0 else 0,
                "unique_scenarios": metrics_df['scenario'].nunique() if len(metrics_df) > 0 else 0,
                "unique_elements": metrics_df['element_label'].nunique() if len(metrics_df) > 0 else 0,
                "year_range": {
                    "min": int(metrics_df['timestamp_year'].min()) if len(metrics_df) > 0 else None,
                    "max": int(metrics_df['timestamp_year'].max()) if len(metrics_df) > 0 else None
                }
            }
            
            # Add success rate
            if summary["total_jobs"] > 0:
                summary["success_rate"] = (summary["successful_jobs"] / summary["total_jobs"]) * 100
            else:
                summary["success_rate"] = 0
            
            # Add top failing countries/scenarios
            if len(jobs_df) > 0:
                failed_jobs = jobs_df[jobs_df['job_status'] != 'success']
                if len(failed_jobs) > 0:
                    summary["top_failing_countries"] = failed_jobs['country'].value_counts().head(5).to_dict()
                    summary["top_failing_scenarios"] = failed_jobs['scenario'].value_counts().head(5).to_dict()
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to create summary report: {e}")
            return {"error": str(e)}
    
    def get_data_quality_report(self, run_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate data quality report.
        
        Args:
            run_id: Optional run ID (defaults to latest)
            
        Returns:
            Dict with data quality metrics
        """
        if run_id is None:
            latest_run = self.get_latest_run_summary()
            if not latest_run:
                return {"error": "No validation runs found"}
            run_id = latest_run['run_id']
        
        try:
            metrics_df = self.get_metrics_dataframe(run_id)
            
            if len(metrics_df) == 0:
                return {"error": "No metrics found for this run"}
            
            # Calculate data quality metrics
            quality_report = {
                "run_id": run_id,
                "total_metrics": len(metrics_df),
                "missing_values": metrics_df['value'].isnull().sum(),
                "zero_values": (metrics_df['value'] == 0).sum(),
                "negative_values": (metrics_df['value'] < 0).sum(),
                "outliers": {},
                "value_ranges": {}
            }
            
            # Calculate outliers and ranges by element
            for element in metrics_df['element_label'].unique():
                element_data = metrics_df[metrics_df['element_label'] == element]['value']
                
                # Basic statistics
                quality_report["value_ranges"][element] = {
                    "min": float(element_data.min()),
                    "max": float(element_data.max()),
                    "mean": float(element_data.mean()),
                    "std": float(element_data.std())
                }
                
                # Outliers using IQR method
                Q1 = element_data.quantile(0.25)
                Q3 = element_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = element_data[(element_data < lower_bound) | (element_data > upper_bound)]
                
                quality_report["outliers"][element] = len(outliers)
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Failed to generate data quality report: {e}")
            return {"error": str(e)}