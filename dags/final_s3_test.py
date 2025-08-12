#!/usr/bin/env python3
"""
Final test of S3 connection with correct bucket name
"""
import logging
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def final_s3_test():
    """Final comprehensive S3 test"""
    bucket_name = "threat-intel-data-lake"
    
    logger.info("🚀 Final S3 Connection Test")
    logger.info("=" * 50)
    logger.info(f"Bucket: {bucket_name}")
    logger.info(f"Region: eu-north-1")
    logger.info(f"Connection: aws_default")
    logger.info("=" * 50)
    
    try:
        # Initialize S3Hook
        s3_hook = S3Hook(aws_conn_id='aws_default')
        logger.info("✅ S3Hook initialized successfully")
        
        # Test bucket access
        if s3_hook.check_for_bucket(bucket_name):
            logger.info(f"✅ Bucket '{bucket_name}' is accessible!")
            
            # List objects
            try:
                keys = s3_hook.list_keys(bucket_name=bucket_name, max_items=5)
                logger.info(f"✅ Listed {len(keys)} objects in bucket")
                for key in keys:
                    logger.info(f"   📄 {key}")
            except Exception as e:
                logger.warning(f"⚠️ Could not list objects: {e}")
            
            # Test upload with a tiny file
            try:
                test_content = "Connection test successful!"
                test_file = "/tmp/connection_test.txt"
                
                with open(test_file, 'w') as f:
                    f.write(test_content)
                
                test_key = "test/final_connection_test.txt"
                s3_hook.load_file(
                    filename=test_file,
                    key=test_key,
                    bucket_name=bucket_name,
                    replace=True
                )
                
                logger.info(f"✅ Successfully uploaded test file!")
                logger.info(f"   📍 Location: s3://{bucket_name}/{test_key}")
                
                # Verify and clean up
                if s3_hook.check_for_key(test_key, bucket_name):
                    logger.info("✅ Upload verified!")
                    s3_hook.delete_objects(bucket=bucket_name, keys=[test_key])
                    logger.info("✅ Test file cleaned up")
                
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDenied':
                    logger.error("❌ Upload failed: Access Denied")
                    logger.error("💡 Your IAM user needs s3:PutObject permission")
                else:
                    logger.error(f"❌ Upload failed: {error_code}")
                return False
                
        else:
            logger.error(f"❌ Bucket '{bucket_name}' is not accessible")
            return False
            
    except Exception as e:
        logger.error(f"❌ S3 test failed: {e}")
        return False

def main():
    """Run the final test"""
    success = final_s3_test()
    
    logger.info("\n" + "=" * 50)
    if success:
        logger.info("🎉 SUCCESS! Your S3 connection is working perfectly!")
        logger.info("Your threat intelligence pipeline is ready to run!")
        logger.info("\nNext steps:")
        logger.info("1. Go to Airflow UI: http://localhost:8080")
        logger.info("2. Run the 'threat_intel_pipeline' DAG")
        logger.info("3. Monitor the data uploads to S3")
    else:
        logger.error("❌ S3 connection issues remain")
        logger.error("Please check IAM permissions for your user")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
