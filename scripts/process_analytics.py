#!/usr/bin/env python3
"""
Process analytics data and compute aggregated metrics.

Usage:
    python3 process_analytics.py --baseline asthma_baseline --csv validation_results.csv
    python3 process_analytics.py --baseline asthma_baseline --all
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import glob


# Cost data mapping - maps scenario names to CSV tags
SCENARIO_TO_COST_TAG = {
    # Cardiovascular interventions
    'cv1_scenario': 'CV1',
    'cv2a_scenario': 'CV2a',
    'cv2b_scenario': 'CV2b',
    'cv3a_scenario': 'CV3a',
    'cv3b_scenario': 'CV3b',
    'cv3c_scenario': 'CV3c',
    'cv3d_scenario': 'CV3d',
    'cv4a_scenario': 'CV4a',
    'cv4b_scenario': 'CV4b',
    'cv5a_scenario': 'CV5a',
    'cv5b_scenario': 'CV5b',
    'cv6_scenario': 'CV6',
    'cv7_scenario': 'CV7',
    # Diabetes interventions
    'd1_scenario': 'D1',
    'd2_scenario': 'D2',
    'd3_scenario': 'D3',
    'd5_scenario': 'D5',
    'd6_scenario': 'D6',
    'd7_scenario': 'D7',
    # Chronic respiratory interventions
    'asthma_cr1_scenario': 'CR1',
    'asthma_cr1': 'CR1',
    'cr1_scenario': 'CR1',
    'cr2_scenario': 'CR2',
    'asthma_cr3_scenario': 'CR3',
    'cr3_scenario': 'CR3',
    'cr4_scenario': 'CR4',
    # Tobacco interventions
    't1_scenario': 'T1',
    'tobacco_t1': 'T1',
    't2_scenario': 'T2',
    'tobacco_t2': 'T2',
    't3_scenario': 'T3',
    'tobacco_t3': 'T3',
    't4_scenario': 'T4',
    'tobacco_t4': 'T4',
    't5_scenario': 'T5',
    'tobacco_t5': 'T5',
    't6_scenario': 'T6',
    'tobacco_t6': 'T6',
    't7_scenario': 'T7',
    # Alcohol interventions
    'a1_scenario': 'A1',
    'a2_scenario': 'A2',
    'a3_scenario': 'A3',
    'a4_scenario': 'A4',
    'a5_scenario': 'A5',
    # Unhealthy diet interventions
    'u1_scenario': 'U1',
    'u2_scenario': 'U2',
    'u3_scenario': 'U3',
    'u4_scenario': 'U4',
    'u5_scenario': 'U5',
    'u9_scenario': 'U9',
    # Physical activity interventions
    'p1_scenario': 'P1',
    'p2_scenario': 'P2'
}


def load_cost_data(csv_path="Appendix 3 Costs Reverse Engineering - TABLE.csv"):
    """Load cost per capita data from CSV."""
    costs = {}
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            for row in reader:
                if len(row) >= 5 and row[0].strip():  # Has TAG and TOTAL columns
                    tag = row[0].strip()
                    total_cost = float(row[4].strip())
                    costs[tag] = total_cost
    except (FileNotFoundError, ValueError) as e:
        print(f"Warning: Could not load cost data: {e}")
    
    return costs


def calculate_discounted_value(value, year, base_year=2025, discount_rate=0.03):
    """Apply discounting to a value."""
    years_from_base = year - base_year
    if years_from_base <= 0:
        return value
    discount_factor = 1 / ((1 + discount_rate) ** years_from_base)
    return value * discount_factor


# Modular metric definitions - easily adjustable
METRICS_CONFIG = {
    "deaths_averted_2030": {
        "name": "Total deaths averted by 2030",
        "event_type": "echo",
        "element_labels": ["Deceased-DsFreeSus", "Deceased-AsthmaEpsd"],
        "year_filter": lambda y: y <= 2030,
        "aggregation": "sum"
    },
    "deaths_averted_2035": {
        "name": "Total deaths averted by 2035",
        "event_type": "echo",
        "element_labels": ["Deceased-DsFreeSus", "Deceased-AsthmaEpsd"],
        "year_filter": lambda y: y <= 2035,
        "aggregation": "sum"
    },
    "cases_averted_2030": {
        "name": "Cases averted by 2030",
        "event_type": "echo",
        "element_labels": ["AsthmaEpsd"],
        "year_filter": lambda y: y <= 2030,
        "aggregation": "sum"
    },
    "cases_averted_2035": {
        "name": "Cases averted by 2035",
        "event_type": "echo",
        "element_labels": ["AsthmaEpsd"],
        "year_filter": lambda y: y <= 2035,
        "aggregation": "sum"
    },
    "healthy_years_2030": {
        "name": "Total healthy years lived by 2030",
        "event_type": "echo",
        "element_labels": ["Healthy Years Lived"],
        "year_filter": lambda y: y <= 2030,
        "aggregation": "sum"
    },
    "healthy_years_2035": {
        "name": "Total healthy years lived by 2035",
        "event_type": "echo",
        "element_labels": ["Healthy Years Lived"],
        "year_filter": lambda y: y <= 2035,
        "aggregation": "sum"
    },
    "economic_benefit_2030": {
        "name": "Economic benefit (USD) by 2030",
        "event_type": "echo",
        "element_labels": ["Economic Value"],
        "year_filter": lambda y: y <= 2030,
        "aggregation": "sum",
        "apply_discounting": True
    },
    "economic_benefit_2035": {
        "name": "Economic benefit (USD) by 2035",
        "event_type": "echo",
        "element_labels": ["Economic Value"],
        "year_filter": lambda y: y <= 2035,
        "aggregation": "sum",
        "apply_discounting": True
    },
    "intervention_cost_2030": {
        "name": "Intervention cost (USD) by 2030",
        "event_type": "echo",
        "element_labels": ["DsFreeSus", "AsthmaEpsd"],
        "year_filter": lambda y: y <= 2030,
        "aggregation": "cost",
        "apply_discounting": True
    },
    "intervention_cost_2035": {
        "name": "Intervention cost (USD) by 2035",
        "event_type": "echo",
        "element_labels": ["DsFreeSus", "AsthmaEpsd"],
        "year_filter": lambda y: y <= 2035,
        "aggregation": "cost",
        "apply_discounting": True
    }
}


def load_csv_data(csv_path):
    """Load ULID data from CSV file."""
    data_by_country = defaultdict(list)
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row.get('country', 'unknown')
            scenario = row.get('scenario', 'unknown')
            ulid = row.get('ulid')
            if ulid:
                data_by_country[country].append({
                    'ulid': ulid,
                    'scenario': scenario,
                    'country': country
                })
    
    return data_by_country


def find_latest_file(pattern, tmp_dir="tmp"):
    """Find the most recent file matching the pattern."""
    files = glob.glob(str(Path(tmp_dir) / pattern))
    if not files:
        return None
    
    # Sort by modification time and return the latest
    files.sort(key=lambda f: Path(f).stat().st_mtime, reverse=True)
    return files[0]


def check_scenario_files_exist(ulid, scenario, tmp_dir="tmp"):
    """Check if all required files exist for a scenario."""
    required_files = {
        'echo': f"{ulid}_{scenario}_echo_*.json"
    }
    
    file_paths = {}
    for file_type, pattern in required_files.items():
        file_path = find_latest_file(pattern, tmp_dir)
        if not file_path:
            return None
        file_paths[file_type] = file_path
    
    return file_paths


def load_json_file(filepath):
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def calculate_metric(data, metric_config, cost_per_capita=None):
    """Calculate a single metric based on configuration."""
    total = 0
    
    for item in data:
        # Check if element_label matches
        if item.get('element_label') not in metric_config['element_labels']:
            continue
        
        # Check year filter
        year = item.get('timestamp_year')
        if year and not metric_config['year_filter'](year):
            continue
        
        # Get value
        value = item.get('value', 0)
        
        # Handle different aggregation types
        if metric_config['aggregation'] == 'sum':
            # Apply discounting if specified
            if metric_config.get('apply_discounting', False) and year:
                value = calculate_discounted_value(value, year)
            total += value
        elif metric_config['aggregation'] == 'cost' and cost_per_capita is not None:
            # For cost calculations: multiply population by per capita cost
            cost_value = value * cost_per_capita
            
            # Apply discounting if specified
            if metric_config.get('apply_discounting', False):
                cost_value = calculate_discounted_value(cost_value, year)
            
            total += cost_value
    
    return total


def process_comparison(baseline_files, comparison_files, scenario_name=None, cost_data=None, metrics_to_calculate=None):
    """Process comparison between baseline and comparison scenario."""
    results = {}
    
    # Use all metrics if none specified
    if metrics_to_calculate is None:
        metrics_to_calculate = METRICS_CONFIG.keys()
    
    # Get cost per capita for this scenario if available
    cost_per_capita = None
    if cost_data and scenario_name:
        cost_tag = SCENARIO_TO_COST_TAG.get(scenario_name)
        if cost_tag:
            cost_per_capita = cost_data.get(cost_tag, 0)
    
    for metric_key in metrics_to_calculate:
        metric_config = METRICS_CONFIG[metric_key]
        event_type = metric_config['event_type']
        
        # Load data files
        baseline_data = load_json_file(baseline_files[event_type])
        comparison_data = load_json_file(comparison_files[event_type])
        
        # Calculate metrics
        if metric_config.get('aggregation') == 'cost':
            # For cost metrics, only calculate for the comparison scenario
            baseline_value = 0  # No intervention cost for baseline
            comparison_value = calculate_metric(comparison_data, metric_config, cost_per_capita)
        else:
            baseline_value = calculate_metric(baseline_data, metric_config)
            comparison_value = calculate_metric(comparison_data, metric_config)
        
        # Result is COMPARISON - BASELINE (for costs, this shows the cost of intervention)
        results[metric_key] = {
            'name': metric_config['name'],
            'baseline_value': baseline_value,
            'comparison_value': comparison_value,
            'difference': comparison_value - baseline_value
        }
    
    return results


def format_results(country, scenario, results):
    """Format results for display."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Country: {country}")
    lines.append(f"Scenario: {scenario}")
    lines.append(f"{'='*60}")
    
    for metric_key, metric_result in results.items():
        lines.append(f"\n{metric_result['name']}:")
        lines.append(f"  Baseline: {metric_result['baseline_value']:,.0f}")
        lines.append(f"  Comparison: {metric_result['comparison_value']:,.0f}")
        lines.append(f"  Difference: {metric_result['difference']:+,.0f}")
    
    return '\n'.join(lines)


def save_results_json(all_results, output_path):
    """Save results to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)


def save_results_csv(all_results, output_path):
    """Save results to CSV file."""
    rows = []
    
    for country, scenarios in all_results.items():
        for scenario, metrics in scenarios.items():
            for metric_key, metric_data in metrics.items():
                row = {
                    'country': country,
                    'scenario': scenario,
                    'metric': metric_data['name'],
                    'baseline_value': metric_data['baseline_value'],
                    'comparison_value': metric_data['comparison_value'],
                    'difference': metric_data['difference']
                }
                rows.append(row)
    
    if rows:
        with open(output_path, 'w', newline='') as f:
            fieldnames = ['country', 'scenario', 'metric', 'baseline_value', 'comparison_value', 'difference']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description='Process analytics data and compute metrics')
    parser.add_argument('--baseline', required=True,
                       help='Baseline scenario name (e.g., asthma_baseline)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--csv',
                       help='CSV file containing ULIDs')
    group.add_argument('--all', action='store_true',
                       help='Use validation_results.csv')
    parser.add_argument('--output-dir', default='results',
                       help='Output directory for results (default: results)')
    parser.add_argument('--output-format', choices=['json', 'csv', 'both'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--tmp-dir', default='tmp',
                       help='Directory containing fetched JSON files (default: tmp)')
    parser.add_argument('--metrics', nargs='+',
                       help='Specific metrics to calculate (default: all)')
    
    args = parser.parse_args()
    
    # Load CSV data
    csv_path = 'validation_results.csv' if args.all else args.csv
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        return 1
    
    data_by_country = load_csv_data(csv_path)
    
    # Load cost data
    cost_data = load_cost_data()
    
    if not data_by_country:
        print(f"No data found in {csv_path}")
        return 1
    
    # Prepare output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each country
    all_results = {}
    valid_comparisons = 0
    invalid_comparisons = 0
    
    for country, entries in data_by_country.items():
        print(f"Processing {country}...")
        # Find baseline ULID for this country
        baseline_entry = None
        comparison_entries = []
        
        for entry in entries:
            if entry['scenario'] == args.baseline:
                baseline_entry = entry
            else:
                comparison_entries.append(entry)
        
        if not baseline_entry:
            print(f"⚠ No baseline scenario '{args.baseline}' found for {country}")
            continue
        
        # Check if baseline files exist
        baseline_files = check_scenario_files_exist(
            baseline_entry['ulid'], 
            baseline_entry['scenario'],
            args.tmp_dir
        )
        
        if not baseline_files:
            print(f"⚠ Missing files for baseline {country}/{args.baseline}")
            invalid_comparisons += 1
            continue
        
        # Process each comparison scenario
        country_results = {}
        
        for comp_entry in comparison_entries:
            # Check if comparison files exist
            comp_files = check_scenario_files_exist(
                comp_entry['ulid'],
                comp_entry['scenario'],
                args.tmp_dir
            )
            
            if not comp_files:
                print(f"⚠ Missing files for {country}/{comp_entry['scenario']}")
                invalid_comparisons += 1
                continue
            
            # Calculate metrics
            results = process_comparison(
                baseline_files, 
                comp_files,
                comp_entry['scenario'],
                cost_data,
                args.metrics
            )
            
            country_results[comp_entry['scenario']] = results
            valid_comparisons += 1
        
        if country_results:
            all_results[country] = country_results
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.output_format in ['json', 'both']:
        json_path = output_dir / f"analytics_results_{timestamp}.json"
        save_results_json(all_results, json_path)
        print(f"\n✓ JSON results saved to: {json_path}")
    
    if args.output_format in ['csv', 'both']:
        csv_path = output_dir / f"analytics_results_{timestamp}.csv"
        save_results_csv(all_results, csv_path)
        print(f"✓ CSV results saved to: {csv_path}")
    
    
    return 0


if __name__ == "__main__":
    exit(main())
