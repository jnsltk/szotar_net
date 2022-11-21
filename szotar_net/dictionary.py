import os.path
import sys

import dragonmapper.hanzi
import requests
from szotar_net import config
from szotar_net.word import Entry, SzofajSzint, Sense, Pelda
import chinese_converter
from dragonmapper import hanzi
from bs4 import BeautifulSoup, NavigableString, Tag
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
        return chinese_converter.to_traditional(word)

    def render_pclass(self, pclass):
        # Extract single attributes that are needed for the Entry class
        cszo_elements = pclass.find_all("span", {"class": "cszo"})
        cszo = ""
        cszo_alt = ""
        for c in cszo_elements:
            if c is not None and dragonmapper.hanzi.has_chinese(c.get_text()):
                if cszo == "":
                    cszo = c.get_text()
                elif cszo_alt == "":
                    cszo_alt += c.get_text()
                else:
                    cszo_alt += ", " + c.get_text()

        cszo_regi = pclass.find("span", {"class": "regicszo"})
        if cszo_regi is not None:
            cszo_regi = cszo_regi.get_text()

        index = pclass.find("span", {"class": "homo"})
        if index is not None:
            index = index.get_text().strip()

        pinyin = pclass.find("span", {"class": "pinyin_cszo"}).get_text()

        # Innentől nehezebb hahaha
        # There are seemingly three possibilites:
        # 1. If the entry is simple, only has one sense, then it is in the same line as the pinyin with example underneath
        # 2. If the entry has more than one sense, then there are arabic numerals and they start in the next line
        # 3. If the entry has different meanings that have different part of speech then there are roman numerals

        szofaj = ""
        roman_n = ""
        arab_n = ""
        jel_valt = ""
        # Case 1 --> when there is nytan and a single line definition
        if pclass.find("span", {"class": "nytan"}):
            szofaj = pclass.find("span", {"class": "nytan"}).get_text().strip()

            jel_valt = ""
            for s in pclass.find("span", {"class": "pinyin_cszo"}).next_siblings:
                if s.name == "div":
                    break
                if szofaj is not None:
                    if s.get_text().strip() == szofaj:
                        continue
                jel_valt += s.get_text()
            jel_valt = jel_valt.strip()
        # need another case where there is no nytan, eg 画蛇添足 STILL NEED TO WORK ON THE CONDITION OF THE IF STATEMENT
        elif isinstance(pclass.find("span", {"class": "pinyin_cszo"}).next_sibling, NavigableString):
            jel_valt = ""
            for s in pclass.find("span", {"class": "pinyin_cszo"}).next_siblings:
                if s.name == "div":
                    break
                else:
                    jel_valt += s.get_text()
            jel_valt = jel_valt.strip()

        # Case 2 and 3
        if pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div"):
            div_sibling = pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div")
            num = div_sibling.find("b")
            if num is not None:
                if re.match(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$", num.get_text()):
                    roman_n = num.get_text().strip() + " "
                elif re.match(r"^[1-9]+\.\s*$", num.get_text()):
                    arab_n = num.get_text().strip() + " "

            if szofaj is None:
                szofaj = div_sibling.find("span", {"class": "nytan"})
                if szofaj is not None:
                    szofaj = szofaj.get_text().strip()
                else:
                    szofaj = ""

        # Only for testing, will need for loops, perhaps every class created in separate method

        senses = [Sense("#"+jel_valt)]
        content = [SzofajSzint(senses, szofaj, roman_n)]
        entry = Entry(cszo, pinyin, content, cszo_regi, cszo_alt, index)
        print(entry)

    def query(self, chinese_word):
        # Get the page content
        r = self.s.get(self.query_url + chinese_word)
        soup = BeautifulSoup(r.content, "html.parser")
        word = ""
        for element in soup.find_all("div", {"class": "pclass"}):
            self.render_pclass(element)
        self.render_pclass(soup.find("div", {"class": "pclass_last"}))

        # Very ugly for now, needs a complete rework using the word classes
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
