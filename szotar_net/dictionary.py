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

    def render_entry(self, pclass):
        # Extract single attributes that are needed for the Entry class
        cszo = ""
        cszo_alt = ""

        cszo_elements = pclass.find_all("span", {"class": "cszo"})
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

        # get content
        content = self.extract_szofaj_szint(pclass)

        entry = Entry(cszo, pinyin, content, cszo_regi, cszo_alt, index)
        print(entry)  # Will replace with colorful print function or something

    def extract_szofaj_szint(self, pclass):
        roman_num = ""

        # There are seemingly three possibilities:
        # 1. If the entry is simple, only has one sense, then it is in the same line as the pinyin with example underneath
        # 2. If the entry has more than one sense, then there are arabic numerals and they start in the next line
        # 3. If the entry has different meanings that have different part of speech then there are roman numerals
        # somehow also need to account for the case where there's a one-line definition

        szofaj = None
        jel_valt = ""
        # Case 1.1 --> when there is nytan and a single line definition -- WORKS
        num = None
        if pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div"):
            div_sibling = pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div")
            num = div_sibling.find("b")

        if pclass.find("span", {"class": "nytan"}) and num is None:
            szofaj = pclass.find("span", {"class": "nytan"}).get_text().strip()

            for s in pclass.find("span", {"class": "pinyin_cszo"}).next_siblings:
                if s.name == "div":
                    break
                if szofaj is not None:
                    if s.get_text().strip() == szofaj:
                        continue
                jel_valt += s.get_text()
            jel_valt = jel_valt.strip()
            senses = [jel_valt]
            return [SzofajSzint(senses, szofaj, roman_num)]
        # Case 1.2 --> no nytan, single line definition -- WORKS
        elif isinstance(pclass.find("span", {"class": "pinyin_cszo"}).next_sibling, NavigableString) and num is None:
            for s in pclass.find("span", {"class": "pinyin_cszo"}).next_siblings:
                if s.name == "div":
                    break
                else:
                    jel_valt += s.get_text()
            jel_valt = jel_valt.strip()
            senses = [jel_valt]
            return [SzofajSzint(senses, szofaj, roman_num)]

        # In case there are either roman numerals or arabic numerals:

        szofajszint_list = []
        sense_list = []

        if pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div"):
            div_siblings = pclass.find("span", {"class": "pinyin_cszo"}).find_next_siblings("div")
            for div_sibling in div_siblings:
                either_num = self.extract_nums(pclass, div_sibling)
                if isinstance(either_num, Sense):
                    sense_list.append(either_num)
                    szofaj = pclass.find("span", {"class": "nytan"})
                    if szofaj:
                        szofaj = szofaj.get_text().strip()
                    else:
                        szofaj = ""
                else:
                    szofajszint_list.append(either_num)
        if sense_list:
            return [SzofajSzint(sense_list, szofaj)]

        return szofajszint_list

    def extract_nums(self, pclass, div_sibling):
        # first iterates through the list of divs passed in, checks each if it contains roman numbers or arabic numbers
        # if roman, extracts szofaj, then calls itself again
        # if arabic, extracts senses (by calling extract_sense() )
        # in the end creates senses, puts them in a list, creates szofajszint and returns it
        szofaj = None
        roman_num = ""
        senses = []
        num = div_sibling.find("b")
        if div_sibling == pclass.find("div", {"class": "frazeo"}):
            pass
        if num is not None:
            if re.match(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$", num.get_text()):
                roman_num = num.get_text().strip()
                szofaj = div_sibling.find("span", {"class": "nytan"}).get_text().strip()

                jel = ""
                for s in div_sibling.find("span", {"class": "nytan"}).next_siblings:
                    if s.name == "div":
                        break
                    if szofaj is not None:
                        if s.get_text().strip() == szofaj:
                            continue
                    jel += s.get_text()
                jel = jel.strip()
                if jel != "":
                    senses = [jel]

                div_ar_siblings = num.find_next_siblings("div")
                for div_ar_sibling in div_ar_siblings:
                    senses.append(self.extract_nums(pclass, div_ar_sibling))

            elif re.match(r"^[1-9]+\.\s*$", num.get_text()):
                return self.extract_sense(div_sibling, szofaj)

        if szofaj is None:
            szofaj = div_sibling.find("span", {"class": "nytan"})
            if szofaj is not None:
                szofaj = szofaj.get_text().strip()
            else:
                szofaj = ""
        return SzofajSzint(senses, szofaj, roman_num)
    def extract_sense(self, div_sibling, szofaj):
        jel_valt = ""
        szam = div_sibling.find("b").get_text().strip()

        for s in div_sibling.find("b").next_siblings:
            if s.name == "div":
                break
            if szofaj is not None:
                if s.get_text().strip() == szofaj:
                    continue
            jel_valt += s.get_text()
        jel_valt = jel_valt.strip()
        # extract jel_valt and szam

        # for loop for extracting all examples (peldak):
        peldak = self.extract_pelda(div_sibling) or ""

        return Sense(jel_valt, "", szam)

    def extract_pelda(self, div_sibling):
        peldak = []
        hun_text = ""
        pinyin = ""
        zh_sc = ""
        for pelda in div_sibling.find_next_siblings("div"):
            zh_sc = pelda.find("span", {"class": "kif"})
            pinyin = pelda.find("span", {"class": "pinyin"})
            hun_text = "hello"

            if zh_sc and pinyin and hun_text:
                zh_sc = zh_sc.get_text().strip()
                pinyin = pinyin.get_text().strip()
                # hun_text = hun_text.get_text().strip()
                peldak.append(Pelda(hun_text, pinyin, zh_sc))

        return peldak

    def query(self, chinese_word):
        # Get the page content
        chinese_word = chinese_converter.to_simplified(chinese_word)
        r = self.s.get(self.query_url + chinese_word)
        soup = BeautifulSoup(r.content, "html.parser")
        word = ""
        for element in soup.find_all("div", {"class": "pclass"}):
            self.render_entry(element)
        self.render_entry(soup.find("div", {"class": "pclass_last"}))

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
