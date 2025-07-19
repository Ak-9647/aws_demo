# Project Structure

## Directory Organization

```
production-analytics-agent/
├── infrastructure/          # Terraform Infrastructure-as-Code
│   ├── vpc.tf              # VPC and networking configuration
│   ├── iam.tf              # IAM roles and policies
│   ├── ecr.tf              # Elastic Container Registry
│   └── ecs.tf              # ECS Fargate configuration
├── agent/                  # Core AI agent implementation
│   ├── main.py             # Agent entry point and LangGraph workflow
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Agent container definition
├── gui/                    # Streamlit web interface
│   ├── app.py              # Streamlit application
│   └── Dockerfile          # GUI container definition
└── .github/                # CI/CD pipeline
    └── workflows/
        └── deploy.yml      # GitHub Actions deployment
```

## Component Responsibilities

### Infrastructure (`/infrastructure/`)
- **vpc.tf**: Network configuration, subnets, security groups
- **iam.tf**: Least-privilege IAM roles for all components
- **ecr.tf**: Container registry for Docker images
- **ecs.tf**: ECS Fargate service definitions

### Agent (`/agent/`)
- **main.py**: LangGraph workflow, AgentCore integration, tool orchestration
- **requirements.txt**: Python dependencies (boto3, pandas, matplotlib, etc.)
- **Dockerfile**: Multi-stage container build for production deployment

### GUI (`/gui/`)
- **app.py**: Streamlit interface for user queries and result visualization
- **Dockerfile**: Lightweight container for web interface

### CI/CD (`/.github/workflows/`)
- **deploy.yml**: Automated build, test, and deployment pipeline

## Architecture Patterns

### Modular Design
- Each component (infrastructure, agent, GUI) is independently deployable
- Clear separation of concerns between data processing, UI, and infrastructure
- Standardized interfaces between AgentCore components

### Security-First Approach
- All components use IAM least-privilege principles
- Secure communication between services
- Proper credential management and rotation

### Observability Integration
- CloudWatch logging and metrics throughout
- Performance monitoring and alerting
- Usage tracking and cost optimization

## Development Guidelines
- Use Docker for consistent development environments
- Terraform for all infrastructure changes
- Follow AWS Well-Architected Framework principles
- Implement proper error handling and logging
- Maintain clear documentation for each component