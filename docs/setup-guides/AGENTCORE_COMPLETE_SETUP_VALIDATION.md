# AgentCore Complete Setup Validation Guide

## Overview

This document provides comprehensive, step-by-step validation instructions for setting up all three AgentCore components: Memory, Identity, and Gateway. Each section includes exact values, specific commands, and validation steps.

## 🎯 Prerequisites Checklist

Before starting, ensure you have:

- [ ] AWS Console access with Bedrock permissions
- [ ] AWS CLI configured with appropriate credentials
- [ ] Agent ID: `hosted_agent_jqgjl-fJiyIV95k9`
- [ ] Region: `us-west-2`
- [ ] Account ID: `280383026847` (replace with your actual account)

## 📋 Part 1: AgentCore Memory Setup

### Step 1.1: Navigate to Memory Console

1. **URL**: https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/memory
2. **Action**: Click the orange "Create memory" button

### Step 1.2: Create Conversation Memory

**Configuration Values**:
```
Memory name: production-analytics-agent-conversation-memory
Short-term memory expiration: 7 days
Long-term strategy: ✅ Built-in strategies → Summarization
Strategy name: conversation_summarization_v1
Namespace: /strategies/memory/conversation/sessions/{sessionId}
```

**Steps**:
1. Enter memory name: `production-analytics-agent-conversation-memory`
2. Set expiration: `7` days
3. Check "Built-in strategies"
4. Select "Summarization" checkbox
5. Click "Create memory"
6. **Record Memory ID**: `CONV_MEMORY_ID_HERE`

### Step 1.3: Create User Preferences Memory

**Configuration Values**:
```
Memory name: production-analytics-agent-user-preferences
Short-term memory expiration: 30 days
Long-term strategy: ✅ Built-in strategies → Semantic memory
Strategy name: user_preferences_semantic_v1
Namespace: /strategies/memory/users/{userId}/preferences
```

**Steps**:
1. Click "Create memory" again
2. Enter memory name: `production-analytics-agent-user-preferences`
3. Set expiration: `30` days
4. Check "Built-in strategies"
5. Select "Semantic memory"
6. Click "Create memory"
7. **Record Memory ID**: `USER_PREF_MEMORY_ID_HERE`

### Step 1.4: Create Session Context Memory

**Configuration Values**:
```
Memory name: production-analytics-agent-session-context
Short-term memory expiration: 1 days
Long-term strategy: None (unchecked)
```

**Steps**:
1. Click "Create memory" again
2. Enter memory name: `production-analytics-agent-session-context`
3. Set expiration: `1` days
4. Leave long-term strategies unchecked
5. Click "Create memory"
6. **Record Memory ID**: `SESSION_MEMORY_ID_HERE`

### Step 1.5: Create Analytics Context Memory

**Configuration Values**:
```
Memory name: production-analytics-agent-analytics-context
Short-term memory expiration: 14 days
Long-term strategy: ✅ Built-in strategies → Summarization
Strategy name: analytics_summarization_v1
Namespace: /strategies/memory/analytics/{userId}/patterns
```

**Steps**:
1. Click "Create memory" again
2. Enter memory name: `production-analytics-agent-analytics-context`
3. Set expiration: `14` days
4. Check "Built-in strategies"
5. Select "Summarization"
6. Click "Create memory"
7. **Record Memory ID**: `ANALYTICS_MEMORY_ID_HERE`

### Step 1.6: Update Environment Variables

Add these to your ECS task definition or environment:

```bash
# AgentCore Memory Configuration
export CONVERSATION_MEMORY_ID="CONV_MEMORY_ID_HERE"
export USER_PREFERENCES_MEMORY_ID="USER_PREF_MEMORY_ID_HERE"
export SESSION_CONTEXT_MEMORY_ID="SESSION_MEMORY_ID_HERE"
export ANALYTICS_CONTEXT_MEMORY_ID="ANALYTICS_MEMORY_ID_HERE"
export AGENTCORE_MEMORY_ENABLED=true
```

### Step 1.7: Validation Commands

```bash
# Test memory access
aws bedrock-agent get-memory --memory-id CONV_MEMORY_ID_HERE --region us-west-2
aws bedrock-agent get-memory --memory-id USER_PREF_MEMORY_ID_HERE --region us-west-2
aws bedrock-agent get-memory --memory-id SESSION_MEMORY_ID_HERE --region us-west-2
aws bedrock-agent get-memory --memory-id ANALYTICS_MEMORY_ID_HERE --region us-west-2

# List all memories
aws bedrock-agent list-memories --region us-west-2
```

## 📋 Part 2: AgentCore Identity Setup

### Step 2.1: Navigate to Identity Console

1. **URL**: https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/identity
2. **View**: Identity overview with Inbound and Outbound sections

### Step 2.2: Configure Outbound Identity (OAuth Client)

**Configuration Values**:
```
Name: production-analytics-agent-oauth-client
Provider: GitHub (or your preferred provider)
Client ID: your-github-client-id
Client Secret: your-github-client-secret
```

**Steps**:
1. In Outbound Identity section, click "Add OAuth client / API key"
2. Select "Add OAuth Client"
3. Enter name: `production-analytics-agent-oauth-client`
4. Select provider: GitHub
5. Enter your OAuth credentials
6. Click "Add OAuth Client"
7. **Record Client ID**: `OAUTH_CLIENT_ID_HERE`

### Step 2.3: Configure API Keys

**Configuration Values**:
```
Name: production-analytics-agent-api-key
API Key: your-external-api-key-value
Description: External API access for analytics agent
```

**Steps**:
1. Click "Add OAuth client / API key" again
2. Select "Add API key"
3. Enter name: `production-analytics-agent-api-key`
4. Enter your API key value
5. Click "Add"
6. **Record API Key ID**: `API_KEY_ID_HERE`

### Step 2.4: Update Environment Variables

```bash
# AgentCore Identity Configuration
export GITHUB_OAUTH_CLIENT_ID="OAUTH_CLIENT_ID_HERE"
export EXTERNAL_API_KEY="API_KEY_ID_HERE"
export AGENTCORE_IDENTITY_ENABLED=true
export INBOUND_AUTH_REQUIRED=false
export OUTBOUND_AUTH_ENABLED=true
```

### Step 2.5: Update IAM Permissions

Add to your existing IAM role policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:GetIdentity",
                "bedrock:CreateIdentity",
                "bedrock:UpdateIdentity",
                "bedrock:DeleteIdentity",
                "bedrock:ListIdentities"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:280383026847:identity/*"
            ]
        }
    ]
}
```

## 📋 Part 3: AgentCore Gateway Setup

### Step 3.1: Create Secrets in AWS Secrets Manager

**Execute these commands with your actual values**:

```bash
# PostgreSQL connection secret
aws secretsmanager create-secret \
  --name "production-analytics-postgres-connection" \
  --description "PostgreSQL connection string for analytics database" \
  --secret-string '{
    "host": "production-analytics-agent-analytics-cluster.cluster-cxayeoogcra9.us-west-2.rds.amazonaws.com",
    "port": "5432",
    "database": "analytics",
    "username": "analytics_user",
    "password": "REPLACE_WITH_ACTUAL_PASSWORD"
  }' \
  --region us-west-2

# Redshift connection secret
aws secretsmanager create-secret \
  --name "production-analytics-redshift-connection" \
  --description "Redshift connection string for data warehouse" \
  --secret-string '{
    "host": "analytics-warehouse.xyz.us-west-2.redshift.amazonaws.com",
    "port": "5439",
    "database": "warehouse",
    "username": "warehouse_user",
    "password": "REPLACE_WITH_ACTUAL_PASSWORD"
  }' \
  --region us-west-2

# Market API key secret
aws secretsmanager create-secret \
  --name "production-analytics-market-api-key" \
  --description "Market data API key" \
  --secret-string '{"api_key": "REPLACE_WITH_ACTUAL_API_KEY"}' \
  --region us-west-2

# Weather API token secret
aws secretsmanager create-secret \
  --name "production-analytics-weather-token" \
  --description "Weather API bearer token" \
  --secret-string '{"token": "REPLACE_WITH_ACTUAL_TOKEN"}' \
  --region us-west-2
```

### Step 3.2: Create IAM Role for Gateway

```bash
# Create trust policy file
cat > /tmp/gateway-trust-policy.json << 'EOF'
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

# Create the gateway service role
aws iam create-role \
  --role-name ProductionAnalyticsGatewayRole \
  --assume-role-policy-document file:///tmp/gateway-trust-policy.json \
  --description "Service role for AgentCore Gateway"

# Create permissions policy file
cat > /tmp/gateway-permissions-policy.json << 'EOF'
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
        "arn:aws:secretsmanager:us-west-2:280383026847:secret:production-analytics-*"
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
      "Resource": "arn:aws:logs:us-west-2:280383026847:log-group:/aws/agentcore/gateway*"
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
aws iam put-role-policy \
  --role-name ProductionAnalyticsGatewayRole \
  --policy-name GatewayPermissions \
  --policy-document file:///tmp/gateway-permissions-policy.json
```

### Step 3.3: Update Gateway Configuration File

Update `infrastructure/agentcore-gateway.yaml` with your account ID:

```bash
# Replace ACCOUNT placeholder with actual account ID
sed -i 's/ACCOUNT/280383026847/g' infrastructure/agentcore-gateway.yaml
```

### Step 3.4: Deploy Gateway (When Service Available)

```bash
# Note: These commands are placeholders for when AgentCore Gateway becomes available
# Currently, manual setup through AWS Console is required

# Future deployment command:
aws bedrock-agent create-gateway \
  --gateway-name production-analytics-gateway \
  --configuration file://infrastructure/agentcore-gateway.yaml \
  --service-role-arn arn:aws:iam::280383026847:role/ProductionAnalyticsGatewayRole \
  --region us-west-2
```

### Step 3.5: Run Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy-agentcore-gateway.sh

# Run deployment script
./scripts/deploy-agentcore-gateway.sh
```

## 🧪 Validation and Testing

### Test Memory Integration

```bash
# Run memory integration test
python3 -c "
from agent.agentcore_memory_integration import get_agentcore_memory
memory = get_agentcore_memory()
health = memory.health_check()
print(f'Memory Health: {health}')
"
```

### Test Identity Integration

```bash
# Run identity integration test
python3 scripts/test_identity_integration.py
```

### Test Gateway Integration

```bash
# Run gateway integration test
python3 scripts/test-gateway.py
```

## 📊 Complete Environment Configuration

### Final Environment Variables

Add all these to your ECS task definition or Lambda environment:

```bash
# AgentCore Memory
export CONVERSATION_MEMORY_ID="CONV_MEMORY_ID_HERE"
export USER_PREFERENCES_MEMORY_ID="USER_PREF_MEMORY_ID_HERE"
export SESSION_CONTEXT_MEMORY_ID="SESSION_MEMORY_ID_HERE"
export ANALYTICS_CONTEXT_MEMORY_ID="ANALYTICS_MEMORY_ID_HERE"
export AGENTCORE_MEMORY_ENABLED=true

# AgentCore Identity
export GITHUB_OAUTH_CLIENT_ID="OAUTH_CLIENT_ID_HERE"
export EXTERNAL_API_KEY="API_KEY_ID_HERE"
export AGENTCORE_IDENTITY_ENABLED=true
export INBOUND_AUTH_REQUIRED=false
export OUTBOUND_AUTH_ENABLED=true

# AgentCore Gateway
export AGENTCORE_GATEWAY_NAME="production-analytics-gateway"
export AGENTCORE_GATEWAY_ENABLED=true

# Core Configuration
export AWS_REGION=us-west-2
export AGENTCORE_AGENT_ID=hosted_agent_jqgjl-fJiyIV95k9
export ACCOUNT_ID=280383026847
```

### Complete IAM Policy

Combine all permissions into your agent's IAM role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:GetMemory",
                "bedrock:PutMemory",
                "bedrock:DeleteMemory",
                "bedrock:ListMemories",
                "bedrock:UpdateMemory"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:280383026847:memory/production-analytics-agent-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:GetIdentity",
                "bedrock:CreateIdentity",
                "bedrock:UpdateIdentity",
                "bedrock:DeleteIdentity",
                "bedrock:ListIdentities"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:280383026847:identity/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:GetGateway",
                "bedrock:InvokeGateway",
                "bedrock:ListGateways"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:280383026847:gateway/production-analytics-gateway"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": [
                "arn:aws:secretsmanager:us-west-2:280383026847:secret:production-analytics-*"
            ]
        }
    ]
}
```

## ✅ Validation Checklist

### Memory Setup Validation
- [ ] 4 memory resources created in AgentCore console
- [ ] Memory IDs recorded and added to environment variables
- [ ] IAM permissions updated for memory access
- [ ] Memory integration test passes

### Identity Setup Validation
- [ ] OAuth client configured in AgentCore console
- [ ] API keys added to identity configuration
- [ ] Environment variables updated with identity settings
- [ ] IAM permissions updated for identity access

### Gateway Setup Validation
- [ ] Secrets created in AWS Secrets Manager
- [ ] IAM role created for gateway service
- [ ] Gateway configuration file updated with account ID
- [ ] Gateway integration test passes (fallback mode)

### Integration Validation
- [ ] All environment variables configured
- [ ] IAM policies updated with all required permissions
- [ ] Agent code updated to use AgentCore components
- [ ] End-to-end testing completed

## 🚨 Important Notes

### Service Availability
- **Memory**: ✅ Available in preview
- **Identity**: ✅ Available in preview
- **Gateway**: ⏳ Coming soon (fallback mode implemented)

### Security Considerations
- Replace all placeholder values with actual credentials
- Use AWS Secrets Manager for sensitive information
- Follow least-privilege IAM principles
- Enable CloudWatch logging for all components

### Cost Optimization
- Monitor usage through CloudWatch metrics
- Set up billing alerts for AgentCore services
- Review memory retention policies regularly
- Optimize gateway connection pooling

## 🎯 Success Criteria

After completing this setup, you should have:

1. **Functional Memory System**: Conversation history and user preferences stored
2. **Secure Identity Management**: OAuth and API key authentication configured
3. **Gateway Integration**: Secure connections to external resources (with fallback)
4. **Comprehensive Monitoring**: CloudWatch metrics and logging enabled
5. **Production Readiness**: All security and performance optimizations in place

## 📞 Support and Troubleshooting

### Common Issues
1. **Permission Denied**: Check IAM policies and resource ARNs
2. **Service Not Available**: Verify region and service availability
3. **Configuration Errors**: Validate JSON syntax and required fields
4. **Network Issues**: Check VPC and security group configurations

### Getting Help
- AWS Support for service-specific issues
- Bedrock documentation for API references
- CloudWatch logs for debugging information
- This documentation for setup guidance

---

**Status**: ✅ **COMPLETE VALIDATION GUIDE**  
**Last Updated**: 2025-07-22  
**Version**: v4.1  
**Components**: Memory ✅ | Identity ✅ | Gateway ✅