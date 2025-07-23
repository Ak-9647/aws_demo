# AgentCore Development Guide

## Development Environment Setup

This repository is optimized for Amazon Bedrock AgentCore development with advanced LangGraph workflows, MCP integration, and comprehensive memory management.

### Repository Structure
```
production-analytics-agent/
├── .kiro/                      # Kiro IDE configuration
│   ├── settings/
│   │   └── mcp.json           # MCP server configuration
│   └── steering/              # Development guidance documents
├── agent/                     # Core agent implementation
│   ├── main.py               # HTTP server and entry point
│   ├── langgraph_workflow.py # LangGraph workflow engine
│   ├── analytics_engine.py   # Core analytics processing
│   ├── conversation_memory.py # Memory management
│   ├── mcp_analytics_tools.py # MCP tool integration
│   ├── agentcore_integration.py # AgentCore components
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Container definition
├── gui/                      # Streamlit web interface
├── infrastructure/           # Terraform IaC
├── docs/                    # All documentation
└── scripts/                 # Utility scripts
```

### Key Development Principles

#### 1. AgentCore-First Architecture
- **Memory Integration**: All conversations stored in DynamoDB with Redis caching
- **Gateway Usage**: External integrations through secure AgentCore gateways
- **Identity Management**: Cognito-based authentication with role-based access
- **Observability**: Comprehensive CloudWatch monitoring and alerting

#### 2. LangGraph Workflow Design
- **Multi-step Processing**: 7-node workflow for intelligent query handling
- **Context Awareness**: Historical conversation context influences responses
- **Task Decomposition**: Complex queries broken into manageable components
- **Error Resilience**: Graceful degradation when components fail

#### 3. MCP Tool Integration
- **Intelligent Selection**: Tools chosen based on query content and context
- **Parallel Execution**: Multiple tools can run simultaneously
- **Fallback Mechanisms**: Built-in alternatives when external tools fail
- **Security First**: All external connections secured and audited

### Development Workflow

#### Local Development
```bash
# 1. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r agent/requirements.txt

# 2. Configure MCP tools
export PATH="$HOME/.local/bin:$PATH"
uvx --version  # Verify MCP tool runner

# 3. Run agent locally
cd agent
python main.py

# 4. Run GUI locally
cd gui
streamlit run app.py
```

#### Testing Strategy
```bash
# Unit tests for core components
python -m pytest agent/tests/

# MCP integration tests
python test_mcp_simple.py

# End-to-end workflow tests
python test_langgraph_workflow.py
```

#### Container Development
```bash
# Build agent container
docker build -t analytics-agent ./agent/

# Build GUI container
docker build -t analytics-gui ./gui/

# Test locally
docker run -p 8080:8080 analytics-agent
docker run -p 8501:8501 analytics-gui
```

### AgentCore Integration Patterns

#### Memory Management
```python
# Conversation storage pattern
from conversation_memory import ConversationMemory

memory = ConversationMemory()
memory.store_conversation(
    session_id="user-session-123",
    query="Analyze sales data",
    response={"analysis": "...", "visualizations": [...]}
)

# Context retrieval pattern
context = memory.get_conversation_history(session_id, limit=5)
```

#### MCP Tool Usage
```python
# Tool selection and execution
from mcp_analytics_tools import MCPAnalyticsTools

mcp_tools = MCPAnalyticsTools()
relevant_tools = mcp_tools.get_relevant_tools_for_query(query)

for tool_info in relevant_tools:
    result = await mcp_tools.call_mcp_tool(
        tool_info['tool'], 
        tool_info['function'], 
        parameters
    )
```

#### LangGraph Workflow
```python
# Workflow state management
from langgraph_workflow import get_workflow

workflow = get_workflow()
result = workflow.process_query(
    query="Complex analytics request",
    session_id="user-session-123",
    user_id="user-456"
)
```

### Configuration Management

#### Environment Variables
```bash
# Core AgentCore Configuration
export AWS_REGION=us-west-2
export AGENTCORE_AGENT_ID=your-agent-id
export AGENTCORE_AGENT_ALIAS_ID=TSTALIASID

# Memory Configuration
export CONVERSATION_TABLE=production-analytics-agent-conversation-history
export USER_PREFERENCES_TABLE=production-analytics-agent-user-preferences
export REDIS_ENDPOINT=production-analytics-agent-redis.cache.amazonaws.com

# MCP Configuration
export MCP_CONFIG_PATH=.kiro/settings/mcp.json
export ALLOWED_DIRECTORIES=/tmp,/data

# Database Configuration
export POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db
export REDSHIFT_CONNECTION_STRING=redshift://user:pass@host:5439/db

# Feature Flags
export MCP_ENABLED=true
export MEMORY_ENABLED=true
export ADVANCED_ANALYTICS=true
export DEBUG_MODE=false
```

#### MCP Server Configuration
```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "disabled": false,
      "autoApprove": ["search_aws_docs", "get_aws_service_info"]
    },
    "postgres": {
      "command": "uvx", 
      "args": ["mcp-server-postgres@latest"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      },
      "disabled": false,
      "autoApprove": ["query_database", "get_schema", "list_tables"]
    }
  }
}
```

### Deployment Patterns

#### Infrastructure as Code
```bash
# Deploy infrastructure
cd infrastructure
terraform init
terraform plan
terraform apply

# Deploy application
docker build -t analytics-agent ./agent/
docker tag analytics-agent:latest ${ECR_REPO}:v4.1
docker push ${ECR_REPO}:v4.1

# Update ECS service
aws ecs update-service --cluster production-analytics-agent-cluster \
  --service production-analytics-agent-service \
  --force-new-deployment
```

#### CI/CD Integration
```yaml
# .github/workflows/deploy.yml
name: Deploy Analytics Agent
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Deploy
        run: |
          docker build -t analytics-agent ./agent/
          # Push to ECR and update ECS
```

### Monitoring and Debugging

#### CloudWatch Integration
```python
import boto3
import logging

# Structured logging for CloudWatch
logger = logging.getLogger(__name__)
logger.info("Query processed", extra={
    "session_id": session_id,
    "query_type": intent['type'],
    "processing_time": elapsed_time,
    "mcp_tools_used": len(mcp_enhancements)
})
```

#### Performance Monitoring
```python
# Custom metrics for AgentCore
cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(
    Namespace='Analytics/Agent',
    MetricData=[
        {
            'MetricName': 'QueryProcessingTime',
            'Value': processing_time,
            'Unit': 'Seconds'
        }
    ]
)
```

### Security Best Practices

#### IAM Roles and Policies
- **Least Privilege**: Each component has minimal required permissions
- **Role Separation**: Different roles for agent, GUI, and infrastructure
- **Resource-based Policies**: Fine-grained access to specific resources

#### Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **Secrets Management**: API keys and credentials in AWS Secrets Manager
- **Network Security**: VPC isolation with security groups
- **Audit Logging**: Comprehensive logging of all operations

### Development Guidelines

#### Code Organization
- **Modular Design**: Each component has clear responsibilities
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Testing**: Unit tests, integration tests, and end-to-end tests
- **Documentation**: Inline documentation and comprehensive guides

#### Performance Optimization
- **Caching**: Redis for session data, query result caching
- **Connection Pooling**: Database connection reuse
- **Async Processing**: Non-blocking operations where possible
- **Resource Management**: Proper cleanup of resources

#### Scalability Considerations
- **Stateless Design**: Agent containers are stateless for easy scaling
- **Database Scaling**: Read replicas for read-heavy workloads
- **Cache Scaling**: Redis cluster mode for high availability
- **Load Balancing**: Application Load Balancer with health checks

This development guide ensures consistent, secure, and scalable AgentCore development practices across the entire analytics agent platform.