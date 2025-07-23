# MCP Integration Guide

## Model Context Protocol (MCP) Integration

The Production Analytics Agent v4.1 leverages Model Context Protocol (MCP) to extend its capabilities through external tools and services, providing enhanced data access, processing, and analysis capabilities.

### What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI agents to securely call external tools through standardized interfaces. MCP allows the analytics agent to:

- Access external data sources and APIs
- Execute specialized analytics functions
- Generate visualizations and dashboards
- Query databases and data warehouses
- Retrieve documentation and best practices

### MCP Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  LangGraph      │     │  MCP Analytics  │     │  External MCP   │
│  Workflow       │────►│  Tools Module   │────►│  Servers        │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        ▲                       ▲
        │                        │                       │
        ▼                        │                       │
┌─────────────────┐             │                       │
│                 │             │                       │
│  Analytics      │─────────────┘                       │
│  Engine         │                                     │
│                 │                                     │
└─────────────────┘                                     │
        │                                               │
        ▼                                               │
┌─────────────────┐                                     │
│                 │                                     │
│  AgentCore      │─────────────────────────────────────┘
│  Gateways       │
│                 │
└─────────────────┘
```

### MCP Tool Ecosystem

The analytics agent integrates with 9 specialized MCP servers:

#### 1. AWS Documentation Server
- **Purpose**: Automatic AWS service documentation and best practices lookup
- **Use Cases**: 
  - Query AWS service configurations and limitations
  - Retrieve best practices for analytics services
  - Get troubleshooting guidance for AWS integrations
- **Integration**: Triggered when queries mention AWS services (S3, Athena, Redshift, etc.)

#### 2. PostgreSQL Database Server
- **Purpose**: Direct database querying and schema analysis
- **Use Cases**:
  - Execute SQL queries on analytics databases
  - Retrieve table schemas and metadata
  - Perform database performance analysis
- **Security**: Uses secure connection strings stored in AWS Secrets Manager

#### 3. Filesystem Operations Server
- **Purpose**: Secure file system access for data operations
- **Use Cases**:
  - Read CSV, JSON, and Parquet files
  - Write analysis results and exports
  - Manage temporary data processing files
- **Security**: Restricted to approved directories (/tmp, /data)

#### 4. Advanced Analytics Server
- **Purpose**: Specialized statistical analysis and ML operations
- **Use Cases**:
  - Advanced statistical computations
  - Anomaly detection algorithms
  - Time series forecasting
  - Dataset profiling and quality assessment
- **Integration**: Automatically invoked for complex analytical queries

#### 5. Visualization Server
- **Purpose**: Enhanced chart creation and dashboard generation
- **Use Cases**:
  - Create interactive visualizations
  - Generate multi-chart dashboards
  - Export visualizations in multiple formats
  - Apply advanced styling and themes

#### 6. AWS Analytics Services Server
- **Purpose**: Integration with AWS analytics ecosystem
- **Use Cases**:
  - Execute Athena queries on data lakes
  - Browse AWS Glue data catalogs
  - Manage QuickSight dashboards
  - Optimize data warehouse operations

#### 7. Redshift Data Warehouse Server
- **Purpose**: Large-scale data warehouse operations
- **Use Cases**:
  - Execute complex analytical queries
  - Perform data warehouse optimization
  - Manage large dataset operations
  - Generate performance reports

#### 8. Web Search Server
- **Purpose**: Current information retrieval and market research
- **Use Cases**:
  - Retrieve latest market trends
  - Validate external data sources
  - Gather competitive intelligence
  - Access real-time information
- **Security**: Uses Brave Search API with rate limiting

#### 9. GitHub Integration Server
- **Purpose**: Code repository access and analysis
- **Use Cases**:
  - Access analytics code repositories
  - Retrieve configuration files
  - Analyze code patterns and best practices
  - Manage version control integration

### MCP Workflow Integration

#### Query Processing Pipeline

The MCP integration is seamlessly embedded in the LangGraph workflow:

```python
# MCP Enhancement Node in LangGraph Workflow
def _enhance_with_mcp(self, state: AnalyticsState) -> AnalyticsState:
    query = state['query']
    intent = state['intent']
    
    # Intelligent tool selection based on query content
    relevant_tools = self.mcp_tools.get_relevant_tools_for_query(query, intent)
    
    # Execute relevant MCP tools in parallel
    mcp_results = []
    for tool_info in relevant_tools:
        if tool_info['relevance'] == 'high':
            result = await self.mcp_tools.call_mcp_tool(
                tool_info['tool'], 
                tool_info['function'], 
                tool_info['parameters']
            )
            mcp_results.append(result)
    
    # Integrate results into workflow state
    state['mcp_enhancements'] = mcp_results
    return state
```

#### Tool Selection Logic

The system uses intelligent algorithms to select relevant MCP tools:

1. **Keyword Analysis**: Scans query for relevant terms (AWS, SQL, chart, etc.)
2. **Intent Recognition**: Uses query intent to determine appropriate tools
3. **Context Awareness**: Considers conversation history and user preferences
4. **Relevance Scoring**: Ranks tools by relevance (high, medium, low)

Example tool selection:
```python
def get_relevant_tools_for_query(self, query: str, intent: dict) -> List[dict]:
    tools = []
    
    # AWS-related queries
    if any(service in query.lower() for service in ['s3', 'athena', 'redshift', 'glue']):
        tools.append({
            'tool': 'aws-docs',
            'function': 'search_aws_docs',
            'relevance': 'high',
            'parameters': {'query': query}
        })
    
    # Database queries
    if intent.get('type') == 'database_query' or 'sql' in query.lower():
        tools.append({
            'tool': 'postgres',
            'function': 'query_database',
            'relevance': 'high',
            'parameters': {'query': intent.get('sql_query')}
        })
    
    # Visualization requests
    if any(viz in query.lower() for viz in ['chart', 'graph', 'plot', 'dashboard']):
        tools.append({
            'tool': 'visualization',
            'function': 'create_chart',
            'relevance': 'medium',
            'parameters': {'chart_type': intent.get('visualization_type')}
        })
    
    return tools
```

### Configuration Management

#### MCP Server Configuration

The MCP servers are configured in `.kiro/settings/mcp.json`:

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
    },
    "postgres": {
      "command": "uvx", 
      "args": ["mcp-server-postgres@latest"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      },
      "disabled": false,
      "autoApprove": ["query_database", "get_schema", "list_tables"]
    },
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem@latest"],
      "env": {
        "ALLOWED_DIRECTORIES": "/tmp,/data"
      },
      "disabled": false,
      "autoApprove": ["read_file", "write_file", "list_directory"]
    },
    "data-analysis": {
      "command": "uvx",
      "args": ["mcp-server-data-analysis@latest"],
      "disabled": false,
      "autoApprove": ["analyze_dataset", "detect_anomalies", "forecast_timeseries"]
    },
    "visualization": {
      "command": "uvx",
      "args": ["mcp-server-visualization@latest"],
      "disabled": false,
      "autoApprove": ["create_chart", "generate_dashboard", "export_visualization"]
    },
    "aws-analytics": {
      "command": "uvx",
      "args": ["mcp-server-aws-analytics@latest"],
      "env": {
        "AWS_REGION": "us-west-2"
      },
      "disabled": false,
      "autoApprove": ["query_athena", "browse_glue_catalog", "manage_quicksight"]
    },
    "redshift": {
      "command": "uvx",
      "args": ["mcp-server-redshift@latest"],
      "env": {
        "REDSHIFT_CONNECTION_STRING": "${REDSHIFT_CONNECTION_STRING}"
      },
      "disabled": false,
      "autoApprove": ["execute_query", "optimize_warehouse", "generate_report"]
    },
    "web-search": {
      "command": "uvx",
      "args": ["mcp-server-brave-search@latest"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      },
      "disabled": false,
      "autoApprove": ["search_web", "get_market_trends", "validate_data_source"]
    },
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github@latest"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      },
      "disabled": false,
      "autoApprove": ["access_repository", "retrieve_config", "analyze_code"]
    }
  }
}
```

#### Environment Variables

```bash
# MCP Configuration
MCP_CONFIG_PATH=.kiro/settings/mcp.json
ALLOWED_DIRECTORIES=/tmp,/data

# Database Connections
POSTGRES_CONNECTION_STRING=postgresql://analytics_admin:password@production-analytics-agent-analytics-cluster.cluster-cxayeoogcra9.us-west-2.rds.amazonaws.com:5432/analytics
REDSHIFT_CONNECTION_STRING=redshift://user:pass@host:5439/db

# External API Keys
BRAVE_API_KEY=your-brave-search-api-key
GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token

# AWS Configuration
AWS_REGION=us-west-2
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
- **Tool Result Caching**: Cache frequently used MCP tool results in Redis
- **Connection Pooling**: Reuse connections to external services
- **Parallel Execution**: Execute multiple MCP tools simultaneously
- **Timeout Management**: Prevent slow tools from blocking workflow

#### Monitoring & Metrics
- **Tool Performance**: Track execution time and success rates
- **Usage Analytics**: Monitor which tools are most frequently used
- **Error Tracking**: Detailed logging of MCP tool failures
- **Cost Monitoring**: Track usage of paid external services

### Error Handling Strategy

#### Graceful Degradation
```python
async def call_mcp_tool_with_fallback(self, tool_name: str, function: str, parameters: dict):
    try:
        # Attempt MCP tool call
        result = await self.call_mcp_tool(tool_name, function, parameters)
        return result
    except MCPToolException as e:
        logger.warning(f"MCP tool {tool_name} failed: {e}")
        
        # Fallback to built-in capabilities
        if tool_name == 'postgres':
            return self.fallback_database_query(parameters)
        elif tool_name == 'visualization':
            return self.fallback_chart_generation(parameters)
        else:
            return {'error': f'Tool {tool_name} unavailable', 'fallback': True}
```

#### Retry Logic
- **Exponential Backoff**: Automatic retry for transient failures
- **Circuit Breaker**: Prevent cascading failures
- **Health Checks**: Regular health monitoring of MCP servers
- **Failover**: Switch to alternative tools when primary tools fail

### Testing Strategy

#### Unit Testing
```bash
# Test individual MCP tool integrations
python -m pytest agent/tests/test_mcp_tools.py

# Test tool selection logic
python -m pytest agent/tests/test_tool_selection.py

# Test error handling
python -m pytest agent/tests/test_mcp_error_handling.py
```

#### Integration Testing
```bash
# Test end-to-end MCP workflows
python test_mcp_integration.py

# Test with external service mocking
python test_mcp_mocked.py

# Performance testing
python test_mcp_performance.py
```

#### Production Monitoring
```bash
# Health check all MCP servers
python scripts/check_mcp_health.py

# Monitor tool performance
aws logs filter-log-events --log-group-name /ecs/production-analytics-agent-agent --filter-pattern "MCP_TOOL"

# Alert on failures
aws cloudwatch put-metric-alarm --alarm-name "MCP-Tool-Failures" --metric-name "MCPToolErrors"
```

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

### Troubleshooting

#### Common Issues

1. **MCP Server Not Starting**
   ```bash
   # Check uvx installation
   uvx --version
   
   # Test server manually
   uvx awslabs.aws-documentation-mcp-server@latest
   ```

2. **Tool Selection Not Working**
   ```python
   # Debug tool selection
   tools = mcp_tools.get_relevant_tools_for_query(query, intent)
   print(f"Selected tools: {tools}")
   ```

3. **Authentication Failures**
   ```bash
   # Check environment variables
   echo $POSTGRES_CONNECTION_STRING
   echo $BRAVE_API_KEY
   
   # Verify secrets in AWS
   aws secretsmanager get-secret-value --secret-id production-analytics-agent-secrets
   ```

4. **Performance Issues**
   ```python
   # Monitor tool execution time
   start_time = time.time()
   result = await mcp_tools.call_mcp_tool(tool, function, params)
   execution_time = time.time() - start_time
   logger.info(f"Tool {tool} executed in {execution_time:.2f}s")
   ```

### Future Enhancements

#### Planned MCP Integrations
- **Slack Integration**: For notifications and collaborative analytics
- **Email Server**: For automated report distribution
- **Calendar Integration**: For scheduled analytics runs
- **Document Generation**: For automated report creation

#### Advanced Features
- **Tool Chaining**: Automatic chaining of related MCP tools
- **Smart Caching**: Intelligent caching based on query patterns
- **Load Balancing**: Distribute load across multiple tool instances
- **Custom Tools**: Framework for creating organization-specific MCP tools

This MCP integration provides the analytics agent with powerful extensibility while maintaining security, performance, and reliability standards.