# Threat Intelligence Aggregation Platform

## Overview
Aggregates threat data from open APIs, stores them in AWS, and visualizes insights.

## Features
- Airflow-based ETL pipeline
- AWS S3 and RDS integration
- Streamlit dashboard

## Structure
- `dags/`: Airflow DAGs
- `etl/`: Python ETL scripts
- `dashboard/`: Streamlit visualizations
- `infra/`: Cloud setup and deployment

## Usage
1. Clone repo and install dependencies.
2. Set up `.env` or Airflow secrets for API keys.
3. Run Airflow scheduler & webserver.
4. Access dashboard from `dashboard/app.py`