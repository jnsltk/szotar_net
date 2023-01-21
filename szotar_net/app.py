import getpass
import os
import sys

from szotar_net import common, config
from szotar_net.dictionary import SzotarNet


class App:
    def __init__(self):
        self.check_credentials()
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

    def check_credentials(self):
        if config.get("SzotarNet", "email") and config.get("SzotarNet", "password"):
            return
        else:
            os.system('clear')
            print(common.get_logo())
            print("It appears you haven't added a szotar.net username and password yet. "
                  "\nYou'll need one to use this tool. You can register for free at \nhttps://www.szotar.net/egyeb/regisztracio/\n\n"
                  "Would you like to add your credentials now?\n"
                  "[Y]es / [N]o ")
            input_str = ""
            while True:
                input_str = input("> ")
                if input_str.lower() == "n" or input_str.lower() == "no":
                    break
                elif input_str.lower() == "y" or input_str.lower() == "yes":
                    self.add_credentials()
                    return
            sys.exit(0)

    def add_credentials(self):
        email = input("Please enter your email address: ")
        password = getpass.getpass("Please enter your password: ")

        config.set('SzotarNet', 'email', email)
        config.set('SzotarNet', 'password', password)
        with open(config.get("paths", "config_file"), "w") as configfile:
            config.write(configfile)

    def end(self):
        self.dict.end()
