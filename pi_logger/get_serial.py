"""
Print to screen the serial number of the pi the script is run from
"""
import logging
from pi_logger import PINAME
from pi_logger.local_loggers import getserial

LOG = logging.getLogger(f"pi_logger_{PINAME}.get_serial")

if __name__ == "__main__":
    print(getserial())
