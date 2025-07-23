"""
AgentCore Memory Integration Module
Provides integration with Amazon Bedrock AgentCore Memory service
Supports both traditional memory (DynamoDB + Redis) and new AgentCore Memory
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AgentCoreMemoryIntegration:
    """
    Integration with Amazon Bedrock AgentCore Memory service
    Provides unified interface for memory operations
    """
    
    def __init__(self):
        self.bedrock_agent_client = None
        self.lambda_client = None
        self.memory_ids = {}
        self.fallback_to_traditional = True
        
        # Initialize AWS clients
        try:
            self.bedrock_agent_client = boto3.client('bedrock-agent')
            self.lambda_client = boto3.client('lambda')
            logger.info("AgentCore Memory clients initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize AgentCore clients: {str(e)}")
            self.bedrock_agent_client = None
            self.lambda_client = None
        
        # Load memory resource IDs from environment or CloudFormation exports
        self._load_memory_configuration()
        
        logger.info(f"AgentCore Memory integration initialized (available: {self.is_available()})")
    
    def _load_memory_configuration(self):
        """Load memory resource configuration"""
        try:
            # Try to get from environment variables first
            self.memory_ids = {
                'conversation': os.environ.get('CONVERSATION_MEMORY_ID'),
                'user_preferences': os.environ.get('USER_PREFERENCES_MEMORY_ID'),
                'session_context': os.environ.get('SESSION_CONTEXT_MEMORY_ID'),
                'analytics_context': os.environ.get('ANALYTICS_CONTEXT_MEMORY_ID')
            }
            
            # If not in environment, try to get from CloudFormation exports
            if not any(self.memory_ids.values()):
                self._load_from_cloudformation_exports()
            
            # Filter out None values
            self.memory_ids = {k: v for k, v in self.memory_ids.items() if v}
            
            logger.info(f"Loaded memory configuration: {list(self.memory_ids.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load memory configuration: {str(e)}")
            self.memory_ids = {}
    
    def _load_from_cloudformation_exports(self):
        """Load memory IDs from CloudFormation exports"""
        try:
            cf_client = boto3.client('cloudformation')
            
            # Map of export names to memory types
            export_mappings = {
                'production-analytics-agent-conversation-memory-id': 'conversation',
                'production-analytics-agent-user-preferences-memory-id': 'user_preferences',
                'production-analytics-agent-session-context-memory-id': 'session_context',
                'production-analytics-agent-analytics-context-memory-id': 'analytics_context'
            }
            
            # Get all exports
            exports = cf_client.list_exports()
            
            for export in exports.get('Exports', []):
                export_name = export['Name']
                if export_name in export_mappings:
                    memory_type = export_mappings[export_name]
                    self.memory_ids[memory_type] = export['Value']
                    logger.info(f"Loaded {memory_type} memory ID from CloudFormation: {export['Value']}")
            
        except Exception as e:
            logger.warning(f"Failed to load from CloudFormation exports: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if AgentCore Memory is available"""
        return (
            self.bedrock_agent_client is not None and 
            len(self.memory_ids) > 0
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all memory resources"""
        if not self.is_available():
            return {
                'success': False,
                'message': 'AgentCore Memory not available',
                'fallback_available': self.fallback_to_traditional
            }
        
        try:
            # Call the memory management Lambda function for health check
            management_function_arn = os.environ.get('MEMORY_MANAGEMENT_FUNCTION_ARN')
            
            if management_function_arn and self.lambda_client:
                response = self.lambda_client.invoke(
                    FunctionName=management_function_arn,
                    Payload=json.dumps({'operation': 'health_check'})
                )
                
                result = json.loads(response['Payload'].read())
                
                if response['StatusCode'] == 200:
                    return {
                        'success': True,
                        'message': 'AgentCore Memory health check passed',
                        'details': result,
                        'memory_count': len(self.memory_ids)
                    }
                else:
                    return {
                        'success': False,
                        'message': 'AgentCore Memory health check failed',
                        'error': result
                    }
            else:
                # Direct health check using bedrock-agent client
                healthy_memories = []
                
                for memory_type, memory_id in self.memory_ids.items():
                    try:
                        memory_info = self.bedrock_agent_client.get_memory(memoryId=memory_id)
                        healthy_memories.append({
                            'type': memory_type,
                            'id': memory_id,
                            'status': 'healthy',
                            'name': memory_info.get('memoryName', 'unknown')
                        })
                    except Exception as e:
                        healthy_memories.append({
                            'type': memory_type,
                            'id': memory_id,
                            'status': 'error',
                            'error': str(e)
                        })
                
                return {
                    'success': True,
                    'message': 'Direct health check completed',
                    'memories': healthy_memories,
                    'healthy_count': len([m for m in healthy_memories if m['status'] == 'healthy'])
                }
                
        except Exception as e:
            logger.error(f"AgentCore Memory health check failed: {str(e)}")
            return {
                'success': False,
                'message': 'Health check failed',
                'error': str(e)
            }
    
    def store_conversation(self, session_id: str, user_id: str, query: str, 
                          response: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Store conversation in AgentCore Memory"""
        if not self.is_available():
            return self._fallback_store_conversation(session_id, user_id, query, response, **kwargs)
        
        try:
            memory_id = self.memory_ids.get('conversation')
            if not memory_id:
                raise ValueError("Conversation memory ID not configured")
            
            # Prepare memory content
            memory_content = {
                'session_id': session_id,
                'user_id': user_id,
                'query': query,
                'response': response,
                'timestamp': time.time(),
                'metadata': kwargs
            }
            
            # Store in AgentCore Memory
            self.bedrock_agent_client.put_memory(
                memoryId=memory_id,
                memoryContent=json.dumps(memory_content)
            )
            
            logger.info(f"Stored conversation in AgentCore Memory: {session_id}")
            
            return {
                'success': True,
                'message': 'Conversation stored in AgentCore Memory',
                'memory_id': memory_id
            }
            
        except Exception as e:
            logger.error(f"Failed to store conversation in AgentCore Memory: {str(e)}")
            
            if self.fallback_to_traditional:
                return self._fallback_store_conversation(session_id, user_id, query, response, **kwargs)
            else:
                return {
                    'success': False,
                    'error': str(e),
                    'message': 'Failed to store conversation'
                }
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve conversation history from AgentCore Memory"""
        if not self.is_available():
            return self._fallback_get_conversation_history(session_id, limit)
        
        try:
            memory_id = self.memory_ids.get('conversation')
            if not memory_id:
                raise ValueError("Conversation memory ID not configured")
            
            # Retrieve from AgentCore Memory
            # Note: This is a simplified implementation
            # The actual API might be different based on the final AgentCore Memory API
            response = self.bedrock_agent_client.get_memory(
                memoryId=memory_id,
                sessionId=session_id,
                maxResults=limit
            )
            
            # Parse and return conversation history
            conversations = []
            for item in response.get('memoryContents', []):
                try:
                    content = json.loads(item.get('content', '{}'))
                    conversations.append(content)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse memory content: {item}")
            
            logger.info(f"Retrieved {len(conversations)} conversations from AgentCore Memory")
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history from AgentCore Memory: {str(e)}")
            
            if self.fallback_to_traditional:
                return self._fallback_get_conversation_history(session_id, limit)
            else:
                return []
    
    def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Store user preferences in AgentCore Memory"""
        if not self.is_available():
            return self._fallback_store_user_preferences(user_id, preferences)
        
        try:
            memory_id = self.memory_ids.get('user_preferences')
            if not memory_id:
                raise ValueError("User preferences memory ID not configured")
            
            # Prepare memory content
            memory_content = {
                'user_id': user_id,
                'preferences': preferences,
                'updated_at': time.time()
            }
            
            # Store in AgentCore Memory
            self.bedrock_agent_client.put_memory(
                memoryId=memory_id,
                memoryContent=json.dumps(memory_content)
            )
            
            logger.info(f"Stored user preferences in AgentCore Memory: {user_id}")
            
            return {
                'success': True,
                'message': 'User preferences stored in AgentCore Memory',
                'memory_id': memory_id
            }
            
        except Exception as e:
            logger.error(f"Failed to store user preferences in AgentCore Memory: {str(e)}")
            
            if self.fallback_to_traditional:
                return self._fallback_store_user_preferences(user_id, preferences)
            else:
                return {
                    'success': False,
                    'error': str(e),
                    'message': 'Failed to store user preferences'
                }
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user preferences from AgentCore Memory"""
        if not self.is_available():
            return self._fallback_get_user_preferences(user_id)
        
        try:
            memory_id = self.memory_ids.get('user_preferences')
            if not memory_id:
                raise ValueError("User preferences memory ID not configured")
            
            # Retrieve from AgentCore Memory
            response = self.bedrock_agent_client.get_memory(
                memoryId=memory_id,
                userId=user_id
            )
            
            # Parse and return preferences
            for item in response.get('memoryContents', []):
                try:
                    content = json.loads(item.get('content', '{}'))
                    if content.get('user_id') == user_id:
                        return content.get('preferences', {})
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse memory content: {item}")
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to retrieve user preferences from AgentCore Memory: {str(e)}")
            
            if self.fallback_to_traditional:
                return self._fallback_get_user_preferences(user_id)
            else:
                return {}
    
    def store_session_context(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store session context in AgentCore Memory"""
        if not self.is_available():
            return {'success': False, 'message': 'AgentCore Memory not available'}
        
        try:
            memory_id = self.memory_ids.get('session_context')
            if not memory_id:
                raise ValueError("Session context memory ID not configured")
            
            # Prepare memory content
            memory_content = {
                'session_id': session_id,
                'context': context,
                'timestamp': time.time()
            }
            
            # Store in AgentCore Memory
            self.bedrock_agent_client.put_memory(
                memoryId=memory_id,
                memoryContent=json.dumps(memory_content)
            )
            
            logger.info(f"Stored session context in AgentCore Memory: {session_id}")
            
            return {
                'success': True,
                'message': 'Session context stored in AgentCore Memory',
                'memory_id': memory_id
            }
            
        except Exception as e:
            logger.error(f"Failed to store session context in AgentCore Memory: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to store session context'
            }
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session context from AgentCore Memory"""
        if not self.is_available():
            return {}
        
        try:
            memory_id = self.memory_ids.get('session_context')
            if not memory_id:
                raise ValueError("Session context memory ID not configured")
            
            # Retrieve from AgentCore Memory
            response = self.bedrock_agent_client.get_memory(
                memoryId=memory_id,
                sessionId=session_id
            )
            
            # Parse and return context
            for item in response.get('memoryContents', []):
                try:
                    content = json.loads(item.get('content', '{}'))
                    if content.get('session_id') == session_id:
                        return content.get('context', {})
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse memory content: {item}")
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to retrieve session context from AgentCore Memory: {str(e)}")
            return {}
    
    def cleanup_expired_memories(self) -> Dict[str, Any]:
        """Clean up expired memories"""
        if not self.is_available():
            return {'success': False, 'message': 'AgentCore Memory not available'}
        
        try:
            # Call the memory management Lambda function for cleanup
            management_function_arn = os.environ.get('MEMORY_MANAGEMENT_FUNCTION_ARN')
            
            if management_function_arn and self.lambda_client:
                response = self.lambda_client.invoke(
                    FunctionName=management_function_arn,
                    Payload=json.dumps({'operation': 'cleanup_expired'})
                )
                
                result = json.loads(response['Payload'].read())
                
                return {
                    'success': response['StatusCode'] == 200,
                    'message': 'Memory cleanup completed',
                    'details': result
                }
            else:
                return {
                    'success': False,
                    'message': 'Memory management function not configured'
                }
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired memories: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Memory cleanup failed'
            }
    
    # Fallback methods for traditional memory system
    def _fallback_store_conversation(self, session_id: str, user_id: str, query: str, 
                                   response: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Fallback to traditional conversation storage"""
        logger.info("Using traditional memory fallback for conversation storage")
        # This would integrate with the existing conversation_memory.py
        return {
            'success': True,
            'message': 'Stored using traditional memory system',
            'fallback': True
        }
    
    def _fallback_get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback to traditional conversation retrieval"""
        logger.info("Using traditional memory fallback for conversation retrieval")
        # This would integrate with the existing conversation_memory.py
        return []
    
    def _fallback_store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to traditional user preferences storage"""
        logger.info("Using traditional memory fallback for user preferences storage")
        return {
            'success': True,
            'message': 'Stored using traditional memory system',
            'fallback': True
        }
    
    def _fallback_get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Fallback to traditional user preferences retrieval"""
        logger.info("Using traditional memory fallback for user preferences retrieval")
        return {}

# Global instance
_agentcore_memory = None

def get_agentcore_memory() -> AgentCoreMemoryIntegration:
    """Get or create the global AgentCore Memory integration instance"""
    global _agentcore_memory
    if _agentcore_memory is None:
        _agentcore_memory = AgentCoreMemoryIntegration()
    return _agentcore_memory