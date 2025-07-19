# Technology Stack

## Core Technologies
- **Runtime**: Python 3.13
- **Agent Framework**: LangGraph for agent workflow orchestration
- **AWS SDK**: boto3 for AWS service integration
- **Containerization**: Docker with multi-stage builds
- **Infrastructure**: Terraform for Infrastructure-as-Code
- **Frontend**: Streamlit for web GUI
- **Container Registry**: Amazon ECR
- **Compute**: Amazon ECS Fargate

## Key Libraries & Frameworks
- **Data Processing**: pandas, matplotlib, numpy
- **Agent Logic**: LangGraph, boto3
- **Web Framework**: Streamlit
- **AWS Integration**: Amazon Bedrock AgentCore components

## Build System & Commands

### Docker Operations
```bash
# Build agent container
docker build -t analytics-agent ./agent/

# Build GUI container  
docker build -t analytics-gui ./gui/

# Run locally for development
docker run -p 8501:8501 analytics-gui
```

### Infrastructure Management
```bash
# Initialize Terraform
terraform init

# Plan infrastructure changes
terraform plan

# Apply infrastructure
terraform apply

# Destroy infrastructure
terraform destroy
```

### Development Workflow
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run agent locally (development)
python agent/main.py

# Run Streamlit GUI locally
streamlit run gui/app.py
```

## CI/CD Pipeline
- **Build**: GitHub Actions or shell scripts
- **Registry**: Amazon ECR for container images
- **Deployment**: Automated deployment to AgentCore Runtime and ECS Fargate
- **Monitoring**: CloudWatch integration for observability

## Security Requirements
- IAM least-privilege roles for all components
- MFA and budget alarms enabled
- User authentication via Cognito/JWT
- Secure credential management