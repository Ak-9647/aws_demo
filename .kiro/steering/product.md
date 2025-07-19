# Product Overview

## Production-Grade Data Analytics AI Agent

A secure, scalable AI agent system built on Amazon Bedrock AgentCore that processes natural language analytics queries and generates insights from data sources.

### Core Capabilities
- **Natural Language Analytics**: Accepts plain-language queries like "Summarize sales by region for Q2 and plot trends"
- **Secure Data Processing**: Reads from S3 and integrated data sources with proper IAM controls
- **Code Execution**: Uses Bedrock AgentCore's sandboxed Python interpreter for pandas/matplotlib operations
- **Memory Management**: Maintains conversational context with short-term and long-term memory
- **Web Interface**: Streamlit GUI for user interactions and result visualization

### Key Components
- **AgentCore Runtime**: Dockerized agent execution environment
- **AgentCore Memory**: Managed conversational storage
- **AgentCore Gateway**: External tool and API integration
- **AgentCore Identity**: User authentication and authorization
- **AgentCore Observability**: CloudWatch telemetry and monitoring
- **Frontend GUI**: Streamlit web application

### Target Users
Data analysts, business users, and stakeholders who need to query and visualize data through natural language interactions.