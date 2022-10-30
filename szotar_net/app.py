from szotar_net import config
from szotar_net.dictionary import SzotarNet


class App:
    def __init__(self):
        self.dict = SzotarNet()

    def quicksearch(self, word):
        # Implement quicksearch first since that's easier
        print(self.dict.query(word))

    def end(self):
        self.dict.end()
