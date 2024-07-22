#!/bin/bash

# Create necessary directories
mkdir -p docs/models/ docs/scenarios/

# Run the new shell scripts to generate model and scenario lists
./generate_model_list.sh
./generate_scenarios_list.sh

# Copy JSON files to docs directory
cp ./list_of_countries.json ./docs/
cp ./list_of_models.json ./docs/
cp ./list_of_scenarios.json ./docs/
cp ./list_of_results.json ./docs/

# Copy model and scenario JSON files while preserving directory structure
rsync -av --include='*/' --include='*.json' --exclude='*' ./models/ ./docs/models/
rsync -av --include='*/' --include='*.json' --exclude='*' ./scenarios/ ./docs/scenarios/

echo "Build process completed."