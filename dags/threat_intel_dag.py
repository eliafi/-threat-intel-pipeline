from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from etl.fetch_otx import fetch_otx_pulses
from etl.upload_s3 import upload_to_s3, create_s3_bucket_if_not_exists
import logging
import json
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

logger = logging.getLogger(__name__)

with DAG(
    dag_id='threat_intel_pipeline',
    default_args=default_args,
    description='ETL pipeline for threat intelligence',
    schedule=None,
    catchup=False,
    max_active_runs=1,
) as dag:

    def run_fetch_otx(**kwargs):
        logger.info("Fetch task started")
        try:


            api_key = Variable.get("OTX_API_KEY")
        except KeyError:
            logger.error("OTX_API_KEY variable not set")
            raise ValueError("OTX_API_KEY variable must be set in Airflow Variables")
        file_name = fetch_otx_pulses(api_key)
        logger.info(f"Fetch task completed, file saved: {file_name}")
        return file_name

    def transform_task(raw_filename: str, **kwargs) -> str:
        logger.info(f"Transform task started for {raw_filename}")
        file_path = f'/opt/airflow/data/{raw_filename}'
        with open(file_path) as f:
            data = json.load(f)
        df = pd.json_normalize(data.get('results', []))
        processed = raw_filename.replace('.json', '_processed.csv')
        df.to_csv(f'/opt/airflow/data/{processed}', index=False)
        logger.info(f"Transformation completed, processed file: {processed}")
        return processed

    def upload_to_s3_task(processed_filename: str, **kwargs) -> str:
        """Upload processed threat intelligence data to S3"""
        logger.info(f"S3 upload task started for {processed_filename}")
        
        # Get S3 configuration from Airflow Variables (with defaults)
        try:
            bucket_name = Variable.get("S3_BUCKET_NAME", default_var="threat-intel-data-lake")
            aws_conn_id = Variable.get("AWS_CONN_ID", default_var="aws_default")
        except Exception as e:
            logger.warning(f"Could not get S3 variables: {e}, using defaults")
            bucket_name = "threat-intel-data-lake"
            aws_conn_id = "aws_default"
        
        # Ensure bucket exists
        create_s3_bucket_if_not_exists(bucket_name=bucket_name, aws_conn_id=aws_conn_id)
        
        # Upload file
        s3_key = upload_to_s3(
            processed_filename=processed_filename,
            aws_conn_id=aws_conn_id,
            bucket_name=bucket_name
        )
        
        logger.info(f"Successfully uploaded to S3: s3://{bucket_name}/{s3_key}")
        return s3_key

    fetch = PythonOperator(
        task_id='fetch_otx_data',
        python_callable=run_fetch_otx,
        execution_timeout=timedelta(minutes=5),  # Much shorter timeout
        retries=1,  # Reduced retries
        retry_delay=timedelta(minutes=1),
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_task,
        execution_timeout=timedelta(minutes=15),  # Increased timeout
        retries=1,
        retry_delay=timedelta(minutes=1),
        op_args=['{{ ti.xcom_pull(task_ids="fetch_otx_data") }}'],
    )

    upload_s3 = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3_task,
        execution_timeout=timedelta(minutes=10),
        retries=2,
        retry_delay=timedelta(minutes=2),
        op_args=['{{ ti.xcom_pull(task_ids="transform_data") }}'],
    )

    # Define the workflow pipeline
    fetch >> transform >> upload_s3
