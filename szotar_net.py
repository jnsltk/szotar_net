#!/usr/bin/env python3
import argparse
import sys
from szotar_net.app import App


def main():
    # Create the parser
    parser = argparse.ArgumentParser(prog="szotar_net",
                                     description="Termninál szotar.net kínai-magyar szótár kliens")

    # Add the arguments
    parser.add_argument("-q",
                        dest="word",
                        metavar="<word>",
                        help="Gyors keresés")

    # Execute the parse_args() method
    args = parser.parse_args()

    app = App()

    if args.word:
        app.quicksearch(word=args.word)
    else:
        print("Szótár mód nincs még kész, használd a gyorskeresést (írd be, hogy \"szotar_net -q <szó>\")")
        sys.exit(0)

    app.end()


if __name__ == "__main__":
    main()

# https://fanyi.youdao.com/openapi.do?keyfrom=blog125&key=21376174&type=data&doctype=json&version=1.1&q=%E6%9C%89%E9%81%93
