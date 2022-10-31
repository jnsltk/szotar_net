import os.path
import sys

import requests
from szotar_net import config
from szotar_net.word import Entry, SzofajSzint, Sense, Pelda
import chinese_converter
from dragonmapper import hanzi
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

    def extract_entry(self, pclass):
        cszok = pclass.find_all("span", {"class": "cszo"})
        cszo = ""
        cszo_alt = ""
        for c in cszok:
            if hanzi.has_chinese(c.get_text()):
                if not cszo:
                    cszo += c.get_text()
                else:
                    cszo_alt += c.get_text()

        cszo_regi = pclass.find("span", {"class": "cszo_regi"})
        index = pclass.find("span", {"class": "homo"})
        pinyin = pclass.find("span", {"class": "pinyin_cszo"}).get_text()

        content = None

        # If the entry has many SzofajSzint loop through them and add them to list
        # Find all divs that have a b that contains roman numerals
        def find_szofaj_szint(tag):
            if tag.b is None:
                return False
            return tag.name == "div" and re.match(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$", tag.b.string)

        szofaj_szint_divs = pclass.find_all(find_szofaj_szint)
        # Need to add case for when there is no SzofajSzint
        for div in szofaj_szint_divs:
            if content is None:
                content = []
            content.append(self.construct_szofaj_szint(self.extract_szofaj_szint_div(div)))

        return cszo, pinyin, content, cszo_regi, cszo_alt, index

    def construct_entry(self, cszo, pinyin="", content="", cszo_regi="", cszo_alt="", index=""):
        return Entry(cszo, pinyin, content, cszo_regi, cszo_alt, index)

    def extract_szofaj_szint_div(self, div):
        roman_num = div.find("b", string=re.compile(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$")).get_text()
        szofaj = div.find("span", {"class": "nytan"})

        senses = []

        def find_sense(tag):
            if tag.b is None:
                return False
            return tag.name == "div" and re.match(r"^[1-9]+\.\s*$", tag.b.string)

        sense_divs = div.find_all(find_sense)
        for div in sense_divs:
            senses.append(self.construct_sense(self.extract_sense_div(div)))

        return senses, szofaj, roman_num

    def construct_szofaj_szint(self, senses, szofaj="", roman_num=""):
        return SzofajSzint(senses, szofaj, roman_num)

    def construct_sense(self, jel_valt, peldak="", szam=""):
        return Sense(jel_valt, peldak, szam)

    def extract_sense_div(self, div):
        szam = div.find("b").get_text().strip()
        # first find szam and peldak then decompose everything else and take the rest
        peldak = []
        def find_pelda(tag):
            if tag.span is None:
                return False
            return tag.span["class"] == ["kif"]
        peldak_div = div.find_all(find_pelda)
        for pelda_div in peldak_div:
            peldak.append(self.construct_pelda(self.extract_pelda(pelda_div)))

        div.find("b").decompose()
        divs = div.find_all("div")
        for d in divs:
            d.decompose()
        jel_valt = div.get_text()

        return jel_valt, peldak, szam


        # decompose

    def construct_pelda(self, hun_text, pinyin="", zh_sc=""):
        return Pelda(hun_text, pinyin, zh_sc)

    def extract_pelda(self, pelda_div):
        zh_sc = pelda_div.find("span", {"class": "kif"})
        pinyin = pelda_div.find("span", {"class": "pinyin"})
        pelda_div.find("span", {"class": "kif"}).decompose()
        pelda_div.find("span", {"class": "pinyin"}).decompose()
        hun_text = pelda_div.get_text()

        return hun_text, pinyin, zh_sc

    def print_entries(self, entries):
        print(entries.__str__)


    # Very ugly for now, needs a complete rework using the word classes
    def query(self, chinese_word):
        # Get the page content
        r = self.s.get(self.query_url + chinese_word)
        soup = BeautifulSoup(r.content, "html.parser")

        # Extract data and build word
        # Data we need:
        # Entry: cszo, pinyin, content, cszo_regi=None, index=None
        # SzofajSzint: senses, szofaj=None, roman_num=None
        # Sense: jel_valt, peldak, szam=None
        # Peldak: hun_text, pinyin, zh_sc

        entries = []

        pclasses = soup.find_all("div", {"class": "pclass"})
        if pclasses is not None:
            for pclass in pclasses:
                entries.append(self.construct_entry(self.extract_entry(pclass)))

        pclass_last = soup.find("div", {"class": "pclass_last"})
        entries.append(self.construct_entry(self.extract_entry(pclass_last)))

        self.print_entries(entries)

        # r = self.s.get(self.query_url + chinese_word)
        # soup = BeautifulSoup(r.content, "html.parser")
        # word = ""
        # if soup.find("span", class_="cszo") is None:
        #     return word
        # headword = soup.find("span", class_="cszo").text
        # trad = self.get_trad(headword)
        # pinyin = soup.find("span", class_="pinyin_cszo").text
        # soup.find("span", {"class": "cszo"}).decompose()
        # soup.find("span", {"class": "pinyin_cszo"}).decompose()
        # if soup.find("div", {"class": "frazeo"}) is not None:
        #     soup.find("div", {"class": "frazeo"}).decompose()
        # entry = ""
        # for tag in soup.find_all("span", {"class": "kif"}):
        #     if tag.string is not None:
        #         tag.string.insert_before("\n" + " | ")
        # for element in soup.find_all("div", {"class": "pclass"}):
        #     element_text = element.text.strip()
        #     for i, c in enumerate(element_text):
        #         if c.isdigit():
        #             if element_text.startswith(headword):
        #                 missing_hanzi = ""
        #             else:
        #                 missing_hanzi = headword.strip()
        #             element_text = "{0}{1}{2} {3} {4}".format(missing_hanzi, element_text[:i].strip(),
        #                                                       element_text[i].strip(), pinyin, element_text[i + 1:])
        #             break
        #     entry = entry + " \n" + element_text
        # if soup.find_all("div", {"class": "pclass"}) is not None:
        #     entry += "\n"
        # entry = entry + soup.find("div", class_="pclass_last").text.strip()
        # entry = re.sub(r"(I*V*I+[.])", r"\n\1", entry)
        # entry = re.sub(r"([0-9][.])", r"\n\1", entry)
        # while entry.startswith(" " or "1"):
        #     entry = entry[1:]
        # if headword == "" and pinyin == "":
        #     trad = ""
        # word = headword + " " + trad + " " + pinyin + " " + entry
        # while word.startswith("\n" or " "):
        #     word = word[1:]
        # return word

    def end(self):
        self.s.close()
