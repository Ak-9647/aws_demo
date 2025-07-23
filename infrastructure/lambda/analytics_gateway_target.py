"""
Analytics Gateway Target Lambda Function
Handles requests from AgentCore Gateway for analytics operations
"""

import json
import logging
import boto3
import os
import psycopg2
import requests
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

# Initialize AWS clients
secrets_client = boto3.client('secretsmanager')

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for AgentCore Gateway requests
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
        if path == '/analyze':
            return handle_analyze_request(request_data)
        elif path == '/query':
            return handle_database_query(request_data)
        elif path == '/schema':
            return handle_schema_request(request_data)
        elif path == '/health':
            return handle_health_check()
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return create_response(500, {'error': 'Internal server error'})

def handle_analyze_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle analytics analysis requests
    """
    try:
        # Extract analysis parameters
        data = request_data.get('data', [])
        analysis_type = request_data.get('analysis_type', 'statistical')
        parameters = request_data.get('parameters', {})
        
        # Perform basic analysis (in production, this would call external services)
        if analysis_type == 'statistical':
            results = perform_statistical_analysis(data, parameters)
        elif analysis_type == 'anomaly_detection':
            results = perform_anomaly_detection(data, parameters)
        elif analysis_type == 'predictive':
            results = perform_predictive_analysis(data, parameters)
        else:
            return create_response(400, {'error': f'Unsupported analysis type: {analysis_type}'})
        
        response = {
            'analysis_id': f'analysis_{context.aws_request_id if context else "unknown"}',
            'results': results,
            'processing_time': 0.5,  # Simulated processing time
            'status': 'completed'
        }
        
        return create_response(200, response)
        
    except Exception as e:
        logger.error(f"Error in analyze request: {str(e)}")
        return create_response(500, {'error': 'Analysis failed'})

def handle_database_query(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle database query requests
    """
    try:
        sql = request_data.get('sql', '')
        parameters = request_data.get('parameters', [])
        timeout = request_data.get('timeout', 30)
        max_rows = request_data.get('max_rows', 1000)
        
        if not sql:
            return create_response(400, {'error': 'SQL query is required'})
        
        # Get database connection string from Secrets Manager
        connection_string = get_secret_value(os.getenv('POSTGRES_CONNECTION_STRING'))
        
        # Execute query
        results = execute_database_query(connection_string, sql, parameters, max_rows, timeout)
        
        return create_response(200, results)
        
    except Exception as e:
        logger.error(f"Error in database query: {str(e)}")
        return create_response(500, {'error': 'Database query failed'})

def handle_schema_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle database schema requests
    """
    try:
        table_name = request_data.get('table_name')
        
        # Get database connection string from Secrets Manager
        connection_string = get_secret_value(os.getenv('POSTGRES_CONNECTION_STRING'))
        
        # Get schema information
        schema_info = get_database_schema(connection_string, table_name)
        
        return create_response(200, schema_info)
        
    except Exception as e:
        logger.error(f"Error in schema request: {str(e)}")
        return create_response(500, {'error': 'Schema request failed'})

def handle_health_check() -> Dict[str, Any]:
    """
    Handle health check requests
    """
    try:
        # Check database connectivity
        connection_string = get_secret_value(os.getenv('POSTGRES_CONNECTION_STRING'))
        db_healthy = test_database_connection(connection_string)
        
        health_status = {
            'status': 'healthy' if db_healthy else 'degraded',
            'database': 'healthy' if db_healthy else 'unhealthy',
            'timestamp': context.aws_request_id if context else "unknown"
        }
        
        return create_response(200, health_status)
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return create_response(500, {'status': 'unhealthy', 'error': str(e)})

def perform_statistical_analysis(data: list, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform statistical analysis on the data
    """
    if not data:
        return {'summary': 'No data provided for analysis'}
    
    # Basic statistical analysis (simplified)
    numeric_data = []
    for item in data:
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, (int, float)):
                    numeric_data.append(value)
        elif isinstance(item, (int, float)):
            numeric_data.append(item)
    
    if not numeric_data:
        return {'summary': 'No numeric data found for statistical analysis'}
    
    # Calculate basic statistics
    mean_val = sum(numeric_data) / len(numeric_data)
    sorted_data = sorted(numeric_data)
    median_val = sorted_data[len(sorted_data) // 2]
    min_val = min(numeric_data)
    max_val = max(numeric_data)
    
    return {
        'summary': f'Statistical analysis of {len(numeric_data)} data points',
        'metrics': {
            'mean': round(mean_val, 2),
            'median': median_val,
            'min': min_val,
            'max': max_val,
            'count': len(numeric_data)
        },
        'insights': [
            f'Average value is {round(mean_val, 2)}',
            f'Data range spans from {min_val} to {max_val}',
            f'Median value is {median_val}'
        ]
    }

def perform_anomaly_detection(data: list, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform anomaly detection on the data
    """
    # Simplified anomaly detection using IQR method
    numeric_data = extract_numeric_data(data)
    
    if len(numeric_data) < 4:
        return {'summary': 'Insufficient data for anomaly detection'}
    
    # Calculate IQR
    sorted_data = sorted(numeric_data)
    q1 = sorted_data[len(sorted_data) // 4]
    q3 = sorted_data[3 * len(sorted_data) // 4]
    iqr = q3 - q1
    
    # Define outlier bounds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Find anomalies
    anomalies = [x for x in numeric_data if x < lower_bound or x > upper_bound]
    
    return {
        'summary': f'Anomaly detection completed on {len(numeric_data)} data points',
        'metrics': {
            'total_points': len(numeric_data),
            'anomalies_found': len(anomalies),
            'anomaly_rate': round(len(anomalies) / len(numeric_data) * 100, 2),
            'bounds': {'lower': lower_bound, 'upper': upper_bound}
        },
        'insights': [
            f'Found {len(anomalies)} anomalous data points',
            f'Anomaly rate: {round(len(anomalies) / len(numeric_data) * 100, 2)}%',
            f'Normal range: {round(lower_bound, 2)} to {round(upper_bound, 2)}'
        ]
    }

def perform_predictive_analysis(data: list, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform predictive analysis on the data
    """
    numeric_data = extract_numeric_data(data)
    
    if len(numeric_data) < 3:
        return {'summary': 'Insufficient data for predictive analysis'}
    
    # Simple linear trend prediction
    n = len(numeric_data)
    x_values = list(range(n))
    
    # Calculate linear regression coefficients
    sum_x = sum(x_values)
    sum_y = sum(numeric_data)
    sum_xy = sum(x * y for x, y in zip(x_values, numeric_data))
    sum_x2 = sum(x * x for x in x_values)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    # Predict next few values
    predictions = []
    for i in range(3):  # Predict next 3 values
        pred_value = slope * (n + i) + intercept
        predictions.append(round(pred_value, 2))
    
    return {
        'summary': f'Predictive analysis based on {len(numeric_data)} data points',
        'metrics': {
            'trend_slope': round(slope, 4),
            'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
            'predictions': predictions
        },
        'insights': [
            f'Data shows {"upward" if slope > 0 else "downward" if slope < 0 else "stable"} trend',
            f'Predicted next values: {", ".join(map(str, predictions))}',
            f'Trend strength: {"strong" if abs(slope) > 1 else "moderate" if abs(slope) > 0.1 else "weak"}'
        ]
    }

def extract_numeric_data(data: list) -> list:
    """
    Extract numeric values from mixed data structure
    """
    numeric_data = []
    for item in data:
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, (int, float)):
                    numeric_data.append(value)
        elif isinstance(item, (int, float)):
            numeric_data.append(item)
    return numeric_data

def execute_database_query(connection_string: str, sql: str, parameters: list, max_rows: int, timeout: int) -> Dict[str, Any]:
    """
    Execute SQL query against the database
    """
    import time
    start_time = time.time()
    
    try:
        # Parse connection string (simplified)
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Execute query with timeout
        cursor.execute(sql, parameters)
        
        # Fetch results
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(max_rows)
        else:
            columns = []
            rows = []
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        cursor.close()
        conn.close()
        
        return {
            'query_id': f'query_{int(time.time())}',
            'columns': [{'name': col, 'type': 'unknown', 'nullable': True} for col in columns],
            'rows': rows,
            'row_count': len(rows),
            'execution_time_ms': round(execution_time, 2),
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'query_id': f'query_{int(time.time())}',
            'columns': [],
            'rows': [],
            'row_count': 0,
            'execution_time_ms': round((time.time() - start_time) * 1000, 2),
            'status': 'error',
            'error': str(e)
        }

def get_database_schema(connection_string: str, table_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get database schema information
    """
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Query for table information
        if table_name:
            cursor.execute("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
        else:
            cursor.execute("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Organize results by table
        tables = {}
        for row in results:
            table, column, data_type, nullable = row
            if table not in tables:
                tables[table] = {
                    'table_name': table,
                    'schema_name': 'public',
                    'columns': [],
                    'indexes': [],
                    'row_count': 0
                }
            
            tables[table]['columns'].append({
                'column_name': column,
                'data_type': data_type,
                'is_nullable': nullable == 'YES',
                'default_value': None,
                'is_primary_key': False,
                'is_foreign_key': False
            })
        
        return {
            'database_name': 'analytics',
            'tables': list(tables.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}")
        return {
            'database_name': 'analytics',
            'tables': [],
            'error': str(e)
        }

def test_database_connection(connection_string: str) -> bool:
    """
    Test database connectivity
    """
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def get_secret_value(secret_arn: str) -> str:
    """
    Get secret value from AWS Secrets Manager
    """
    try:
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        secret_data = json.loads(response['SecretString'])
        return secret_data.get('connection_string', '')
    except Exception as e:
        logger.error(f"Error getting secret: {str(e)}")
        raise

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