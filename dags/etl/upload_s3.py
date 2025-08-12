import os
import logging
from datetime import datetime
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

logger = logging.getLogger(__name__)

def upload_to_s3(processed_filename: str, aws_conn_id: str = 'aws_default', bucket_name: str = 'threat-intel-data-lake'):
    """
    Upload processed threat intelligence data to S3
    
    Args:
        processed_filename: Name of the processed CSV file to upload
        aws_conn_id: Airflow connection ID for AWS credentials
        bucket_name: S3 bucket name for threat intelligence data
    
    Returns:
        str: S3 key path where file was uploaded
    """
    try:
        # Initialize S3 Hook
        s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        
        # Local file path
        local_file_path = f'/opt/airflow/data/{processed_filename}'
        
        # S3 key with date partitioning for better organization
        date_partition = datetime.now().strftime('%Y/%m/%d')
        s3_key = f'threat-intel/processed/{date_partition}/{processed_filename}'
        
        # Check if local file exists
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File {local_file_path} not found")
        
        logger.info(f"Uploading {local_file_path} to s3://{bucket_name}/{s3_key}")
        
        # Upload file to S3
        s3_hook.load_file(
            filename=local_file_path,
            key=s3_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        # Get file size for logging
        file_size = os.path.getsize(local_file_path)
        logger.info(f"Successfully uploaded {processed_filename} ({file_size} bytes) to S3")
        
        return s3_key
        
    except Exception as e:
        logger.error(f"Failed to upload {processed_filename} to S3: {str(e)}")
        raise

def create_s3_bucket_if_not_exists(bucket_name: str, aws_conn_id: str = 'aws_default', region: str = 'eu-north-1'):
    """
    Create S3 bucket if it doesn't exist
    
    Args:
        bucket_name: Name of the S3 bucket to create
        aws_conn_id: Airflow connection ID for AWS credentials
        region: AWS region to create bucket in (default: eu-north-1)
    """
    try:
        s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        
        if not s3_hook.check_for_bucket(bucket_name):
            logger.info(f"Bucket {bucket_name} does not exist. Creating...")
            s3_hook.create_bucket(bucket_name=bucket_name, region_name=region)
            logger.info(f"Successfully created bucket {bucket_name}")
        else:
            logger.info(f"Bucket {bucket_name} already exists")
            
    except Exception as e:
        logger.error(f"Failed to create bucket {bucket_name}: {str(e)}")
        raise

def list_s3_threat_intel_files(bucket_name: str, aws_conn_id: str = 'aws_default', prefix: str = 'threat-intel/'):
    """
    List all threat intelligence files in S3 bucket
    
    Args:
        bucket_name: S3 bucket name
        aws_conn_id: Airflow connection ID for AWS credentials
        prefix: S3 prefix to filter files
    
    Returns:
        list: List of S3 keys matching the prefix
    """
    try:
        s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        
        keys = s3_hook.list_keys(bucket_name=bucket_name, prefix=prefix)
        logger.info(f"Found {len(keys)} threat intelligence files in S3")
        
        return keys
        
    except Exception as e:
        logger.error(f"Failed to list S3 files: {str(e)}")
        raise
