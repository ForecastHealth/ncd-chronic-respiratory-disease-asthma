- Run python -m validation_suite.tui for each scenario for ./countries/list_of_pruned_countries.json
   - Outputs ./validation_results.csv
- Run ./scripts/fetch_analytics.py on ./validation_results.csv
   - Takes a while with necessary 5 second pause between obtaining JSON responses (analytics API requirement)
- Run ./scripts/process_analytics.py with --baseline being e.g. `asthma_baseline`
   - Produces e.g. ./results/analytics_results_20250818_123317.csv
- Run ./upload_results.sh ./results/analytics_results_20250818_123317.csv

