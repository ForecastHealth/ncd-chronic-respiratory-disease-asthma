#!/bin/bash

# Multi-Repository Investment Case Runner
# Runs investment case generation for asthma, copd, cvd, and diabetes repositories
# Usage: ./run_all_investment_cases.sh [--repos repo1,repo2] [--skip-upload]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"  # Parent directory containing all repos
LOG_FILE="$SCRIPT_DIR/all_investment_cases_$(date +%Y%m%d_%H%M%S).log"
RESULTS_DIR="$SCRIPT_DIR/combined_results_$(date +%Y%m%d_%H%M%S)"

# Default repositories
DEFAULT_REPOS=("ncd-asthma" "ncd-copd" "ncd-cvd" "ncd-diabetes")
SELECTED_REPOS=()
SKIP_UPLOAD=false

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repos)
            IFS=',' read -ra SELECTED_REPOS <<< "$2"
            shift 2
            ;;
        --skip-upload)
            SKIP_UPLOAD=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--repos repo1,repo2] [--skip-upload]"
            echo ""
            echo "Options:"
            echo "  --repos        Comma-separated list of repositories (default: all)"
            echo "  --skip-upload  Skip the database upload step"
            echo "  --help         Show this help message"
            echo ""
            echo "Available repositories: ${DEFAULT_REPOS[*]}"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Use default repos if none specified
if [ ${#SELECTED_REPOS[@]} -eq 0 ]; then
    SELECTED_REPOS=("${DEFAULT_REPOS[@]}")
fi

# Logging functions
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_header() {
    log ""
    log "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "${CYAN}$1${NC}"
    log "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_step() {
    log "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ${GREEN}▶${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_success() {
    log "${GREEN}✓${NC} $1"
}

# Start
log_header "Multi-Repository Investment Case Automation"
log "Started at: $(date)"
log "Repositories to process: ${SELECTED_REPOS[*]}"
log "Base directory: $BASE_DIR"
log "Results will be collected in: $RESULTS_DIR"

# Create results collection directory
mkdir -p "$RESULTS_DIR"

# Track success/failure
declare -A REPO_STATUS
declare -A REPO_RESULTS

# Process each repository
TOTAL_START=$(date +%s)

for repo in "${SELECTED_REPOS[@]}"; do
    REPO_PATH="$BASE_DIR/$repo"
    
    log_header "Processing repository: $repo"
    
    # Check if repository exists
    if [ ! -d "$REPO_PATH" ]; then
        log_error "Repository not found: $REPO_PATH"
        REPO_STATUS["$repo"]="NOT_FOUND"
        continue
    fi
    
    # Check if investment case script exists
    if [ ! -f "$REPO_PATH/run_investment_case.sh" ]; then
        log_warning "Investment case script not found in $repo, attempting to copy from asthma..."
        
        # Try to copy from asthma repo if it exists
        if [ -f "$SCRIPT_DIR/run_investment_case.sh" ]; then
            cp "$SCRIPT_DIR/run_investment_case.sh" "$REPO_PATH/"
            chmod +x "$REPO_PATH/run_investment_case.sh"
            log_success "Script copied to $repo"
        else
            log_error "Could not find investment case script to copy"
            REPO_STATUS["$repo"]="NO_SCRIPT"
            continue
        fi
    fi
    
    # Run the investment case for this repository
    log_step "Running investment case for $repo..."
    
    cd "$REPO_PATH"
    REPO_START=$(date +%s)
    
    # Prepare command
    CMD="./run_investment_case.sh"
    if [ "$SKIP_UPLOAD" = true ]; then
        # The single-repo script will skip upload if .env.local is missing
        # But we can also explicitly tell it to skip if needed
        true  # No explicit flag needed, it auto-detects
    fi
    
    # Run and capture result
    if $CMD 2>&1 | tee -a "$LOG_FILE"; then
        REPO_STATUS["$repo"]="SUCCESS"
        
        # Find and copy the results file
        LATEST_RESULT=$(ls -t results/analytics_results_*.csv 2>/dev/null | head -1)
        if [ -n "$LATEST_RESULT" ] && [ -f "$LATEST_RESULT" ]; then
            # Copy with repo prefix
            cp "$LATEST_RESULT" "$RESULTS_DIR/${repo}_$(basename "$LATEST_RESULT")"
            REPO_RESULTS["$repo"]="$RESULTS_DIR/${repo}_$(basename "$LATEST_RESULT")"
            log_success "Results saved: ${repo}_$(basename "$LATEST_RESULT")"
        else
            log_warning "No results file found for $repo"
            REPO_RESULTS["$repo"]="NO_FILE"
        fi
    else
        REPO_STATUS["$repo"]="FAILED"
        log_error "Investment case failed for $repo"
    fi
    
    REPO_END=$(date +%s)
    REPO_DURATION=$((REPO_END - REPO_START))
    log "Repository $repo took $((REPO_DURATION / 60)) minutes and $((REPO_DURATION % 60)) seconds"
done

# Return to original directory
cd "$SCRIPT_DIR"

# Generate summary report
log_header "Summary Report"

log "Repository Status:"
for repo in "${SELECTED_REPOS[@]}"; do
    status="${REPO_STATUS["$repo"]:-UNKNOWN}"
    case "$status" in
        SUCCESS)
            log "  ${GREEN}✓${NC} $repo: Success"
            ;;
        FAILED)
            log "  ${RED}✗${NC} $repo: Failed"
            ;;
        NOT_FOUND)
            log "  ${YELLOW}⚠${NC} $repo: Repository not found"
            ;;
        NO_SCRIPT)
            log "  ${YELLOW}⚠${NC} $repo: Script not found"
            ;;
        *)
            log "  ${YELLOW}?${NC} $repo: Unknown status"
            ;;
    esac
done

log ""
log "Results Files:"
for repo in "${SELECTED_REPOS[@]}"; do
    if [ "${REPO_STATUS["$repo"]}" = "SUCCESS" ]; then
        result="${REPO_RESULTS["$repo"]}"
        if [ "$result" != "NO_FILE" ] && [ -n "$result" ]; then
            log "  $repo: $result"
        fi
    fi
done

# Create combined CSV if multiple successful results
SUCCESS_COUNT=0
for repo in "${SELECTED_REPOS[@]}"; do
    if [ "${REPO_STATUS["$repo"]}" = "SUCCESS" ] && [ "${REPO_RESULTS["$repo"]}" != "NO_FILE" ]; then
        ((SUCCESS_COUNT++))
    fi
done

if [ $SUCCESS_COUNT -gt 1 ]; then
    log ""
    log_step "Combining results files..."
    
    COMBINED_FILE="$RESULTS_DIR/combined_analytics_results.csv"
    FIRST=true
    
    for repo in "${SELECTED_REPOS[@]}"; do
        result="${REPO_RESULTS["$repo"]}"
        if [ "${REPO_STATUS["$repo"]}" = "SUCCESS" ] && [ "$result" != "NO_FILE" ] && [ -f "$result" ]; then
            if [ "$FIRST" = true ]; then
                # Copy first file with header
                cp "$result" "$COMBINED_FILE"
                FIRST=false
            else
                # Append without header
                tail -n +2 "$result" >> "$COMBINED_FILE"
            fi
        fi
    done
    
    log_success "Combined results saved to: $COMBINED_FILE"
    
    # Optional: Upload combined results
    if [ "$SKIP_UPLOAD" = false ] && [ -f "$SCRIPT_DIR/.env.local" ]; then
        log_step "Uploading combined results to database..."
        
        # Check if upload script exists
        if [ -f "$SCRIPT_DIR/upload_results.sh" ]; then
            if "$SCRIPT_DIR/upload_results.sh" "$COMBINED_FILE" 2>&1 | tee -a "$LOG_FILE"; then
                log_success "Combined results uploaded successfully"
            else
                log_warning "Failed to upload combined results"
            fi
        else
            log_warning "Upload script not found, skipping database upload"
        fi
    fi
fi

# Final summary
TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

log ""
log_header "Process Complete"
log "Total time: $((TOTAL_DURATION / 60)) minutes and $((TOTAL_DURATION % 60)) seconds"
log "Results collected in: $RESULTS_DIR"
log "Log file: $LOG_FILE"

# Exit with appropriate code
FAILED_COUNT=0
for repo in "${SELECTED_REPOS[@]}"; do
    if [ "${REPO_STATUS["$repo"]}" = "FAILED" ]; then
        ((FAILED_COUNT++))
    fi
done

if [ $FAILED_COUNT -gt 0 ]; then
    log ""
    log "${YELLOW}Warning: $FAILED_COUNT repositories failed${NC}"
    exit 1
else
    log ""
    log "${GREEN}All repositories processed successfully!${NC}"
    exit 0
fi