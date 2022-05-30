import argparse


def build_upload_parser():
    my_parser = argparse.ArgumentParser()

    group = my_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbose",
        help="increase output verbosity",
        action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="decrease output verbosity", action="store_true"
    )
    my_parser.add_argument(
        "-H",
        "--host",
        help="server IP address",
        metavar="")
    my_parser.add_argument(
        "-p", "--port", help="server port", required=True, metavar=""
    )
    my_parser.add_argument(
        "-s", "--src", help="source file path", required=True, metavar=""
    )
    my_parser.add_argument(
        "-n",
        "--name",
        help="file name",
        required=True,
        metavar="")

    return my_parser


def build_download_parser():
    my_parser = argparse.ArgumentParser()

    group = my_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbose",
        help="increase output verbosity",
        action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="decrease output verbosity", action="store_true"
    )
    my_parser.add_argument(
        "-H",
        "--host",
        help="server IP address",
        metavar="")
    my_parser.add_argument(
        "-p", "--port", help="server port", required=True, metavar=""
    )
    my_parser.add_argument(
        "-d", "--dst", help="destination file path", required=True, metavar=""
    )
    my_parser.add_argument(
        "-n",
        "--name",
        help="file name",
        required=True,
        metavar="")

    return my_parser
