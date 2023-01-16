import chinese_converter
import dragonmapper
from dragonmapper import transcriptions
import re

superscript = ["\u00b9", "\u00b2", "\u00b3", "\u2074", "\u2075", "\u2076", "\u2077", "\u2078", "\u2079"]


class Entry:
    # Main entry class, corresponds to pclass and pclass_last html classes -- homonyms
    def __init__(self,
                 cszo,  # sometimes there are multiple
                 pinyin,
                 content,
                 cszo_regi=None,
                 cszo_alt=None,
                 index=None
                 ):
        self.cszo = cszo
        if cszo_regi is not None and cszo_regi == chinese_converter.to_traditional(cszo):
            self.trad = cszo_regi
        else:
            self.trad = chinese_converter.to_traditional(cszo)
        self.cszo_alt = cszo_alt or ""
        self.pinyin = pinyin
        self.zhuyin = dragonmapper.transcriptions.pinyin_to_zhuyin(pinyin)
        if index:
            self.index = superscript[int(index) - 1]  # corresponds to homo class
        else:
            self.index = ""
        self.content = content

    def __str__(self):
        cszo_str = self.cszo
        index_str = ""
        if self.index:
            index_str = self.index + " "
        else:
            cszo_str += " "
        trad_str = "[" + self.trad + "] "
        cszo_alt_str = ""
        if self.cszo_alt:
            cszo_alt_str = "(" + self.cszo_alt + ") "
        pron = self.pinyin + " "
        content_str = ""
        for c in self.content:
            content_str += c.__str__()
        return cszo_str + index_str + trad_str + cszo_alt_str + pron + content_str




class SzofajSzint:
    # Ahol releváns, ott római számokkal jelölten különítettük el a különböző szófajú jelentéseket.
    #  A szószintű egységeknél szögletes zárójelben jelenik meg a szófajt jelölő címke
    def __init__(self,
                 senses,
                 szofaj=None,
                 roman_num=None):
        self.szofaj = szofaj or ""
        self.roman_num = roman_num or ""
        self.senses = senses

    def __str__(self):
        sense_str = ""
        for sense in self.senses:
            sense_str += sense.__str__() + "\n"
        if sense_str.endswith("\n"):
            sense_str = sense_str[:-1]
        rom_str = ""
        if self.roman_num:
            rom_str = self.roman_num + " "
        szofaj_str = ""
        if self.szofaj:
            szofaj_str = self.szofaj + " "
        nl = ""
        if rom_str and szofaj_str and len(self.senses) > 1:
            nl = "\n"
            if not re.match(r"^[1-9]+\.\s*$", sense_str[:2]):
                return nl + rom_str + szofaj_str + sense_str
            return nl + rom_str + szofaj_str + nl + sense_str
        elif rom_str and szofaj_str and len(self.senses) == 1:
            return "\n" + rom_str + szofaj_str + sense_str
        elif not rom_str and re.match(r"^[1-9]+\.\s*$", sense_str[:2]):
            nl = "\n"
            return szofaj_str + nl + sense_str
        return nl + rom_str + szofaj_str + nl + sense_str



class Sense:
    # Egyazon szófaji jelentésosztályon belül (bekarikázott) arab számok választják el egymástól a kü-
    # lönálló jelentésváltozatokat.
    def __init__(self,
                 jel_valt,
                 peldak=None,
                 szam=None):
        self.szam = szam or ""
        self.jel_valt = jel_valt
        self.peldak = peldak or ""

    def __str__(self):
        pld_str = ""
        if self.peldak != "":
            for pld in self.peldak:
                pld_str += "\n" + pld.__str__()
        szam_str = ""
        if self.szam != "":
            szam_str = self.szam + " "

        return szam_str + self.jel_valt + pld_str


class Pelda:
    def __init__(self,
                 hun_text,
                 pinyin,
                 zh_sc):
        self.hun_text = hun_text
        self.pinyin = pinyin
        self.zhuyin = dragonmapper.transcriptions.pinyin_to_zhuyin(pinyin)
        self.zh_sc = zh_sc
        self.zh_tc = chinese_converter.to_traditional(zh_sc)

    def __str__(self):
        # Alap, minden sc
        zh_text = self.zh_sc
        pron = self.pinyin
        line = " | "
        return line + zh_text + line + pron + line + self.hun_text



