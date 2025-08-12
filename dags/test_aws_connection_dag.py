from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def test_aws_connection(**context):
    """Test AWS S3 connection using Airflow S3Hook"""
    logger.info("🔍 Testing AWS S3 connection...")
    
    try:
        # Initialize S3 Hook with aws_default connection
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        # Test 1: List buckets
        logger.info("Testing bucket listing...")
        buckets = s3_hook.list_buckets()
        logger.info(f"✅ Successfully connected! Found {len(buckets)} buckets:")
        for bucket in buckets:
            logger.info(f"  - {bucket}")
        
        # Test 2: Check if threat-intel-pipeline bucket exists
        bucket_name = 'threat-intel-pipeline'
        bucket_exists = s3_hook.check_for_bucket(bucket_name)
        
        if bucket_exists:
            logger.info(f"✅ Bucket '{bucket_name}' exists and is accessible!")
            
            # Test 3: Try to list objects in the bucket
            try:
                keys = s3_hook.list_keys(bucket_name=bucket_name, max_keys=5)
                logger.info(f"✅ Found {len(keys)} objects in bucket:")
                for key in keys:
                    logger.info(f"  - {key}")
            except Exception as e:
                logger.info(f"ℹ️  Bucket is empty or no list permission: {e}")
                
        else:
            logger.warning(f"❌ Bucket '{bucket_name}' does not exist or is not accessible")
            logger.info("💡 You may need to create the bucket first")
        
        # Test 4: Try a simple upload test
        try:
            test_content = f"Connection test from Airflow - {datetime.now()}"
            test_key = "test/airflow_connection_test.txt"
            
            s3_hook.load_string(
                string_data=test_content,
                key=test_key,
                bucket_name=bucket_name,
                replace=True
            )
            logger.info(f"✅ Successfully uploaded test file to s3://{bucket_name}/{test_key}")
            
            # Clean up test file
            s3_hook.delete_objects(bucket=bucket_name, keys=[test_key])
            logger.info("✅ Test file cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Upload test failed: {e}")
        
        logger.info("🏁 AWS connection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ AWS connection test failed: {e}")
        raise

with DAG(
    dag_id='test_aws_connection',
    default_args=default_args,
    description='Test AWS S3 connection',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    max_active_runs=1,
    tags=['test', 'aws', 's3'],
) as dag:

    test_connection = PythonOperator(
        task_id='test_aws_s3_connection',
        python_callable=test_aws_connection,
        execution_timeout=timedelta(minutes=5),
    )

    test_connection
