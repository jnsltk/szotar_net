from termcolor import colored

from szotar_net import config

COLOURS = {
    "roman_num": ("magenta", None, ["bold"]),
    "arabic_num": ("light_green", None, ["bold"]),
    "misc": ("yellow", None, None),
    "pelda_zh": ("light_blue", None, None),
    "pelda_pinyin": (None , None, ["bold"]),
    "logo_green": ("green", None, None),
    "logo_yellow": ("yellow", None, None),
}

TONES = [
    config.get("ToneColours", "tone_1"),
    config.get("ToneColours", "tone_2"),
    config.get("ToneColours", "tone_3"),
    config.get("ToneColours", "tone_4"),
    config.get("ToneColours", "tone_5"),
]

style = COLOURS

def get_colour_string(string, text_type):
    return colored(string, *style[text_type])

def get_tone_colour(string:str, tone:int):
    if config.get("Settings", "tone_colours"):
        return colored(string, TONES[tone - 1])
    return string