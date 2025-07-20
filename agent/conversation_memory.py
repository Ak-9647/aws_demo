"""
Conversation Memory Management for Analytics Agent
"""

import json
import logging
import boto3
import redis
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Memory management for conversation context and user preferences"""
    
    def __init__(self):
        """Initialize memory connections"""
        self.dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        self.redis_client = None
        self.conversation_table = None
        self.preferences_table = None
        
        # Get table names from environment variables or use defaults
        self.conversation_table_name = os.getenv(
            'CONVERSATION_TABLE', 
            'production-analytics-agent-conversation-history'
        )
        self.preferences_table_name = os.getenv(
            'USER_PREFERENCES_TABLE',
            'production-analytics-agent-user-preferences'
        )
        self.redis_endpoint = os.getenv(
            'REDIS_ENDPOINT',
            'production-analytics-agent-redis.cache.amazonaws.com'
        )
        
        self._init_connections()
    
    def _init_connections(self):
        """Initialize database connections with proper error handling"""
        try:
            # Initialize DynamoDB tables
            self.conversation_table = self.dynamodb.Table(self.conversation_table_name)
            self.preferences_table = self.dynamodb.Table(self.preferences_table_name)
            logger.info(f"DynamoDB tables initialized: {self.conversation_table_name}, {self.preferences_table_name}")
            
            # Initialize Redis connection
            self._init_redis()
            
        except Exception as e:
            logger.error(f"Failed to initialize memory connections: {e}")
            raise
    
    def _init_redis(self):
        """Initialize Redis connection with fallback handling"""
        try:
            # Parse Redis endpoint (handle both hostname and full URLs)
            redis_host = self.redis_endpoint
            if '://' in redis_host:
                # Extract hostname from URL
                redis_host = redis_host.split('://')[1].split(':')[0]
            elif ':' in redis_host:
                # Extract hostname from host:port format
                redis_host = redis_host.split(':')[0]
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis connection established to {redis_host}")
            
        except Exception as e:
            logger.warning(f"Redis connection failed, operating in DynamoDB-only mode: {e}")
            self.redis_client = None
    
    def is_redis_available(self) -> bool:
        """Check if Redis is available"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    def store_conversation(self, session_id: str, query: str, response: str, user_id: str = None) -> bool:
        """
        Store conversation in both DynamoDB and Redis
        
        Args:
            session_id: Unique session identifier
            query: User query
            response: Agent response
            user_id: Optional user identifier
            
        Returns:
            bool: True if stored successfully
        """
        try:
            timestamp = int(datetime.utcnow().timestamp())
            expires_at = int((datetime.utcnow() + timedelta(days=30)).timestamp())
            
            # Prepare conversation item
            conversation_item = {
                'session_id': session_id,
                'timestamp': timestamp,
                'query': query,
                'response': response,
                'expires_at': expires_at,
                'created_at': datetime.utcnow().isoformat()
            }
            
            if user_id:
                conversation_item['user_id'] = user_id
            
            # Store in DynamoDB (primary storage)
            self.conversation_table.put_item(Item=conversation_item)
            logger.debug(f"Stored conversation in DynamoDB for session {session_id}")
            
            # Store in Redis for fast access (if available)
            self._store_in_redis_cache(session_id, query, response, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return False
    
    def _store_in_redis_cache(self, session_id: str, query: str, response: str, timestamp: int):
        """Store conversation in Redis cache"""
        if not self.is_redis_available():
            return
        
        try:
            redis_key = f"conversation:{session_id}"
            conversation_data = {
                'query': query,
                'response': response,
                'timestamp': timestamp
            }
            
            # Store as a list (most recent first)
            self.redis_client.lpush(redis_key, json.dumps(conversation_data))
            
            # Keep only last 20 conversations
            self.redis_client.ltrim(redis_key, 0, 19)
            
            # Set expiration (24 hours)
            self.redis_client.expire(redis_key, 86400)
            
            logger.debug(f"Cached conversation in Redis for session {session_id}")
            
        except Exception as e:
            logger.warning(f"Failed to cache in Redis: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation items (most recent first)
        """
        try:
            # Try Redis first for speed
            if self.is_redis_available():
                cached_conversations = self._get_from_redis_cache(session_id, limit)
                if cached_conversations:
                    return cached_conversations
            
            # Fallback to DynamoDB
            return self._get_from_dynamodb(session_id, limit)
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    def _get_from_redis_cache(self, session_id: str, limit: int) -> List[Dict[str, Any]]:
        """Retrieve conversations from Redis cache"""
        try:
            redis_key = f"conversation:{session_id}"
            conversations = self.redis_client.lrange(redis_key, 0, limit - 1)
            
            if conversations:
                result = []
                for conv_json in conversations:
                    try:
                        conv_data = json.loads(conv_json)
                        result.append(conv_data)
                    except json.JSONDecodeError:
                        continue
                
                logger.debug(f"Retrieved {len(result)} conversations from Redis cache")
                return result
            
        except Exception as e:
            logger.warning(f"Redis cache retrieval failed: {e}")
        
        return []
    
    def _get_from_dynamodb(self, session_id: str, limit: int) -> List[Dict[str, Any]]:
        """Retrieve conversations from DynamoDB"""
        try:
            response = self.conversation_table.query(
                KeyConditionExpression='session_id = :session_id',
                ExpressionAttributeValues={':session_id': session_id},
                ScanIndexForward=False,  # Most recent first
                Limit=limit
            )
            
            conversations = response.get('Items', [])
            logger.debug(f"Retrieved {len(conversations)} conversations from DynamoDB")
            return conversations
            
        except Exception as e:
            logger.error(f"DynamoDB retrieval failed: {e}")
            return []
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences and learned patterns
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of user preferences
        """
        try:
            response = self.preferences_table.get_item(Key={'user_id': user_id})
            preferences = response.get('Item', {})
            
            # Remove DynamoDB metadata
            if preferences:
                preferences.pop('user_id', None)
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences
        
        Args:
            user_id: User identifier  
            preferences: Preferences dictionary
            
        Returns:
            bool: True if updated successfully
        """
        try:
            item = {
                'user_id': user_id,
                **preferences,
                'updated_at': datetime.utcnow().isoformat(),
                'version': preferences.get('version', 0) + 1
            }
            
            self.preferences_table.put_item(Item=item)
            logger.debug(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False
    
    def get_session_context(self, session_id: str, include_preferences: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive session context including history and preferences
        
        Args:
            session_id: Session identifier
            include_preferences: Whether to include user preferences
            
        Returns:
            Dictionary with session context
        """
        context = {
            'session_id': session_id,
            'conversation_history': self.get_conversation_history(session_id),
            'redis_available': self.is_redis_available(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add user preferences if available and requested
        if include_preferences and context['conversation_history']:
            # Try to get user_id from recent conversations
            for conv in context['conversation_history']:
                if 'user_id' in conv:
                    user_id = conv['user_id']
                    context['user_preferences'] = self.get_user_preferences(user_id)
                    context['user_id'] = user_id
                    break
        
        return context
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all data for a session (useful for testing or privacy)
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if cleared successfully
        """
        try:
            # Clear Redis cache
            if self.is_redis_available():
                redis_key = f"conversation:{session_id}"
                self.redis_client.delete(redis_key)
            
            # Note: We don't delete from DynamoDB for audit purposes
            # In production, you might want to add a "deleted" flag instead
            
            logger.info(f"Cleared session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False
    
    def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics about a conversation session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with conversation statistics
        """
        try:
            conversations = self.get_conversation_history(session_id, limit=100)
            
            if not conversations:
                return {'message': 'No conversations found for this session'}
            
            # Calculate statistics
            total_conversations = len(conversations)
            
            # Calculate average query length
            query_lengths = [len(conv.get('query', '').split()) for conv in conversations]
            avg_query_length = sum(query_lengths) / len(query_lengths) if query_lengths else 0
            
            # Find time span
            timestamps = [conv.get('timestamp', 0) for conv in conversations]
            if timestamps:
                first_timestamp = min(timestamps)
                last_timestamp = max(timestamps)
                time_span_minutes = (last_timestamp - first_timestamp) / 60
            else:
                time_span_minutes = 0
            
            return {
                'session_id': session_id,
                'total_conversations': total_conversations,
                'avg_query_length': round(avg_query_length, 1),
                'time_span_minutes': round(time_span_minutes, 1),
                'first_conversation': datetime.fromtimestamp(first_timestamp).isoformat() if timestamps else None,
                'last_conversation': datetime.fromtimestamp(last_timestamp).isoformat() if timestamps else None,
                'redis_cache_active': self.is_redis_available()
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation stats: {e}")
            return {'error': str(e)}

# Global memory instance
memory_instance = None

def get_memory() -> ConversationMemory:
    """Get or create the global memory instance"""
    global memory_instance
    if memory_instance is None:
        memory_instance = ConversationMemory()
    return memory_instance