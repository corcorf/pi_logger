"""Console script for pi_logger."""
import argparse
import sys
import logging

from pi_logger import PINAME

LOG = logging.getLogger(f"pi_logger_{PINAME}.cli")


def get_local_logger_arguments():
    """
    Get a reading frequency as an argument when the script is run from CLI
    """
    LOG.debug("fetching arguments")
    description = 'Log ambient conditions at a specified frequency.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--freq", dest='frequency', type=int, nargs='?',
                        default=None, const=300,
                        help='Frequency of readings in seconds')
    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='set the logging module to debug mode')
    parser.add_argument('--setup_db', action='store_const',
                        const=True, default=False,
                        help='initilise the local database')
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(get_local_logger_arguments())  # pragma: no cover
