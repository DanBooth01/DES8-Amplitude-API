from modules.log_initialise import setup_logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from modules.run_extract import extract_json

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


extract_json(start_time, end_time, url, data_dir, max_retry, delay)