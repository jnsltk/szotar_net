#!/usr/bin/env python3
import argparse
import sys
from szotar_net.app import App


def main():
    # Create the parser
    parser = argparse.ArgumentParser(prog="szotar_net",
                                     description="Szotar.net Chinese-Hungarian dictionary client in the terminal")

    # Add the arguments
    parser.add_argument("-q",
                        dest="word",
                        metavar="<word>",
                        help="Quick search")

    # Execute the parse_args() method
    args = parser.parse_args()

    app = App()

    if args.word:
        app.quicksearch(word=args.word)
    else:
        print("Query mode not ready yet, use quick search (type \"szotar_net -q <word>\")")
        sys.exit(0)

    app.end()


if __name__ == "__main__":
    main()
