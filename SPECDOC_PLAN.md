# Multi-Country Multi-Scenario Database System

## Core Requirements
Run all countries for all scenarios and save results to SQLite database for inspection and change monitoring. Keep existing cloud execution infrastructure (AWS Batch, analytics API) but centralize result storage.

## Database Schema

```sql
-- Track batch executions
CREATE TABLE validation_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    git_commit TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'running', 'completed', 'failed'
    total_jobs INTEGER,
    successful_jobs INTEGER,
    failed_jobs INTEGER
);

-- Store individual job results
CREATE TABLE job_results (
    run_id INTEGER,
    country TEXT NOT NULL,
    scenario TEXT NOT NULL,
    ulid TEXT NOT NULL,
    job_status TEXT NOT NULL,  -- 'success', 'failed', 'timeout'
    submitted_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (run_id) REFERENCES validation_runs(run_id),
    PRIMARY KEY (run_id, country, scenario)
);

-- Store the actual analytics metrics
CREATE TABLE metrics (
    run_id INTEGER,
    country TEXT NOT NULL,
    scenario TEXT NOT NULL,
    ulid TEXT NOT NULL,
    element_label TEXT NOT NULL,
    timestamp_year INTEGER NOT NULL,
    value REAL NOT NULL,
    FOREIGN KEY (run_id) REFERENCES validation_runs(run_id),
    PRIMARY KEY (run_id, country, scenario, element_label, timestamp_year)
);

-- Indexes for performance
CREATE INDEX idx_metrics_country_scenario ON metrics(country, scenario);
CREATE INDEX idx_metrics_element ON metrics(element_label);
CREATE INDEX idx_metrics_year ON metrics(timestamp_year);
CREATE INDEX idx_job_results_status ON job_results(job_status);
```

## Detailed Implementation Plan

### 1. Database Module (`utilities/validation_db.py`)

**Purpose**: SQLite database management with schema creation and data operations.

**Key Components**:
```python
class ValidationDatabase:
    def __init__(self, db_path="validation_results.db")
    def setup_schema()
    def start_validation_run(git_commit, total_jobs) -> run_id
    def update_run_status(run_id, status, successful_jobs, failed_jobs)
    def record_job_result(run_id, country, scenario, ulid, status, submitted_at, completed_at)
    def store_metrics(run_id, country, scenario, ulid, metrics_data)
    def get_failed_jobs(run_id) -> List[Tuple[country, scenario]]
    def needs_rerun(country, scenario, current_git_commit) -> bool
```

**Implementation Details**:
- Use `sqlite3` with connection pooling
- Implement proper error handling and transaction management
- Add method to parse CSV analytics data into normalized metrics
- Include data validation for required fields
- Support batch insertions for performance

### 2. Enhanced Multi-Country Runner (`scripts/run_all_validations.py`)

**Purpose**: Orchestrate full validation runs with database integration.

**Key Components**:
```python
class EnhancedValidationRunner:
    def __init__(self, db_path="validation_results.db")
    def discover_scenarios() -> List[str]
    def load_countries() -> List[str]  
    def generate_all_combinations() -> List[Tuple[country, scenario]]
    def filter_combinations_needing_rerun(combinations, git_commit) -> List[Tuple]
    def submit_jobs_with_throttling(combinations)
    def monitor_job_progress(job_ids)
    def fetch_and_store_results(completed_jobs)
```

**Implementation Details**:
- Integrate with existing `utilities/multi_country.py` for job submission
- Use existing throttling and AWS Batch integration
- Add git commit detection: `subprocess.check_output(['git', 'rev-parse', 'HEAD'])`
- Implement incremental execution: only run combinations that need updates
- Add comprehensive logging and progress reporting
- Handle partial failures gracefully with retry logic

### 3. Analytics Integration (`utilities/analytics/database_processor.py`)

**Purpose**: Bridge between analytics API and database storage.

**Key Components**:
```python
class DatabaseAnalyticsProcessor:
    def __init__(self, db_path="validation_results.db")
    def fetch_analytics_for_ulid(ulid) -> Dict
    def parse_analytics_csv(csv_content) -> List[Dict]
    def store_analytics_in_db(run_id, country, scenario, ulid, analytics_data)
    def maintain_csv_compatibility(analytics_data) -> str  # Optional
```

**Implementation Details**:
- Extend existing `utilities/analytics/processor.py`
- Keep existing CSV export as fallback during transition
- Parse analytics CSV format: `element_label,timestamp_year,value`
- Add data validation and type conversion
- Handle missing or malformed analytics data gracefully

### 4. Command-Line Interface (`scripts/validate_changes.py`)

**Purpose**: Simple CLI for maintainers to run validations and query results.

**Key Components**:
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--countries', nargs='+', help='Specific countries to run')
    parser.add_argument('--scenarios', nargs='+', help='Specific scenarios to run')
    parser.add_argument('--force', action='store_true', help='Force re-run all combinations')
    parser.add_argument('--query', help='Run SQL query on results')
    parser.add_argument('--status', action='store_true', help='Show recent run status')
```

**Implementation Details**:
- Default behavior: run only combinations that need updates
- Support for selective country/scenario execution
- Built-in query interface for common questions
- Status reporting with job success/failure counts
- Integration with existing validation infrastructure

### 5. Query Interface (`utilities/query_results.py`)

**Purpose**: Convenient methods for analyzing stored results.

**Key Components**:
```python
class ResultsQuery:
    def __init__(self, db_path="validation_results.db")
    def get_latest_run_summary() -> Dict
    def compare_scenarios(country, scenario_a, scenario_b) -> DataFrame
    def get_failed_jobs(run_id=None) -> List[Dict]
    def get_metric_trends(element_label, countries=None) -> DataFrame
    def export_results_csv(run_id, output_path)
```

**Implementation Details**:
- Use pandas for data analysis and export
- Implement common queries as methods
- Support CSV export for backward compatibility
- Add visualization helpers for key metrics
- Include data quality checks and validation

## File Structure

```
utilities/
├── validation_db.py              # Database management
├── analytics/
│   ├── database_processor.py     # Analytics → DB integration
│   └── processor.py              # Existing (enhanced)
└── query_results.py              # Query interface

scripts/
├── run_all_validations.py        # Enhanced runner
├── validate_changes.py           # CLI interface
└── existing scripts...           # Unchanged

validation_results.db              # SQLite database
```

## Migration Strategy

### Phase 1: Database Setup
1. Create `utilities/validation_db.py` with schema
2. Add database initialization to existing scripts
3. Test schema with sample data

### Phase 2: Parallel Storage
1. Enhance analytics processor to store in both CSV and database
2. Update multi-country runner to record job metadata
3. Validate data consistency between CSV and database

### Phase 3: CLI Integration
1. Create `scripts/validate_changes.py` with incremental execution
2. Add query interface for result inspection
3. Document new workflow for maintainers

### Phase 4: Full Migration
1. Switch default behavior to database-first
2. Make CSV export optional
3. Add comprehensive documentation and examples

## Key Benefits

- **Centralized Storage**: All results in single SQLite database
- **Change Tracking**: Git commit tracking for incremental execution
- **Performance**: Only run combinations that need updates
- **Backward Compatibility**: Keep existing cloud infrastructure
- **Query Flexibility**: SQL interface for complex analysis
- **Maintainer Friendly**: Simple CLI for common operations

## Maintainer Workflow

1. **Make changes** to model files or scenarios
2. **Run validation**: `python scripts/validate_changes.py`
3. **System automatically**:
   - Detects changed files via git commit
   - Identifies combinations needing re-execution
   - Submits jobs to existing cloud infrastructure
   - Stores results in centralized database
4. **Query results**: `python scripts/validate_changes.py --query "SELECT * FROM metrics WHERE country='USA'"`
5. **Check status**: `python scripts/validate_changes.py --status`

This approach preserves all existing cloud execution capabilities while providing the centralized storage and change tracking benefits you need.