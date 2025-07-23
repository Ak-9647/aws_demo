# AgentCore Gateway Manual Setup Guide

## Overview

AgentCore Gateway provides secure, managed connections to external data sources and services. This guide covers manual setup of gateway components for the Production Analytics Agent v4.1.

## Gateway Components

### 1. REST Gateway
Secure HTTP/HTTPS connections to external APIs and web services.

### 2. Database Gateway
Managed connections to relational databases (PostgreSQL, MySQL, Redshift).

### 3. S3 Gateway
Secure access to S3 buckets for data lake operations.

### 4. Custom Gateway
Extensible gateway for specialized integrations.

## Prerequisites

- AWS CLI configured with appropriate permissions
- AgentCore service enabled in your AWS account
- VPC and networking components configured
- IAM roles and policies prepared

## Manual Setup Steps

### Step 1: Create Gateway Configuration

Create the gateway configuration file:

```yaml
# infrastructure/agentcore-gateway.yaml
apiVersion: bedrock/v1
kind: Gateway
metadata:
  name: production-analytics-gateway
  namespace: production
spec:
  gateways:
    - name: rest-gateway
      type: REST
      configuration:
        endpoints:
          - name: market-data-api
            url: https://api.marketdata.com/v1
            authentication:
              type: API_KEY
              secretArn: arn:aws:secretsmanager:us-west-2:ACCOUNT:secret:market-api-key
            rateLimiting:
              requestsPerSecond: 10
              burstCapacity: 50
            timeout: 30s
            retryPolicy:
              maxRetries: 3
              backoffMultiplier: 2
          
          - name: weather-api
            url: https://api.weather.com/v1
            authentication:
              type: BEARER_TOKEN
              secretArn: arn:aws:secretsmanager:us-west-2:ACCOUNT:secret:weather-token
            rateLimiting:
              requestsPerSecond: 5
              burstCapacity: 20
    
    - name: database-gateway
      type: DATABASE
      configuration:
        connections:
          - name: analytics-postgres
            type: POSTGRESQL
            connectionString:
              secretArn: arn:aws:secretsmanager:us-west-2:ACCOUNT:secret:postgres-connection
            pooling:
              minConnections: 2
              maxConnections: 20
              idleTimeout: 300s
            ssl:
              enabled: true
              mode: require
          
          - name: data-warehouse
            type: REDSHIFT
            connectionString:
              secretArn: arn:aws:secretsmanager:us-west-2:ACCOUNT:secret:redshift-connection
            pooling:
              minConnections: 1
              maxConnections: 10
              idleTimeout: 600s
    
    - name: s3-gateway
      type: S3
      configuration:
        buckets:
          - name: analytics-data-lake
            bucket: production-analytics-data-lake
            region: us-west-2
            permissions:
              - READ
              - WRITE
            pathPrefix: /analytics/
          
          - name: processed-results
            bucket: production-analytics-results
            region: us-west-2
            permissions:
              - READ
              - WRITE
              - DELETE
            pathPrefix: /results/
  
  security:
    encryption:
      inTransit: true
      atRest: true
    authentication:
      required: true
    authorization:
      rbac: true
  
  monitoring:
    cloudWatch:
      enabled: true
      logGroup: /aws/agentcore/gateway
      metricsNamespace: AgentCore/Gateway
    
    alerting:
      enabled: true
      thresholds:
        errorRate: 5%
        latency: 5000ms
        connectionFailures: 3
##
# Step 2: Create Secrets in AWS Secrets Manager

Store connection strings and API keys securely:

```bash
# Create PostgreSQL connection secret
aws secretsmanager create-secret \
  --name "production-analytics-postgres-connection" \
  --description "PostgreSQL connection string for analytics database" \
  --secret-string '{
    "host": "analytics-db.cluster-xyz.us-west-2.rds.amazonaws.com",
    "port": "5432",
    "database": "analytics",
    "username": "analytics_user",
    "password": "secure_password_here"
  }'

# Create Redshift connection secret
aws secretsmanager create-secret \
  --name "production-analytics-redshift-connection" \
  --description "Redshift connection string for data warehouse" \
  --secret-string '{
    "host": "analytics-warehouse.xyz.us-west-2.redshift.amazonaws.com",
    "port": "5439",
    "database": "warehouse",
    "username": "warehouse_user",
    "password": "secure_password_here"
  }'

# Create API key secrets
aws secretsmanager create-secret \
  --name "production-analytics-market-api-key" \
  --description "Market data API key" \
  --secret-string '{"api_key": "your_market_api_key_here"}'

aws secretsmanager create-secret \
  --name "production-analytics-weather-token" \
  --description "Weather API bearer token" \
  --secret-string '{"token": "your_weather_token_here"}'
```

### Step 3: Create IAM Roles and Policies

Create the gateway service role:

```bash
# Create trust policy for AgentCore Gateway
cat > gateway-trust-policy.json << EOF
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
  --assume-role-policy-document file://gateway-trust-policy.json \
  --description "Service role for AgentCore Gateway"

# Create gateway permissions policy
cat > gateway-permissions-policy.json << EOF
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
        "arn:aws:secretsmanager:us-west-2:*:secret:production-analytics-*"
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
        "arn:aws:s3:::production-analytics-data-lake/*",
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
      "Resource": "arn:aws:logs:us-west-2:*:log-group:/aws/agentcore/gateway*"
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
  --policy-document file://gateway-permissions-policy.json
```

### Step 4: Deploy Gateway Configuration

Deploy the gateway using AWS CLI:

```bash
# Deploy the gateway configuration
aws bedrock-agent create-gateway \
  --gateway-name production-analytics-gateway \
  --configuration file://infrastructure/agentcore-gateway.yaml \
  --service-role-arn arn:aws:iam::ACCOUNT:role/ProductionAnalyticsGatewayRole \
  --region us-west-2

# Wait for deployment to complete
aws bedrock-agent describe-gateway \
  --gateway-id GATEWAY_ID \
  --region us-west-2
```

### Step 5: Create Gateway Integration Script

Create a deployment script for easier management:

```bash
#!/bin/bash
# scripts/deploy-agentcore-gateway.sh

set -e

echo "🚀 Deploying AgentCore Gateway..."

# Configuration
GATEWAY_NAME="production-analytics-gateway"
REGION="us-west-2"
ROLE_NAME="ProductionAnalyticsGatewayRole"

# Check if gateway already exists
if aws bedrock-agent describe-gateway --gateway-name $GATEWAY_NAME --region $REGION 2>/dev/null; then
    echo "⚠️  Gateway already exists. Updating configuration..."
    aws bedrock-agent update-gateway \
        --gateway-name $GATEWAY_NAME \
        --configuration file://infrastructure/agentcore-gateway.yaml \
        --region $REGION
else
    echo "📝 Creating new gateway..."
    aws bedrock-agent create-gateway \
        --gateway-name $GATEWAY_NAME \
        --configuration file://infrastructure/agentcore-gateway.yaml \
        --service-role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/$ROLE_NAME \
        --region $REGION
fi

# Wait for deployment
echo "⏳ Waiting for gateway deployment..."
aws bedrock-agent wait gateway-available \
    --gateway-name $GATEWAY_NAME \
    --region $REGION

echo "✅ Gateway deployed successfully!"

# Test gateway connectivity
echo "🔍 Testing gateway connections..."
python3 scripts/test-gateway.py

echo "🎉 AgentCore Gateway setup complete!"
```

## Gateway Integration in Agent Code

### Step 6: Create Gateway Client

Create the gateway integration module:

```python
# agent/agentcore_gateway_integration.py
import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GatewayConnection:
    name: str
    type: str
    endpoint: str
    status: str

class AgentCoreGateway:
    """AgentCore Gateway integration for secure external connections."""
    
    def __init__(self, gateway_name: str = "production-analytics-gateway"):
        self.gateway_name = gateway_name
        self.bedrock_client = boto3.client('bedrock-agent')
        self.gateway_info = None
        self._initialize_gateway()
    
    def _initialize_gateway(self):
        """Initialize gateway connection and retrieve configuration."""
        try:
            response = self.bedrock_client.describe_gateway(
                gatewayName=self.gateway_name
            )
            self.gateway_info = response['gateway']
            logger.info(f"Connected to AgentCore Gateway: {self.gateway_name}")
        except Exception as e:
            logger.error(f"Failed to initialize gateway: {e}")
            self.gateway_info = None
    
    def get_gateway_status(self) -> Dict[str, Any]:
        """Get current gateway status and health."""
        if not self.gateway_info:
            return {"status": "unavailable", "error": "Gateway not initialized"}
        
        try:
            response = self.bedrock_client.get_gateway_status(
                gatewayName=self.gateway_name
            )
            return {
                "status": response.get('status', 'unknown'),
                "connections": response.get('connections', []),
                "last_updated": response.get('lastUpdated'),
                "health_check": response.get('healthCheck', {})
            }
        except Exception as e:
            logger.error(f"Failed to get gateway status: {e}")
            return {"status": "error", "error": str(e)}
    
    def execute_rest_call(self, endpoint_name: str, method: str, 
                         path: str, params: Optional[Dict] = None,
                         headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute REST API call through gateway."""
        try:
            request_data = {
                "endpoint": endpoint_name,
                "method": method,
                "path": path,
                "parameters": params or {},
                "headers": headers or {}
            }
            
            response = self.bedrock_client.invoke_gateway(
                gatewayName=self.gateway_name,
                gatewayType="REST",
                requestData=json.dumps(request_data)
            )
            
            return json.loads(response['responseData'])
        except Exception as e:
            logger.error(f"REST call failed: {e}")
            return {"error": str(e), "success": False}
    
    def execute_database_query(self, connection_name: str, query: str,
                              parameters: Optional[List] = None) -> Dict[str, Any]:
        """Execute database query through gateway."""
        try:
            request_data = {
                "connection": connection_name,
                "query": query,
                "parameters": parameters or []
            }
            
            response = self.bedrock_client.invoke_gateway(
                gatewayName=self.gateway_name,
                gatewayType="DATABASE",
                requestData=json.dumps(request_data)
            )
            
            return json.loads(response['responseData'])
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return {"error": str(e), "success": False}
    
    def access_s3_data(self, bucket_name: str, operation: str,
                       key: str, data: Optional[bytes] = None) -> Dict[str, Any]:
        """Access S3 data through gateway."""
        try:
            request_data = {
                "bucket": bucket_name,
                "operation": operation,
                "key": key
            }
            
            if data and operation in ["PUT", "UPLOAD"]:
                request_data["data"] = data.decode('utf-8') if isinstance(data, bytes) else data
            
            response = self.bedrock_client.invoke_gateway(
                gatewayName=self.gateway_name,
                gatewayType="S3",
                requestData=json.dumps(request_data)
            )
            
            return json.loads(response['responseData'])
        except Exception as e:
            logger.error(f"S3 operation failed: {e}")
            return {"error": str(e), "success": False}
    
    def list_available_connections(self) -> List[GatewayConnection]:
        """List all available gateway connections."""
        if not self.gateway_info:
            return []
        
        connections = []
        try:
            for gateway_config in self.gateway_info.get('gateways', []):
                gateway_type = gateway_config.get('type')
                
                if gateway_type == 'REST':
                    for endpoint in gateway_config.get('configuration', {}).get('endpoints', []):
                        connections.append(GatewayConnection(
                            name=endpoint['name'],
                            type='REST',
                            endpoint=endpoint['url'],
                            status='active'
                        ))
                
                elif gateway_type == 'DATABASE':
                    for conn in gateway_config.get('configuration', {}).get('connections', []):
                        connections.append(GatewayConnection(
                            name=conn['name'],
                            type=conn['type'],
                            endpoint=f"{conn['type']} Database",
                            status='active'
                        ))
                
                elif gateway_type == 'S3':
                    for bucket in gateway_config.get('configuration', {}).get('buckets', []):
                        connections.append(GatewayConnection(
                            name=bucket['name'],
                            type='S3',
                            endpoint=bucket['bucket'],
                            status='active'
                        ))
        
        except Exception as e:
            logger.error(f"Failed to list connections: {e}")
        
        return connections

# Example usage and testing
if __name__ == "__main__":
    gateway = AgentCoreGateway()
    
    # Test gateway status
    status = gateway.get_gateway_status()
    print(f"Gateway Status: {status}")
    
    # List available connections
    connections = gateway.list_available_connections()
    print(f"Available Connections: {len(connections)}")
    for conn in connections:
        print(f"  - {conn.name} ({conn.type}): {conn.endpoint}")
```

## Testing Gateway Integration

### Step 7: Create Gateway Test Script

```python
# scripts/test-gateway.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent'))

from agentcore_gateway_integration import AgentCoreGateway
import json

def test_gateway_integration():
    """Test AgentCore Gateway integration."""
    print("🧪 Testing AgentCore Gateway Integration...")
    
    # Initialize gateway
    gateway = AgentCoreGateway()
    
    # Test 1: Gateway Status
    print("\n1. Testing Gateway Status...")
    status = gateway.get_gateway_status()
    print(f"   Status: {status.get('status', 'unknown')}")
    
    # Test 2: List Connections
    print("\n2. Testing Connection Listing...")
    connections = gateway.list_available_connections()
    print(f"   Found {len(connections)} connections:")
    for conn in connections:
        print(f"   - {conn.name} ({conn.type})")
    
    # Test 3: Database Query (if available)
    print("\n3. Testing Database Query...")
    db_result = gateway.execute_database_query(
        "analytics-postgres",
        "SELECT version();"
    )
    if db_result.get('success'):
        print("   ✅ Database query successful")
    else:
        print(f"   ❌ Database query failed: {db_result.get('error')}")
    
    # Test 4: REST API Call (if available)
    print("\n4. Testing REST API Call...")
    rest_result = gateway.execute_rest_call(
        "market-data-api",
        "GET",
        "/health"
    )
    if rest_result.get('success'):
        print("   ✅ REST API call successful")
    else:
        print(f"   ❌ REST API call failed: {rest_result.get('error')}")
    
    # Test 5: S3 Access (if available)
    print("\n5. Testing S3 Access...")
    s3_result = gateway.access_s3_data(
        "analytics-data-lake",
        "LIST",
        "/"
    )
    if s3_result.get('success'):
        print("   ✅ S3 access successful")
    else:
        print(f"   ❌ S3 access failed: {s3_result.get('error')}")
    
    print("\n🎉 Gateway integration tests completed!")

if __name__ == "__main__":
    test_gateway_integration()
```

## Troubleshooting

### Common Issues

1. **Gateway Not Found**
   - Verify gateway name and region
   - Check IAM permissions for bedrock-agent service

2. **Connection Failures**
   - Verify secrets in AWS Secrets Manager
   - Check security group configurations
   - Validate connection strings

3. **Permission Denied**
   - Review IAM role policies
   - Ensure proper resource ARNs
   - Check service trust relationships

4. **Timeout Issues**
   - Adjust timeout settings in gateway configuration
   - Check network connectivity
   - Review rate limiting settings

### Monitoring and Alerts

Monitor gateway performance through CloudWatch:

```bash
# View gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace "AgentCore/Gateway" \
  --metric-name "RequestCount" \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Check gateway logs
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/agentcore/gateway"
```

## Next Steps

1. **Deploy Gateway**: Run the deployment script
2. **Test Integration**: Execute the test script
3. **Monitor Performance**: Set up CloudWatch dashboards
4. **Configure Alerts**: Create SNS notifications for failures
5. **Update Agent Code**: Integrate gateway client into main agent

## Security Considerations

- All connections use encryption in transit and at rest
- API keys and credentials stored in AWS Secrets Manager
- IAM roles follow least-privilege principles
- Network access controlled through security groups
- Audit logging enabled for all gateway operations

This manual setup provides secure, scalable gateway integration for the Production Analytics Agent v4.1.