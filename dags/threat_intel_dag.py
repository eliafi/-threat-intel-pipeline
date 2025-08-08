from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from etl.fetch_otx import fetch_otx_pulses
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

    fetch >> transform
