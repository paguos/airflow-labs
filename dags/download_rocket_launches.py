import json
import pathlib

import airflow
import requests
import requests.exceptions as requests_excetions

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from loguru import logger

dag = DAG(
    dag_id="dowload_rocket_launches",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval=None
)

download_launches = BashOperator(
    task_id="download_launches",
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",
    dag=dag
)

def _get_pictures():
    # Ensure directory exists
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True)

    # Download all pictures in launches.json
    with open("/tmp/launches.json") as f:
        launches = json.load(f)
        image_urls = [launch["image"] for launch in launches["results"]]

        logger.info(f"Downloading '{len(image_urls)}' images ...")
        for image_url in image_urls:
            try:
                logger.debug(f"Downloading {image_url} ...")
                response = requests.get(image_url, timeout=20)
                logger.debug(f"Download complete!")

                image_filename = image_url.split("/")[-1]
                target_file = f"/tmp/images/{image_filename}"

                logger.debug(f"Saving image {target_file} ...")
                with open(target_file, "wb") as f:
                    f.write(response.content)
                logger.debug(f"Image saved!")

            except requests_excetions.MissingSchema:
                logger.error(f"{image_url} appears to be an invlaid URL.")
            except requests_excetions.ConnectionError:
                logger.error(f"Could not connect to {image_url}")
        logger.info(f"Download complete!")

get_pictures = PythonOperator(
    task_id="get_pictures",
    python_callable=_get_pictures,
    dag=dag
)

notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images"',
    dag=dag
)

download_launches >> get_pictures >> notify
