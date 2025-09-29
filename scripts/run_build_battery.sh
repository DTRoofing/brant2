#!/bin/bash
# Comprehensive Build Test Battery Script
# This script runs all build verification tests in sequence

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERBOSE=false
SKIP_DOCKER=false
OUTPUT_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -v, --verbose     Enable verbose output"
            echo "  --skip-docker     Skip Docker build tests"
            echo "  -o, --output DIR  Output directory for reports"
            echo "  -h, --help        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
}

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local output_file="$OUTPUT_DIR/${test_name}_${TIMESTAMP}.log"
    
    log "Running $test_name..."
    
    if $VERBOSE; then
        echo "Command: $test_command"
    fi
    
    # Run the test and capture output
    if eval "$test_command" > "$output_file" 2>&1; then
        log_success "$test_name completed successfully"
        return 0
    else
        log_error "$test_name failed"
        if $VERBOSE; then
            echo "Error output:"
            tail -20 "$output_file"
        fi
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        log_error "pyproject.toml not found. Please run from project root."
        exit 1
    fi
    
    # Check Docker (if not skipping)
    if [[ "$SKIP_DOCKER" == "false" ]]; then
        if ! command -v docker &> /dev/null; then
            log_warning "Docker not found. Skipping Docker tests."
            SKIP_DOCKER=true
        else
            # Check if Docker daemon is running
            if ! docker info &> /dev/null; then
                log_warning "Docker daemon not running. Skipping Docker tests."
                SKIP_DOCKER=true
            fi
        fi
    fi
    
    log_success "Prerequisites check completed"
}

# Main test execution
main() {
    echo "🏗️  COMPREHENSIVE BUILD TEST BATTERY"
    echo "===================================="
    echo "Timestamp: $(date)"
    echo "Output Directory: $OUTPUT_DIR"
    echo "Verbose: $VERBOSE"
    echo "Skip Docker: $SKIP_DOCKER"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Test results tracking
    declare -A test_results
    total_tests=0
    passed_tests=0
    
    # Test 1: Dependency Verification
    total_tests=$((total_tests + 1))
    verbose_flag=""
    if $VERBOSE; then
        verbose_flag="--verbose"
    fi
    
    if run_test "dependency_verification" "python3 scripts/dependency_verifier.py $verbose_flag --output $OUTPUT_DIR/dependency_report_${TIMESTAMP}.txt"; then
        test_results["dependency_verification"]="PASS"
        passed_tests=$((passed_tests + 1))
    else
        test_results["dependency_verification"]="FAIL"
    fi
    
    # Test 2: Comprehensive Build Tests
    total_tests=$((total_tests + 1))
    docker_flag=""
    if $SKIP_DOCKER; then
        docker_flag="--skip-docker"
    fi
    
    if run_test "comprehensive_build" "python3 scripts/comprehensive_build_test_plan.py $verbose_flag $docker_flag --output $OUTPUT_DIR/build_report_${TIMESTAMP}.txt"; then
        test_results["comprehensive_build"]="PASS"
        passed_tests=$((passed_tests + 1))
    else
        test_results["comprehensive_build"]="FAIL"
    fi
    
    # Test 3: Cloud Run Emulation (if Docker available)
    if [[ "$SKIP_DOCKER" == "false" ]]; then
        total_tests=$((total_tests + 1))
        if run_test "cloud_run_emulation" "python3 scripts/cloud_run_emulator.py $verbose_flag --service all"; then
            test_results["cloud_run_emulation"]="PASS"
            passed_tests=$((passed_tests + 1))
        else
            test_results["cloud_run_emulation"]="FAIL"
        fi
    fi
    
    # Test 4: Integration Tests
    total_tests=$((total_tests + 1))
    if run_test "integration_tests" "python3 -m pytest tests/integration/ -v --tb=short"; then
        test_results["integration_tests"]="PASS"
        passed_tests=$((passed_tests + 1))
    else
        test_results["integration_tests"]="FAIL"
    fi
    
    # Test 5: E2E Tests
    total_tests=$((total_tests + 1))
    if run_test "e2e_tests" "python3 -m pytest tests/e2e/ -v --tb=short"; then
        test_results["e2e_tests"]="PASS"
        passed_tests=$((passed_tests + 1))
    else
        test_results["e2e_tests"]="FAIL"
    fi
    
    # Generate final summary report
    summary_file="$OUTPUT_DIR/summary_report_${TIMESTAMP}.txt"
    
    cat > "$summary_file" << EOF
🏗️ COMPREHENSIVE BUILD TEST BATTERY SUMMARY
==========================================

Execution Time: $(date)
Total Tests: $total_tests
Passed: $passed_tests
Failed: $((total_tests - passed_tests))
Success Rate: $(( passed_tests * 100 / total_tests ))%

DETAILED RESULTS:
$(printf "%-25s | %s\n" "Test Name" "Status")
$(printf "%-25s-|-%s\n" "-------------------------" "------")
EOF
    
    for test_name in "${!test_results[@]}"; do
        status="${test_results[$test_name]}"
        if [[ "$status" == "PASS" ]]; then
            printf "%-25s | ✅ %s\n" "$test_name" "$status" >> "$summary_file"
        else
            printf "%-25s | ❌ %s\n" "$test_name" "$status" >> "$summary_file"
        fi
    done
    
    echo "" >> "$summary_file"
    
    if [[ $passed_tests -eq $total_tests ]]; then
        echo "🎉 BUILD READY: All tests passed!" >> "$summary_file"
        echo "✅ The codebase is ready for Cloud Run deployment." >> "$summary_file"
    else
        echo "🚨 BUILD NOT READY: $((total_tests - passed_tests)) test(s) failed" >> "$summary_file"
        echo "⚠️ The Cloud Run deployment may fail." >> "$summary_file"
    fi
    
    # Display summary
    echo ""
    echo "📊 FINAL SUMMARY:"
    echo "=================="
    cat "$summary_file"
    
    echo ""
    echo "📁 All test results saved to: $OUTPUT_DIR"
    echo "📄 Summary report: $summary_file"
    
    # Exit with appropriate code
    if [[ $passed_tests -eq $total_tests ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
