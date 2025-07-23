# Creating AgentCore Gateways - Step-by-Step Guide

**Important**: AgentCore Gateways must be created manually through the AWS Console as they are not yet supported by Terraform.

## Prerequisites

All supporting infrastructure has been deployed via Terraform. You need to create 3 gateways using the resources below:

### Available Resources (from Terraform output)
```bash
# Lambda Function for Database Gateway
analytics_gateway_lambda_arn = "arn:aws:lambda:us-west-2:280383026847:function:production-analytics-agent-analytics-gateway-target"

# S3 Bucket for Data Gateway  
analytics_data_bucket = "production-analytics-agent-analytics-data-839dae02"

# Secrets for Authentication
analytics_api_secret_arn = "arn:aws:secretsmanager:us-west-2:280383026847:secret:production-analytics-agent-analytics-api-key-WTuOca"
database_connection_secret_arn = "arn:aws:secretsmanager:us-west-2:280383026847:secret:production-analytics-agent-database-connection-Eyk3V0"

# Database Endpoint
rds_cluster_endpoint = "production-analytics-agent-analytics-cluster.cluster-cxayeoogcra9.us-west-2.rds.amazonaws.com"
```

## Gateway Creation Steps

### 1. Analytics REST API Gateway

#### Step 1: Navigate to AgentCore Gateways
1. Go to AWS Console → Amazon Bedrock → AgentCore → Gateways
2. Click "Create gateway"

#### Step 2: Configure Gateway
- **Gateway Name**: `production-analytics-agent-analytics-gateway`
- **Description**: `REST API gateway for external analytics services`

#### Step 3: Create Target
- **Target Name**: `analytics-api-target`
- **Target Type**: `REST API`
- **Base URL**: `https://api.example.com/analytics` (replace with your actual API)
- **Schema**: Upload `schemas/analytics-api-schema.json`

#### Step 4: Configure Authentication
- **Outbound Auth Type**: `API Key`
- **API Key Secret**: `arn:aws:secretsmanager:us-west-2:280383026847:secret:production-analytics-agent-analytics-api-key-WTuOca`
- **Header Name**: `X-API-Key`

#### Step 5: Configure Inbound Auth
- **Inbound Auth**: `Cognito Quick Setup`
- **User Pool**: Select the deployed Cognito user pool

#### Step 6: Create Gateway
- Review configuration and click "Create gateway"

---

### 2. Database Gateway

#### Step 1: Create New Gateway
1. Click "Create gateway" again
2. **Gateway Name**: `production-analytics-agent-database-gateway`
3. **Description**: `Database gateway for PostgreSQL analytics cluster`

#### Step 2: Create Target
- **Target Name**: `database-target`
- **Target Type**: `Lambda ARN`
- **Lambda ARN**: `arn:aws:lambda:us-west-2:280383026847:function:production-analytics-agent-analytics-gateway-target`
- **Schema**: Upload `schemas/database-gateway-schema.json`

#### Step 3: Configure Authentication
- **Outbound Auth Type**: `IAM Role`
- **IAM Role**: Use the Lambda execution role (auto-configured)

#### Step 4: Configure Inbound Auth
- **Inbound Auth**: `None` (internal use only)

#### Step 5: Create Gateway
- Review configuration and click "Create gateway"

---

### 3. S3 Data Gateway

#### Step 1: Create New Gateway
1. Click "Create gateway" again
2. **Gateway Name**: `production-analytics-agent-s3-gateway`
3. **Description**: `S3 gateway for analytics data access`

#### Step 2: Create Target
- **Target Name**: `s3-data-target`
- **Target Type**: `S3`
- **Bucket Name**: `production-analytics-agent-analytics-data-839dae02`
- **Prefix**: `analytics/` (optional)

#### Step 3: Configure Authentication
- **Outbound Auth Type**: `IAM Role`
- **IAM Role**: Use the AgentCore runtime role

#### Step 4: Configure Inbound Auth
- **Inbound Auth**: `None` (internal use only)

#### Step 5: Create Gateway
- Review configuration and click "Create gateway"

---

## Schema Files

The schema files are already created in the `schemas/` directory:

### Analytics API Schema (`schemas/analytics-api-schema.json`)
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Analytics API",
    "version": "1.0.0"
  },
  "paths": {
    "/analyze": {
      "post": {
        "summary": "Analyze data",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "query": {"type": "string"},
                  "data_source": {"type": "string"},
                  "parameters": {"type": "object"}
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Analysis results",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "results": {"type": "object"},
                    "visualizations": {"type": "array"},
                    "insights": {"type": "array"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Database Gateway Schema (`schemas/database-gateway-schema.json`)
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Database Gateway",
    "version": "1.0.0"
  },
  "paths": {
    "/query": {
      "post": {
        "summary": "Execute database query",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "sql": {"type": "string"},
                  "parameters": {"type": "array"},
                  "limit": {"type": "integer"}
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Query results",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "rows": {"type": "array"},
                    "columns": {"type": "array"},
                    "row_count": {"type": "integer"}
                  }
                }
              }
            }
          }
        }
      }
    },
    "/schema": {
      "get": {
        "summary": "Get database schema",
        "responses": {
          "200": {
            "description": "Database schema",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "tables": {"type": "array"},
                    "views": {"type": "array"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## Verification Steps

After creating all gateways:

### 1. Check Gateway Status
1. Go to AgentCore → Gateways
2. Verify all 3 gateways show "Active" status
3. Note down the Gateway ARNs for agent configuration

### 2. Test Gateway Connectivity
1. Use the "Test" feature in each gateway
2. Verify authentication is working
3. Check CloudWatch logs for any errors

### 3. Update Agent Configuration
Add the gateway ARNs to your agent environment variables:

```bash
# Add to agent environment
ANALYTICS_GATEWAY_ARN=arn:aws:bedrock:us-west-2:280383026847:agent-gateway/production-analytics-agent-analytics-gateway
DATABASE_GATEWAY_ARN=arn:aws:bedrock:us-west-2:280383026847:agent-gateway/production-analytics-agent-database-gateway
S3_GATEWAY_ARN=arn:aws:bedrock:us-west-2:280383026847:agent-gateway/production-analytics-agent-s3-gateway
```

## Troubleshooting

### Common Issues

#### Gateway Creation Fails
- **Check IAM Permissions**: Ensure you have bedrock:CreateGateway permissions
- **Verify Resources**: Confirm Lambda function and S3 bucket exist
- **Schema Validation**: Ensure schema files are valid OpenAPI 3.0

#### Authentication Issues
- **Secret Access**: Verify the Lambda has access to Secrets Manager
- **IAM Roles**: Check that roles have necessary permissions
- **Cognito Setup**: Ensure user pool is properly configured

#### Lambda Function Issues
- **Function Exists**: Verify Lambda function is deployed and active
- **Permissions**: Check Lambda has bedrock:InvokeGateway permission
- **Logs**: Check CloudWatch logs for Lambda execution errors

### Getting Help

1. **AWS Console**: Use the built-in help and documentation
2. **CloudWatch Logs**: Check logs for detailed error messages
3. **IAM Policy Simulator**: Test permissions before creating gateways
4. **AWS Support**: Contact AWS support for AgentCore-specific issues

## Next Steps

Once all gateways are created:

1. **Update Documentation**: Record the actual gateway ARNs
2. **Test Integration**: Verify agent can use all gateways
3. **Monitor Performance**: Set up CloudWatch monitoring
4. **Security Review**: Ensure all authentication is properly configured

The gateways will enable the agent to:
- Access external analytics APIs
- Query the PostgreSQL database directly
- Read/write data from S3 buckets
- Integrate with other AWS services securely

This completes the AgentCore Gateway setup for the Production Analytics Agent v4.1.