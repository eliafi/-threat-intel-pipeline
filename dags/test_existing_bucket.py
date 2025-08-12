#!/usr/bin/env python3
"""
Test access to existing threat-intel-data-lake bucket
"""
import logging
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_existing_bucket():
    """Test access to the existing threat-intel-data-lake bucket"""
    bucket_name = "threat-intel-data-lake"
    
    logger.info(f"🔍 Testing access to existing bucket: {bucket_name}")
    
    try:
        # Initialize S3Hook with your Airflow connection
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        # Check if bucket exists and is accessible
        if s3_hook.check_for_bucket(bucket_name):
            logger.info(f"✅ Bucket '{bucket_name}' exists and is accessible!")
            
            # List existing objects
            try:
                keys = s3_hook.list_keys(bucket_name=bucket_name, max_items=10)
                logger.info(f"📋 Found {len(keys)} objects in bucket:")
                for key in keys[:5]:  # Show first 5
                    logger.info(f"   - {key}")
                    
                if len(keys) > 5:
                    logger.info(f"   ... and {len(keys) - 5} more objects")
                    
            except Exception as e:
                logger.warning(f"Could not list objects: {e}")
            
            # Test upload capability with a small test file
            test_upload(s3_hook, bucket_name)
            
            return True
            
        else:
            logger.error(f"❌ Bucket '{bucket_name}' does not exist or is not accessible")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ AWS Client Error: {error_code}")
        logger.error(f"Error message: {e.response['Error']['Message']}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def test_upload(s3_hook, bucket_name):
    """Test uploading a small file"""
    logger.info("🧪 Testing upload capability...")
    
    try:
        # Create a test file
        test_content = f"Test upload from threat-intel-pipeline at {logging.Formatter().formatTime()}"
        test_file_path = "/tmp/test_upload.txt"
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        # Upload test file
        test_key = "test/connection_test.txt"
        s3_hook.load_file(
            filename=test_file_path,
            key=test_key,
            bucket_name=bucket_name,
            replace=True
        )
        
        logger.info(f"✅ Successfully uploaded test file to s3://{bucket_name}/{test_key}")
        
        # Verify the upload by checking if the object exists
        if s3_hook.check_for_key(key=test_key, bucket_name=bucket_name):
            logger.info("✅ Test file verified in S3!")
            
            # Clean up test file
            s3_hook.delete_objects(bucket=bucket_name, keys=[test_key])
            logger.info("✅ Test file cleaned up")
        else:
            logger.warning("⚠️ Test file upload might have failed - object not found")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ Upload failed: {error_code}")
        
        if error_code == 'AccessDenied':
            logger.error("💡 Your IAM user needs s3:PutObject permission")
        elif error_code == 'NoSuchBucket':
            logger.error("💡 The bucket doesn't exist")
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Upload test failed: {e}")
        return False

def main():
    """Run the bucket access test"""
    logger.info("=" * 60)
    logger.info("🪣 Testing Existing S3 Bucket Access")
    logger.info("=" * 60)
    
    success = test_existing_bucket()
    
    if success:
        logger.info("\n✅ SUCCESS: You can use the existing bucket!")
        logger.info("Your threat intelligence pipeline is ready to upload data.")
    else:
        logger.error("\n❌ FAILURE: Cannot access the existing bucket")
        logger.error("You may need to check IAM permissions or bucket settings.")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
