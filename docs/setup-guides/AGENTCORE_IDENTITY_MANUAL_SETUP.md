# AgentCore Identity Manual Setup Guide

## Overview

AgentCore Identity provides authentication and authorization capabilities for your agent. This guide covers setting up both Inbound Identity (for authenticating callers to your agent) and Outbound Identity (for your agent to access external resources) based on the actual AWS Console interface.

## Prerequisites

- AWS Console access to Amazon Bedrock AgentCore
- Agent ID: `hosted_agent_jqgjl-fJiyIV95k9`
- Appropriate IAM permissions for Bedrock and Identity services

## Identity Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   AgentCore     │    │   External      │
│   Callers       │───►│   Identity      │───►│   Resources     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     Inbound Auth           Agent Runtime         Outbound Auth
```

## Part 1: Inbound Identity Setup

### Purpose
Inbound Identity authenticates and authorizes callers to access your agent, tool runtime, or Gateway.

### Step 1: Navigate to Identity Console
1. Go to: https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agentcore/identity
2. You'll see the Identity overview with Inbound and Outbound sections

### Step 2: Create Inbound Identity (Optional for Basic Setup)
For the Production Analytics Agent, we'll initially use the hosted agent without additional inbound authentication, but here's how to set it up if needed:

**When to Use Inbound Identity:**
- When you need to restrict access to your agent
- When integrating with external authentication systems
- When you need fine-grained access control

**Configuration Options:**
- **IAM or JSON web tokens**: For AWS-based authentication
- **OAuth tokens**: For external OAuth providers

## Part 2: Outbound Identity Setup

### Purpose
Outbound Identity allows your agent or Gateway to access downstream resources like APIs, databases, and external services.

### Step 3: Create OAuth Client for External Resources

1. **Click "Add OAuth client / API key"** in the Outbound Identity section

2. **Add OAuth Client Configuration:**
   - **Name**: `production-analytics-agent-oauth-client`
   - **Provider**: Select appropriate provider (GitHub, Google, Microsoft, Salesforce, or Slack)
   - Click "Add OAuth Client"

### Step 4: Create API Key for External Services

1. **Click "Add OAuth client / API key"** again
2. **Select "Add API key"** from the dropdown

3. **API Key Configuration:**
   - **Name**: `production-analytics-agent-api-key`
   - **API key**: `your-external-api-key-here`
   - Click "Add"

## Part 3: Integration with Existing Infrastructure

### Current Infrastructure Integration

Our existing infrastructure already includes:
- **Cognito User Pool**: `us-west-2_e7K0T5HdW`
- **Cognito Client ID**: `79ghtj1rb5v77qqmusr7blsh4f`
- **IAM Roles**: Comprehensive role-based access control

### Required Updates to Existing Code

#### 1. Update Agent Configuration

Add AgentCore Identity configuration to your agent:

```python
# agent/agentcore_identity_integration.py
import boto3
import os
from typing import Dict, Any, Optional

class AgentCoreIdentityIntegration:
    def __init__(self):
        self.bedrock_agent_client = boto3.client('bedrock-agent')
        self.oauth_clients = {}
        self.api_keys = {}
        
        # Load identity configuration
        self._load_identity_configuration()
    
    def _load_identity_configuration(self):
        """Load identity configuration from environment"""
        self.oauth_clients = {
            'github': os.environ.get('GITHUB_OAUTH_CLIENT_ID'),
            'google': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
        }
        
        self.api_keys = {
            'external_api': os.environ.get('EXTERNAL_API_KEY'),
            'analytics_api': os.environ.get('ANALYTICS_API_KEY'),
        }
    
    def get_oauth_token(self, provider: str) -> Optional[str]:
        """Get OAuth token for external provider"""
        # Implementation would use AgentCore Identity APIs
        pass
    
    def authenticate_request(self, request_context: Dict[str, Any]) -> bool:
        """Authenticate incoming request using AgentCore Identity"""
        # Implementation would validate tokens using AgentCore
        pass
```

#### 2. Update Environment Variables

Add these to your ECS task definition or Lambda environment:

```bash
# OAuth Configuration
GITHUB_OAUTH_CLIENT_ID=your-github-client-id
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id

# API Key Configuration
EXTERNAL_API_KEY=your-external-api-key
ANALYTICS_API_KEY=your-analytics-api-key

# AgentCore Identity Configuration
AGENTCORE_IDENTITY_ENABLED=true
INBOUND_AUTH_REQUIRED=false
OUTBOUND_AUTH_ENABLED=true
```

#### 3. Update IAM Permissions

Add AgentCore Identity permissions to your existing IAM roles:

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
                "arn:aws:bedrock:us-west-2:*:identity/*"
            ]
        }
    ]
}
```

## Part 4: Integration with Existing Authentication

### Cognito Integration

Since we already have Cognito set up, we can integrate it with AgentCore Identity:

```python
# agent/cognito_agentcore_bridge.py
import boto3
from typing import Dict, Any

class CognitoAgentCoreBridge:
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp')
        self.user_pool_id = 'us-west-2_e7K0T5HdW'
        self.client_id = '79ghtj1rb5v77qqmusr7blsh4f'
    
    def validate_cognito_token(self, token: str) -> Dict[str, Any]:
        """Validate Cognito JWT token"""
        try:
            response = self.cognito_client.get_user(AccessToken=token)
            return {
                'valid': True,
                'user_id': response['Username'],
                'attributes': response['UserAttributes']
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def bridge_to_agentcore(self, cognito_user: Dict[str, Any]) -> str:
        """Bridge Cognito user to AgentCore Identity"""
        # Implementation would create AgentCore identity session
        pass
```

## Part 5: Testing and Validation

### Test Script for Identity Integration

```python
# scripts/test_identity_integration.py
import boto3
import json
from agent.agentcore_identity_integration import AgentCoreIdentityIntegration

def test_identity_integration():
    """Test AgentCore Identity integration"""
    identity = AgentCoreIdentityIntegration()
    
    # Test OAuth client configuration
    print("Testing OAuth clients...")
    for provider, client_id in identity.oauth_clients.items():
        if client_id:
            print(f"✅ {provider}: {client_id[:10]}...")
        else:
            print(f"❌ {provider}: Not configured")
    
    # Test API key configuration
    print("\nTesting API keys...")
    for service, api_key in identity.api_keys.items():
        if api_key:
            print(f"✅ {service}: {api_key[:10]}...")
        else:
            print(f"❌ {service}: Not configured")

if __name__ == "__main__":
    test_identity_integration()
```

## Part 6: Security Considerations

### Best Practices

1. **Token Management**
   - Store OAuth tokens securely in AWS Secrets Manager
   - Implement token refresh mechanisms
   - Use short-lived tokens where possible

2. **API Key Security**
   - Rotate API keys regularly
   - Use different keys for different environments
   - Monitor API key usage

3. **Access Control**
   - Implement least-privilege access
   - Use role-based access control
   - Audit identity operations regularly

### Monitoring and Alerting

```python
# Add to your CloudWatch monitoring
IDENTITY_METRICS = [
    'AuthenticationAttempts',
    'AuthenticationFailures', 
    'TokenRefreshes',
    'APIKeyUsage'
]
```

## Part 7: Integration with Existing Components

### Database Integration
The identity system integrates with our database integration:

```python
# In database_integration.py
def get_connection_with_identity(self, user_context: Dict[str, Any]):
    """Get database connection with user identity context"""
    # Use AgentCore Identity to get appropriate credentials
    pass
```

### LangGraph Workflow Integration
Add identity context to workflow state:

```python
# In langgraph_workflow.py
class AnalyticsState(TypedDict):
    # ... existing fields ...
    user_identity: Dict[str, Any]
    auth_context: Dict[str, Any]
```

## Summary

AgentCore Identity provides:
- **Inbound Authentication**: Control who can access your agent
- **Outbound Authentication**: Secure access to external resources
- **OAuth Integration**: Support for major OAuth providers
- **API Key Management**: Secure storage and rotation of API keys

The integration enhances our existing Cognito-based authentication while providing additional capabilities for external resource access.

---

**Status**: Ready for Manual Setup  
**Integration**: Enhances existing Cognito authentication  
**Security**: Enterprise-grade identity management  
**Next Steps**: Set up OAuth clients and API keys as needed