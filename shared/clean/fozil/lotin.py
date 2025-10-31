from clean.trie import trie_from_words
import json
import re
import os

PATH = "clean/fozil" # Bu yerga Dateset turgan pathni kiriting

if PATH == "":
    raise FileNotFoundError("Fayl Pathi topilmadi, iltimos PATH ni kiriting!")

# Kerakli datasetni yuklab olish
with open(os.path.join(PATH, "Umumiy.json"), "r", encoding="utf-8") as file:
    suzlar = json.load(file)
with open(os.path.join(PATH, "Umumiy_cap.json"), "r", encoding="utf-8") as file:
    suzlar_cap = json.load(file)
with open(os.path.join(PATH, "kirill_lotin.json"), "r", encoding="utf-8") as file:
    kirill_latin = json.load(file)
with open(os.path.join(PATH, "chilar.json"), "r", encoding="utf-8") as file:
    chilar = json.load(file)
with open(os.path.join(PATH, "chilar_cap.json"), "r", encoding="utf-8") as file:
    chilar_cap = json.load(file)

# TRIE RE COMPILE qilish
suzlar_re = re.compile(r"\b"+trie_from_words(suzlar))
suzlar_cap_re = re.compile(r"\b"+trie_from_words(suzlar_cap),re.IGNORECASE)
kirill_latin_re = re.compile("|".join(kirill_latin.keys()))
chilar_re = re.compile(r"\b"+trie_from_words(chilar)+r"\b")
chilar_cap_re = re.compile(r"\b"+trie_from_words(chilar_cap)+r"\b",re.IGNORECASE)
sanalar_re = re.compile(r"(\d+)\s+(yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|oktabr|sentyabr|oktyabr|noyabr|dekabr|yil|y)",re.IGNORECASE)

def lotinga(text):
    text = re.sub(r"(ʻ|‘|`|ʼ|’)","'", text)
    text = re.sub(r"(o|g|O|G)'",r"\1‘",text)
    text = re.sub(r"([A-Za-z])'([A-Za-z])?",r"\1’\2",text)
    text = re.sub(r"'",r"",text)
    text = re.sub(r"«([^»]+)»","“\\1”",text)
    text = suzlar_re.sub(lambda x: suzlar[x.group(0)],text)
    text = suzlar_cap_re.sub(lambda x: suzlar_cap[x.group(0).capitalize()],text)
    text = re.sub(r"([A-ZА-ЩЫ-ЯЎҚҒҲ])Ё|(АЪ|ЕЪ)Ё([A-ZА-ЯЎҚҒҲ])|ЪЁ([A-ZА-ЯЎҚҒҲ])|Ё([A-ZА-ЯЎҚҒҲ])",r"\1\2YO\3\4\5",text)
    text = re.sub(r"([A-ZА-ЩЫ-ЯЎҚҒҲ])Ю|(АЪ|ЕЪ)Ю([A-ZА-ЯЎҚҒҲ])|ЪЮ([A-ZА-ЯЎҚҒҲ])|Ю([A-ZА-ЯЎҚҒҲ])",r"\1\2YU\3\4\5",text)
    text = re.sub(r"([A-ZА-ЯЎҚҒҲЁ])Ч|Ч([A-ZА-ЯЎҚҒҲ])",r"\1CH\2",text)
    text = re.sub(r"([A-ZА-ЯЎҚҒҲЁ])Ш|Ш([A-ZА-ЯЎҚҒҲ])",r"\1SH\2",text)
    text = re.sub(r"([A-ZА-ЯЎҚҒҲЁ])Щ|Щ([A-ZА-ЯЎҚҒҲ])",r"\1SH\2",text)
    text = re.sub(r"([A-ZА-ЯЎҚҒҲЁ])Я|Я([A-ZА-ЯЎҚҒҲ])",r"\1YA\2",text)
    text = kirill_latin_re.sub(lambda x: kirill_latin[x.group(0)],text)
    text = re.sub(r"([AOUEIЕ][‘’]?)Ц([A-ZЕa-zе])|([aoueiе][‘’]?)Ц([A-ZЕ])",r"\1\3TS\2\4",text)
    text = re.sub(r"([aoueiе][‘’]?)Ц([a-zе])",r"\1Ts\2",text)
    text = re.sub(r"([aoueiеAOUEIЕ][‘’]?)ц([a-zеA-ZЕ])",r"\1ts\2",text)
    text = re.sub(r"Ц","S",text)
    text = re.sub(r"ц","s",text)
    text = re.sub(r"([\W]|_)Е([A-ZЕ])|^Е([A-ZЕ])|([AOUEIЕ]‘?)Е$|([AOUEIЕ]‘?)Е([\W]|_)|([AOUEIЕ]‘?)Е([A-ZЕ])|([aoueiе]‘?)Е([A-ZЕ])",r"\1\4\5\7\9YE\2\3\6\8\10",text)
    text = re.sub(r"([\W]|_)Е([a-zе])|^Е([a-zе])|([aoueiе]‘?)Е$|([aoueiе]‘?)Е([\W]|_)|([AOUEIЕ]‘?)Е([a-zе])|([aoueiе]‘?)Е([a-zе])|^Е|([\W]|_)Е",r"\1\4\5\7\9\11Ye\2\3\6\8\10",text)
    text = re.sub("Е","E",text)
    text = re.sub(r"^е|([\W]|_)е|([aoueiеAOUEIЕ]‘?)е",r"\1\2ye",text)
    text = re.sub("е","e",text)
    text = sanalar_re.sub(r"\1-\2",text)
    text = chilar_re.sub(lambda x: chilar[x.group(0)],text)
    text = chilar_cap_re.sub(lambda x: chilar_cap[x.group(0).capitalize()],text)
    return text
