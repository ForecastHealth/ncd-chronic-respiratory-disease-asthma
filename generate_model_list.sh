#!/bin/bash

# generate_model_list.sh
# Generates the list of models.

# Function to get the file_id from the metadata
get_file_id() {
    local file="$1"
    jq -r '.metadata.file_id // empty' "$file"
}

# Main script
echo '{"models": [' > list_of_models.json

first=true

# Iterate through all JSON files in ./models/*/
for model in ./models/*/*.json; do
    if [ -f "$model" ]; then
        name=$(get_file_id "$model")
        if [ -z "$name" ]; then
            name=$(basename "$model")
        fi

        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> list_of_models.json
        fi

        cat << EOF >> list_of_models.json
    {
        "name": "$name",
        "path": "$model"
    }
EOF
    fi
done

echo ']}' >> list_of_models.json

# Pretty-print the JSON
jq '.' list_of_models.json > temp.json && mv temp.json list_of_models.json

echo "Generated list_of_models.json"