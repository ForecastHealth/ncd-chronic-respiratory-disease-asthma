#!/usr/bin/env python3
"""
CLI entry point for model validation.

This script provides a command-line interface to the validation utilities.
The actual validation logic is implemented in the utilities package modules.

Usage:
python utilities/validate_model_changes.py [options]
"""

import argparse
import sys

from . import (
    validate_model_changes,
    DEFAULT_MODEL,
    DEFAULT_SCENARIO, 
    DEFAULT_ENVIRONMENT
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate model changes before committing to main branch. Supports single-country or multi-country validation.",
        prog="validate_model_changes"
    )
    
    parser.add_argument(
        '--model',
        default=DEFAULT_MODEL,
        help=f"Path to the model JSON file (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        '--scenario',
        default=DEFAULT_SCENARIO,
        help=f"Path to the scenario JSON file (default: {DEFAULT_SCENARIO})"
    )
    parser.add_argument(
        '--environment',
        default=DEFAULT_ENVIRONMENT,
        choices=['default', 'standard', 'appendix_3'],
        help=f"Environment to use for API testing (default: {DEFAULT_ENVIRONMENT})"
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=3,
        help="Polling interval in seconds (default: 3)"
    )
    parser.add_argument(
        '--max-wait-time',
        type=int,
        default=3600,
        help="Maximum wait time in seconds (default: 3600)"
    )
    parser.add_argument(
        '--skip-api-test',
        action='store_true',
        help="Skip remote API testing (for offline validation)"
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help="Skip cleanup of temporary files"
    )
    parser.add_argument(
        '--countries',
        help="Path to countries JSON file for multi-country validation"
    )
    parser.add_argument(
        '--max-instances',
        type=int,
        default=100,
        help="Maximum number of concurrent AWS Batch instances (default: 100)"
    )
    parser.add_argument(
        '--no-analytics',
        action='store_true',
        help="Skip analytics generation"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress detailed output (only show errors)"
    )
    
    args = parser.parse_args()
    
    # Run validation
    success = validate_model_changes(
        model_path=args.model,
        scenario_path=args.scenario,
        environment=args.environment,
        poll_interval=args.poll_interval,
        max_wait_time=args.max_wait_time,
        skip_api_test=args.skip_api_test,
        no_cleanup=args.no_cleanup,
        verbose=not args.quiet,
        generate_analytics=not args.no_analytics,
        countries_path=args.countries,
        max_instances=args.max_instances
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()