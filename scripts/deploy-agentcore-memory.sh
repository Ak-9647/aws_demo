#!/bin/bash

# Deploy AgentCore Memory Resources using CloudFormation
# Since AgentCore Memory is in preview, we use CloudFormation instead of Terraform

set -e

# Configuration
STACK_NAME="production-analytics-agent-agentcore-memory"
TEMPLATE_FILE="infrastructure/agentcore-memory.yaml"
REGION="us-west-2"
PROJECT_NAME="production-analytics-agent"
ENVIRONMENT="production"
AGENT_ID="hosted_agent_jqgjl-fJiyIV95k9"

echo "🚀 Deploying AgentCore Memory Resources"
echo "========================================"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Project: $PROJECT_NAME"
echo "Agent ID: $AGENT_ID"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI is not configured or credentials are invalid"
    echo "Please run 'aws configure' to set up your credentials"
    exit 1
fi

echo "✅ AWS CLI configured"

# Check if the template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ CloudFormation template not found: $TEMPLATE_FILE"
    exit 1
fi

echo "✅ CloudFormation template found"

# Validate the CloudFormation template
echo "🔍 Validating CloudFormation template..."
if aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $REGION > /dev/null; then
    echo "✅ CloudFormation template is valid"
else
    echo "❌ CloudFormation template validation failed"
    exit 1
fi

# Check if stack already exists
if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION > /dev/null 2>&1; then
    echo "📝 Stack exists, updating..."
    OPERATION="update-stack"
    WAIT_CONDITION="stack-update-complete"
else
    echo "🆕 Stack doesn't exist, creating..."
    OPERATION="create-stack"
    WAIT_CONDITION="stack-create-complete"
fi

# Deploy the stack
echo "🚀 Deploying stack..."
aws cloudformation $OPERATION \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --parameters \
        ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
        ParameterKey=AgentId,ParameterValue=$AGENT_ID \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Stack deployment initiated successfully"
else
    echo "❌ Stack deployment failed"
    exit 1
fi

# Wait for stack deployment to complete
echo "⏳ Waiting for stack deployment to complete..."
aws cloudformation wait $WAIT_CONDITION --stack-name $STACK_NAME --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Stack deployment completed successfully"
else
    echo "❌ Stack deployment failed or timed out"
    echo "Check the CloudFormation console for details:"
    echo "https://console.aws.amazon.com/cloudformation/home?region=$REGION#/stacks"
    exit 1
fi

# Get stack outputs
echo ""
echo "📊 Stack Outputs:"
echo "=================="
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

# Test the memory resources
echo ""
echo "🧪 Testing AgentCore Memory Resources..."
echo "========================================"

# Get the memory management function ARN
FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`MemoryManagementFunctionArn`].OutputValue' \
    --output text)

if [ -n "$FUNCTION_ARN" ]; then
    echo "🔍 Testing memory management function..."
    
    # Test health check
    aws lambda invoke \
        --function-name $FUNCTION_ARN \
        --payload '{"operation": "health_check"}' \
        --region $REGION \
        /tmp/memory-test-response.json > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Memory management function is working"
        echo "Response:"
        cat /tmp/memory-test-response.json | jq .
        rm -f /tmp/memory-test-response.json
    else
        echo "❌ Memory management function test failed"
    fi
else
    echo "⚠️  Could not find memory management function ARN"
fi

echo ""
echo "🎉 AgentCore Memory deployment completed!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo "1. Update your agent code to use the new AgentCore Memory resources"
echo "2. Test the memory functionality in your application"
echo "3. Monitor the CloudWatch logs for any issues"
echo ""
echo "🔗 Useful Links:"
echo "• CloudFormation Console: https://console.aws.amazon.com/cloudformation/home?region=$REGION#/stacks"
echo "• AgentCore Console: https://console.aws.amazon.com/bedrock/home?region=$REGION#/agents"
echo "• Lambda Console: https://console.aws.amazon.com/lambda/home?region=$REGION#/functions"
echo ""
echo "✅ Deployment completed successfully!"