"""
Lambda function for memory cleanup
Removes old conversation history and optimizes storage
"""

import boto3
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal

def lambda_handler(event, context):
    """
    Clean up old conversation history and optimize memory usage
    """
    
    dynamodb = boto3.resource('dynamodb')
    conversation_table = dynamodb.Table(os.environ['CONVERSATION_TABLE'])
    
    try:
        # Calculate cutoff time (30 days ago)
        cutoff_time = datetime.now() - timedelta(days=30)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        # Scan for old conversations
        response = conversation_table.scan(
            FilterExpression='#ts < :cutoff',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={':cutoff': cutoff_timestamp}
        )
        
        deleted_count = 0
        
        # Delete old conversations
        with conversation_table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(
                    Key={
                        'session_id': item['session_id'],
                        'timestamp': item['timestamp']
                    }
                )
                deleted_count += 1
        
        # Log cleanup results
        print(f"Cleaned up {deleted_count} old conversation records")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully cleaned up {deleted_count} records',
                'cutoff_date': cutoff_time.isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }