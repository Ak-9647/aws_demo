"""
Simple Analytics Gateway Target Lambda Function
Minimal implementation without external dependencies
"""

import json
import logging
import boto3
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Simple Lambda handler for AgentCore Gateway requests
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Extract request information
        http_method = event.get('httpMethod', 'POST')
        path = event.get('path', '/')
        body = event.get('body', '{}')
        
        # Parse request body
        if isinstance(body, str):
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                request_data = {}
        else:
            request_data = body
        
        # Route request based on path
        if path == '/health':
            return create_response(200, {
                'status': 'healthy',
                'message': 'Gateway target is working',
                'timestamp': context.aws_request_id if context else 'unknown'
            })
        elif path == '/query':
            return create_response(200, {
                'message': 'Query endpoint received',
                'query': request_data.get('sql', 'No SQL provided'),
                'status': 'success'
            })
        elif path == '/schema':
            return create_response(200, {
                'database_name': 'analytics',
                'tables': [
                    {
                        'table_name': 'sample_table',
                        'columns': [
                            {'name': 'id', 'type': 'integer'},
                            {'name': 'name', 'type': 'varchar'}
                        ]
                    }
                ]
            })
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return create_response(500, {'error': 'Internal server error', 'details': str(e)})

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create HTTP response for Lambda
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body, default=str)
    }