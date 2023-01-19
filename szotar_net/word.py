import chinese_converter
import dragonmapper
from dragonmapper import transcriptions
from szotar_net import colours, config, common


superscript = ["\u00b9", "\u00b2", "\u00b3", "\u2074", "\u2075", "\u2076", "\u2077", "\u2078", "\u2079"]


class Entry:
    # Main entry class, corresponds to pclass and pclass_last html classes -- homonyms
    def __init__(self,
                 cszo,  # sometimes there are multiple
                 pinyin,
                 content,
                 cszo_regi=None,
                 cszo_variant=None,
                 index=None
                 ):
        self.cszo = cszo
        if cszo_regi and cszo_regi == chinese_converter.to_traditional(cszo):
            self.trad = cszo_regi
        else:
            self.trad = chinese_converter.to_traditional(cszo)
        self.cszo_variant = cszo_variant or ""
        self.pinyin = pinyin
        self.zhuyin = dragonmapper.transcriptions.pinyin_to_zhuyin(pinyin)
        if index:
            self.index = superscript[int(index) - 1]  # corresponds to homo class
        else:
            self.index = ""
        self.content = content

    def __str__(self):
        # Set the correct headword based on config file
        cszo_str = ""
        alt_hanzi = ""
        if config.get("Settings", "hanzi") == "both_trad_first":
            cszo_str = self.trad
            alt_hanzi = self.cszo
        elif config.get("Settings", "hanzi") == "both_simp_first":
            cszo_str = self.cszo
            alt_hanzi = self.trad
        elif config.get("Settings", "hanzi") == "trad":
            cszo_str = self.trad
        elif config.get("Settings", "hanzi") == "simp":
            cszo_str = self.cszo
        else:
            common.config_error()

        zhuyin_col = common.pron_tone_colour(self.zhuyin, cszo_str)
        pinyin_col = common.pron_tone_colour(dragonmapper.transcriptions.zhuyin_to_pinyin(self.zhuyin), cszo_str)

        cszo_str = common.zh_text_colour(cszo_str)
        alt_hanzi = "〔" + common.zh_text_colour(alt_hanzi) + "〕"

        index_str = ""
        if self.index:
            index_str = self.index + " "
            cszo_str = "【" + cszo_str + index_str + "】"
        else:
            cszo_str = "【" + cszo_str + "】"

        cszo_variant_str = ""
        if self.cszo_variant:
            cszo_variant_str = "(" + self.cszo_variant + ") "

        pron = ""

        if config.get("Settings", "pron") == "both_zhuyin_first":
            pron = zhuyin_col + " " + pinyin_col
        elif config.get("Settings", "pron") == "both_pinyin_first":
            pron = pinyin_col + " " + zhuyin_col
        elif config.get("Settings", "pron") == "zhuyin":
            pron = zhuyin_col
        elif config.get("Settings", "pron") == "pinyin":
            pron = pinyin_col
        else:
            common.config_error()
        pron += " "

        content_str = ""
        for c in self.content:
            content_str += c.__str__()

        return cszo_str + alt_hanzi + cszo_variant_str + pron + content_str  + "\n"  + "\n"




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
        while sense_str.endswith("\n"):
            sense_str = sense_str[:-1]

        rom_str = ""
        if self.roman_num:
            rom_str = colours.get_colour_string(self.roman_num, "roman_num") + " "

        szofaj_str = ""
        if self.szofaj:
            szofaj_str = colours.get_colour_string(self.szofaj, "misc") + " "

        # Case 1.1 --> when there is nytan and a single line definition
        if not self.roman_num and self.szofaj and len(self.senses) == 1:
            return (szofaj_str + sense_str).strip()

        # Case 1.2 --> no nytan, single line definition
        if not self.roman_num and not self.szofaj and len(self.senses) == 1:
            return sense_str.strip()

        # Case 2 --> Only arabic numerals:
        if not self.roman_num and len(self.senses) > 1:
            return szofaj_str + "\n" + sense_str

        # Case 3 --> There are roman numerals:
        if self.roman_num:
            # 3.1 --> Single line definition
            if len(self.senses) == 1:
                return "\n" + rom_str + sense_str
            # 3.2 --> Has more senses, arabic numerals
            elif len(self.senses) > 1:
                if any(char.isdigit() for char in sense_str[:5]):
                    return "\n" + rom_str + szofaj_str + "\n" + sense_str
                return "\n" + rom_str + szofaj_str + sense_str

        return ""




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
        if self.peldak:
            for pld in self.peldak:
                pld_str += "\n" + pld.__str__()
        szam_str = ""
        if self.szam:
            szam_str = colours.get_colour_string(self.szam, "arabic_num") + " "

        return "  " + szam_str + self.jel_valt + pld_str


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
        if config.getboolean("Settings", "show_examples"):
            # Get the correct example string based on the config
            zh_text = ""
            if config.get("Settings", "example_hanzi") == "trad":
                zh_text = self.zh_tc
            elif config.get("Settings", "example_hanzi") == "simp":
                zh_text = self.zh_sc
            else:
                common.config_error()
            zh_text = colours.get_colour_string(zh_text, "pelda_zh")

            # Get the correct pronunciation based on the config
            pron = ""
            if config.get("Settings", "example_pron") == "zhuyin":
                pron = self.zhuyin
            elif config.get("Settings", "example_pron") == "pinyin":
                pron = colours.get_colour_string(self.pinyin, "pelda_pinyin")
            else:
                common.config_error()
            line = colours.get_colour_string(" | ", "misc")
            if config.getboolean("Settings", "show_example_pron"):
                return "   " + line + zh_text + line + pron + line + self.hun_text
            return "   " + line + zh_text + line + self.hun_text
        return



