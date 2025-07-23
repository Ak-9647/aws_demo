"""
AgentCore Integration Module
Integrates Memory, Identity, Gateways, and Built-in Tools with MCP
"""

import json
import logging
import boto3
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import requests
import uuid

logger = logging.getLogger(__name__)

class AgentCoreIntegration:
    """
    Integration layer for AgentCore Memory, Identity, Gateways, and MCP tools
    """
    
    def __init__(self):
        self.bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        self.agent_id = os.getenv('AGENTCORE_AGENT_ID', 'your-agent-id')
        self.agent_alias_id = os.getenv('AGENTCORE_AGENT_ALIAS_ID', 'TSTALIASID')
        self.session_id = None
        self.memory_id = None
        
        # Initialize built-in tools
        self.builtin_tools = {
            'code_interpreter': self._setup_code_interpreter(),
            'knowledge_base': self._setup_knowledge_base(),
            'web_search': self._setup_web_search()
        }
        
        # Initialize MCP tools
        self.mcp_tools = self._initialize_mcp_tools()
        
        logger.info("AgentCore integration initialized")
    
    def create_session_with_memory(self, user_id: str = None, session_name: str = None) -> str:
        """
        Create a new session with AgentCore Memory
        """
        try:
            # Create memory resource first
            memory_response = self._create_memory_resource(user_id)
            self.memory_id = memory_response.get('memoryId')
            
            # Create session with memory
            session_response = self.bedrock_agent.create_agent_session(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionName=session_name or f"analytics-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                memoryId=self.memory_id,
                clientToken=str(uuid.uuid4())
            )
            
            self.session_id = session_response['sessionId']
            logger.info(f"Created session {self.session_id} with memory {self.memory_id}")
            
            return self.session_id
            
        except Exception as e:
            logger.error(f"Failed to create session with memory: {e}")
            # Fallback to session without memory
            self.session_id = str(uuid.uuid4())
            return self.session_id
    
    def _create_memory_resource(self, user_id: str = None) -> Dict[str, Any]:
        """
        Create AgentCore Memory resource
        """
        try:
            response = self.bedrock_agent.create_memory(
                memoryName=f"analytics-memory-{user_id or 'anonymous'}",
                description="Memory for analytics conversations and user preferences",
                tags={
                    'Purpose': 'Analytics',
                    'UserId': user_id or 'anonymous',
                    'CreatedAt': datetime.now().isoformat()
                }
            )
            
            logger.info(f"Created memory resource: {response['memoryId']}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create memory resource: {e}")
            return {}
    
    def invoke_with_tools(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke agent with integrated tools and memory
        """
        try:
            # Prepare the request with tools and context
            request_payload = {
                'agentId': self.agent_id,
                'agentAliasId': self.agent_alias_id,
                'sessionId': self.session_id or self.create_session_with_memory(),
                'inputText': query
            }
            
            # Add memory context if available
            if self.memory_id:
                request_payload['memoryId'] = self.memory_id
            
            # Add session attributes for context
            if context:
                request_payload['sessionState'] = {
                    'sessionAttributes': {
                        'userContext': json.dumps(context),
                        'timestamp': datetime.now().isoformat(),
                        'toolsAvailable': json.dumps(list(self.builtin_tools.keys()) + list(self.mcp_tools.keys()))
                    }
                }
            
            # Invoke the agent
            response = self.bedrock_agent.invoke_agent(**request_payload)
            
            # Process the streaming response
            result = self._process_agent_response(response)
            
            # Enhance with MCP tool results if needed
            enhanced_result = self._enhance_with_mcp_tools(result, query)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Failed to invoke agent with tools: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': True
            }
    
    def _process_agent_response(self, response) -> Dict[str, Any]:
        """
        Process streaming response from AgentCore
        """
        result = {
            'success': True,
            'response_text': '',
            'tool_calls': [],
            'memory_updates': [],
            'citations': []
        }
        
        try:
            # Process the event stream
            for event in response.get('completion', []):
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result['response_text'] += chunk['bytes'].decode('utf-8')
                
                elif 'trace' in event:
                    trace = event['trace']
                    if 'orchestrationTrace' in trace:
                        # Process tool invocations
                        orch_trace = trace['orchestrationTrace']
                        if 'invocation' in orch_trace:
                            result['tool_calls'].append(orch_trace['invocation'])
                
                elif 'returnControl' in event:
                    # Handle return control for custom tools
                    control = event['returnControl']
                    result['return_control'] = control
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
            result['success'] = False
            result['error'] = str(e)
            return result
    
    def _enhance_with_mcp_tools(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Enhance results with MCP tool capabilities
        """
        try:
            # Determine if MCP tools should be used based on query
            mcp_enhancements = []
            
            # AWS documentation lookup for AWS-related queries
            if any(aws_term in query.lower() for aws_term in ['aws', 'amazon', 's3', 'ec2', 'lambda', 'dynamodb']):
                aws_info = self._call_mcp_tool('aws-docs', 'search_aws_docs', {'query': query})
                if aws_info:
                    mcp_enhancements.append({
                        'tool': 'aws-docs',
                        'result': aws_info
                    })
            
            # Web search for current information
            if any(search_term in query.lower() for search_term in ['latest', 'current', 'recent', 'news']):
                web_results = self._call_mcp_tool('web-search', 'web_search', {'query': query})
                if web_results:
                    mcp_enhancements.append({
                        'tool': 'web-search',
                        'result': web_results
                    })
            
            # Add MCP enhancements to result
            if mcp_enhancements:
                result['mcp_enhancements'] = mcp_enhancements
                result['enhanced'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing with MCP tools: {e}")
            return result
    
    def _call_mcp_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call an MCP tool (placeholder for actual MCP integration)
        """
        try:
            # This would be replaced with actual MCP tool invocation
            logger.info(f"Calling MCP tool {server_name}:{tool_name} with params: {parameters}")
            
            # Mock response for demonstration
            if server_name == 'aws-docs':
                return {
                    'documentation': f"AWS documentation for: {parameters.get('query', '')}",
                    'relevant_services': ['S3', 'DynamoDB', 'Lambda'],
                    'source': 'AWS Documentation'
                }
            elif server_name == 'web-search':
                return {
                    'results': [
                        {
                            'title': f"Latest information about {parameters.get('query', '')}",
                            'url': 'https://example.com',
                            'snippet': 'Recent developments and updates...'
                        }
                    ],
                    'source': 'Web Search'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {server_name}:{tool_name}: {e}")
            return None
    
    def _setup_code_interpreter(self) -> Dict[str, Any]:
        """
        Setup AgentCore built-in code interpreter
        """
        return {
            'name': 'code_interpreter',
            'description': 'Execute Python code for data analysis and visualization',
            'enabled': True,
            'capabilities': ['pandas', 'matplotlib', 'numpy', 'seaborn', 'plotly']
        }
    
    def _setup_knowledge_base(self) -> Dict[str, Any]:
        """
        Setup AgentCore knowledge base integration
        """
        return {
            'name': 'knowledge_base',
            'description': 'Query knowledge base for domain-specific information',
            'enabled': True,
            'knowledge_base_id': os.getenv('KNOWLEDGE_BASE_ID', 'your-kb-id')
        }
    
    def _setup_web_search(self) -> Dict[str, Any]:
        """
        Setup AgentCore web search capability
        """
        return {
            'name': 'web_search',
            'description': 'Search the web for current information',
            'enabled': True
        }
    
    def _initialize_mcp_tools(self) -> Dict[str, Any]:
        """
        Initialize available MCP tools
        """
        return {
            'aws_docs': {
                'server': 'aws-docs',
                'tools': ['search_aws_docs', 'get_aws_service_info'],
                'description': 'AWS documentation and service information'
            },
            'github': {
                'server': 'github',
                'tools': ['search_repositories', 'get_file_contents'],
                'description': 'GitHub repository access and code search'
            },
            'web_search': {
                'server': 'web-search',
                'tools': ['web_search'],
                'description': 'Web search for current information'
            },
            'filesystem': {
                'server': 'filesystem',
                'tools': ['read_file', 'write_file', 'list_directory'],
                'description': 'File system operations'
            }
        }
    
    def setup_identity_integration(self, oauth_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Setup AgentCore Identity integration
        """
        try:
            identity_config = {
                'inbound_auth': {
                    'enabled': True,
                    'oauth_provider': oauth_config.get('provider', 'cognito') if oauth_config else 'cognito',
                    'client_id': oauth_config.get('client_id') if oauth_config else os.getenv('OAUTH_CLIENT_ID'),
                    'scopes': oauth_config.get('scopes', ['openid', 'profile', 'email']) if oauth_config else ['openid', 'profile', 'email']
                },
                'outbound_auth': {
                    'enabled': True,
                    'api_key_management': True,
                    'oauth_client_management': True
                }
            }
            
            logger.info("Identity integration configured")
            return identity_config
            
        except Exception as e:
            logger.error(f"Failed to setup identity integration: {e}")
            return {}
    
    def setup_gateway_integration(self, gateway_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Setup AgentCore Gateway integration for external APIs
        """
        try:
            gateway_config = gateway_config or {}
            
            default_gateways = {
                'analytics_api': {
                    'type': 'REST',
                    'base_url': gateway_config.get('analytics_api_url', 'https://api.analytics.example.com'),
                    'auth_type': 'api_key',
                    'endpoints': [
                        {'path': '/data/query', 'method': 'POST'},
                        {'path': '/data/export', 'method': 'GET'},
                        {'path': '/insights/generate', 'method': 'POST'}
                    ]
                },
                'external_db': {
                    'type': 'DATABASE',
                    'connection_string': gateway_config.get('db_connection'),
                    'auth_type': 'credentials',
                    'operations': ['SELECT', 'INSERT', 'UPDATE']
                }
            }
            
            logger.info("Gateway integration configured")
            return default_gateways
            
        except Exception as e:
            logger.error(f"Failed to setup gateway integration: {e}")
            return {}
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get summary of current memory state
        """
        try:
            if not self.memory_id:
                return {'status': 'no_memory', 'message': 'No memory resource active'}
            
            # Get memory details (placeholder for actual API call)
            memory_summary = {
                'memory_id': self.memory_id,
                'session_id': self.session_id,
                'conversations_count': 0,  # Would be retrieved from actual API
                'last_updated': datetime.now().isoformat(),
                'memory_size': '0 KB',  # Would be retrieved from actual API
                'status': 'active'
            }
            
            return memory_summary
            
        except Exception as e:
            logger.error(f"Failed to get memory summary: {e}")
            return {'status': 'error', 'error': str(e)}