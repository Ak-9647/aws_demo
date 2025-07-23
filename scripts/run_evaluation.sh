#!/bin/bash

# Production Analytics Agent v4.1 - Evaluation Runner
# Comprehensive testing and evaluation script

set -e

echo "🚀 Production Analytics Agent v4.1 - Evaluation Suite"
echo "============================================================"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EVALUATION_SCRIPT="$SCRIPT_DIR/evaluation_suite.py"
REPORT_DIR="$PROJECT_ROOT/evaluation_reports"

# Create reports directory
mkdir -p "$REPORT_DIR"

# Check dependencies
echo "🔧 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is required but not installed"
    exit 1
fi

# Check required Python packages
python3 -c "import boto3, requests" 2>/dev/null || {
    echo "❌ Required Python packages missing. Installing..."
    python3 -m pip install boto3 requests --break-system-packages || {
        echo "❌ Failed to install required packages"
        exit 1
    }
}

echo "✅ Dependencies check passed"

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
aws sts get-caller-identity > /dev/null || {
    echo "❌ AWS credentials not configured"
    echo "Please run: aws configure"
    exit 1
}
echo "✅ AWS credentials configured"

# Check infrastructure status
echo "🏗️ Checking infrastructure status..."

# Check if GUI is accessible
GUI_URL="http://analytics-gui-alb-1184070249.us-west-2.elb.amazonaws.com"
if curl -s --head "$GUI_URL" | head -n 1 | grep -q "200 OK"; then
    echo "✅ GUI is accessible"
else
    echo "⚠️ GUI may not be accessible at $GUI_URL"
fi

# Check Lambda function
LAMBDA_FUNCTION="production-analytics-agent-analytics-gateway-target"
if aws lambda get-function --function-name "$LAMBDA_FUNCTION" > /dev/null 2>&1; then
    echo "✅ Lambda function exists"
else
    echo "❌ Lambda function not found: $LAMBDA_FUNCTION"
    exit 1
fi

# Check RDS cluster
RDS_CLUSTER="production-analytics-agent-analytics-cluster"
if aws rds describe-db-clusters --db-cluster-identifier "$RDS_CLUSTER" > /dev/null 2>&1; then
    echo "✅ RDS cluster exists"
else
    echo "❌ RDS cluster not found: $RDS_CLUSTER"
    exit 1
fi

echo "✅ Infrastructure check passed"

# Run evaluation
echo ""
echo "📊 Running evaluation suite..."
echo "============================================================"

cd "$PROJECT_ROOT"

# Run the evaluation with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORT_DIR/evaluation_report_$TIMESTAMP.json"

python3 "$EVALUATION_SCRIPT" | tee "$REPORT_DIR/evaluation_log_$TIMESTAMP.txt"

# Move the generated report to reports directory
if [ -f "evaluation_report.json" ]; then
    mv "evaluation_report.json" "$REPORT_FILE"
    echo "📄 Report saved to: $REPORT_FILE"
fi

echo ""
echo "✅ Evaluation completed!"
echo "============================================================"

# Generate summary
if [ -f "$REPORT_FILE" ]; then
    echo "📋 Quick Summary:"
    python3 -c "
import json
with open('$REPORT_FILE', 'r') as f:
    report = json.load(f)
    summary = report['evaluation_summary']
    print(f\"  • Total Tests: {summary['total_tests']}\")
    print(f\"  • Success Rate: {summary['success_rate']}\")
    print(f\"  • Overall Status: {summary['overall_status']}\")
    print(f\"  • Duration: {summary['total_duration']:.1f}s\")
"
fi

echo ""
echo "🔗 Next Steps:"
echo "  1. Review the detailed report: $REPORT_FILE"
echo "  2. Address any failed tests"
echo "  3. Monitor system performance"
echo "  4. Schedule regular evaluations"

exit 0