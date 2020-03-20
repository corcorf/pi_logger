"""Console script for pi_logger."""
import argparse
import sys


def main():
    """Console script for pi_logger."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "pi_logger.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
