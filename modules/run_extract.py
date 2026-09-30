## import packages
import requests
import os
import time
import logging
import zipfile
import gzip
import io


logger = logging.getLogger(__name__)

def extract_json(start_time:str, end_time:str, url:str, data_dir:str, max_retry:int, delay:int):
    """Use this function to call the amplitude API and parse the zip file into a json file

    Args:
        start_time (str): _description_
        end_time (str): _description_
        url (str): _description_
        data_dir (str): _description_
        max_retry (str): _description_
        delay (str): _description_
    """

    # Define Variables

    params = {
        'start' : start_time,
        'end' : end_time
    }

    # Create folder to store data
    os.makedirs(data_dir, exist_ok= True)

    # Set while loop conditions
    attempt = 0

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

