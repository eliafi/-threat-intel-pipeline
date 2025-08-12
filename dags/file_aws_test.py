#!/usr/bin/env python3
"""
AWS connection test that writes results to file
"""
import os
from datetime import datetime
import logging
from pathlib import Path
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from botocore.exceptions import ClientError

def write_log(message):
    """Write message to log file"""
    with open('/opt/airflow/data/aws_test_results.txt', 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")

# Clear previous results
with open('/opt/airflow/data/aws_test_results.txt', 'w') as f:
    f.write("AWS Connection Test Results\n")
    f.write("=" * 50 + "\n")

write_log("🔍 Starting AWS connection test...")

# Test 1: Environment variables
access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region = os.environ.get('AWS_DEFAULT_REGION')

if access_key and secret_key:
    write_log(f"✅ Environment variables found: {access_key[:8]}...")
    write_log(f"   Region: {region or 'Not set'}")
else:
    write_log("❌ No environment variables found")

# Test 2: Airflow connection
try:
    from airflow.hooks.base import BaseHook
    conn = BaseHook.get_connection('aws_default')
    if conn.login and conn.password:
        write_log(f"✅ Airflow connection found: {conn.login[:8]}...")
        write_log(f"   Connection type: {conn.conn_type}")
        write_log(f"   Extra: {conn.extra}")
    else:
        write_log("❌ Airflow connection not found or incomplete")
        write_log(f"   Login: {conn.login}")
        write_log(f"   Password: {'Set' if conn.password else 'Not set'}")
except Exception as e:
    write_log(f"❌ Airflow connection error: {str(e)}")

# Test 3: boto3 S3 test
try:
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
    
    s3 = boto3.client('s3', region_name='eu-north-1')
    response = s3.list_buckets()
    write_log(f"✅ S3 connection successful! Found {len(response['Buckets'])} buckets")
    
    for bucket in response['Buckets']:
        write_log(f"   - {bucket['Name']}")
        
    # Test bucket access
    try:
        bucket_response = s3.head_bucket(Bucket='threat-intel-pipeline')
        write_log("✅ threat-intel-pipeline bucket is accessible!")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        write_log(f"❌ threat-intel-pipeline bucket error: {error_code}")
        
except NoCredentialsError:
    write_log("❌ S3 connection failed: No credentials found")
except ClientError as e:
    write_log(f"❌ S3 connection failed: {e.response['Error']['Code']}")
except Exception as e:
    write_log(f"❌ S3 connection failed: {str(e)}")

write_log("🏁 Test completed!")

print("Test completed - check data/aws_test_results.txt for results")

"""
Enhanced S3 upload module for threat intelligence data
Uses Airflow's S3Hook to properly handle AWS credentials
"""

logger = logging.getLogger(__name__)

class ThreatIntelS3Uploader:
    def __init__(self, aws_conn_id='aws_default', bucket_name='threat-intel-pipeline'):
        """
        Initialize S3 uploader with Airflow connection
        
        Args:
            aws_conn_id: Airflow connection ID for AWS credentials
            bucket_name: S3 bucket name for storing threat intel data
        """
        self.aws_conn_id = aws_conn_id
        self.bucket_name = bucket_name
        self.s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        
    def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            # Check if bucket exists
            if not self.s3_hook.check_for_bucket(self.bucket_name):
                logger.info(f"Creating bucket: {self.bucket_name}")
                self.s3_hook.create_bucket(
                    bucket_name=self.bucket_name,
                    region_name='eu-north-1'
                )
                logger.info(f"✅ Bucket {self.bucket_name} created successfully")
            else:
                logger.info(f"✅ Bucket {self.bucket_name} already exists")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                logger.info(f"✅ Bucket {self.bucket_name} already owned by you")
            elif error_code == 'BucketAlreadyExists':
                logger.warning(f"⚠️ Bucket {self.bucket_name} already exists (owned by someone else)")
                raise
            else:
                logger.error(f"❌ Error creating bucket: {error_code}")
                raise
                
    def upload_file(self, local_file_path: str, s3_key: str = None) -> bool:
        """
        Upload a file to S3 with automatic key generation
        
        Args:
            local_file_path: Path to local file
            s3_key: S3 object key (optional, auto-generated if not provided)
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Ensure bucket exists
            self.ensure_bucket_exists()
            
            # Generate S3 key if not provided
            if not s3_key:
                file_path = Path(local_file_path)
                timestamp = datetime.now()
                s3_key = f"threat-intel/processed/{timestamp.year:04d}/{timestamp.month:02d}/{timestamp.day:02d}/{file_path.name}"
            
            logger.info(f"📤 Uploading {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            
            # Upload file using S3Hook
            self.s3_hook.load_file(
                filename=local_file_path,
                key=s3_key,
                bucket_name=self.bucket_name,
                replace=True
            )
            
            logger.info(f"✅ Successfully uploaded to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload {local_file_path}: {str(e)}")
            return False
    
    def list_bucket_contents(self):
        """List all objects in the bucket"""
        try:
            keys = self.s3_hook.list_keys(bucket_name=self.bucket_name, prefix='threat-intel/')
            logger.info(f"📋 Found {len(keys)} objects in bucket:")
            for key in keys:
                logger.info(f"   - {key}")
            return keys
        except Exception as e:
            logger.error(f"❌ Failed to list bucket contents: {str(e)}")
            return []

def upload_processed_data(processed_filename: str) -> bool:
    """
    Airflow task function to upload processed threat intelligence data
    
    Args:
        processed_filename: Name of the processed CSV file
        
    Returns:
        bool: True if upload successful
    """
    uploader = ThreatIntelS3Uploader()
    
    # Full path to the processed file
    file_path = f"/opt/airflow/data/{processed_filename}"
    
    # Upload the file
    success = uploader.upload_file(file_path)
    
    if success:
        logger.info(f"✅ Successfully uploaded {processed_filename} to S3")
        # List bucket contents for verification
        uploader.list_bucket_contents()
    else:
        logger.error(f"❌ Failed to upload {processed_filename} to S3")
        raise Exception(f"S3 upload failed for {processed_filename}")
    
    return success

# Test function
def test_s3_connection():
    """Test S3 connection and upload functionality"""
    logger.info("🧪 Testing S3 connection...")
    
    try:
        uploader = ThreatIntelS3Uploader()
        
        # Test bucket access
        uploader.ensure_bucket_exists()
        
        # List contents
        uploader.list_bucket_contents()
        
        logger.info("✅ S3 connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ S3 connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    test_s3_connection()
