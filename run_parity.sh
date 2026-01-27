#!/bin/bash
# Run parity tests comparing Rust vs Python engine outputs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUST_BINARY="${RUST_BINARY:-/home/rory/Documents/botech-rust/target/release/run_model}"
COUNTRIES="${COUNTRIES:-/home/rory/Documents/botech-model-utilities/botech_sd_utilities/data/countries/list_of_pruned_countries.json}"

# Use test countries for quick runs: ./run_parity.sh --test
if [[ "$1" == "--test" ]]; then
    COUNTRIES="/home/rory/Documents/botech-model-utilities/botech_sd_utilities/data/countries/list_of_test_countries.json"
    echo "Running with test countries (8 countries)"
fi

cd "$SCRIPT_DIR"

fh parity \
    --model model.json \
    --scenarios-dir scenarios \
    --countries "$COUNTRIES" \
    --rust-binary "$RUST_BINARY" \
    --report parity_report.txt \
    --verbose
