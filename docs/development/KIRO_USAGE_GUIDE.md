# Kiro IDE Usage Guide for Analytics Agent Development

**Author**: Akshay Ramesh  
**License**: MIT

## Table of Contents
1. [Introduction to Kiro](#introduction-to-kiro)
2. [Setting Up Your Workspace](#setting-up-your-workspace)
3. [Kiro Features for This Project](#kiro-features-for-this-project)
4. [Development Workflow with Kiro](#development-workflow-with-kiro)
5. [Advanced Kiro Techniques](#advanced-kiro-techniques)
6. [Troubleshooting with Kiro](#troubleshooting-with-kiro)

## Introduction to Kiro

Kiro is an AI-powered IDE that enhances developer productivity through intelligent code assistance, autonomous development modes, and seamless integration with your development workflow.

### Key Benefits for This Project
- **Autonomous Infrastructure**: Let Kiro manage Terraform deployments
- **Intelligent Code Generation**: Generate LangGraph workflows and AWS integrations
- **Context-Aware Assistance**: Kiro understands your entire codebase
- **Seamless AWS Integration**: Built-in support for AWS services

## Setting Up Your Workspace

### 1. Workspace Configuration
```bash
# Initialize Kiro workspace
kiro init production-analytics-agent

# Configure steering files
mkdir -p .kiro/steering
```

### 2. Steering Files Setup
Create steering files to guide Kiro's behavior:

#### `.kiro/steering/tech.md`
```markdown
# Technology Stack
- Runtime: Python 3.13
- Agent Framework: LangGraph
- AWS Services: Bedrock AgentCore, ECS, ECR, S3
- Infrastructure: Terraform
- Frontend: Streamlit
```

#### `.kiro/steering/structure.md`
```markdown
# Project Structure
- /infrastructure: Terraform IaC
- /agent: LangGraph agent code
- /gui: Streamlit interface
- /docs: Documentation
```

#### `.kiro/steering/product.md`
```markdown
# Product Requirements
- Natural language analytics queries
- Secure AWS deployment
- Scalable architecture
- Production-ready monitoring
```

### 3. Context Configuration
```bash
# Add files to Kiro context
#File infrastructure/
#Folder agent/
#Codebase
```

## Kiro Features for This Project

### 1. Autopilot Mode
Enable autonomous development for routine tasks:

```bash
# Enable autopilot for infrastructure changes
kiro autopilot enable --scope infrastructure/

# Let Kiro handle Terraform updates
"Update the VPC configuration to add additional subnets"
```

### 2. Context Management
Leverage Kiro's context awareness:

```bash
# Reference specific files
"Update #File agent/main.py to add error handling"

# Work with folders
"Optimize all files in #Folder infrastructure/"

# Use codebase context
"Analyze #Codebase for security vulnerabilities"
```

### 3. Problem Detection
Kiro automatically identifies issues:

```bash
# View current problems
#Problems

# Get terminal output
#Terminal

# Check git status
#Git Diff
```

## Development Workflow with Kiro

### Phase 1: Infrastructure Development
```bash
# 1. Ask Kiro to create infrastructure
"Create Terraform files for AWS VPC, ECR, S3, and IAM roles for AgentCore"

# 2. Review and apply
kiro review infrastructure/
terraform apply

# 3. Let Kiro handle outputs
"Extract Terraform outputs and save to environment variables"
```

### Phase 2: Agent Development
```bash
# 1. Generate LangGraph agent
"Create a LangGraph agent in #File agent/main.py that processes analytics queries"

# 2. Add AWS integrations
"Add boto3 integration to connect with S3 and Bedrock services"

# 3. Create Docker configuration
"Generate a production-ready Dockerfile for the agent"
```

### Phase 3: GUI Development
```bash
# 1. Create Streamlit interface
"Build a Streamlit app in #Folder gui/ that connects to the AgentCore endpoint"

# 2. Add visualization features
"Add plotly charts and data visualization to the GUI"

# 3. Configure deployment
"Create Docker configuration for the Streamlit app"
```

### Phase 4: Testing & Deployment
```bash
# 1. Generate test scripts
"Create test scripts in #Folder scripts/ for local development"

# 2. Build and deploy
"Build Docker images and push to ECR using the build script"

# 3. Monitor deployment
"Check #Terminal for deployment status and #Problems for any issues"
```

## Advanced Kiro Techniques

### 1. Specs for Complex Features
Create structured development plans:

```bash
# Create a spec for analytics features
kiro spec create analytics-enhancement

# Define requirements in the spec
- Natural language query processing
- Data visualization generation
- Real-time analytics dashboard
- Performance optimization
```

### 2. Hooks for Automation
Set up automated workflows:

```bash
# Create deployment hook
kiro hook create deploy-on-save
# Trigger: File save in infrastructure/
# Action: Run terraform plan and apply

# Create testing hook
kiro hook create test-on-commit
# Trigger: Git commit
# Action: Run test suite and build containers
```

### 3. MCP Integration
Configure Model Context Protocol for external tools:

```json
// .kiro/settings/mcp.json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "disabled": false,
      "autoApprove": ["get_documentation", "search_docs"]
    },
    "terraform-helper": {
      "command": "uvx",
      "args": ["terraform-mcp-server@latest"],
      "disabled": false,
      "autoApprove": ["validate", "plan"]
    }
  }
}
```

### 4. Context Optimization
Maximize Kiro's understanding:

```bash
# Include relevant documentation
#[[file:docs/TECHNICAL_GUIDE.md]]

# Reference API specifications
#[[file:api/openapi.yaml]]

# Include configuration files
#[[file:infrastructure/variables.tf]]
```

## Kiro Commands for This Project

### Infrastructure Management
```bash
# Deploy infrastructure
"Deploy the Terraform infrastructure and capture outputs"

# Update configuration
"Update #File infrastructure/variables.tf with new region settings"

# Scale resources
"Modify the ECS configuration to support auto-scaling"
```

### Code Development
```bash
# Generate agent logic
"Create a LangGraph workflow that handles data analysis requests"

# Add error handling
"Add comprehensive error handling to #File agent/main.py"

# Optimize performance
"Review #Codebase and suggest performance optimizations"
```

### Testing & Debugging
```bash
# Run tests
"Execute the test suite and report results"

# Debug issues
"Analyze #Problems and suggest fixes"

# Check deployment
"Verify the deployment status using #Terminal output"
```

### Documentation
```bash
# Generate docs
"Create API documentation for the agent endpoints"

# Update README
"Update #File README.md with deployment instructions"

# Create guides
"Generate user guide for the Streamlit interface"
```

## Troubleshooting with Kiro

### Common Issues and Kiro Solutions

#### 1. Terraform Errors
```bash
# Problem: Terraform state issues
"Fix the Terraform state conflict in #File infrastructure/"

# Problem: Resource dependencies
"Analyze #Codebase and fix resource dependency issues"
```

#### 2. Docker Build Failures
```bash
# Problem: Container build errors
"Debug the Docker build failure in #File agent/Dockerfile"

# Problem: Dependency conflicts
"Resolve Python dependency conflicts in #File agent/requirements.txt"
```

#### 3. AWS Permission Issues
```bash
# Problem: IAM permission errors
"Review and fix IAM policies in #File infrastructure/iam.tf"

# Problem: VPC connectivity
"Debug VPC configuration issues in #File infrastructure/vpc.tf"
```

#### 4. Agent Runtime Errors
```bash
# Problem: LangGraph workflow issues
"Debug the agent workflow in #File agent/main.py using #Terminal logs"

# Problem: Bedrock integration
"Fix Bedrock API integration issues in the agent code"
```

### Kiro Debugging Workflow
1. **Identify Issue**: Use `#Problems` to see current issues
2. **Gather Context**: Check `#Terminal` and `#Git Diff`
3. **Ask Kiro**: Describe the problem with relevant context
4. **Apply Fix**: Let Kiro suggest and implement solutions
5. **Verify**: Test the fix and monitor results

## Best Practices with Kiro

### 1. Effective Prompting
```bash
# ✅ Good: Specific with context
"Update #File agent/main.py to add retry logic for Bedrock API calls"

# ❌ Poor: Vague request
"Fix the agent"
```

### 2. Context Management
```bash
# ✅ Good: Include relevant files
"Optimize the deployment process using #File scripts/build-and-push.sh and #Folder infrastructure/"

# ❌ Poor: No context
"Optimize deployment"
```

### 3. Iterative Development
```bash
# Step 1: Basic implementation
"Create basic LangGraph agent structure"

# Step 2: Add features
"Add data processing capabilities to the existing agent"

# Step 3: Optimize
"Optimize the agent for production deployment"
```

### 4. Documentation Integration
```bash
# Reference documentation
"Following the patterns in #File docs/TECHNICAL_GUIDE.md, add monitoring to the agent"

# Update documentation
"Update #File docs/ with the new features added to the agent"
```

## Kiro Shortcuts and Tips

### Quick Commands
- `#File filename` - Reference specific file
- `#Folder path/` - Reference entire folder
- `#Codebase` - Analyze entire project
- `#Problems` - View current issues
- `#Terminal` - Check terminal output
- `#Git Diff` - See recent changes

### Productivity Tips
1. **Use Autopilot** for routine tasks like formatting and testing
2. **Create Specs** for complex features requiring multiple steps
3. **Set up Hooks** for automated workflows
4. **Leverage MCP** for external tool integration
5. **Maintain Context** by referencing relevant files and folders

### Advanced Features
- **Steering Rules**: Guide Kiro's behavior with project-specific instructions
- **Multi-file Operations**: Work across multiple files simultaneously
- **Parallel Execution**: Let Kiro handle multiple tasks concurrently
- **Context Preservation**: Kiro remembers your project structure and preferences

## Integration with AWS Development

### AWS-Specific Kiro Usage
```bash
# Deploy to AWS
"Deploy #Folder infrastructure/ to AWS and configure AgentCore"

# Monitor AWS resources
"Check the status of AWS resources created by Terraform"

# Debug AWS issues
"Analyze CloudWatch logs for the deployed agent"

# Optimize AWS costs
"Review #Codebase and suggest AWS cost optimizations"
```

### Bedrock AgentCore Integration
```bash
# Configure AgentCore
"Set up Bedrock AgentCore deployment using the ECR image"

# Test agent
"Create test cases for the AgentCore endpoint"

# Monitor performance
"Add CloudWatch monitoring to the AgentCore deployment"
```

---

This guide helps you leverage Kiro's full potential for developing and deploying the Production Analytics Agent. Remember that Kiro learns from your project context, so the more you use it with specific references to your files and folders, the better it becomes at assisting you.

For more Kiro features, use the command palette (Cmd/Ctrl+Shift+P) and search for "Kiro" commands.