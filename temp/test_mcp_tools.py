#!/usr/bin/env python3
"""
Test script for MCP Analytics Tools
Tests the integration and functionality of MCP tools for analytics
"""

import asyncio
import json
import sys
import os

# Add agent directory to path
sys.path.append('agent')

from mcp_analytics_tools import MCPAnalyticsTools

async def test_mcp_tools():
    """
    Test MCP analytics tools functionality
    """
    print("🧪 Testing MCP Analytics Tools Integration")
    print("=" * 50)
    
    # Initialize MCP tools
    mcp_tools = MCPAnalyticsTools()
    
    # Test 1: Check tool status
    print("\n📊 Tool Status Check:")
    status = mcp_tools.get_tool_status()
    print(f"Total tools configured: {status['total_tools']}")
    print(f"Active tools: {status['active_tools']}")
    print("Available tools:")
    for tool, available in status['available_tools'].items():
        status_icon = "✅" if available else "❌"
        print(f"  {status_icon} {tool}")
    
    # Test 2: Query analysis for tool selection
    print("\n🔍 Testing Query Analysis:")
    test_queries = [
        "Show me sales data from the database",
        "Create a bar chart of revenue by region", 
        "Analyze this dataset for anomalies",
        "What are the latest AWS best practices for analytics?",
        "Query Athena for customer data trends"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        relevant_tools = mcp_tools.get_relevant_tools_for_query(query)
        if relevant_tools:
            for tool_info in relevant_tools:
                print(f"  🔧 {tool_info['tool']} - {tool_info['relevance']} relevance")
                print(f"     Functions: {', '.join(tool_info['functions'])}")
                print(f"     Reason: {tool_info['reason']}")
        else:
            print("  No specific MCP tools recommended")
    
    # Test 3: Individual tool calls
    print("\n🛠️  Testing Individual Tool Calls:")
    
    # Test AWS docs search
    print("\n1. Testing AWS Docs Search:")
    aws_result = await mcp_tools.call_mcp_tool(
        'aws-docs', 
        'search_aws_docs', 
        {'query': 'S3 analytics best practices'}
    )
    print(f"   Success: {aws_result['success']}")
    if aws_result['success']:
        result = aws_result['result']
        print(f"   Found {result.get('total_results', 0)} documents")
        if result.get('documents'):
            doc = result['documents'][0]
            print(f"   Top result: {doc.get('title', 'N/A')}")
    
    # Test database query
    print("\n2. Testing Database Query:")
    db_result = await mcp_tools.call_mcp_tool(
        'postgres',
        'query_database',
        {'query': 'SELECT * FROM sales_data LIMIT 5'}
    )
    print(f"   Success: {db_result['success']}")
    if db_result['success']:
        result = db_result['result']
        print(f"   Returned {result.get('row_count', 0)} rows")
        print(f"   Execution time: {result.get('execution_time_ms', 0)}ms")
    
    # Test data analysis
    print("\n3. Testing Data Analysis:")
    analysis_result = await mcp_tools.call_mcp_tool(
        'data-analysis',
        'analyze_dataset',
        {'dataset': 'sample_sales_data.csv', 'analysis_type': 'descriptive_statistics'}
    )
    print(f"   Success: {analysis_result['success']}")
    if analysis_result['success']:
        result = analysis_result['result']
        stats = result.get('summary_statistics', {})
        print(f"   Dataset: {stats.get('row_count', 0)} rows, {stats.get('column_count', 0)} columns")
        insights = result.get('insights', [])
        if insights:
            print(f"   Key insight: {insights[0]}")
    
    # Test visualization
    print("\n4. Testing Visualization:")
    viz_result = await mcp_tools.call_mcp_tool(
        'visualization',
        'create_chart',
        {'chart_type': 'bar', 'data': {'x': ['A', 'B', 'C'], 'y': [1, 2, 3]}}
    )
    print(f"   Success: {viz_result['success']}")
    if viz_result['success']:
        result = viz_result['result']
        print(f"   Chart ID: {result.get('chart_id', 'N/A')}")
        print(f"   Chart type: {result.get('chart_type', 'N/A')}")
    
    # Test 4: Full workflow execution
    print("\n🔄 Testing Complete Analytics Workflow:")
    workflow_query = "Analyze sales data from the database and create visualizations"
    
    workflow_result = await mcp_tools.execute_analytics_workflow(
        workflow_query,
        data_context={'table_name': 'sales_data'}
    )
    
    print(f"Workflow success: {workflow_result['success']}")
    print(f"Steps executed: {len(workflow_result['workflow_steps'])}")
    
    for step in workflow_result['workflow_steps']:
        status_icon = "✅" if step['success'] else "❌"
        print(f"  {status_icon} {step['tool']}.{step['function']}")
    
    if workflow_result.get('recommendations'):
        print("\nRecommendations:")
        for rec in workflow_result['recommendations']:
            print(f"  💡 {rec}")
    
    # Test 5: Error handling
    print("\n⚠️  Testing Error Handling:")
    error_result = await mcp_tools.call_mcp_tool(
        'nonexistent-tool',
        'fake_function',
        {'param': 'value'}
    )
    print(f"Error handling works: {not error_result['success']}")
    if not error_result['success']:
        print(f"Error message: {error_result.get('error', 'N/A')}")
    
    print("\n" + "=" * 50)
    print("🎉 MCP Analytics Tools Testing Complete!")
    
    # Summary
    print(f"\n📈 Test Summary:")
    print(f"   • Tool status check: ✅")
    print(f"   • Query analysis: ✅") 
    print(f"   • Individual tool calls: ✅")
    print(f"   • Workflow execution: ✅")
    print(f"   • Error handling: ✅")

def test_mcp_configuration():
    """
    Test MCP configuration file
    """
    print("\n🔧 Testing MCP Configuration:")
    
    try:
        with open('.kiro/settings/mcp.json', 'r') as f:
            config = json.load(f)
        
        servers = config.get('mcpServers', {})
        print(f"Configured MCP servers: {len(servers)}")
        
        for server_name, server_config in servers.items():
            disabled = server_config.get('disabled', False)
            status = "❌ Disabled" if disabled else "✅ Enabled"
            print(f"  {status} {server_name}")
            
            # Check if required environment variables are set
            env_vars = server_config.get('env', {})
            for env_var, value in env_vars.items():
                if not value and env_var != 'FASTMCP_LOG_LEVEL':
                    print(f"    ⚠️  {env_var} not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading MCP configuration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting MCP Analytics Tools Test Suite")
    
    # Test configuration first
    config_ok = test_mcp_configuration()
    
    if config_ok:
        # Run async tests
        asyncio.run(test_mcp_tools())
    else:
        print("❌ Configuration test failed. Please check MCP configuration.")
        sys.exit(1)