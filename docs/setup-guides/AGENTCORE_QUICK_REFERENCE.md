# AgentCore Quick Reference Card

## 🔧 Essential Configuration Values

### Core Settings
```bash
AWS_REGION=us-west-2
ACCOUNT_ID=280383026847
AGENTCORE_AGENT_ID=hosted_agent_jqgjl-fJiyIV95k9
```

### Memory Resource Names
```bash
# Memory Names (for console creation)
production-analytics-agent-conversation-memory    # 7 days, Summarization
production-analytics-agent-user-preferences       # 30 days, Semantic
production-analytics-agent-session-context        # 1 day, None
production-analytics-agent-analytics-context      # 14 days, Summarization
```

### Identity Resource Names
```bash
# Identity Names (for console creation)
production-analytics-agent-oauth-client           # OAuth client
production-analytics-agent-api-key               # API key
```

### Gateway Resource Names
```bash
# Gateway Name
production-analytics-gateway

# Secrets Manager Names
production-analytics-postgres-connection
production-analytics-redshift-connection
production-analytics-market-api-key
production-analytics-weather-token

# IAM Role Name
ProductionAnalyticsGatewayRole
```

## 🌐 Console URLs

### AgentCore Services
```
Memory:   https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/memory
Identity: https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/identity
Gateway:  https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/gateway
```

### Supporting Services
```
Secrets Manager: https://us-west-2.console.aws.amazon.com/secretsmanager/
IAM Roles:       https://console.aws.amazon.com/iam/home#/roles
CloudWatch:      https://us-west-2.console.aws.amazon.com/cloudwatch/
```

## ⚡ Quick Commands

### Memory Validation
```bash
# List all memories
aws bedrock-agent list-memories --region us-west-2

# Get specific memory
aws bedrock-agent get-memory --memory-id MEMORY_ID --region us-west-2
```

### Secrets Management
```bash
# List secrets
aws secretsmanager list-secrets --region us-west-2 | grep production-analytics

# Get secret value
aws secretsmanager get-secret-value --secret-id SECRET_NAME --region us-west-2
```

### IAM Role Validation
```bash
# Check role exists
aws iam get-role --role-name ProductionAnalyticsGatewayRole

# List role policies
aws iam list-role-policies --role-name ProductionAnalyticsGatewayRole
```

## 🧪 Testing Commands

### Memory Test
```bash
python3 -c "
from agent.agentcore_memory_integration import get_agentcore_memory
memory = get_agentcore_memory()
print(f'Health: {memory.health_check()}')
"
```

### Gateway Test
```bash
python3 scripts/test-gateway.py
```

### Database Test
```bash
python3 agent/test_database_integration.py
```

## 📋 Environment Variables Template

```bash
# AgentCore Core
export AWS_REGION=us-west-2
export AGENTCORE_AGENT_ID=hosted_agent_jqgjl-fJiyIV95k9

# Memory Configuration
export CONVERSATION_MEMORY_ID="REPLACE_WITH_ACTUAL_ID"
export USER_PREFERENCES_MEMORY_ID="REPLACE_WITH_ACTUAL_ID"
export SESSION_CONTEXT_MEMORY_ID="REPLACE_WITH_ACTUAL_ID"
export ANALYTICS_CONTEXT_MEMORY_ID="REPLACE_WITH_ACTUAL_ID"
export AGENTCORE_MEMORY_ENABLED=true

# Identity Configuration
export GITHUB_OAUTH_CLIENT_ID="REPLACE_WITH_ACTUAL_ID"
export EXTERNAL_API_KEY="REPLACE_WITH_ACTUAL_KEY"
export AGENTCORE_IDENTITY_ENABLED=true
export INBOUND_AUTH_REQUIRED=false
export OUTBOUND_AUTH_ENABLED=true

# Gateway Configuration
export AGENTCORE_GATEWAY_NAME="production-analytics-gateway"
export AGENTCORE_GATEWAY_ENABLED=true

# Database Configuration
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:5432/db"
export REDSHIFT_CONNECTION_STRING="redshift://user:pass@host:5439/db"
```

## 🔐 IAM Policy Template

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
                "bedrock:UpdateMemory",
                "bedrock:GetIdentity",
                "bedrock:CreateIdentity",
                "bedrock:UpdateIdentity",
                "bedrock:DeleteIdentity",
                "bedrock:ListIdentities",
                "bedrock:GetGateway",
                "bedrock:InvokeGateway",
                "bedrock:ListGateways"
            ],
            "Resource": [
                "arn:aws:bedrock:us-west-2:280383026847:memory/production-analytics-agent-*",
                "arn:aws:bedrock:us-west-2:280383026847:identity/*",
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

## 🚀 Deployment Scripts

### Memory Deployment
```bash
# No automated deployment - manual console setup required
# Follow: docs/AGENTCORE_MEMORY_MANUAL_SETUP.md
```

### Identity Deployment
```bash
# No automated deployment - manual console setup required
# Follow: docs/AGENTCORE_IDENTITY_MANUAL_SETUP.md
```

### Gateway Deployment
```bash
chmod +x scripts/deploy-agentcore-gateway.sh
./scripts/deploy-agentcore-gateway.sh
```

## 📊 Monitoring Queries

### CloudWatch Metrics
```bash
# Memory usage
aws cloudwatch get-metric-statistics \
  --namespace "AWS/Bedrock" \
  --metric-name "MemoryUsage" \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average

# Gateway requests
aws cloudwatch get-metric-statistics \
  --namespace "AgentCore/Gateway" \
  --metric-name "RequestCount" \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

### Log Groups
```bash
# List AgentCore log groups
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/agentcore" \
  --region us-west-2

# View recent logs
aws logs tail /aws/agentcore/memory --follow --region us-west-2
```

## 🔍 Troubleshooting Quick Fixes

### Common Issues
```bash
# Permission denied
aws sts get-caller-identity  # Check credentials
aws iam get-role --role-name ProductionAnalyticsGatewayRole  # Check role

# Service not found
aws bedrock-agent list-memories --region us-west-2  # Check service availability

# Connection timeout
aws secretsmanager get-secret-value --secret-id production-analytics-postgres-connection --region us-west-2  # Check secrets
```

### Reset Commands
```bash
# Delete and recreate IAM role
aws iam delete-role-policy --role-name ProductionAnalyticsGatewayRole --policy-name GatewayPermissions
aws iam delete-role --role-name ProductionAnalyticsGatewayRole
# Then recreate using setup guide

# Update secret values
aws secretsmanager update-secret --secret-id SECRET_NAME --secret-string '{"key": "new_value"}'
```

## 📞 Support Resources

### Documentation Links
- [Memory Setup](docs/AGENTCORE_MEMORY_MANUAL_SETUP.md)
- [Identity Setup](docs/AGENTCORE_IDENTITY_MANUAL_SETUP.md)
- [Gateway Setup](docs/AGENTCORE_GATEWAY_MANUAL_SETUP.md)
- [Complete Validation](docs/AGENTCORE_COMPLETE_SETUP_VALIDATION.md)

### AWS Documentation
- [Bedrock AgentCore](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [IAM Roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)

---

**Quick Reference v4.1** | **Last Updated**: 2025-07-22 | **Status**: ✅ Complete