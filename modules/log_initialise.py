## Packages
import os
import logging


def setup_logging(log_dir:str, timestamp:str):
    """This will initialise the logger.

    Args:
        log_dir (str): where you want your logs saved
        timestamp (str): name of log file
    """

    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{log_dir}/{timestamp}.log"

    ## Configure logging so messages are written to the log files

    logging.basicConfig(
        filename = log_filename,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level = logging.INFO
    )

    ## Create the logger and confirm that it has been successfully set up

    return logging.getLogger()