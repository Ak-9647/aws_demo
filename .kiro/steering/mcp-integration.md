# MCP Integration Guide

## Model Context Protocol (MCP) Integration

The Production Analytics Agent v4.1 leverages Model Context Protocol (MCP) to extend its capabilities through external tools and services, providing enhanced data access, processing, and analysis capabilities.

### MCP Architecture Overview

#### Core Components
- **MCP Server Manager**: Manages connections to 9 specialized MCP servers
- **Tool Selection Engine**: Intelligently selects relevant tools based on query content
- **Workflow Integration**: Seamlessly integrates MCP tools into LangGraph workflows
- **Error Handling**: Graceful fallback mechanisms when MCP tools are unavailable

#### MCP Tool Ecosystem

##### 1. AWS Documentation Server
- **Purpose**: Automatic AWS service documentation and best practices lookup
- **Use Cases**: 
  - Query AWS service configurations and limitations
  - Retrieve best practices for analytics services
  - Get troubleshooting guidance for AWS integrations
- **Integration**: Triggered when queries mention AWS services (S3, Athena, Redshift, etc.)

##### 2. PostgreSQL Database Server
- **Purpose**: Direct database querying and schema analysis
- **Use Cases**:
  - Execute SQL queries on analytics databases
  - Retrieve table schemas and metadata
  - Perform database performance analysis
- **Security**: Uses secure connection strings stored in AWS Secrets Manager

##### 3. Filesystem Operations Server
- **Purpose**: Secure file system access for data operations
- **Use Cases**:
  - Read CSV, JSON, and Parquet files
  - Write analysis results and exports
  - Manage temporary data processing files
- **Security**: Restricted to approved directories (/tmp, /data)

##### 4. Advanced Analytics Server
- **Purpose**: Specialized statistical analysis and ML operations
- **Use Cases**:
  - Advanced statistical computations
  - Anomaly detection algorithms
  - Time series forecasting
  - Dataset profiling and quality assessment
- **Integration**: Automatically invoked for complex analytical queries

##### 5. Visualization Server
- **Purpose**: Enhanced chart creation and dashboard generation
- **Use Cases**:
  - Create interactive visualizations
  - Generate multi-chart dashboards
  - Export visualizations in multiple formats
  - Apply advanced styling and themes

##### 6. AWS Analytics Services Server
- **Purpose**: Integration with AWS analytics ecosystem
- **Use Cases**:
  - Execute Athena queries on data lakes
  - Browse AWS Glue data catalogs
  - Manage QuickSight dashboards
  - Optimize data warehouse operations

##### 7. Redshift Data Warehouse Server
- **Purpose**: Large-scale data warehouse operations
- **Use Cases**:
  - Execute complex analytical queries
  - Perform data warehouse optimization
  - Manage large dataset operations
  - Generate performance reports

##### 8. Web Search Server
- **Purpose**: Current information retrieval and market research
- **Use Cases**:
  - Retrieve latest market trends
  - Validate external data sources
  - Gather competitive intelligence
  - Access real-time information
- **Security**: Uses Brave Search API with rate limiting

##### 9. GitHub Integration Server
- **Purpose**: Code repository access and analysis
- **Use Cases**:
  - Access analytics code repositories
  - Retrieve configuration files
  - Analyze code patterns and best practices
  - Manage version control integration

### MCP Workflow Integration

#### Query Processing Pipeline
```python
# MCP Enhancement Node in LangGraph Workflow
def _enhance_with_mcp(self, state: AnalyticsState) -> AnalyticsState:
    query = state['query']
    intent = state['intent']
    
    # Intelligent tool selection based on query content
    relevant_tools = self.mcp_tools.get_relevant_tools_for_query(query, intent)
    
    # Execute relevant MCP tools
    for tool_info in relevant_tools:
        if tool_info['relevance'] == 'high':
            result = await self.mcp_tools.call_mcp_tool(
                tool_info['tool'], 
                tool_info['function'], 
                parameters
            )
            
            # Integrate results into workflow state
            state['mcp_enhancements'].append(result)
    
    return state
```

#### Tool Selection Logic
- **Keyword Analysis**: Scans query for relevant terms (AWS, SQL, chart, etc.)
- **Intent Recognition**: Uses query intent to determine appropriate tools
- **Context Awareness**: Considers conversation history and user preferences
- **Relevance Scoring**: Ranks tools by relevance (high, medium, low)

#### Error Handling Strategy
- **Graceful Degradation**: Continues processing even if MCP tools fail
- **Fallback Mechanisms**: Uses built-in capabilities when external tools unavailable
- **Retry Logic**: Automatic retry for transient failures
- **Error Logging**: Comprehensive logging for debugging and monitoring

### Configuration Management

#### MCP Server Configuration
```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": ["search_aws_docs", "get_aws_service_info"]
    }
  }
}
```

#### Environment Variables
```bash
# MCP Configuration
MCP_CONFIG_PATH=.kiro/settings/mcp.json
ALLOWED_DIRECTORIES=/tmp,/data
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db
REDSHIFT_CONNECTION_STRING=redshift://user:pass@host:5439/db
BRAVE_API_KEY=your-brave-search-api-key
GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token
```

### Security Considerations

#### Access Control
- **Tool Permissions**: Each MCP tool has specific permission scopes
- **Auto-Approval Lists**: Pre-approved functions for seamless operation
- **Rate Limiting**: Prevents abuse of external APIs and services
- **Audit Logging**: All MCP tool invocations are logged for security

#### Data Protection
- **Secure Connections**: All MCP communications use encrypted channels
- **Credential Management**: API keys and tokens stored in AWS Secrets Manager
- **Data Isolation**: MCP tools operate in isolated environments
- **Privacy Controls**: User data protection across all external integrations

### Performance Optimization

#### Caching Strategy
- **Tool Result Caching**: Cache frequently used MCP tool results
- **Connection Pooling**: Reuse connections to external services
- **Parallel Execution**: Execute multiple MCP tools simultaneously
- **Timeout Management**: Prevent slow tools from blocking workflow

#### Monitoring & Metrics
- **Tool Performance**: Track execution time and success rates
- **Usage Analytics**: Monitor which tools are most frequently used
- **Error Tracking**: Detailed logging of MCP tool failures
- **Cost Monitoring**: Track usage of paid external services

### Development Guidelines

#### Adding New MCP Tools
1. **Tool Registration**: Add server configuration to mcp.json
2. **Integration Logic**: Implement tool selection logic in workflow
3. **Error Handling**: Add appropriate fallback mechanisms
4. **Testing**: Create comprehensive test cases for new tools
5. **Documentation**: Update user guides and technical documentation

#### Best Practices
- **Minimal Dependencies**: Keep MCP tool dependencies lightweight
- **Idempotent Operations**: Ensure MCP tool calls can be safely retried
- **Resource Management**: Properly clean up resources after tool execution
- **Version Management**: Pin MCP server versions for stability

### Testing Strategy

#### Unit Testing
- **Tool Selection**: Test intelligent tool selection algorithms
- **Error Handling**: Verify graceful degradation mechanisms
- **Configuration**: Validate MCP server configuration parsing

#### Integration Testing
- **End-to-End Workflows**: Test complete workflows with MCP integration
- **External Service Mocking**: Mock external services for reliable testing
- **Performance Testing**: Validate performance under various load conditions

#### Production Monitoring
- **Health Checks**: Regular health checks for all MCP servers
- **Performance Monitoring**: Track tool execution times and success rates
- **Alert Configuration**: Automated alerts for MCP tool failures

This MCP integration provides the analytics agent with powerful extensibility, allowing it to leverage external tools and services while maintaining security, performance, and reliability standards.