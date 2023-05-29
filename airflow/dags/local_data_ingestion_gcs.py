import os
import logging
import airflow 
import pandas as pd

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingest import ingest_data_to_postgresql

PG_HOST=os.getenv('PG_HOST')
PG_USER=os.getenv('PG_USER')
PG_PASSWORD=os.getenv('PG_PASSWORD')
PG_PORT=os.getenv('PG_PORT')
PG_DATABASE=os.getenv('PG_DATABASE')


path_to_local_home = os.environ.get("AIRFLOW_HOME","/opt/airflow")
#create dictionary with the years and urls of the maize data
years_dict = dict()
years_dict['2017'] = 'http://kilimodata.org/datastore/dump/63fa57a5-a7c2-40e1-a728-f9546fa383ef?bom=True'
years_dict['2018'] = 'http://kilimodata.org/datastore/dump/e1a72ec2-e347-4264-8ac9-d4ec3659610a?bom=True'

def convert_csv_to_parquet(file_csv,file_parquet):
    df = pd.read_csv(f"{path_to_local_home}/{file_csv}")
    df.to_parquet(f"{path_to_local_home}/{file_parquet}")

default_args = {
    "owner":"airflow",
    "start_date":days_ago(1),
    "depends_on_past":False,
    "retries":1,
}

#DAG
with DAG(
    dag_id="local_ingest_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=["local_dag"]
) as dag:
    
    for year, url in years_dict.items():
        csv_file = f'maize_{year}.csv'

        download_data_task = BashOperator(
            task_id=f"download_data_task_{year}",
            bash_command=f"curl -sS {url} > {path_to_local_home}/{csv_file}"
        )

        ingest_data_task = PythonOperator(
            task_id=f"ingest_data_task_{year}",
            python_callable=ingest_data_to_postgresql,
            op_kwargs = dict(
                user=PG_USER,
                password=PG_PASSWORD,
                host=PG_HOST,
                port=PG_PORT,
                db=PG_DATABASE,
                file_csv = f"{path_to_local_home}/{csv_file}",
                year=year,
            )

        )

        download_data_task >> ingest_data_task