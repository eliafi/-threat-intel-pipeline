# threat_intel_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from etl.fetch_otx import fetch_otx_pulses

def run_fetch_otx(**kwargs):
    api_key = Variable.get("OTX_API_KEY")  # Securely retrieved
    fetch_otx_pulses(api_key)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='threat_intel_pipeline',
    default_args=default_args,
    description='ETL pipeline for threat intelligence',
    schedule=None,      # Runs only when manually triggered
    catchup=False,
    max_active_runs=1,
)

fetch_otx_task = PythonOperator(
    task_id='fetch_otx_data',
    python_callable=run_fetch_otx,
    dag=dag
)


fetch_otx_task