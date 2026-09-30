import boto3
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')


## Create log folder
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
log_filename = f"{log_dir}/load_{timestamp}.log"

## Configure logging so messages are written to the log files

logging.basicConfig(
    filename = log_filename,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO
)

## Create the logger and confirm that it has been successfully set up

logger = logging.getLogger()
logger.info("Logger successfuly initialised")

s3_client = boto3.client(
    's3',
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)


files_to_upload = os.listdir('data')


#List all items in S3 bucket
objects = s3_client.list_objects_v2(Bucket= AWS_BUCKET_NAME)

files_in_bucket= []

for obj in objects['Contents']:
    files_in_bucket.append(obj['Key'])

#Upload files that aren't in s3 bucket:
for file in files_to_upload:
    file_to_upload = f'data/{file}'
    filename_s3 = file
    if file not in objects['Contents']:
        try:
            s3_client.upload_file(file_to_upload, AWS_BUCKET_NAME, filename_s3)
            print(f'{file} uploaded successfully')
            logger.info(f'{file} uploaded successfully')
            os.remove(file_to_upload)
        except Exception as e:
            print(f'An error has occured: {e}')
            logger.error(f'An error has occured: {e}')
    else:
        print(f"{file} has already been uploaded")
        logger.info(f"{file} has already been uploaded")
