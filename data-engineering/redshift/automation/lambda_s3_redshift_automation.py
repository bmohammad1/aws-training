import json
import boto3
import logging
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
redshift_data = boto3.client('redshift-data')

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Process each S3 event
        for record in event['Records']:
            if record['eventName'].startswith('ObjectCreated'):
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                logger.info(f"Processing: s3://{bucket_name}/{object_key}")
                
                # Send notification
                send_notification(bucket_name, object_key)
                
                # Process if parquet file
                if object_key.endswith('.parquet'):
                    process_parquet_file(bucket_name, object_key)
        
        return {'statusCode': 200, 'body': 'Success'}
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def send_notification(bucket_name, object_key):
    """Send SNS notification"""
    try:
        message = f"""
    NEW FILE UPLOADED TO S3!

Bucket: {bucket_name}
File: {object_key}
Time: {datetime.utcnow().isoformat()}
Status: Starting Redshift processing...

This is an automated notification from your S3-Redshift pipeline.
        """
        
        sns_client.publish(
            TopicArn=os.getenv('SNS_TOPIC_ARN'),
            Message=message,
            Subject=f"S3 Upload: {object_key.split('/')[-1]}"
        )
        
        logger.info("Upload notification sent successfully")
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")

def process_parquet_file(bucket_name, object_key):
    """Process parquet file for Redshift"""
    try:
        # Determine table name based on your file patterns
        if 'order_flattened' in object_key or 'orders/' in object_key:
            table_name = 'orders'
            primary_key = 'order_orderId'
        elif 'order_items' in object_key or 'order-items/' in object_key:
            table_name = 'order_items'
            primary_key = 'itemId'
        else:
            logger.info(f"Unknown file pattern: {object_key}. Skipping processing.")
            return
        
        logger.info(f"Detected file type: {table_name} table")
        
        # Perform UPSERT operation
        perform_upsert(bucket_name, object_key, table_name, primary_key)
        
    except Exception as e:
        logger.error(f"Error processing parquet: {str(e)}")
        send_error_notification(bucket_name, object_key, str(e))

def perform_upsert(bucket_name, object_key, table_name, primary_key):
    """Perform UPSERT operation using staging table"""
    try:
        staging_table = f"{table_name}_staging"
        
        logger.info(f"Starting UPSERT operation for {table_name}")
        
        # Step 1: Clear staging table
        clear_sql = f"DELETE FROM {staging_table}"
        
        # Step 2: Load data into staging table (with ACCESS_KEY_ID and SECRET_ACCESS_KEY)
        copy_sql = f"""
        COPY {staging_table}
        FROM 's3://{bucket_name}/{object_key}'
        ACCESS_KEY_ID '{os.environ.get('AWS_ACCESS_KEY_ID')}'
        SECRET_ACCESS_KEY '{os.environ.get('AWS_SECRET_ACCESS_KEY')}'
        SESSION_TOKEN '{os.environ.get('AWS_SESSION_TOKEN')}'
        FORMAT AS PARQUET
        """
        
        # Step 3: Delete existing records that will be updated
        delete_sql = f"""
        DELETE FROM {table_name}
        WHERE {primary_key} IN (SELECT {primary_key} FROM {staging_table})
        """
        
        # Step 4: Insert all records from staging
        insert_sql = f"INSERT INTO {table_name} SELECT * FROM {staging_table}"
        
        # Execute all SQL commands
        sql_commands = [
            ("Clear staging table", clear_sql),
            ("Load data to staging", copy_sql),
            ("Delete existing records", delete_sql),
            ("Insert new records", insert_sql)
        ]
        
        for step_name, sql in sql_commands:
            logger.info(f"Executing: {step_name}")
            logger.info(f"SQL: {sql[:200]}...")  # Log first 200 chars for debugging
            
            response = redshift_data.execute_statement(
                WorkgroupName=os.getenv('REDSHIFT_WORKGROUP'),
                Database=os.getenv('REDSHIFT_DATABASE'),
                Sql=sql
            )
            
            query_id = response['Id']
            wait_for_query_completion(query_id)
            logger.info(f"Completed: {step_name}")
        
        # Send success notification
        send_success_notification(bucket_name, object_key, table_name)
        
    except Exception as e:
        logger.error(f"Error in UPSERT: {str(e)}")
        send_error_notification(bucket_name, object_key, str(e))
        raise

def wait_for_query_completion(query_id, max_wait_time=300):
    """Wait for Redshift query to complete"""
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        response = redshift_data.describe_statement(Id=query_id)
        status = response['Status']
        
        if status == 'FINISHED':
            logger.info(f"Query {query_id} completed successfully")
            return
        elif status in ['FAILED', 'ABORTED']:
            error_msg = response.get('Error', 'Unknown error')
            raise Exception(f"Query {query_id} failed: {error_msg}")
        
        time.sleep(5)
    
    raise Exception(f"Query {query_id} timed out after {max_wait_time} seconds")

def send_success_notification(bucket_name, object_key, table_name):
    """Send success notification"""
    try:
        message = f"""
    SUCCESS: Redshift Load Complete!

File: s3://{bucket_name}/{object_key}
Table: {table_name}
Operation: UPSERT (Delete + Insert)
Completed: {datetime.utcnow().isoformat()}
Status: Data loaded successfully

Your data is now available in Redshift for analysis!
        """
        
        sns_client.publish(
            TopicArn=os.getenv('SNS_TOPIC_ARN'),
            Message=message,
            Subject=f"SUCCESS: {table_name} data loaded"
        )
        
        logger.info("Success notification sent")
        
    except Exception as e:
        logger.error(f"Error sending success notification: {str(e)}")

def send_error_notification(bucket_name, object_key, error_msg):
    """Send error notification"""
    try:
        message = f"""
    ERROR: Redshift Load Failed

File: s3://{bucket_name}/{object_key}
Time: {datetime.utcnow().isoformat()}
Error: {error_msg}

Please check CloudWatch logs for detailed information:
Log Group: /aws/lambda/S3RedshiftAutomation

Troubleshooting steps:
1. Verify file format is correct
2. Check Redshift table exists
3. Verify IAM permissions
        """
        
        sns_client.publish(
            TopicArn=os.getenv('SNS_TOPIC_ARN'),
            Message=message,
            Subject="ERROR: Redshift Load Failed"
        )
        
    except Exception as e:
        logger.error(f"Error sending error notification: {str(e)}")