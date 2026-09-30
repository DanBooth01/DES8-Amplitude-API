from modules.log_initialise import setup_logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from modules.run_extract import extract_json
from modules.load_to_S3 import load_to_S3
import os

load_dotenv()

# Load logger
timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
logger = setup_logging('log', timestamp)
logger.info('Logger successfully initialised')


# Define Variables
url = "https://analytics.eu.amplitude.com/api/2/export"
start_time = (datetime.now() + timedelta(days = -1)).strftime("%Y%m%dT%H")
end_time = datetime.now().strftime("%Y%m%dT%H")
data_dir = 'data'
delay = 10
max_retry = 5

# Extract data into data folder
extract_json(start_time, end_time, url, data_dir, max_retry, delay)


# Set up AWS credentials

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# Upload data to S3
load_to_S3(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME)
