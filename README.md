# Production Analytics Agent v4.1

🚀 **Enterprise-ready AI agent built on Amazon Bedrock AgentCore with advanced LangGraph workflows, MCP integration, and intelligent memory management.**

[![AgentCore](https://img.shields.io/badge/Amazon%20Bedrock-AgentCore-orange)](https://aws.amazon.com/bedrock/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-blue)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/MCP-Integration-green)](https://modelcontextprotocol.io/)
[![AWS](https://img.shields.io/badge/AWS-Production%20Ready-yellow)](https://aws.amazon.com/)

**Author**: Akshay Ramesh  
**License**: MIT

## 🎯 What's New in v4.1

- **🧠 LangGraph Workflow Engine**: 7-node intelligent query processing pipeline
- **🔗 MCP Tool Integration**: 9 specialized Model Context Protocol tools
- **💾 Advanced Memory System**: DynamoDB + Redis with conversation continuity
- **🔐 AgentCore Identity**: Cognito-based authentication with role-based access
- **🌐 Secure Gateways**: REST, Database, and S3 integrations
- **📊 Real Chart Generation**: Matplotlib/Plotly with base64 export

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   LangGraph      │    │   MCP Tools     │
│   Web GUI       │◄──►│   Workflow       │◄──►│   (9 servers)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AgentCore     │    │   Memory Layer   │    │   Data Sources  │
│   Runtime       │◄──►│   DynamoDB+Redis │◄──►│   S3+RDS+APIs   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Repository Structure
```
production-analytics-agent/
├── 🤖 agent/                   # Core agent implementation
│   ├── main.py                # HTTP server and entry point
│   ├── langgraph_workflow.py  # LangGraph workflow engine
│   ├── analytics_engine.py    # Core analytics processing
│   ├── conversation_memory.py # Memory management
│   ├── mcp_analytics_tools.py # MCP tool integration
│   └── agentcore_integration.py # AgentCore components
├── 🖥️ gui/                     # Streamlit web interface
├── 🏗️ infrastructure/          # Terraform infrastructure
├── 📚 docs/                    # All documentation
├── ⚙️ .kiro/                   # Kiro IDE configuration
│   ├── settings/mcp.json      # MCP server configuration
│   └── steering/              # Development guidance
└── 🧪 scripts/                # Utility and test scripts
```

## 🚀 Quick Start

### Prerequisites
- **AWS Account** with Bedrock AgentCore access
- **Docker** and **Python 3.13+**
- **Terraform** for infrastructure
- **uvx** for MCP tools (auto-installed)

### 1. Local Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd production-analytics-agent

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r agent/requirements.txt

# Install MCP tools
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Run Agent Locally
```bash
# Start the agent
cd agent
python main.py
# Agent runs on http://localhost:8080

# Start the GUI (new terminal)
cd gui
streamlit run app.py
# GUI available at http://localhost:8501
```

### 3. Test MCP Integration
```bash
# Test MCP tools
python test_mcp_simple.py

# Test complete workflow
python test_langgraph_workflow.py
```

## 🏭 Production Deployment

### Infrastructure Deployment
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

### Container Deployment
```bash
# Build and deploy agent
docker build -t analytics-agent ./agent/
docker tag analytics-agent:latest ${ECR_REPO}:v4.1
docker push ${ECR_REPO}:v4.1

# Update ECS service
aws ecs update-service --cluster production-analytics-agent-cluster \
  --service production-analytics-agent-service --force-new-deployment
```

## 🛠️ Key Features

### 🧠 Intelligent Query Processing
- **Multi-step Reasoning**: Complex queries broken into manageable tasks
- **Context Awareness**: Remembers conversation history across sessions
- **Intent Recognition**: Understands query complexity and requirements
- **Smart Recommendations**: Context-aware suggestions based on user patterns

### 🔗 MCP Tool Ecosystem
1. **AWS Documentation** - Automatic service guidance and best practices
2. **PostgreSQL Database** - Direct SQL execution and schema analysis
3. **Filesystem Operations** - Secure file management and processing
4. **Advanced Analytics** - Statistical analysis and anomaly detection
5. **Visualization Engine** - Interactive chart and dashboard creation
6. **AWS Analytics Services** - Athena, Glue, and QuickSight integration
7. **Redshift Warehouse** - Large-scale data warehouse operations
8. **Web Search** - Current market data and trend analysis
9. **GitHub Integration** - Code repository access and analysis

### 📊 Advanced Analytics
- **Statistical Analysis**: Correlation, regression, significance tests
- **Anomaly Detection**: IQR-based outlier identification
- **Time Series Forecasting**: Predictive analytics with trend analysis
- **Real Visualizations**: Base64-encoded PNG charts with custom themes
- **Interactive Dashboards**: Multi-chart visualizations with drill-down

### 💾 Memory & Context
- **Conversation Continuity**: Maintains context across multiple sessions
- **User Preference Learning**: Adapts to individual query patterns
- **Smart Context Synthesis**: Intelligent extraction from conversation history
- **Dual-layer Storage**: Redis for speed, DynamoDB for persistence

## 🔧 Configuration

### Environment Variables
```bash
# AgentCore Configuration
export AGENTCORE_AGENT_ID=your-agent-id
export AWS_REGION=us-west-2

# Memory Configuration  
export CONVERSATION_TABLE=production-analytics-agent-conversation-history
export REDIS_ENDPOINT=production-analytics-agent-redis.cache.amazonaws.com

# MCP Configuration
export MCP_CONFIG_PATH=.kiro/settings/mcp.json
export POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db

# Feature Flags
export MCP_ENABLED=true
export MEMORY_ENABLED=true
export ADVANCED_ANALYTICS=true
```

### MCP Server Configuration
The `.kiro/settings/mcp.json` file configures 9 MCP servers for enhanced capabilities. See [MCP Integration Guide](.kiro/steering/mcp-integration.md) for details.

## 📊 Performance Metrics

- **Query Response Time**: < 5 seconds for standard analytics
- **Memory Efficiency**: < 2GB RAM per container instance  
- **Cache Hit Rate**: > 80% for frequently accessed data
- **System Availability**: 99.9% uptime with automated failover
- **Scalability**: Supports 100+ concurrent users

## 🎯 Usage Examples

### Natural Language Queries
```bash
# Complex Analytics
"Analyze sales trends, detect anomalies, and create forecasts with visualizations"

# Multi-step Processing
"Query the database for customer data, analyze retention patterns, and generate a dashboard"

# Context-Aware Queries
"Based on our previous analysis, show me the regional breakdown"

# MCP-Enhanced Queries
"Search AWS documentation for Athena best practices and apply them to our data warehouse"
```

### API Usage
```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: user-session-123" \
  -d '{"query": "Analyze sales performance with anomaly detection"}'
```

## 📚 Documentation

### Core Documentation
- � [Usenr Guide](docs/USER_GUIDE.md) - End-user documentation
- 🚀 [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production deployment
- 🔧 [Technical Guide](docs/TECHNICAL_GUIDE.md) - Architecture deep-dive
- 💰 [Cost Breakdown](docs/AWS_COST_BREAKDOWN.md) - AWS cost analysis

### Development Guides
- 🛠️ [AgentCore Development](.kiro/steering/agentcore-development.md) - Development patterns
- 🔗 [MCP Integration](.kiro/steering/mcp-integration.md) - MCP tool integration
- 🏗️ [Technical Architecture](.kiro/steering/technical-architecture.md) - System design
- 📋 [Project Status](docs/TODO.md) - Current status and roadmap

### Development with Kiro IDE

This project is optimized for development with **Kiro IDE**. Kiro provides:
- **Autonomous Development**: Let Kiro handle infrastructure and deployment
- **Context-Aware Assistance**: Understands your entire codebase and steering documents
- **Intelligent Code Generation**: Generate LangGraph workflows and MCP integrations
- **Seamless AWS Integration**: Built-in support for Bedrock AgentCore

**Quick Kiro Commands:**
```bash
# Deploy infrastructure with new components
"Deploy the Terraform infrastructure including the new gateway and identity components"

# Test MCP integration
"Test all MCP tools and verify they're working correctly"

# Update agent with new features
"Update the agent to use the latest LangGraph workflow with MCP enhancement"

# Monitor deployment
"Check the health of all deployed components and show metrics"
```

See the [Kiro Usage Guide](docs/KIRO_USAGE_GUIDE.md) for comprehensive instructions.

## 🧪 Testing & Evaluation

### Comprehensive Evaluation Suite
```bash
# Run complete evaluation suite
./scripts/run_evaluation.sh

# Run specific test categories
python3 scripts/evaluation_suite.py

# View evaluation results
cat evaluation_reports/evaluation_report_*.json
```

### Test Categories
- **Infrastructure**: Health checks for all AWS components (GUI, Lambda, RDS, Redis, ECS)
- **Functional**: Core analytics capabilities and accuracy testing
- **Performance**: Response time, throughput, and concurrent user testing
- **Security**: Authentication, authorization, and data protection validation
- **Integration**: Gateway connectivity and external system integration

### Individual Tests
```bash
# Unit tests
python -m pytest agent/tests/

# MCP integration tests  
python test_mcp_simple.py

# End-to-end workflow tests
python test_langgraph_workflow.py

# Load testing
python scripts/load_test.py
```

### Evaluation Metrics
- **Success Rate Target**: >90% for production readiness
- **Response Time**: <5 seconds (95th percentile)
- **Throughput**: >25 requests/second
- **Availability**: >99.5% uptime
- **Security**: Zero critical vulnerabilities

## 🔐 Security

- **🔒 End-to-end Encryption**: All data encrypted at rest and in transit
- **🎫 Identity Management**: Cognito user pools with MFA support
- **🛡️ IAM Integration**: Least-privilege access with role-based permissions
- **📝 Audit Logging**: Comprehensive CloudWatch logging and monitoring
- **🔑 Secrets Management**: AWS Secrets Manager for credentials

## 🚀 Advanced Features

1. **LangGraph Workflows**: 7-node processing pipeline with intelligent task decomposition
2. **MCP Tool Integration**: 9 external tools for enhanced capabilities
3. **Memory-Driven Insights**: Persistent conversation context with user learning
4. **Real-Time Processing**: Sub-5 second response times for complex analytics
5. **Enterprise Security**: AWS-native security with comprehensive audit logging
6. **Auto-Scaling**: Handles varying workloads with ECS Fargate auto-scaling

## 🛠️ Development Workflow

### With Kiro IDE (Recommended)
```bash
# Open in Kiro
kiro open .

# Use context-aware development with steering documents
"Update #File agent/main.py following the AgentCore development patterns"
"Deploy #Folder infrastructure/ with the new gateway components"
"Test the MCP integration using #Terminal and show results"
```

### Traditional Development
```bash
# Test agent locally
./scripts/test-agent.sh

# Deploy infrastructure
cd infrastructure
terraform init && terraform apply

# Build and push containers
./scripts/build-and-push.sh $(aws sts get-caller-identity --query Account --output text) us-west-2
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the [AgentCore Development Guide](.kiro/steering/agentcore-development.md)
4. Test thoroughly with MCP integration
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Akshay Ramesh**
- GitHub: [@Ak-9647](https://github.com/Ak-9647)
- Project: [aws_demo](https://github.com/Ak-9647/aws_demo)

## 🙏 Acknowledgments

- Built with Amazon Bedrock AgentCore v4.1 capabilities
- Powered by LangGraph for intelligent agent workflows
- Enhanced with Model Context Protocol (MCP) integration
- Optimized for Kiro IDE development experience
- Follows AWS Well-Architected Framework principles

---

**Built with ❤️ for Amazon Bedrock AgentCore**