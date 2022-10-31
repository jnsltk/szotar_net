import re

while True:
    roman = input("enter roman num ")
    if roman == "":
        break
    if re.match(r"^[1-9]+\.\s*$", roman):
        print("Yay")
    else:
        print("Nay")


# r"^[1-9]+\.\s*$"
# r"^(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\.\s*$"