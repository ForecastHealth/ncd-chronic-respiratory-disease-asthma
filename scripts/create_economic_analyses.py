#!/usr/bin/env python3

import json
import glob
import os
import argparse

def create_economic_analyses():
    # Initialize list to store economic analyses
    economic_analyses = []
    
    # Load countries data
    countries_file_path = './list_of_countries.json'
    country_iso3_codes = []
    
    if os.path.exists(countries_file_path):
        try:
            # Load countries data
            with open(countries_file_path, 'r', encoding='utf-8') as f:
                countries_data = json.load(f)
            
            # Extract ISO3 codes
            country_iso3_codes = [country['iso3'] for country in countries_data['countries']]
            print(f"Using countries from: {countries_file_path}")
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Error processing countries file: {e}")
            return
    else:
        print(f"Countries file not found: {countries_file_path}")
        return
    
    # Ensure economic-analyses directory exists
    os.makedirs('./economic-analyses', exist_ok=True)
    
    # Process each economic analysis template
    template_files = glob.glob('./economic-analyses-templates/*.json')
    if not template_files:
        print("No economic analysis templates found in ./economic-analyses-templates/")
        return
    
    analyses_created = 0
    
    for template_path in template_files:
        try:
            # Load the template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template_filename = os.path.basename(template_path)
            template_name = os.path.splitext(template_filename)[0]
            
            baseline_scenario_stub = template_data.get('baseline_name', '')
            comparison_scenario_stub = template_data.get('comparator_name', '')
            
            # For each country, create an analysis record if both scenarios exist
            for iso3 in country_iso3_codes:
                baseline_scenario_file = f"./scenarios/{baseline_scenario_stub}_{iso3}.json"
                comparison_scenario_file = f"./scenarios/{comparison_scenario_stub}_{iso3}.json"
                
                # Check if both scenario files exist for this country
                if os.path.exists(baseline_scenario_file) and os.path.exists(comparison_scenario_file):
                    # Add ISO3 code to name and description if they exist
                    name = template_data.get('name', '')
                    description = template_data.get('description', '')
                    
                    if name:
                        name = f"{name} - {iso3}"
                    
                    if description:
                        description = f"{description} - {iso3}"
                        
                    analysis = {
                        'name': name,
                        'description': description,
                        'baseline_scenario_label': f"{baseline_scenario_stub}_{iso3}",
                        'comparator_scenario_label': f"{comparison_scenario_stub}_{iso3}",
                        'numerator_label': template_data.get('numerator', ''),
                        'denominator_label': template_data.get('denominator', '')
                    }
                    economic_analyses.append(analysis)
                    analyses_created += 1
                else:
                    if not os.path.exists(baseline_scenario_file):
                        print(f"Warning: Baseline scenario file not found for {iso3}: {baseline_scenario_file}")
                    if not os.path.exists(comparison_scenario_file):
                        print(f"Warning: Comparison scenario file not found for {iso3}: {comparison_scenario_file}")
                
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Error processing template {template_path}: {e}")
    
    # Write output to file
    with open('./list_of_economic_analyses.json', 'w', encoding='utf-8') as f:
        json.dump(economic_analyses, f, indent=4, ensure_ascii=False)
    
    print(f"Created {analyses_created} economic analyses for {len(country_iso3_codes)} countries and {len(template_files)} analysis templates.")
    print(f"Total records: {len(economic_analyses)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create economic analyses using templates and country-specific scenarios')
    args = parser.parse_args()
    
    create_economic_analyses()