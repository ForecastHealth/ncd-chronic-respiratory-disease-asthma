# Simplified Multi-Country Multi-Scenario Database System

## Core Requirements
Run all countries for all scenarios and save results to SQLite database for inspection and change monitoring.

## Implementation Plan

### 1. SQLite Database Schema (`validation_db.py`)
- **validation_runs**: Track each batch execution (timestamp, git_commit, status)
- **results**: Store analytics data (run_id, country, scenario, job_id, ulid, analytics_json)
- Simple, focused schema - no CSV compatibility needed

### 2. Enhanced Multi-Country Runner (`run_all_validations.py`)
- Discover all available scenarios automatically
- Load country list from existing configuration
- Generate all scenario×country combinations
- Submit jobs with proper throttling
- Save all results directly to SQLite database

### 3. Database Integration (`database.py`)
- SQLite connection management
- Insert analytics data as JSON
- Simple query interface for inspection
- Basic reporting functions

### 4. Modified Analytics Processor
- Remove CSV export functionality
- Save analytics data directly to database
- Maintain ULID tracking for job correlation

## Key Benefits
- Single source of truth in SQLite database
- Easy to inspect results and track changes over time
- Simplified codebase without CSV/database duplication
- All scenarios × all countries in one execution

## Deliverables
- SQLite database with simple schema
- Enhanced validation runner for all combinations
- Database storage integration
- Basic query tools for inspection
