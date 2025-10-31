import re
# from clean.fozil import lotinga
from shared.clean.trie import lugat

VOC = lugat

# 1. Roman digits convert to words.
def roman2digit(s):
    roman = {'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000, 'IV':4, 'IX':9, 'XL':40, 'XC':90, 'CD':400, 'CM':900}
    i = 0
    num = 0
    while i < len(s):
        if i+1<len(s) and s[i:i+2] in roman:
            num+=roman[s[i:i+2]]
            i+=2
        else:
            num+=roman[s[i]]
            i+=1
    return str(num)

def replace_roman(match):
    matched = match.group(2)
    # IIV is not roman digit. It means "Ichki ishlar vazirligi"
    if matched == 'IIV':
        return match.group(1)+'iiv'+match.group(3)
    # In this dataset, X is not roman digit. It means "iks" like "Iphone x" in our dataset
    if matched == 'X':
        return match.group(1)+'iks'+match.group(3)
    number = roman2digit(matched)
    word = num2word(number)
    if word[-1] == 'i' or word[-1] == 'a':
        word += 'nchi'
    else:
        word += 'inchi'
    return match.group(1)+word+match.group(3)


def three_digit(a):
    if len(a) < 3:
        a = '0'*(3-len(a))+a
    yuz, on, bir = a
    word = ''

    birlik = {
        '0': "",
        '1': "bir",
        '2': "ikki",
        '3': "uch",
        '4': "to'rt",
        '5': "besh",
        '6': "olti",
        '7': "yetti",
        '8': "sakkiz",
        '9': "to'qqiz"
    }
    onlik = {
        '0': "",
        '1': " o'n",
        '2': " yigirma",
        '3': " o'ttiz",
        '4': " qirq",
        '5': " ellik",
        '6': " oltmish",
        '7': " yetmish",
        '8': " sakson",
        '9': " to'qson"
    }
    yuzlik = {
        '0': "",
        '1': "bir yuz",
        '2': "ikki yuz",
        '3': "uch yuz",
        '4': "to'rt yuz",
        '5': "besh yuz",
        '6': "olti yuz",
        '7': "yetti yuz",
        '8': "sakkiz yuz",
        '9': "to'qqiz yuz"
    }
    # yuzlar xonasi
    word += yuzlik[yuz]
    # o'nlar xonasi
    word += onlik[on]
    # birlar xonasi
    word = word+' '+birlik[bir]
    
    return word

def num2word(n):
    # main function which convert number to word
    # if length of the number greater 15, the function return word of each digit in the number
    # 10 - o'n, 3412355 - uch million to'rt yuz o'n ikki ming uch yuz ellik besh
    # 12345678910111213 - bir ikki uch (...) bir ikki bir uch
    if "." in n: n = n[:n.find(".")]
    if "," in n: n = n[:n.find(",")]
    # clear zeros that do not affect the value
    if n.count("0") != len(n):
        n = n.lstrip("0")
    if len(n) <= 15:
        if int(n) == 0:
            return 'nol'
        names = ["", "ming", "million", "milliard", "trillion", "kvadrillion", "kvintillion", "sekstillion", "septillion", "oktalon", "nonalon", "dekalon", "endekalon", "dodekalon"]
        word = ''
        index = 0
        while len(n) > 3:
            triple = n[len(n)-3:]
            if int(triple) != 0:
                word = three_digit(triple)+' '+names[index]+' '+word
            n = n[:len(n)-3]
            index += 1
        else:
            if int(n) != 0:
                word = three_digit(n)+' '+names[index]+' '+word
        return re.sub(r" +", " ", word).strip()
    elif len(n) == 16:
        return ' '.join(re.sub(r"(0*)(\d+)", zeros, n[i:i+2]) for i in range(0, 16, 2))
    else:
        birlik = {
            '0': "nol",
            '1': "bir",
            '2': "ikki",
            '3': "uch",
            '4': "to'rt",
            '5': "besh",
            '6': "olti",
            '7': "yetti",
            '8': "sakkiz",
            '9': "to'qqiz"
        }
        return ' '.join(birlik[digit] for digit in n)

def float_num2word(n):
    # clear zeros that do not affect the value
    # 35,33400 -> 35,334
    n = n.rstrip("0")
    # float number to words:
    # 1,3 - bir butun o'ndan uch, 15.12 - o'n besh butun yuzdan o'n ikki
    tens = ["o'ndan ", "yuzdan ", "mingdan ", "o'n mingdan ", "yuz mingdan ", "milliondan "]
    if n[-1] in '.,':
        whole, frac = n[:-1], '0'
    elif '.' not in n and ',' not in n:
        whole, frac = n, '0'
    else:
        whole, frac = re.findall(r'\d+', n)
    frac = re.sub(r"(0)(0+$)", r"\1", frac)
    if frac == '0':
        return num2word(whole)
    if len(frac) > len(tens):
        return num2word(whole)+' butun '+' '.join([num2word(num) for num in frac])
    return num2word(whole) + ' butun ' + tens[len(frac)-1] + num2word(frac)


def zeros(match):
    # 03 - nol uch, 007 - nol nol yetti
    return len(match.group(1))*"nol "+num2word(match.group(2))

# Dates (10.02.2005, 23-12-1992, 2024/10/31)
def date(match):
    if match.group(2) is not None:
        full_date = match.group(1)
        split = match.group(2)
    else:
        full_date = match.group(4)
        split = match.group(5)
    date = re.sub(rf"\{split}", r".", full_date)
    date = date.split('.')
    return re.sub(r"(0*)(\d+)", zeros, date[0])+' '+re.sub(r"(0*)(\d+)", zeros, date[1])+' '+re.sub(r"(0*)(\d+)", zeros, date[2])


# Times (15:00, 01:00, )
def time(match):
    return add_yu(num2word(match.group(1)))+' '+re.sub(r"(0*)(\d+)", zeros, match.group(2))

# Site names
def site(match):
    text = re.sub(r"\.", r" nuqta ", match.group(4))
    text = re.sub(r"/", r", ", text)
    return re.sub(r"com", "kom", text)

# Phone number
def phone(match):
    return "plyus "+re.sub(r"(0*)(\d+)", zeros, match.group(3))+" "+re.sub(r"(0*)(\d+)", zeros, match.group(6))+" "+\
        re.sub(r"(0*)(\d+)", zeros, match.group(8))+" "+re.sub(r"(0*)(\d+)", zeros, match.group(10))+" "+\
        re.sub(r"(0*)(\d+)", zeros, match.group(12))

# Fraction (1/5, 23/65564)
def fraction(match):
    return num2word(match.group(2))+'dan '+num2word(match.group(1))

# Floats (1.3, 324.353)
def float(match):
    return float_num2word(match.group())

# 13-13,5, 01.01.2001-98, 192.169.0.1
def bigrest(match):
    number = match.group()
    # Float numbers
    if re.search(r",", number):
        number = re.sub(r"(?<=\d),(?=0{3})", r"", number)
        if number.count(',') == 1 and number[-1] != ',':
            number = float_num2word(number)
        else:
            number = num2word(re.sub(r",", r"", number))
    number = re.sub(r",", r".", number)
    # Dates
    if re.match(r"(?:(\d{2}(\.|/|\-)\d{2}(\.|/|\-)\d{4})|(\d{4}(\.|/|\-)\d{2}(\.|/|\-)\d{2}))\-?$", number):
        number = re.sub(r"(?:(\d{2}(\.|/|\-)\d{2}(\.|/|\-)\d{4})|(\d{4}(\.|/|\-)\d{2}(\.|/|\-)\d{2}))\-?$", date, number)
    # Time
    elif re.match(r"(\d+)\:(\d+)-?$", number):
        number = re.sub(r"(\d+)\:(\d+)-?$", time, number)
    # Fraction
    elif re.match(r"(\d+)/(\d+)-?$", number):
        number = re.sub(r"(\d+)/(\d+)$", fraction, number)
    # Float numbers
    elif re.match(r"\d+\.\d+\-?$", number):
        number = re.sub(r"\d+\.\d+", float, number)
    # rest of numbers
    else:
        number = re.sub(r"\d+", rest, number)
    return number

# Rest of numbers (1/2/5/6/3, 32, 192.168.0.1, 1-2, 1.5-2.5, 4,2-5.6)
def rest(match):
    number = match.group()
    return num2word(number)

# Add (i)nchi to end of number (olti- to oltinchi, sakkiz- to sakkizinchi)
def add_inchi(string):
    if string[-1] in 'aeiou':
        return string+'nchi'
    else:
        return string+'inchi'

# Add (y)u to end of number (olti- to oltiyu, sakkiz- to sakkizu)
def add_yu(string):
    if string[-1] in 'aeiou':
        return string+'yu'
    else:
        return string+'u'

def replace_meaning(match):
    meaning = {
        '$': 'dollar',
        '–': 'minus',
        '+': 'plyus',
        '°C': 'gradus selsiy',
        '°': 'gradus',
        '%': 'foiz',
        '=': 'teng'
    }
    return " "+meaning[match.group()]+" "

def decode(match): # r"(Ğ|ğ|Õ|õ|Ş|ş|Ç|ç)"
    ijuft = {
        'Ğ': "G'",
        'ğ': "g'",
        'Õ': "O'",
        'õ': "o'",
        'Ş': 'Sh',
        'ş': 'sh',
        'Ç': 'Ch',
        'ç': 'ch'
    }
    return ijuft[match.group()]

def encode(match): # r"(?:(?:(O|o|G|g)(‘|ʻ|'|ʼ|’))|(?:(S|s|C|c)(H|h)))"
    juft = {
        'G': 'Ğ',
        'g': 'ğ',
        'O': 'Õ',
        'o': 'õ',
        'S': 'Ş',
        's': 'ş',
        'C': 'Ç',
        'c': 'ç'
    }
    birikma = ''.join(list(map(lambda x: '' if x is None else x, match.groups())))
    return juft[birikma[0]]

def split(text, vocabulary=VOC, limit=100, minimum=1):
    # kiril to latin
    # text = lotinga(text)
    # correct signs
    text = re.sub(r"[´ʻʼ`‘’]", "'", text)
    # correct probels
    text = re.sub(r"[\xa0]", r" ", text)
    # replace all to -
    text = re.sub(r"[\-–—]", r"-", text)
    # replace particle
    text = re.sub(r"\-(chi|a|ya|ku|u|yu|da|e|ey|yey)\b", r"\1", text)
    # replace tire \n
    text = re.sub(r"( \- )|(\n)", ", ", text)
    # correct dash(if it mean sign of number –, else -.)
    text = re.sub(r"([^\dA-Za-z])(-)(\d)", r"\1–\3", text)
    # replace roman to digit
    text = re.sub(r"(^| )(\b[IVX]+\b)( |$)", replace_roman, text)
    # replace combination letters to one letter
    text = re.sub(r"(?:(?:(O|o|G|g)('))|(?:(S|s|C|c)(H|h)))", encode, text)
    # lug'at
    pattern = re.compile(r"\b("+"|".join(re.escape(k) for k in vocabulary)+")")
    text = pattern.sub(lambda m: vocabulary[m.group(0)], text)
    # replace markdown
    text = re.sub(r"\b1[,\.]5\b", " bir yarim ", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # replace site name
    text = re.sub(r"(?:(\bhttps?://(www\.)?)|(\bwww\.))([^ ,]+)", site, text)
    # phone numbers
    text = re.sub(r"(\(?)(\+)(\d{3})(\)|)(\-| |)(\d{2})(\-| |)(\d{3})(\-| |)(\d{2})(\-| |)(\d{2})", phone, text)
    # split numbers and letters
    splitted = re.findall(r"\d[\d,\.\-/:]*|[^\d\n\$–\+°%=]*|[\n\$–\+°%=]", text)
    i = 0
    while i < len(splitted):
        while i != len(splitted)-1 and splitted[i+1].strip(' ') == '':
            splitted.pop(i+1)
            
            if i != len(splitted)-1 and splitted[i].isdigit() and re.search(r"\d", splitted[i+1]):
                splitted[i] = splitted[i]+splitted[i+1]
                splitted.pop(i+1)
        i += 1
    i = 0
    while i < len(splitted):
        if re.search(r"\d", splitted[i]):
            end = ""
            if splitted[i][-1] in [',', '.']:
                end = splitted[i][-1]
                splitted[i] = splitted[i][:-1]
            # correct 200,000,000 to 200000000
            splitted[i] = re.sub(r"(?<=\d),(?=0{3})", r"", splitted[i])
            # replace commas to points
            splitted[i] = re.sub(r",", r".", splitted[i])
            # Dates
            if re.match(r"(?:(\d{2}(\.|/|\-)\d{2}(\.|/|\-)\d{4})|(\d{4}(\.|/|\-)\d{2}(\.|/|\-)\d{2}))\-?$", splitted[i]):
                splitted[i] = re.sub(r"(?:(\d{2}(\.|/|\-)\d{2}(\.|/|\-)\d{4})|(\d{4}(\.|/|\-)\d{2}(\.|/|\-)\d{2}))\-?$", date, splitted[i])
            # Time
            elif re.match(r"(\d+)\:(\d+)-?$", splitted[i]):
                splitted[i] = re.sub(r"(\d+)\:(\d+)-?$", time, splitted[i])
            # Fraction
            elif re.match(r"(\d+)/(\d+)-?$", splitted[i]):
                splitted[i] = re.sub(r"(\d+)/(\d+)$", fraction, splitted[i])
            # Float numbers
            elif re.match(r"\d+\.\d+\-?$", splitted[i]):
                splitted[i] = re.sub(r"\d+\.\d+", float, splitted[i])
            # rest of numbers
            else:
                splitted[i] = re.sub(r"[\d.,]+", bigrest, splitted[i])
            if splitted[i][-1] == "-":
                splitted[i] = add_inchi(splitted[i][:-1])
            splitted[i] = re.sub(r"[^a-z']", r" ", splitted[i])
            splitted[i] = re.sub(r"(?:(?:(O|o|G|g)('))|(?:(S|s|C|c)(H|h)))", encode, splitted[i])
            splitted[i] += end
        elif splitted[i].strip() == '':
            splitted.pop(i)
            continue
        i += 1

    new_text = ' '.join(splitted)
    
    # replace combination letters to one letter
    new_text = re.sub(r"(?:(?:(O|o|G|g)('))|(?:(S|s|C|c)(H|h)))", encode, new_text)
    new_text = re.sub(r"\b[BCDFGHJKLMNPQRSTVWXYZĞŞÇ]\b", lambda m: m.group()+"ï", new_text)
    new_text = re.sub(
        r"\b[BCDFGHJKLMNPQRSTVWXYZĞŞÇ]{2,}",
        lambda m: "".join(ch + "ï" for ch in m.group()),
        new_text
    )

    # replace meaningful characters and short words to full word
    new_text = re.sub(r"(\$|–|\+|°C|\%|\=)", replace_meaning, new_text)
    new_text = re.sub(r"(^| )mln( |\.|,|$)", r"\1million\2", new_text)
    new_text = re.sub(r"(^| )mlrd( |\.|,|$)", r"\1milliard\2", new_text)
    new_text = re.sub(r"(^| )trln( |\.|,|$)", r"\1trillion\2", new_text)
    new_text = re.sub(r"(^| )m( |\.|,|$)", r"\1metr\2", new_text)
    new_text = re.sub(r"(^| )km( |\.|,|$)", r"\1kilometr\2", new_text)
    # remove unnecessary symbols
    new_text = re.sub(r"(?: *[!\?\.,;\:]){2,}", r".", new_text)
    new_text = re.sub(r" *([!\?\.,;\:])", r"\1 ", new_text)
    new_text = re.sub(r"-", r" ", new_text)
    new_text = re.sub(r"c", r"s", new_text)
    new_text = re.sub(r"w", r"v", new_text)
    new_text = re.sub(r"[^abdefghijklmnopqrstuvxyzõğşçï ',\.\?!\:]", r"", new_text.lower())
    new_text = re.sub(r" +(i?nçi|ta|ga|da|tadan|dan|ni|taça|lar|ning|ka|qa)([!\?\.,;\: ])", r"\1\2", new_text)
    new_text = re.sub(r" +", " ", new_text).strip()
    chunks = []
    pointer = 0
    while pointer < len(new_text):
        string = new_text[pointer:pointer+limit]
        if len(string) < limit:
            chunks.append(string)
            pointer += len(string)
            continue
        if string[-1] not in ["!", "?", ".", ",", ":"]:
            part = string[:min(string.rfind("!"), string.rfind("?"), string.rfind("."), string.rfind(":"), string.rfind(","))+1]
            if len(part) < minimum:
                part = string[:string.rfind(" ")+1]
                if len(part) == 0:
                    part = string
            string = part
        chunks.append(string.strip())
        pointer += len(string)
        
    return chunks
