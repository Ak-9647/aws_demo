#!/bin/bash
# AgentCore Gateway Deployment Script
# Production Analytics Agent v4.1

set -e

echo "🚀 Deploying AgentCore Gateway..."

# Configuration
GATEWAY_NAME="production-analytics-gateway"
REGION="${AWS_REGION:-us-west-2}"
ROLE_NAME="ProductionAnalyticsGatewayRole"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    # Check if running in correct directory
    if [[ ! -f "infrastructure/agentcore-gateway.yaml" ]]; then
        print_error "Gateway configuration file not found. Please run from project root."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create secrets in AWS Secrets Manager
create_secrets() {
    print_status "Creating secrets in AWS Secrets Manager..."
    
    # PostgreSQL connection secret
    if ! aws secretsmanager describe-secret --secret-id "production-analytics-postgres-connection" --region $REGION &> /dev/null; then
        print_status "Creating PostgreSQL connection secret..."
        aws secretsmanager create-secret \
            --name "production-analytics-postgres-connection" \
            --description "PostgreSQL connection string for analytics database" \
            --secret-string '{
                "host": "analytics-db.cluster-xyz.'$REGION'.rds.amazonaws.com",
                "port": "5432",
                "database": "analytics",
                "username": "analytics_user",
                "password": "CHANGE_ME_IN_CONSOLE"
            }' \
            --region $REGION > /dev/null
        print_success "PostgreSQL secret created"
    else
        print_warning "PostgreSQL secret already exists"
    fi
    
    # Redshift connection secret
    if ! aws secretsmanager describe-secret --secret-id "production-analytics-redshift-connection" --region $REGION &> /dev/null; then
        print_status "Creating Redshift connection secret..."
        aws secretsmanager create-secret \
            --name "production-analytics-redshift-connection" \
            --description "Redshift connection string for data warehouse" \
            --secret-string '{
                "host": "analytics-warehouse.xyz.'$REGION'.redshift.amazonaws.com",
                "port": "5439",
                "database": "warehouse",
                "username": "warehouse_user",
                "password": "CHANGE_ME_IN_CONSOLE"
            }' \
            --region $REGION > /dev/null
        print_success "Redshift secret created"
    else
        print_warning "Redshift secret already exists"
    fi
    
    # Market API key secret
    if ! aws secretsmanager describe-secret --secret-id "production-analytics-market-api-key" --region $REGION &> /dev/null; then
        print_status "Creating Market API key secret..."
        aws secretsmanager create-secret \
            --name "production-analytics-market-api-key" \
            --description "Market data API key" \
            --secret-string '{"api_key": "CHANGE_ME_IN_CONSOLE"}' \
            --region $REGION > /dev/null
        print_success "Market API key secret created"
    else
        print_warning "Market API key secret already exists"
    fi
    
    # Weather API token secret
    if ! aws secretsmanager describe-secret --secret-id "production-analytics-weather-token" --region $REGION &> /dev/null; then
        print_status "Creating Weather API token secret..."
        aws secretsmanager create-secret \
            --name "production-analytics-weather-token" \
            --description "Weather API bearer token" \
            --secret-string '{"token": "CHANGE_ME_IN_CONSOLE"}' \
            --region $REGION > /dev/null
        print_success "Weather API token secret created"
    else
        print_warning "Weather API token secret already exists"
    fi
}

# Create IAM role and policies
create_iam_role() {
    print_status "Creating IAM role and policies..."
    
    # Create trust policy
    cat > /tmp/gateway-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
    
    # Create or update the gateway service role
    if ! aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
        print_status "Creating gateway service role..."
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file:///tmp/gateway-trust-policy.json \
            --description "Service role for AgentCore Gateway" > /dev/null
        print_success "Gateway service role created"
    else
        print_warning "Gateway service role already exists"
    fi
    
    # Create permissions policy
    cat > /tmp/gateway-permissions-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:$REGION:$ACCOUNT_ID:secret:production-analytics-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::production-analytics-data-lake",
        "arn:aws:s3:::production-analytics-data-lake/*",
        "arn:aws:s3:::production-analytics-results",
        "arn:aws:s3:::production-analytics-results/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:$REGION:$ACCOUNT_ID:log-group:/aws/agentcore/gateway*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "AgentCore/Gateway"
        }
      }
    }
  ]
}
EOF
    
    # Attach the policy to the role
    print_status "Attaching permissions policy..."
    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name GatewayPermissions \
        --policy-document file:///tmp/gateway-permissions-policy.json
    print_success "Permissions policy attached"
    
    # Clean up temporary files
    rm -f /tmp/gateway-trust-policy.json /tmp/gateway-permissions-policy.json
}

# Deploy gateway configuration
deploy_gateway() {
    print_status "Deploying gateway configuration..."
    
    # Update the gateway configuration with actual account ID and region
    sed -e "s/ACCOUNT/$ACCOUNT_ID/g" -e "s/us-west-2/$REGION/g" \
        infrastructure/agentcore-gateway.yaml > /tmp/agentcore-gateway-updated.yaml
    
    # Check if gateway already exists
    if aws bedrock-agent describe-gateway --gateway-name $GATEWAY_NAME --region $REGION &> /dev/null; then
        print_warning "Gateway already exists. Updating configuration..."
        
        # Note: Update gateway command may not exist in current AWS CLI
        # This is a placeholder for when the service becomes available
        print_status "Gateway update functionality not yet available in AWS CLI"
        print_status "Please update gateway configuration manually in AWS Console"
    else
        print_status "Creating new gateway..."
        
        # Note: Create gateway command may not exist in current AWS CLI
        # This is a placeholder for when the service becomes available
        print_status "Gateway creation functionality not yet available in AWS CLI"
        print_status "Please create gateway configuration manually in AWS Console"
        print_status "Use configuration file: /tmp/agentcore-gateway-updated.yaml"
    fi
}

# Test gateway connectivity
test_gateway() {
    print_status "Testing gateway integration..."
    
    # Run Python test script
    if [[ -f "scripts/test-gateway.py" ]]; then
        python3 scripts/test-gateway.py
    else
        print_warning "Gateway test script not found"
    fi
}

# Main deployment flow
main() {
    echo "🔧 AgentCore Gateway Deployment"
    echo "================================"
    echo "Gateway Name: $GATEWAY_NAME"
    echo "Region: $REGION"
    echo "Account: $ACCOUNT_ID"
    echo ""
    
    check_prerequisites
    create_secrets
    create_iam_role
    deploy_gateway
    test_gateway
    
    echo ""
    print_success "AgentCore Gateway deployment completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update secret values in AWS Secrets Manager console"
    echo "2. Create gateway configuration in AWS Bedrock console (when available)"
    echo "3. Test gateway connectivity with: python3 scripts/test-gateway.py"
    echo "4. Monitor gateway performance in CloudWatch"
    echo ""
    echo "🔗 Useful Links:"
    echo "- Secrets Manager: https://console.aws.amazon.com/secretsmanager/"
    echo "- IAM Roles: https://console.aws.amazon.com/iam/home#/roles"
    echo "- CloudWatch: https://console.aws.amazon.com/cloudwatch/"
}

# Run main function
main "$@"