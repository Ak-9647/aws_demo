"""
AgentCore Gateway Integration Module

Provides secure, managed connections to external data sources and services
through Amazon Bedrock AgentCore Gateway.
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class GatewayConnection:
    name: str
    type: str
    endpoint: str
    status: str

class AgentCoreGateway:
    """AgentCore Gateway integration for secure external connections."""
    
    def __init__(self, gateway_name: str = None):
        self.gateway_name = gateway_name or os.getenv('AGENTCORE_GATEWAY_NAME', 'production-analytics-gateway')
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        
        try:
            self.bedrock_client = boto3.client('bedrock-agent', region_name=self.region)
            self.gateway_info = None
            self._initialize_gateway()
        except Exception as e:
            logger.warning(f"AgentCore Gateway not available: {e}")
            self.bedrock_client = None
            self.gateway_info = None
    
    def _initialize_gateway(self):
        """Initialize gateway connection and retrieve configuration."""
        if not self.bedrock_client:
            return
            
        try:
            response = self.bedrock_client.describe_gateway(
                gatewayName=self.gateway_name
            )
            self.gateway_info = response['gateway']
            logger.info(f"Connected to AgentCore Gateway: {self.gateway_name}")
        except Exception as e:
            logger.warning(f"Gateway initialization failed (using fallback): {e}")
            self.gateway_info = None
    
    def is_available(self) -> bool:
        """Check if gateway is available and operational."""
        return self.bedrock_client is not None and self.gateway_info is not None
    
    def get_gateway_status(self) -> Dict[str, Any]:
        """Get current gateway status and health."""
        if not self.is_available():
            return {
                "status": "unavailable", 
                "error": "Gateway not initialized or not available",
                "fallback_mode": True
            }
        
        try:
            response = self.bedrock_client.get_gateway_status(
                gatewayName=self.gateway_name
            )
            return {
                "status": response.get('status', 'unknown'),
                "connections": response.get('connections', []),
                "last_updated": response.get('lastUpdated'),
                "health_check": response.get('healthCheck', {}),
                "fallback_mode": False
            }
        except Exception as e:
            logger.error(f"Failed to get gateway status: {e}")
            return {"status": "error", "error": str(e), "fallback_mode": True}
    
    def execute_rest_call(self, endpoint_name: str, method: str, 
                         path: str, params: Optional[Dict] = None,
                         headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute REST API call through gateway with fallback."""
        if not self.is_available():
            return self._fallback_rest_call(endpoint_name, method, path, params, headers)
        
        try:
            request_data = {
                "endpoint": endpoint_name,
                "method": method,
                "path": path,
                "parameters": params or {},
                "headers": headers or {}
            }
            
            response = self.bedrock_client.invoke_gateway(
                gatewayName=self.gateway_name,
                gatewayType="REST",
                requestData=json.dumps(request_data)
            )
            
            result = json.loads(response['responseData'])
            result['gateway_used'] = True
            return result
            
        except Exception as e:
            logger.error(f"Gateway REST call failed, using fallback: {e}")
            return self._fallback_rest_call(endpoint_name, method, path, params, headers)
    
    def _fallback_rest_call(self, endpoint_name: str, method: str, 
                           path: str, params: Optional[Dict] = None,
                           headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Fallback REST call implementation."""
        import requests
        
        # Simulated endpoint mapping for development
        endpoint_urls = {
            "market-data-api": "https://api.marketdata.com/v1",
            "weather-api": "https://api.weather.com/v1"
        }
        
        base_url = endpoint_urls.get(endpoint_name)
        if not base_url:
            return {
                "error": f"Unknown endpoint: {endpoint_name}",
                "success": False,
                "gateway_used": False
            }
        
        try:
            url = f"{base_url}{path}"
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "success": response.status_code < 400,
                "gateway_used": False
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "gateway_used": False
            }
    
    def execute_database_query(self, connection_name: str, query: str,
                              parameters: Optional[List] = None) -> Dict[str, Any]:
        """Execute database query through gateway with fallback."""
        if not self.is_available():
            return self._fallback_database_query(connection_name, query, parameters)
        
        try:
            request_data = {
                "connection": connection_name,
                "query": query,
                "parameters": parameters or []
            }
            
            response = self.bedrock_client.invoke_gateway(
                gatewayName=self.gateway_name,
                gatewayType="DATABASE",
                requestData=json.dumps(request_data)
            )
            
            result = json.loads(response['responseData'])
            result['gateway_used'] = True
            return result
            
        except Exception as e:
            logger.error(f"Gateway database query failed, using fallback: {e}")
            return self._fallback_database_query(connection_name, query, parameters)
    
    def _fallback_database_query(self, connection_name: str, query: str,
                                parameters: Optional[List] = None) -> Dict[str, Any]:
        """Fallback database query implementation."""
        try:
            # Import database integration for fallback
            from database_integration import DatabaseIntegration
            
            db = DatabaseIntegration()
            result = db.execute_query(query, parameters)
            
            return {
                "data": result,
                "success": True,
                "gateway_used": False,
                "connection": connection_name
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "gateway_used": False,
                "connection": connection_name
            }
    
    def access_s3_data(self, bucket_name: str, operation: str,
                       key: str, data: Optional[bytes] = None) -> Dict[str, Any]:
        """Access S3 data through gateway with fallback."""
        if not self.is_available():
            return self._fallback_s3_access(bucket_name, operation, key, data)
        
        try:
            request_data = {
                "bucket": bucket_name,
                "operation": operation,
                "key": key
            }
            
            if data and operation in ["PUT", "UPLOAD"]:
                request_data["data"] = data.decode('utf-8') if isinstance(data, bytes) else data
            
            response = self.bedrock_client.invoke_gateway(
                gatewayName=self.gateway_name,
                gatewayType="S3",
                requestData=json.dumps(request_data)
            )
            
            result = json.loads(response['responseData'])
            result['gateway_used'] = True
            return result
            
        except Exception as e:
            logger.error(f"Gateway S3 access failed, using fallback: {e}")
            return self._fallback_s3_access(bucket_name, operation, key, data)
    
    def _fallback_s3_access(self, bucket_name: str, operation: str,
                           key: str, data: Optional[bytes] = None) -> Dict[str, Any]:
        """Fallback S3 access implementation."""
        try:
            s3_client = boto3.client('s3', region_name=self.region)
            
            if operation.upper() == "GET":
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                return {
                    "data": response['Body'].read(),
                    "success": True,
                    "gateway_used": False
                }
            
            elif operation.upper() == "PUT":
                s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)
                return {
                    "success": True,
                    "gateway_used": False
                }
            
            elif operation.upper() == "LIST":
                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=key)
                return {
                    "objects": response.get('Contents', []),
                    "success": True,
                    "gateway_used": False
                }
            
            else:
                return {
                    "error": f"Unsupported operation: {operation}",
                    "success": False,
                    "gateway_used": False
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "gateway_used": False
            }
    
    def list_available_connections(self) -> List[GatewayConnection]:
        """List all available gateway connections."""
        connections = []
        
        if not self.is_available():
            # Return simulated connections for development
            return [
                GatewayConnection("analytics-postgres", "DATABASE", "PostgreSQL Database", "simulated"),
                GatewayConnection("data-warehouse", "DATABASE", "Redshift Database", "simulated"),
                GatewayConnection("analytics-data-lake", "S3", "S3 Bucket", "simulated"),
                GatewayConnection("market-data-api", "REST", "Market Data API", "simulated")
            ]
        
        try:
            for gateway_config in self.gateway_info.get('gateways', []):
                gateway_type = gateway_config.get('type')
                
                if gateway_type == 'REST':
                    for endpoint in gateway_config.get('configuration', {}).get('endpoints', []):
                        connections.append(GatewayConnection(
                            name=endpoint['name'],
                            type='REST',
                            endpoint=endpoint['url'],
                            status='active'
                        ))
                
                elif gateway_type == 'DATABASE':
                    for conn in gateway_config.get('configuration', {}).get('connections', []):
                        connections.append(GatewayConnection(
                            name=conn['name'],
                            type=conn['type'],
                            endpoint=f"{conn['type']} Database",
                            status='active'
                        ))
                
                elif gateway_type == 'S3':
                    for bucket in gateway_config.get('configuration', {}).get('buckets', []):
                        connections.append(GatewayConnection(
                            name=bucket['name'],
                            type='S3',
                            endpoint=bucket['bucket'],
                            status='active'
                        ))
        
        except Exception as e:
            logger.error(f"Failed to list connections: {e}")
        
        return connections

# Global gateway instance
_gateway_instance = None

def get_gateway() -> AgentCoreGateway:
    """Get singleton gateway instance."""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = AgentCoreGateway()
    return _gateway_instance

# Example usage and testing
if __name__ == "__main__":
    gateway = AgentCoreGateway()
    
    # Test gateway status
    status = gateway.get_gateway_status()
    print(f"Gateway Status: {status}")
    
    # List available connections
    connections = gateway.list_available_connections()
    print(f"Available Connections: {len(connections)}")
    for conn in connections:
        print(f"  - {conn.name} ({conn.type}): {conn.endpoint} [{conn.status}]")
    
    # Test database query
    db_result = gateway.execute_database_query(
        "analytics-postgres",
        "SELECT 'Gateway test' as message, NOW() as timestamp;"
    )
    print(f"Database Test: {db_result}")