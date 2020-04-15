"""
Print to screen the serial number of the pi the script is run from
"""

from pi_logger.local_loggers import getserial

if __name__ == "__main__":
    print(getserial())
