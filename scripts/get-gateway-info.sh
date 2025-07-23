#!/bin/bash

# Script to get gateway configuration information for AWS Console setup

echo "🚀 AgentCore Gateway Configuration Information"
echo "=============================================="

# Get AWS account and region info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo ""
echo "📋 Basic Information:"
echo "   AWS Account ID: $AWS_ACCOUNT_ID"
echo "   AWS Region: $AWS_REGION"

echo ""
echo "🔧 Gateway Configuration (from Terraform outputs):"

# Check if Terraform has been applied
if [ -f "infrastructure/terraform.tfstate" ]; then
    echo "   ✅ Infrastructure deployed"
    
    # Get all relevant outputs
    echo ""
    echo "📦 Required Resources:"
    
    LAMBDA_ARN=$(cd infrastructure && terraform output -raw analytics_gateway_lambda_arn 2>/dev/null)
    if [ ! -z "$LAMBDA_ARN" ]; then
        echo "   Lambda ARN: $LAMBDA_ARN"
    fi
    
    S3_BUCKET=$(cd infrastructure && terraform output -raw analytics_data_bucket 2>/dev/null)
    if [ ! -z "$S3_BUCKET" ]; then
        echo "   S3 Bucket: $S3_BUCKET"
    fi
    
    API_SECRET_ARN=$(cd infrastructure && terraform output -raw analytics_api_secret_arn 2>/dev/null)
    if [ ! -z "$API_SECRET_ARN" ]; then
        echo "   API Secret ARN: $API_SECRET_ARN"
    fi
    
    DB_SECRET_ARN=$(cd infrastructure && terraform output -raw database_connection_secret_arn 2>/dev/null)
    if [ ! -z "$DB_SECRET_ARN" ]; then
        echo "   DB Secret ARN: $DB_SECRET_ARN"
    fi
    
    RDS_ENDPOINT=$(cd infrastructure && terraform output -raw rds_cluster_endpoint 2>/dev/null)
    if [ ! -z "$RDS_ENDPOINT" ]; then
        echo "   RDS Endpoint: $RDS_ENDPOINT"
    fi
    
    USER_POOL_ID=$(cd infrastructure && terraform output -raw cognito_user_pool_id 2>/dev/null)
    CLIENT_ID=$(cd infrastructure && terraform output -raw cognito_client_id 2>/dev/null)
    if [ ! -z "$USER_POOL_ID" ]; then
        echo "   Cognito User Pool: $USER_POOL_ID"
        echo "   Cognito Client ID: $CLIENT_ID"
    fi
    
else
    echo "   ⚠️  Infrastructure not yet deployed"
    echo "   Run 'cd infrastructure && terraform apply' first"
    exit 1
fi

echo ""
echo "📄 Schema Files Available:"
echo "   ✅ Analytics API Schema: schemas/analytics-api-schema.json"
echo "   ✅ Database Gateway Schema: schemas/database-gateway-schema.json"

echo ""
echo "🌐 Gateway Creation Steps:"
echo ""
echo "🔗 1. Analytics REST API Gateway:"
echo "   Gateway Name: production-analytics-agent-analytics-gateway"
echo "   Target Name: analytics-api-target"
echo "   Target Type: REST API"
echo "   Base URL: https://api.example.com/analytics (replace with actual)"
echo "   Schema: Upload schemas/analytics-api-schema.json"
echo "   Outbound Auth: API Key"
echo "   API Key Secret: $API_SECRET_ARN"
echo "   Header Name: X-API-Key"
echo "   Inbound Auth: Cognito Quick Setup"
echo ""
echo "🗄️  2. Database Gateway:"
echo "   Gateway Name: production-analytics-agent-database-gateway"
echo "   Target Name: database-target"
echo "   Target Type: Lambda ARN"
echo "   Lambda ARN: $LAMBDA_ARN"
echo "   Schema: Upload schemas/database-gateway-schema.json"
echo "   Outbound Auth: IAM Role"
echo "   Inbound Auth: None (internal use)"
echo ""
echo "🪣 3. S3 Data Gateway:"
echo "   Gateway Name: production-analytics-agent-s3-gateway"
echo "   Target Name: s3-data-target"
echo "   Target Type: S3"
echo "   Bucket Name: $S3_BUCKET"
echo "   Prefix: analytics/ (optional)"
echo "   Outbound Auth: IAM Role"
echo "   Inbound Auth: None (internal use)"

echo ""
echo "🔐 Authentication Details:"
echo ""
echo "For Cognito Quick Setup:"
echo "   - Will create new user pool automatically"
echo "   - Scopes: openid, profile, email"
echo ""
echo "To use existing Cognito:"
echo "   - User Pool ID: $USER_POOL_ID"
echo "   - Client ID: $CLIENT_ID"
echo "   - Domain: production-analytics-agent-auth-839dae02"

echo ""
echo "🧪 Testing Commands:"
echo ""
echo "# Test Lambda function:"
echo "aws lambda invoke --function-name production-analytics-agent-analytics-gateway-target \\"
echo "  --payload '{\"httpMethod\":\"POST\",\"path\":\"/query\",\"body\":\"{\\\"sql\\\":\\\"SELECT 1\\\"}\"}' \\"
echo "  response.json && cat response.json"
echo ""
echo "# Test S3 bucket access:"
echo "aws s3 ls s3://$S3_BUCKET/"
echo ""
echo "# Test database connection:"
echo "psql -h $RDS_ENDPOINT -U analytics_admin -d analytics -c 'SELECT version();'"
echo ""
echo "# Test MCP integration:"
echo "python test_mcp_simple.py"

echo ""
echo "✅ Verification Steps:"
echo ""
echo "After creating gateways in AWS Console:"
echo "1. Check all 3 gateways show 'Active' status"
echo "2. Test each gateway using the Test feature"
echo "3. Check CloudWatch logs for any errors"
echo "4. Update agent configuration with gateway ARNs"
echo "5. Deploy agent containers and test end-to-end"

echo ""
echo "🚨 Important Notes:"
echo ""
echo "⚠️  AgentCore Gateways MUST be created manually in AWS Console"
echo "⚠️  Terraform cannot create AgentCore Gateways yet"
echo "⚠️  All supporting infrastructure (Lambda, S3, RDS) is already deployed"
echo "⚠️  Schema files are ready for upload during gateway creation"

echo ""
echo "📚 Documentation:"
echo "   - Detailed Gateway Setup: docs/CREATE_AGENTCORE_GATEWAYS.md"
echo "   - Deployment Guide: docs/DEPLOYMENT_GUIDE.md"
echo "   - MCP Integration: docs/MCP_INTEGRATION_GUIDE.md"
echo "   - Technical Architecture: docs/TECHNICAL_GUIDE.md"

echo ""
echo "🔗 AWS Console Links:"
echo "   AgentCore Gateways: https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/gateways"
echo "   Lambda Functions: https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions"
echo "   S3 Buckets: https://s3.console.aws.amazon.com/s3/buckets?region=us-west-2"
echo "   RDS Clusters: https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#databases:"