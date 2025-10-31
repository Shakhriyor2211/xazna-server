import re

lugat  = {
 'AIRI': 'aiiri',
 'AI': 'eyaay',
 'ATB': 'atibi',
 'B2B': 'biitubii',
 'B2G': 'biitujii',
 'BAA': ' b a a ',
 'BMW': 'biiemdablyu',
 'BYD': 'biivaiydii',
 'DVOICE': 'divoys',
 'FHDYO': 'fi hi di yo',
 'FHDYo': 'fi hi di yo',
 'GPS': 'ji pi es',
 'IBM': 'aybiem',
 'IIB': 'ii ii bi',
 'IIBB': 'ii ii bi bi',
 'IIV': 'ii ii vi',
 'IMEI': 'iimeei',
 'ITI': 'ii ti ii',
 'KFC': 'kiiefsii',
 'LEX': 'leks',
 'LG': 'eljii',
 'MDH': 'em di hi',
 'MIB': 'mi ii bi',
 'MMA': 'ememeii',
 'NKVD': 'en ki vi di',
 "ÕZMTRK": "õzemterka",
 "ÕzMTRK": "õzemterka",
 'OAK': 'oo aa ki',
 'OAV': 'oo aa vi',
 'OÇL': 'oo çi li',
 'OTM': 'oo ti mi',
 'PC': 'pii sii',
 'PPS': 'pi pi es',
 'QDPI': 'qi di pi ii',
 'QR': 'kyuar',
 'RTSIRITI': 'ri ti sii rii tii',
 'STIR': 'stiir',
 'ŞHT': 'şi hi ti',
 'TDPU': 'ti di pi uu',
 'TIV': 'ti ii vi',
 'TV': 'tii vii',
 'UFC': 'yu ef sii',
 'USB': 'yu es bii',
 'VR': 'vii ar',
 'YAIM': 'ya ii mi',
 'YAIT': 'ya ii ti',
 'YAST': 'ya si ti',
 'YOXBB': 'yo xi bi bi',
 'Araloviç': 'araalïviç',
 'Xaldaroviç': 'xaldarïviç',
 'Google': 'gugil',
 'google': 'gugil',
 'Robot': "rõbit",
 'robot': "rõbit",
 'Facebook': "feysbuk",
 'facebook': "feysbuk",
 '1106': "õn bir nol olti",
 '1290': "õn ikki tõqson",
 'xb': "xïbï",
 'online': "onlayn",
 'Capital': 'kapital'
 }

class Trie():
    """Regex::Trie in Python. Creates a Trie out of a list of words. The trie can be exported to a Regex pattern.
    The corresponding Regex should match much faster than a simple Regex union."""

    def __init__(self):
        self.data = {}

    def add(self, word):
        ref = self.data
        for char in word:
            ref[char] = char in ref and ref[char] or {}
            ref = ref[char]
        ref[''] = 1

    def dump(self):
        return self.data

    def quote(self, char):
        return re.escape(char)

    def _pattern(self, pData):
        data = pData
        if "" in data and len(data.keys()) == 1:
            return None

        alt = []
        cc = []
        q = 0
        for char in sorted(data.keys()):
            if isinstance(data[char], dict):
                try:
                    recurse = self._pattern(data[char])
                    alt.append(self.quote(char) + recurse)
                except:
                    cc.append(self.quote(char))
            else:
                q = 1
        cconly = not len(alt) > 0

        if len(cc) > 0:
            if len(cc) == 1:
                alt.append(cc[0])
            else:
                alt.append('[' + ''.join(cc) + ']')

        if len(alt) == 1:
            result = alt[0]
        else:
            result = "(?:" + "|".join(alt) + ")"

        if q:
            if cconly:
                result += "?"
            else:
                result = "(?:%s)?" % result
        return result

    def pattern(self):
        return self._pattern(self.dump())

def trie_from_words(words):
    trie = Trie()
    for word in words:
        trie.add(word)
    return trie.pattern()