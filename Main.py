from modules.log_initialise import setup_logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

logger = setup_logging('log', timestamp)
logger.info('Logger successfully initialised')