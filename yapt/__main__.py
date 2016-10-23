import argparse

import sys
from yapt.wrapper import Wrapper


def main():
    """
    Takes command line arguments and executes searches and installations
    acording to them
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--noconfirm",
                        action="store_true",
                        help="don't ask for confirmation.")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="debug mode (don't execute command).")
    parser.add_argument("-n", "--nocolor",
                        action="store_true",
                        help="no colored output.")
    parser.add_argument("pkg", help="the package to search.", type=str)
    args = parser.parse_args()

    try:
        yapt = Wrapper(args.pkg, args.noconfirm, args.nocolor, args.debug)
        print(yapt.get_output())
        yapt.print_instructions()
        yapt.install_packages(input())
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    main()
