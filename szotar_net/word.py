import chinese_converter
import dragonmapper
from dragonmapper import transcriptions


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
        #if cszo_regi is not None and cszo_regi == chinese_converter.to_traditional(cszo):
        #    self.trad = cszo_regi
        #else:
        #    self.trad = chinese_converter.to_traditional(cszo)
        self.cszo_alt = cszo_alt or ""
        self.pinyin = pinyin
        self.zhuyin = dragonmapper.transcriptions.pinyin_to_zhuyin(pinyin)
        self.index = index or ""  # corresponds to homo class
        self.content = content


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


class Pelda:
    def __init__(self,
                 hun_text,
                 pinyin=None,
                 zh_sc=None):
        self.hun_text = hun_text
        self.pinyin = pinyin or ""
        self.zhuyin = dragonmapper.transcriptions.pinyin_to_zhuyin(pinyin)
        self.zh_sc = zh_sc or ""
        self.zh_tc = chinese_converter.to_traditional(zh_sc)



