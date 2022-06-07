import sys

from app.app_io import post_processing_cli_arguments


def main():
    app_arguments = post_processing_cli_arguments(sys.argv[1:])
    # TODO: parse post processing function chain from control yaml
    # TODO: apply post processing function chain to each alternative/schedule from input data
    # TODO: form output data and file from post processed results


if __name__ == '__main__':
    main()
