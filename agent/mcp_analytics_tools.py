"""
MCP Analytics Tools Integration
Integrates Model Context Protocol tools for enhanced analytics capabilities
"""

import json
import logging
import asyncio
import subprocess
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
# import pandas as pd
# import numpy as np

logger = logging.getLogger(__name__)

class MCPAnalyticsTools:
    """
    Integration layer for MCP tools specifically for analytics use cases
    """
    
    def __init__(self):
        self.available_tools = {}
        self.active_connections = {}
        self.tool_capabilities = self._initialize_tool_capabilities()
        
        # Initialize MCP tool connections
        self._initialize_mcp_connections()
        
        logger.info("MCP Analytics Tools initialized")
    
    def _initialize_tool_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """
        Define capabilities of each MCP tool for analytics
        """
        return {
            'aws-docs': {
                'category': 'documentation',
                'analytics_use_cases': [
                    'AWS service documentation lookup',
                    'Best practices for AWS analytics services',
                    'Configuration guidance for data pipelines'
                ],
                'tools': ['search_aws_docs', 'get_aws_service_info']
            },
            'postgres': {
                'category': 'database',
                'analytics_use_cases': [
                    'SQL query execution',
                    'Database schema analysis',
                    'Data extraction and transformation'
                ],
                'tools': ['query_database', 'get_schema', 'list_tables']
            },
            'filesystem': {
                'category': 'data_access',
                'analytics_use_cases': [
                    'Data file reading and writing',
                    'Dataset management',
                    'Result export and storage'
                ],
                'tools': ['read_file', 'write_file', 'list_directory']
            },
            'data-analysis': {
                'category': 'analytics',
                'analytics_use_cases': [
                    'Advanced statistical analysis',
                    'Anomaly detection',
                    'Time series forecasting',
                    'Dataset profiling'
                ],
                'tools': ['analyze_dataset', 'generate_statistics', 'detect_anomalies', 'forecast_timeseries']
            },
            'visualization': {
                'category': 'visualization',
                'analytics_use_cases': [
                    'Advanced chart creation',
                    'Dashboard generation',
                    'Interactive visualizations',
                    'Export to multiple formats'
                ],
                'tools': ['create_chart', 'generate_dashboard', 'export_visualization']
            },
            'aws-analytics': {
                'category': 'cloud_analytics',
                'analytics_use_cases': [
                    'AWS Athena queries',
                    'AWS Glue catalog exploration',
                    'QuickSight dashboard management'
                ],
                'tools': ['query_athena', 'describe_glue_tables', 'list_quicksight_dashboards']
            },
            'redshift': {
                'category': 'data_warehouse',
                'analytics_use_cases': [
                    'Large-scale data queries',
                    'Data warehouse analytics',
                    'Performance optimization'
                ],
                'tools': ['query_redshift', 'get_schema', 'list_tables']
            },
            'web-search': {
                'category': 'external_data',
                'analytics_use_cases': [
                    'Market research data',
                    'Current trends and insights',
                    'External data validation'
                ],
                'tools': ['web_search']
            }
        }
    
    def _initialize_mcp_connections(self):
        """
        Initialize connections to MCP servers
        """
        try:
            # Check if uvx is available
            result = subprocess.run(['which', 'uvx'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("uvx not found. MCP tools may not be available.")
                return
            
            # Test connection to key analytics tools
            priority_tools = ['aws-docs', 'filesystem', 'postgres']
            
            for tool_name in priority_tools:
                try:
                    self._test_mcp_connection(tool_name)
                    self.available_tools[tool_name] = True
                    logger.info(f"MCP tool {tool_name} is available")
                except Exception as e:
                    logger.warning(f"MCP tool {tool_name} not available: {e}")
                    self.available_tools[tool_name] = False
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP connections: {e}")
    
    def _test_mcp_connection(self, tool_name: str):
        """
        Test connection to an MCP tool
        """
        # This would test actual MCP connection
        # For now, we'll simulate the test
        logger.info(f"Testing MCP connection to {tool_name}")
        return True
    
    async def call_mcp_tool(self, tool_name: str, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool function with parameters
        """
        try:
            if tool_name not in self.available_tools or not self.available_tools[tool_name]:
                return {
                    'success': False,
                    'error': f'MCP tool {tool_name} not available',
                    'fallback_needed': True
                }
            
            # Simulate MCP tool call (replace with actual MCP client call)
            result = await self._simulate_mcp_call(tool_name, function_name, parameters)
            
            return {
                'success': True,
                'tool': tool_name,
                'function': function_name,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}.{function_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name,
                'function': function_name
            }
    
    async def _simulate_mcp_call(self, tool_name: str, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate MCP tool calls for testing (replace with actual MCP client)
        """
        # Simulate different tool responses
        if tool_name == 'aws-docs':
            if function_name == 'search_aws_docs':
                return {
                    'documents': [
                        {
                            'title': f"AWS Documentation for {parameters.get('query', 'analytics')}",
                            'content': 'Comprehensive guide to AWS analytics services...',
                            'url': 'https://docs.aws.amazon.com/analytics/',
                            'relevance_score': 0.95
                        }
                    ],
                    'total_results': 1
                }
        
        elif tool_name == 'postgres':
            if function_name == 'query_database':
                return {
                    'rows': [
                        {'id': 1, 'name': 'Sample Data', 'value': 100},
                        {'id': 2, 'name': 'Test Record', 'value': 200}
                    ],
                    'row_count': 2,
                    'execution_time_ms': 45
                }
            elif function_name == 'get_schema':
                return {
                    'tables': [
                        {
                            'name': 'sales_data',
                            'columns': [
                                {'name': 'id', 'type': 'integer', 'nullable': False},
                                {'name': 'date', 'type': 'date', 'nullable': False},
                                {'name': 'amount', 'type': 'decimal', 'nullable': False}
                            ]
                        }
                    ]
                }
        
        elif tool_name == 'data-analysis':
            if function_name == 'analyze_dataset':
                return {
                    'summary_statistics': {
                        'row_count': 1000,
                        'column_count': 5,
                        'missing_values': 12,
                        'data_types': {'numeric': 3, 'categorical': 2}
                    },
                    'insights': [
                        'Dataset has high data quality with minimal missing values',
                        'Strong correlation detected between sales and marketing spend'
                    ]
                }
            elif function_name == 'detect_anomalies':
                return {
                    'anomalies_detected': 5,
                    'anomaly_score_threshold': 0.8,
                    'anomalous_records': [
                        {'index': 45, 'score': 0.95, 'reason': 'Unusually high sales value'},
                        {'index': 123, 'score': 0.87, 'reason': 'Negative revenue recorded'}
                    ]
                }
        
        elif tool_name == 'visualization':
            if function_name == 'create_chart':
                return {
                    'chart_id': 'chart_123',
                    'chart_type': parameters.get('chart_type', 'bar'),
                    'image_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
                    'interactive_url': 'https://charts.example.com/chart_123'
                }
        
        elif tool_name == 'aws-analytics':
            if function_name == 'query_athena':
                return {
                    'query_execution_id': 'qe-12345',
                    'results': [
                        {'region': 'us-west-2', 'sales': 150000, 'orders': 1200},
                        {'region': 'us-east-1', 'sales': 180000, 'orders': 1450}
                    ],
                    'execution_time_ms': 2340,
                    'data_scanned_bytes': 1024000
                }
        
        # Default response
        return {
            'message': f'Simulated response from {tool_name}.{function_name}',
            'parameters_received': parameters
        }
    
    def get_relevant_tools_for_query(self, query: str, intent: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Determine which MCP tools are most relevant for a given query
        """
        relevant_tools = []
        query_lower = query.lower()
        
        # Database-related queries
        if any(keyword in query_lower for keyword in ['sql', 'database', 'table', 'query', 'select']):
            if 'postgres' in self.available_tools and self.available_tools['postgres']:
                relevant_tools.append({
                    'tool': 'postgres',
                    'functions': ['query_database', 'get_schema'],
                    'relevance': 'high',
                    'reason': 'Query contains database-related keywords'
                })
        
        # AWS-related queries
        if any(keyword in query_lower for keyword in ['aws', 'amazon', 's3', 'athena', 'redshift', 'glue']):
            if 'aws-docs' in self.available_tools and self.available_tools['aws-docs']:
                relevant_tools.append({
                    'tool': 'aws-docs',
                    'functions': ['search_aws_docs'],
                    'relevance': 'high',
                    'reason': 'Query mentions AWS services'
                })
            
            if 'aws-analytics' in self.available_tools and self.available_tools['aws-analytics']:
                relevant_tools.append({
                    'tool': 'aws-analytics',
                    'functions': ['query_athena', 'describe_glue_tables'],
                    'relevance': 'high',
                    'reason': 'Query involves AWS analytics services'
                })
        
        # Data analysis queries
        if any(keyword in query_lower for keyword in ['analyze', 'statistics', 'correlation', 'anomaly', 'trend']):
            if 'data-analysis' in self.available_tools and self.available_tools['data-analysis']:
                relevant_tools.append({
                    'tool': 'data-analysis',
                    'functions': ['analyze_dataset', 'generate_statistics', 'detect_anomalies'],
                    'relevance': 'high',
                    'reason': 'Query requires advanced data analysis'
                })
        
        # Visualization queries
        if any(keyword in query_lower for keyword in ['chart', 'graph', 'plot', 'visualize', 'dashboard']):
            if 'visualization' in self.available_tools and self.available_tools['visualization']:
                relevant_tools.append({
                    'tool': 'visualization',
                    'functions': ['create_chart', 'generate_dashboard'],
                    'relevance': 'high',
                    'reason': 'Query requests data visualization'
                })
        
        # File operations
        if any(keyword in query_lower for keyword in ['file', 'csv', 'excel', 'data file', 'export']):
            if 'filesystem' in self.available_tools and self.available_tools['filesystem']:
                relevant_tools.append({
                    'tool': 'filesystem',
                    'functions': ['read_file', 'write_file'],
                    'relevance': 'medium',
                    'reason': 'Query involves file operations'
                })
        
        # External data queries
        if any(keyword in query_lower for keyword in ['latest', 'current', 'market', 'trends', 'news']):
            if 'web-search' in self.available_tools and self.available_tools['web-search']:
                relevant_tools.append({
                    'tool': 'web-search',
                    'functions': ['web_search'],
                    'relevance': 'medium',
                    'reason': 'Query requires current external information'
                })
        
        return relevant_tools
    
    async def execute_analytics_workflow(self, query: str, data_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a complete analytics workflow using relevant MCP tools
        """
        try:
            workflow_results = {
                'query': query,
                'workflow_steps': [],
                'results': {},
                'recommendations': [],
                'success': True
            }
            
            # Step 1: Identify relevant tools
            relevant_tools = self.get_relevant_tools_for_query(query)
            workflow_results['relevant_tools'] = relevant_tools
            
            # Step 2: Execute tools in logical order
            for tool_info in relevant_tools:
                tool_name = tool_info['tool']
                functions = tool_info['functions']
                
                for function_name in functions:
                    # Prepare parameters based on context
                    parameters = self._prepare_tool_parameters(tool_name, function_name, query, data_context)
                    
                    # Execute tool
                    result = await self.call_mcp_tool(tool_name, function_name, parameters)
                    
                    workflow_results['workflow_steps'].append({
                        'tool': tool_name,
                        'function': function_name,
                        'success': result['success'],
                        'timestamp': result.get('timestamp')
                    })
                    
                    if result['success']:
                        workflow_results['results'][f"{tool_name}_{function_name}"] = result['result']
                    else:
                        workflow_results['success'] = False
                        workflow_results['errors'] = workflow_results.get('errors', [])
                        workflow_results['errors'].append(result.get('error'))
            
            # Step 3: Generate recommendations based on results
            workflow_results['recommendations'] = self._generate_workflow_recommendations(workflow_results)
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error executing analytics workflow: {e}")
            return {
                'query': query,
                'success': False,
                'error': str(e),
                'workflow_steps': [],
                'results': {}
            }
    
    def _prepare_tool_parameters(self, tool_name: str, function_name: str, query: str, data_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare parameters for MCP tool calls based on context
        """
        parameters = {}
        
        if tool_name == 'aws-docs':
            parameters['query'] = query
        elif tool_name == 'postgres':
            if function_name == 'query_database':
                # Extract SQL-like intent from query
                parameters['query'] = self._extract_sql_intent(query)
            elif function_name == 'get_schema':
                parameters['table_name'] = data_context.get('table_name') if data_context else None
        elif tool_name == 'data-analysis':
            if data_context and 'dataset' in data_context:
                parameters['dataset'] = data_context['dataset']
            parameters['analysis_type'] = self._determine_analysis_type(query)
        elif tool_name == 'visualization':
            parameters['chart_type'] = self._determine_chart_type(query)
            parameters['data'] = data_context.get('data') if data_context else None
        elif tool_name == 'web-search':
            parameters['query'] = query
            parameters['num_results'] = 5
        
        return parameters
    
    def _extract_sql_intent(self, query: str) -> str:
        """
        Extract SQL-like intent from natural language query
        """
        # Simple keyword-based SQL generation
        if 'sales' in query.lower():
            return "SELECT * FROM sales_data ORDER BY date DESC LIMIT 100"
        elif 'revenue' in query.lower():
            return "SELECT SUM(amount) as total_revenue FROM sales_data GROUP BY date"
        else:
            return "SELECT * FROM information_schema.tables"
    
    def _determine_analysis_type(self, query: str) -> str:
        """
        Determine the type of analysis needed
        """
        query_lower = query.lower()
        if 'anomaly' in query_lower or 'outlier' in query_lower:
            return 'anomaly_detection'
        elif 'correlation' in query_lower:
            return 'correlation_analysis'
        elif 'trend' in query_lower or 'forecast' in query_lower:
            return 'time_series_analysis'
        else:
            return 'descriptive_statistics'
    
    def _determine_chart_type(self, query: str) -> str:
        """
        Determine the appropriate chart type from query
        """
        query_lower = query.lower()
        if 'bar' in query_lower or 'column' in query_lower:
            return 'bar'
        elif 'line' in query_lower or 'trend' in query_lower:
            return 'line'
        elif 'pie' in query_lower:
            return 'pie'
        elif 'scatter' in query_lower:
            return 'scatter'
        else:
            return 'bar'  # default
    
    def _generate_workflow_recommendations(self, workflow_results: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on workflow results
        """
        recommendations = []
        
        # Analyze results and suggest next steps
        if 'postgres_query_database' in workflow_results['results']:
            recommendations.append("Consider creating an index on frequently queried columns for better performance")
        
        if 'data-analysis_detect_anomalies' in workflow_results['results']:
            anomaly_result = workflow_results['results']['data-analysis_detect_anomalies']
            if anomaly_result.get('anomalies_detected', 0) > 0:
                recommendations.append("Investigate detected anomalies for potential data quality issues")
        
        if 'aws-analytics_query_athena' in workflow_results['results']:
            recommendations.append("Consider partitioning your data in S3 for improved Athena query performance")
        
        if not recommendations:
            recommendations.append("Workflow completed successfully. Consider setting up automated monitoring for similar queries.")
        
        return recommendations
    
    def get_tool_status(self) -> Dict[str, Any]:
        """
        Get status of all MCP tools
        """
        return {
            'available_tools': self.available_tools,
            'tool_capabilities': self.tool_capabilities,
            'total_tools': len(self.tool_capabilities),
            'active_tools': sum(1 for available in self.available_tools.values() if available),
            'last_updated': datetime.now().isoformat()
        }