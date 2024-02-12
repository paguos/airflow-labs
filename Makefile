# Makefile to setup and start Airflow in the current directory and use a custom DAGs folder

# Set AIRFLOW_HOME to the current directory
AIRFLOW_DIRECTORY=$(shell pwd)/.airflow

# Specify the path to your custom DAGs folder
CUSTOM_DAGS_FOLDER=$(shell pwd)/dags

# Initialize Airflow: Set AIRFLOW_HOME environment variable and initialize the database
airflow-init:
	AIRFLOW_HOME=$(AIRFLOW_DIRECTORY) pipenv run airflow db init
	AIRFLOW_HOME=$(AIRFLOW_DIRECTORY) pipenv run airflow users create --username admin --password admin --firstname Anonymous --lastname Admin --role Admin --email admin@example.org

# Start Airflow webserver
airflow-webserver:
	AIRFLOW_HOME=$(AIRFLOW_DIRECTORY) AIRFLOW__CORE__DAGS_FOLDER=$(CUSTOM_DAGS_FOLDER) pipenv run airflow webserver

# Start Airflow scheduler
airflow-scheduler:
	NO_PROXY="*" AIRFLOW_HOME=$(AIRFLOW_DIRECTORY) AIRFLOW__CORE__DAGS_FOLDER=$(CUSTOM_DAGS_FOLDER) pipenv run airflow scheduler

# Shortcut to start both webserver and scheduler
airflow-start: airflow-webserver airflow-scheduler
