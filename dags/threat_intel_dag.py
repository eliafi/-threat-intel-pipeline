from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from etl.fetch_otx import fetch_otx_pulses

def run_fetch_otx():
    api_key = 'YOUR_OTX_API_KEY'  # Use Airflow Variables or Secrets in production
    fetch_otx_pulses(api_key)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'threat_intel_pipeline',
    default_args=default_args,
    description='ETL pipeline for threat intelligence',
    schedule_interval='@daily',
    catchup=False
)

fetch_otx_task = PythonOperator(
    task_id='fetch_otx_data',
    python_callable=run_fetch_otx,
    dag=dag
)

fetch_otx_task