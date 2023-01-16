import dragonmapper.hanzi
import requests
from szotar_net import config
from szotar_net.word import Entry, SzofajSzint, Sense, Pelda
import chinese_converter
from bs4 import BeautifulSoup, NavigableString
import re


def get_trad(word) -> str:
    return chinese_converter.to_traditional(word)


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

    def extract_entry(self, pclass) -> Entry:
        # Extract single attributes that are needed for the Entry class
        cszo = ""
        cszo_alt = ""

        cszo_elements = pclass.find_all("span", {"class": "cszo"})
        for c in cszo_elements:
            if c and dragonmapper.hanzi.has_chinese(c.get_text()):
                if cszo == "":
                    cszo = c.get_text()
                elif cszo_alt == "":
                    cszo_alt += c.get_text()
                else:
                    cszo_alt += ", " + c.get_text()

        cszo_regi = pclass.find("span", {"class": "regicszo"})
        if cszo_regi:
            cszo_regi = cszo_regi.get_text()

        index = pclass.find("span", {"class": "homo"})
        if index:
            index = index.get_text().strip()

        pinyin = pclass.find("span", {"class": "pinyin_cszo"}).get_text()

        # get content
        content = self.extract_szofaj_szint(pclass)

        return Entry(cszo, pinyin, content, cszo_regi, cszo_alt, index)

    def extract_szofaj_szint(self, pclass) -> list[SzofajSzint]:
        roman_num = ""

        # There are seemingly three possibilities:
        # 1. If the entry is simple, only has one sense, then it is in the same line as the pinyin with example underneath
        # 2. If the entry has more than one sense, then there are arabic numerals, and they start in the next line
        # 3. If the entry has different meanings that have different part of speech then there are roman numerals

        szofaj = None
        jel_valt = ""

        # Case 1.1 --> when there is nytan and a single line definition -- WORKS
        num = None
        if pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div"):
            div_sibling = pclass.find("span", {"class": "pinyin_cszo"}).find_next_sibling("div")
            num = div_sibling.find("b")

        if pclass.find("span", {"class": "nytan"}) and not num:
            szofaj = pclass.find("span", {"class": "nytan"}).get_text().strip()

            for s in pclass.find("span", {"class": "pinyin_cszo"}).next_siblings:
                if s.name == "div":
                    break
                if szofaj:
                    if s.get_text().strip() == szofaj:
                        continue
                jel_valt += s.get_text()
            jel_valt = jel_valt.strip()
            senses = [self.create_sense(jel_valt, pclass)]
            return [SzofajSzint(senses, szofaj, roman_num)]

        # Case 1.2 --> no nytan, single line definition -- WORKS
        elif isinstance(pclass.find("span", {"class": "pinyin_cszo"}).next_sibling, NavigableString) and not num:
            for s in pclass.find("span", {"class": "pinyin_cszo"}).next_siblings:
                if s.name == "div":
                    break
                else:
                    jel_valt += s.get_text()
            jel_valt = jel_valt.strip()
            senses = [self.create_sense(jel_valt, pclass)]
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

        szofaj = None
        roman_num = ""
        senses = []
        num = div_sibling.find("b")
        if div_sibling == pclass.find("div", {"class": "frazeo"}):
            pass
        if num:
            if re.match(r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$", num.get_text()):
                roman_num = num.get_text().strip()
                szofaj = div_sibling.find("span", {"class": "nytan"}).get_text().strip()

                jel = ""
                for s in div_sibling.find("span", {"class": "nytan"}).next_siblings:
                    if s.name == "div":
                        break
                    if szofaj:
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

        if not szofaj:
            szofaj = div_sibling.find("span", {"class": "nytan"})
            if szofaj:
                szofaj = szofaj.get_text().strip()
            else:
                szofaj = ""
        return SzofajSzint(senses, szofaj, roman_num)
    def extract_sense(self, div_sibling, szofaj) -> Sense:
        jel_valt = ""
        szam = div_sibling.find("b").get_text().strip()

        for s in div_sibling.find("b").next_siblings:
            if s.name == "div":
                break
            if szofaj:
                if s.get_text().strip() == szofaj:
                    continue
            jel_valt += s.get_text()
        jel_valt = jel_valt.strip()

        return self.create_sense(jel_valt, div_sibling, szam)

    def create_sense(self, jel_valt, div_sibling=None, szam=None, peldak=None) -> Sense:
        if not peldak and div_sibling:
            peldak = self.extract_pelda(div_sibling)
        return Sense(jel_valt, peldak, szam)

    def extract_pelda(self, div_sibling) -> list[Pelda]:
        peldak = []
        hun_text = ""
        pinyin = ""
        zh_sc = ""
        for pelda in div_sibling.find_all("div"):
            zh_sc = pelda.find("span", {"class": "kif"})
            pinyin = pelda.find("span", {"class": "pinyin"})
            hun_text = ""
            if pinyin:
                for s in pelda.find("span", {"class": "pinyin"}).next_siblings:
                    if s.name == "div":
                        break
                    hun_text += s.get_text()


            if zh_sc and pinyin and hun_text:
                zh_sc = zh_sc.get_text().strip()
                pinyin = pinyin.get_text().strip()
                hun_text = hun_text.strip()
                peldak.append(Pelda(hun_text, pinyin, zh_sc))

        return peldak

    def render_entries(self, entries:list[Entry]):
        for entry in entries:
            print(entry)
            print("\n")

    def query(self, chinese_word:str):
        # Get the page content
        chinese_word = chinese_converter.to_simplified(chinese_word)
        r = self.s.get(self.query_url + chinese_word)
        soup = BeautifulSoup(r.content, "html.parser")
        pclass_last = soup.find("div", {"class": "pclass_last"})
        entries = []
        if not pclass_last:
            print("Nincs találat!")
            return
        for element in soup.find_all("div", {"class": "pclass"}):
            entries.append(self.extract_entry(element))
        entries.append(self.extract_entry(pclass_last))

        self.render_entries(entries)

    def end(self):
        self.s.close()
