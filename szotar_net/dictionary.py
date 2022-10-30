import os.path
import sys

import requests
from szotar_net import config
import chinese_converter
from bs4 import BeautifulSoup
import re


class SzotarNet:
    def __init__(self):
        self.login_url = config.get("SzotarNet", "login_url")
        self.query_url = config.get("SzotarNet", "query_url")
        self.payload = {
            "email": config.get("SzotarNet", "email"),
            "password": config.get("SzotarNet", "password"),
            "belepvemarad": "on"
        }
        self.s = requests.Session()
        self.s.post(self.login_url, data=self.payload)
        self.history = {}
        # implement importing history later

    def get_trad(self, word) -> str:
        return "[" + chinese_converter.to_traditional(word) + "]"

    # Very ugly for now, needs a complete rework
    def query(self, chinese_word):
        r = self.s.get(self.query_url + chinese_word)
        soup = BeautifulSoup(r.content, "html.parser")
        word = ""
        if soup.find("span", class_="cszo") is None:
            return word
        headword = soup.find("span", class_="cszo").text
        trad = self.get_trad(headword)
        pinyin = soup.find("span", class_="pinyin_cszo").text
        soup.find("span", {"class": "cszo"}).decompose()
        soup.find("span", {"class": "pinyin_cszo"}).decompose()
        if soup.find("div", {"class": "frazeo"}) is not None:
            soup.find("div", {"class": "frazeo"}).decompose()
        entry = ""
        for tag in soup.find_all("span", {"class": "kif"}):
            if tag.string is not None:
                tag.string.insert_before("\n" + " | ")
        for element in soup.find_all("div", {"class": "pclass"}):
            element_text = element.text.strip()
            for i, c in enumerate(element_text):
                if c.isdigit():
                    if element_text.startswith(headword):
                        missing_hanzi = ""
                    else:
                        missing_hanzi = headword.strip()
                    element_text = "{0}{1}{2} {3} {4}".format(missing_hanzi, element_text[:i].strip(),
                                                              element_text[i].strip(), pinyin, element_text[i + 1:])
                    break
            entry = entry + " \n" + element_text
        if soup.find_all("div", {"class": "pclass"}) is not None:
            entry += "\n"
        entry = entry + soup.find("div", class_="pclass_last").text.strip()
        entry = re.sub(r"(I*V*I+[.])", r"\n\1", entry)
        entry = re.sub(r"([0-9][.])", r"\n\1", entry)
        while entry.startswith(" " or "1"):
            entry = entry[1:]
        if headword == "" and pinyin == "":
            trad = ""
        word = headword + " " + trad + " " + pinyin + " " + entry
        while word.startswith("\n" or " "):
            word = word[1:]
        return word

    def end(self):
        self.s.close()

