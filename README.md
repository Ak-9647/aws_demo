# Production Analytics Agent

A secure, scalable AI agent system built on Amazon Bedrock AgentCore that processes natural language analytics queries and generates insights from data sources.

**Author**: Akshay Ramesh  
**License**: MIT

## Architecture

```
production-analytics-agent/
├── infrastructure/          # Terraform Infrastructure-as-Code
├── agent/                  # Core AI agent implementation
├── gui/                    # Streamlit web interface
└── scripts/                # Deployment and testing scripts
```

## Quick Start

### 1. Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform installed
- Docker installed
- Python 3.13+

### 2. Deploy Infrastructure

```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

### 3. Build and Push Images

```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build and push containers
./scripts/build-and-push.sh $AWS_ACCOUNT_ID us-west-2
```

### 4. Deploy to AgentCore

1. Go to AWS Console → Bedrock → AgentCore → Agent Runtime
2. Click "Host Agent"
3. Configure:
   - **Image**: Use ECR URI from Terraform outputs
   - **IAM Role**: Use AgentCore Runtime role ARN from outputs
   - **CPU/Memory**: Set as needed
4. Deploy and wait for healthy status

### 5. Create Endpoint

1. In AgentCore console, create an endpoint for your agent
2. Test in Agent Sandbox
3. Use endpoint URL in GUI configuration

## Local Development

### Test Agent Locally
```bash
./scripts/test-agent.sh
```

### Run GUI Locally
```bash
cd gui
pip install -r requirements.txt
streamlit run app.py
```

## Key Features

- **Natural Language Analytics**: Plain-language queries
- **Secure Processing**: IAM least-privilege, encrypted storage
- **Scalable Architecture**: ECS Fargate, auto-scaling
- **Observability**: CloudWatch integration
- **Web Interface**: User-friendly Streamlit GUI

## Technology Stack

- **Runtime**: Python 3.13
- **Agent Framework**: LangGraph
- **AWS Services**: Bedrock AgentCore, ECS Fargate, ECR, S3
- **Infrastructure**: Terraform
- **Frontend**: Streamlit
- **Containerization**: Docker

## Security

- IAM least-privilege roles
- Encrypted S3 storage
- VPC with private subnets
- Container image scanning
- Secure credential management

## Monitoring

- CloudWatch logs and metrics
- AgentCore observability dashboard
- Container health checks
- Performance monitoring

## 📚 Documentation

### Quick Start
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [User Guide](docs/USER_GUIDE.md) - How to use the analytics agent
- [Technical Guide](docs/TECHNICAL_GUIDE.md) - Architecture and technical details
- [Kiro Usage Guide](docs/KIRO_USAGE_GUIDE.md) - Maximize productivity with Kiro IDE

### Development with Kiro IDE

This project is optimized for development with **Kiro IDE**. Kiro provides:
- **Autonomous Development**: Let Kiro handle infrastructure and deployment
- **Context-Aware Assistance**: Understands your entire codebase
- **Intelligent Code Generation**: Generate LangGraph workflows and AWS integrations
- **Seamless AWS Integration**: Built-in support for Bedrock AgentCore

**Quick Kiro Commands:**
```bash
# Deploy infrastructure
"Deploy the Terraform infrastructure and capture outputs"

# Build containers
"Build and push Docker containers to ECR"

# Create agent
"Generate a LangGraph agent for analytics queries"

# Add monitoring
"Add CloudWatch monitoring to the deployment"
```

See the [Kiro Usage Guide](docs/KIRO_USAGE_GUIDE.md) for comprehensive instructions.

## 🎯 Usage Examples

### Natural Language Queries
```bash
# Sales Analysis
"Show monthly sales trends for Q4 2024"

# Customer Insights
"Analyze customer retention by segment"

# Performance Metrics
"Compare revenue across regions with growth rates"

# Predictive Analysis
"Forecast next quarter's sales based on current trends"
```

### API Usage
```bash
curl -X POST https://your-agentcore-endpoint/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze sales performance for last quarter"}'
```

## 🚀 Advanced Features

1. **LangGraph Workflows**: Sophisticated agent logic with state management
2. **Multi-Modal Analysis**: Text, charts, and data visualizations
3. **Real-Time Processing**: Fast response times for interactive exploration
4. **Enterprise Security**: AWS-native security with encryption and IAM
5. **Auto-Scaling**: Handles varying workloads automatically

## 🛠️ Development Workflow

### With Kiro IDE (Recommended)
```bash
# Open in Kiro
kiro open .

# Use context-aware development
"Update #File agent/main.py to add error handling"
"Deploy #Folder infrastructure/ to AWS"
"Test the agent using #Terminal output"
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
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Akshay Ramesh**
- GitHub: [@Ak-9647](https://github.com/Ak-9647)
- Project: [aws_demo](https://github.com/Ak-9647/aws_demo)

## 🙏 Acknowledgments

- Built with Amazon Bedrock AgentCore
- Powered by LangGraph for agent workflows
- Optimized for Kiro IDE development experience
- Follows AWS Well-Architected Framework principles