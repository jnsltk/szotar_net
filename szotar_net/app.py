import os

from szotar_net import common
from szotar_net.dictionary import SzotarNet


class App:
    def __init__(self):
        self.dict = SzotarNet()

    def quicksearch(self, word):
        print(self.dict.query(word))

    def interactive_mode(self):
        out = ""
        input_str = ""
        while True:
            if input_str == "\\quit" or input_str == "\\離開": break
            print("==================================================================================================")
            os.system('clear')
            print(common.get_logo())
            if not input_str: print("Welcome to szotar_net, a command-line client for the Szotar.net Chinese Hungarian dictionary.\n"
                                    "Type a Chinese word and press return to get started! Type '\\quit' to quit.\n")
            if out: print(out)
            input_str = input("> ")
            if input_str == "\\quit" or input_str == "\\離開": break
            out = self.dict.query(input_str)

        os.system('clear')


    def end(self):
        self.dict.end()
