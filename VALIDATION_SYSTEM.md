# Multi-Country Multi-Scenario Validation System

This document describes the enhanced validation system that provides centralized storage and change tracking for model validation results.

## Overview

The validation system has been enhanced with:
- **SQLite Database Storage**: All validation results stored in a central database
- **Git Commit Tracking**: Automatic detection of changes for incremental execution
- **Query Interface**: SQL and pandas-based analysis tools
- **CLI Interface**: Simple command-line tools for maintainers
- **Backward Compatibility**: Existing cloud infrastructure and CSV exports maintained

## Quick Start

### 1. Run Full Validation
```bash
# Run all countries and scenarios (only those needing updates)
python scripts/validate_changes.py

# Force rerun everything
python scripts/validate_changes.py --force

# Run specific countries
python scripts/validate_changes.py --countries USA CAN MEX

# Run specific scenarios
python scripts/validate_changes.py --scenarios asthma_cr1_scenario asthma_cr3_scenario
```

### 2. Check Status
```bash
# Show recent validation run status
python scripts/validate_changes.py --status
```

### 3. Query Results
```bash
# Show common query examples
python scripts/validate_changes.py --examples

# Run custom SQL query
python scripts/validate_changes.py --query "SELECT * FROM metrics WHERE country='USA'"

# Export results to CSV
python scripts/validate_changes.py --export-run 123 --output-dir results/
```

## Database Schema

The system uses three main tables:

### `validation_runs`
- `run_id`: Primary key
- `timestamp`: When the run started
- `git_commit`: Git commit hash
- `status`: 'running', 'completed', 'failed'
- `total_jobs`, `successful_jobs`, `failed_jobs`: Job counts

### `job_results`
- `run_id`: Reference to validation run
- `country`: Country ISO3 code
- `scenario`: Scenario name
- `ulid`: Job ULID
- `job_status`: 'success', 'failed', 'timeout'
- `submitted_at`, `completed_at`: Timestamps

### `metrics`
- `run_id`: Reference to validation run
- `country`: Country ISO3 code
- `scenario`: Scenario name
- `ulid`: Job ULID
- `element_label`: Metric name
- `timestamp_year`: Year
- `value`: Metric value

## Key Features

### Incremental Execution
The system automatically detects which country/scenario combinations need to be rerun based on:
- Git commit changes
- Previous job failures
- New combinations that haven't been run before

### Query Interface
Use the built-in query interface for analysis:

```python
from utilities.query_results import ResultsQuery

query = ResultsQuery()
summary = query.get_latest_run_summary()
metrics_df = query.get_metrics_dataframe()
comparison_df = query.compare_scenarios("USA", "scenario_a", "scenario_b")
```

### Analytics Integration
The system integrates with existing analytics processing:
- Fetches results from the analytics API
- Stores metrics in the database
- Maintains CSV export for backward compatibility

## File Structure

```
utilities/
├── validation_db.py              # Database management
├── analytics/
│   ├── database_processor.py     # Analytics → DB integration
│   └── processor.py              # Existing (unchanged)
└── query_results.py              # Query interface

scripts/
├── run_all_validations.py        # Enhanced runner
├── validate_changes.py           # CLI interface
└── existing scripts...           # Unchanged

validation_results.db              # SQLite database
```

## Common Queries

### Show all validation runs
```sql
SELECT * FROM validation_runs ORDER BY timestamp DESC
```

### Find failed jobs
```sql
SELECT jr.country, jr.scenario, jr.job_status 
FROM job_results jr 
JOIN validation_runs vr ON jr.run_id = vr.run_id 
WHERE vr.run_id = (SELECT MAX(run_id) FROM validation_runs) 
AND jr.job_status != 'success'
```

### Compare scenarios
```sql
SELECT country, element_label, timestamp_year, 
       scenario, value 
FROM metrics 
WHERE country = 'USA' 
AND scenario IN ('asthma_cr1_scenario', 'asthma_cr3_scenario')
ORDER BY element_label, timestamp_year, scenario
```

### Success rates by scenario
```sql
SELECT scenario, 
       COUNT(*) as total, 
       SUM(CASE WHEN job_status = 'success' THEN 1 ELSE 0 END) as successful,
       ROUND((SUM(CASE WHEN job_status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as success_rate
FROM job_results 
GROUP BY scenario
```

## Migration from Existing System

The new system is designed to work alongside the existing infrastructure:

1. **Existing Scripts**: All existing scripts continue to work unchanged
2. **CSV Export**: Analytics are still exported to CSV files in the `validation/` directory
3. **Cloud Infrastructure**: AWS Batch jobs and analytics API remain unchanged
4. **Gradual Migration**: You can use both systems in parallel during transition

## Troubleshooting

### Database Issues
- Database file: `validation_results.db` (created automatically)
- Reset database: Delete the file and restart
- Check schema: Use `--query "SELECT name FROM sqlite_master WHERE type='table'"`

### Import Errors
- Ensure you're in the project root directory
- Check that `utilities/` directory is in the Python path
- Install required packages: `pip install pandas` (optional for query interface)

### Performance
- Database operations are optimized with indexes
- Large datasets: Use `--query` with LIMIT clauses
- Export large results to CSV for external analysis

## Advanced Usage

### Custom Analytics Processing
```python
from utilities.analytics.database_processor import DatabaseAnalyticsProcessor

processor = DatabaseAnalyticsProcessor()
results = processor.process_multiple_jobs_with_database(
    jobs=[{"job_name": "...", "country": "USA", "scenario": "..."}],
    run_id=123,
    model_name="model"
)
```

### Batch Data Analysis
```python
from utilities.query_results import ResultsQuery

query = ResultsQuery()
df = query.get_metrics_dataframe()
trends = query.get_metric_trends("population", countries=["USA", "CAN"])
quality_report = query.get_data_quality_report()
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the SPECDOC_PLAN.md for detailed implementation notes
3. Use `--verbose` flag for detailed logging
4. Check database contents with `--query` or `--status` commands