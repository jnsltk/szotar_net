import os
import re
import sys

from termcolor import colored, cprint
from szotar_net.colours import COLOURS

dirname = os.path.dirname(__file__)
print(dirname)
print(os.path.realpath(os.path.join(dirname, '..')))
print(sys.prefix)

while True:
    roman = input("enter roman num ")
    if not roman:
        break
    if re.match(r"^[1-9]+\.*\s*$", roman):
        cprint("Yay", attrs=["bold"])

    else:
        print(type(colored("Nay", *COLOURS["pelda_zh"])))
        print(colored("Nay", *COLOURS["pelda_zh"]))


# r"^[1-9]+\.\s*$"
# r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$"