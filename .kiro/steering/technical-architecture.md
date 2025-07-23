# Technical Architecture Guide

## System Architecture Overview

The Production Analytics Agent v4.1 is built on a sophisticated multi-layer architecture combining Amazon Bedrock AgentCore, LangGraph workflows, and MCP tool integration.

### Architecture Layers

#### 1. Presentation Layer
- **Streamlit GUI**: Web interface with real-time visualization and conversation history
- **REST API**: HTTP endpoints for programmatic access and integration
- **Authentication**: Cognito-based OAuth 2.0 with JWT tokens

#### 2. Intelligence Layer
- **LangGraph Workflow Engine**: Multi-step query processing with intelligent task decomposition
- **MCP Enhancement Node**: Automatic query enrichment using relevant external tools
- **Context Manager**: Session-based conversation memory and user preference learning
- **Query Analyzer**: Intent recognition and complexity assessment

#### 3. Processing Layer
- **Analytics Engine**: Core data processing with pandas, numpy, and statistical libraries
- **Visualization Engine**: Chart generation with matplotlib, plotly, and seaborn
- **Memory Manager**: DynamoDB and Redis integration for persistent and cached storage
- **AgentCore Integration**: Bedrock agent runtime with built-in tools

#### 4. Integration Layer
- **MCP Tools**: 9 specialized tools for external data access and processing
- **Gateway Manager**: Secure connections to REST APIs, databases, and file systems
- **Identity Provider**: Role-based access control with Cognito user pools
- **Observability**: CloudWatch metrics, logs, and custom dashboards

#### 5. Data Layer
- **Analytics Database**: Aurora PostgreSQL for structured data storage
- **Memory Systems**: DynamoDB for conversations, Redis for session caching
- **Data Lake**: S3 buckets for raw data, processed results, and exports
- **External Sources**: Secure gateway connections to third-party APIs and databases

### Key Technical Components

#### LangGraph Workflow
```python
# Workflow nodes in processing order:
1. query_analyzer      # Intent recognition and complexity assessment
2. context_retriever   # Historical context and user preferences
3. task_decomposer     # Break complex queries into manageable tasks
4. mcp_enhancer        # Enhance with relevant MCP tools
5. data_processor      # Execute analytics using core engine
6. result_synthesizer  # Combine results and generate insights
7. memory_updater      # Store conversation and update preferences
```

#### MCP Tool Integration
- **Tool Selection**: Intelligent selection based on query content and context
- **Parallel Execution**: Multiple MCP tools can be invoked simultaneously
- **Error Handling**: Graceful fallback when MCP tools are unavailable
- **Result Enhancement**: MCP results integrated into final response

#### Memory Architecture
- **Short-term Memory**: Redis cache for active session data (24-hour TTL)
- **Long-term Memory**: DynamoDB for conversation history (90-day TTL)
- **User Preferences**: Learning system that adapts to user query patterns
- **Context Synthesis**: Intelligent context extraction from conversation history

### Infrastructure Components

#### Container Architecture
```dockerfile
# Multi-stage Docker build
FROM python:3.13-slim
# Core dependencies: boto3, pandas, matplotlib, plotly, langgraph
# MCP integration: uvx for tool execution
# Memory systems: redis, boto3 for DynamoDB
```

#### AWS Services Integration
- **ECS Fargate**: Containerized agent execution with auto-scaling
- **Application Load Balancer**: Traffic distribution and health checks
- **VPC**: Secure networking with public/private subnets
- **NAT Gateways**: Secure outbound internet access for private subnets
- **Security Groups**: Fine-grained network access control

#### Database Systems
- **Aurora PostgreSQL**: Primary analytics database with read replicas
- **DynamoDB**: Conversation history with global secondary indexes
- **ElastiCache Redis**: Session caching with cluster mode
- **S3**: Data lake with versioning and lifecycle policies

### Security Architecture

#### Authentication & Authorization
- **Cognito User Pools**: User registration and authentication
- **Identity Pools**: Federated identity management
- **IAM Roles**: Least-privilege access with role-based permissions
- **JWT Tokens**: Secure session management with refresh tokens

#### Data Security
- **Encryption at Rest**: All data encrypted using AWS KMS
- **Encryption in Transit**: TLS 1.2+ for all communications
- **Secrets Management**: AWS Secrets Manager for credentials
- **Network Security**: VPC endpoints and security groups

#### Access Control
- **Role-based Access**: Admin and user roles with different permissions
- **Resource-level Security**: Fine-grained access to specific data sources
- **Audit Logging**: Comprehensive logging of all user actions
- **MFA Support**: Multi-factor authentication for admin users

### Performance Optimization

#### Caching Strategy
- **Query Result Caching**: Redis cache for frequently accessed results
- **Connection Pooling**: Database connection reuse for improved performance
- **CDN Integration**: CloudFront for static asset delivery
- **Lazy Loading**: On-demand loading of large datasets

#### Scalability Features
- **Auto-scaling**: ECS service scaling based on CPU and memory metrics
- **Load Balancing**: Application Load Balancer with health checks
- **Database Scaling**: Aurora read replicas for read-heavy workloads
- **Cache Scaling**: Redis cluster mode for high availability

### Monitoring & Observability

#### Metrics & Alerting
- **Custom CloudWatch Metrics**: Query processing time, success rates, error counts
- **Application Metrics**: Memory usage, database connections, cache hit rates
- **Business Metrics**: User engagement, query complexity, feature usage
- **Automated Alerting**: SNS notifications for critical issues

#### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **Log Aggregation**: CloudWatch Logs with custom log groups
- **Error Tracking**: Detailed error logging with stack traces
- **Performance Logging**: Query execution times and resource usage

### Development & Deployment

#### CI/CD Pipeline
- **GitHub Actions**: Automated build, test, and deployment
- **Docker Registry**: ECR for container image storage
- **Infrastructure as Code**: Terraform for all AWS resources
- **Environment Management**: Separate dev, staging, and production environments

#### Testing Strategy
- **Unit Tests**: Core analytics engine and utility functions
- **Integration Tests**: MCP tool integration and database connectivity
- **End-to-end Tests**: Complete workflow testing with real data
- **Performance Tests**: Load testing and scalability validation

### Configuration Management

#### Environment Variables
```bash
# Core Configuration
AWS_REGION=us-west-2
AGENTCORE_AGENT_ID=your-agent-id
CONVERSATION_TABLE=production-analytics-agent-conversation-history
REDIS_ENDPOINT=production-analytics-agent-redis.cache.amazonaws.com

# MCP Configuration
MCP_CONFIG_PATH=.kiro/settings/mcp.json
ALLOWED_DIRECTORIES=/tmp,/data

# Database Configuration
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db
REDSHIFT_CONNECTION_STRING=redshift://user:pass@host:5439/db
```

#### Feature Flags
- **MCP_ENABLED**: Enable/disable MCP tool integration
- **MEMORY_ENABLED**: Enable/disable conversation memory
- **ADVANCED_ANALYTICS**: Enable/disable ML-based features
- **DEBUG_MODE**: Enable detailed logging and debugging

This architecture provides a robust, scalable, and secure foundation for advanced analytics processing with intelligent query handling and comprehensive data integration capabilities.