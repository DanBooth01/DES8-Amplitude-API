## import packages
import requests
import os
from datetime import datetime, timedelta
import time
import logging
from dotenv import load_dotenv
import zipfile
import gzip
import io

load_dotenv()

# Define Variables
url = "https://analytics.eu.amplitude.com/api/2/export"
start_time = (datetime.now() + timedelta(days = -1)).strftime("%Y%m%dT%H")
end_time = datetime.now().strftime("%Y%m%dT%H")
params = {
    'start' : start_time,
    'end' : end_time
}

# List expected files
expected_files = []
first_date = datetime.now() + timedelta(days = -1)
while first_date <= datetime.now():
    expected_files.append(f"{first_date.strftime("%Y-%m-%d-%H")}#0.json")
    first_date+= timedelta(hours=1)

print(expected_files)

    

# Create folder to store data and a temp folder as an intermediate step (for now this is not temp)
data_dir = 'data'
os.makedirs(data_dir, exist_ok= True)

# Create timestamp to name files
timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-&S")

## Create logging folder
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)
log_filename = f"{log_dir}/{timestamp}.log"

## Configure logging so messages are written to the log files

logging.basicConfig(
    filename = log_filename,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO
)

## Create the logger and confirm that it has been successfully set up

logger = logging.getLogger()
logger.info("Logger successfuly initialised")



# Set while loop conditions
max_retry = 5
attempt = 0
delay = 10

while attempt < max_retry:


    # Send GET request
    response = requests.get(url, params=params, auth=(os.getenv('AMP_API_KEY'), os.getenv('AMP_SECRET_KEY')))
    status = response.status_code


    if 200 <= status < 300:
        print("Successful connection")
        logger.info("Successful connection")



        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(".json.gz"):
                    with zip_ref.open(file_name) as f:
                        gzip_bytes = f.read()
                    json_bytes = gzip.decompress(gzip_bytes)
                    clean_file_name = os.path.basename(file_name).removesuffix(".gz")
                    output_path = os.path.join(data_dir, clean_file_name)
                    with open(output_path, "wb") as out_f:
                        out_f.write(json_bytes)


        break



    elif status == 400:
        print("The file size is too large, shorten range and try again")
        logger.info("The file size is too large, shorten range and try again")
        break

    elif status == 404:
        print("No data available for time range requested")
        logger.info("No data available for time range requested")
        break

    elif status == 504:
        print("The amount of data is too large causing a timeout")
        logger.info("The amount of data is too large causing a timeout")
        break
    
    else:
        time.sleep(delay)
        attempt += 1
        print(f"Status code: {status}, retrying attempt number {attempt}")
        logger.info(f"Status code: {status}, retrying attempt number {attempt}")

