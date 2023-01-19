import re
import sys

from pypinyin import lazy_pinyin, Style
from termcolor import cprint

from szotar_net import colours


def config_error():
    cprint("Faulty configuration file, exiting program.", "red", attrs=["bold"])
    sys.exit(1)

def get_zh_text_tone(text:str) -> list[int]:
    pinyin_arr = lazy_pinyin(text, style=Style.TONE3, neutral_tone_with_five=True)

    tone_arr = []
    for word in pinyin_arr:
        tone_num = word[-1]
        tone_arr.append(int(tone_num))
    return tone_arr

def zh_text_colour(text:str) -> str:
    tones = get_zh_text_tone(text)

    col_str = ""
    i = 0
    while i < len(text):
        col_str += colours.get_tone_colour(text[i], tones[i])
        i += 1
    return col_str

def pron_tone_colour(pron_text:str, zh_text:str) -> str:
    separable = False
    if bool(re.search("//", pron_text)):
        separable = True
        pron_arr = pron_text.split("//")
    else:
        pron_arr = pron_text.split()

    tones = get_zh_text_tone(zh_text)

    i = 0
    col_arr = []
    while i < len(pron_arr):
        col_arr.append(colours.get_tone_colour(pron_arr[i], tones[i]))
        i += 1

    col_str = ""
    if separable:
        separator = "//"
    else:
        separator = ""
    for word in col_arr:
        if col_str:
            col_str += separator + word
        else:
            col_str += word

    return col_str

def get_logo() -> str:
     # Prints this logo with original szotar.net colors:
     #               _                        _
     #              | |                      | |
     #  ___ _______ | |_ __ _ _ __ _ __   ___| |_
     # / __|_  / _ \| __/ _` | '__| '_ \ / _ \ __|
     # \__ \/ / (_) | || (_| | |_ | | | |  __/ |_
     # |___/___\___/ \__\__,_|_(_)|_| |_|\___|\__|
     # -=== Kínai-magyar szótár === 漢 匈 辭 典 ===-

    logo = colours.get_colour_string("""               _             """, "logo_green")\
         + colours.get_colour_string("""           _   \n""", "logo_yellow")\
         + colours.get_colour_string("""              | |            """, "logo_green")\
         + colours.get_colour_string("""          | |  \n""", "logo_yellow")\
         + colours.get_colour_string("""  ___ _______ | |_ __ _ _ __ """, "logo_green")\
         + colours.get_colour_string("""_ __   ___| |_ \n""", "logo_yellow")\
         + colours.get_colour_string(""" / __|_  / _ \| __/ _` | '__""", "logo_green")\
         + colours.get_colour_string("""| '_ \ / _ \ __|\n""", "logo_yellow")\
         + colours.get_colour_string(""" \__ \/ / (_) | || (_| | |_ """, "logo_green")\
         + colours.get_colour_string("""| | | |  __/ |_ \n""", "logo_yellow")\
         + colours.get_colour_string(""" |___/___\___/ \__\__,_|_""", "logo_green")\
         + colours.get_colour_string("""(_)|_| |_|\___|\__|\n""", "logo_yellow")\
         + "-=== Kínai-magyar szótár === 漢 匈 辭 典 ===-\n"
    return logo


