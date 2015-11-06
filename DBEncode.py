import sqlite3, re
def splitBopomofo(str):
    bopomofoBoard = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ"
    splited = re.findall("[" + bopomofoBoard + "]+", str)
    return splited
def typeAEncode(str):
    vowelBoard = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
    consonantBoard = "ㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ"
    vowelTransfer = {
        "": "1",
        "ㄇ": "1",
        "ㄈ": "1",
        "ㄏ": "1",
        "ㄅ": "2",
        "ㄆ": "2",
        "ㄉ": "3",
        "ㄊ": "3",
        "ㄋ": "4",
        "ㄌ": "4",
        "ㄖ": "4",
        "ㄍ": "5",
        "ㄎ": "5",
        "ㄐ": "6",
        "ㄑ": "6",
        "ㄒ": "6",
        "ㄓ": "7",
        "ㄗ": "7",
        "ㄔ": "8",
        "ㄘ": "8",
        "ㄕ": "9",
        "ㄙ": "9"
    }
    consonantTransfer = {
        "": "",
        "ㄚ": "A",
        "ㄢ": "A",
        "ㄤ": "A",
        "ㄛ": "B",
        "ㄡ": "B",
        "ㄨㄛ": "B",
        "ㄨㄥ": "B",
        "ㄜ": "C",
        "ㄦ": "C",
        "ㄝ": "D",
        "ㄟ": "D",
        "ㄧㄝ": "D",
        "ㄧㄢ": "D",
        "ㄩㄢ": "D",
        "ㄞ": "E",
        "ㄧㄞ": "E",
        "ㄠ": "F",
        "ㄧㄠ": "F",
        "ㄨ": "G",
        "ㄩ": "G",
        "ㄧㄚ": "H",
        "ㄧㄤ": "H",
        "ㄧㄛ": "I",
        "ㄧㄡ": "I",
        "ㄩㄥ": "I",
        "ㄧ": "J",
        "ㄧㄣ": "J",
        "ㄧㄥ": "J",
        "ㄩㄣ": "J",
        "ㄣ": "K",
        "ㄥ": "K",
        "ㄨㄣ": "K",
        "ㄨㄞ": "L",
        "ㄨㄢ": "L",
        "ㄨㄚ": "M",
        "ㄨㄤ": "M",
        "ㄨㄟ": "N",
        "ㄩㄝ": "N",
    }
    vowel = ""
    consonant = ""
    if str[0] in vowelBoard:
        vowel = str[0]
        consonant = str[1:]
    else:
        consonant = str
    if vowel in vowelTransfer and consonant in consonantTransfer:
        vowel = vowelTransfer[vowel]
        consonant = consonantTransfer[consonant]
        return vowel+consonant
    else:
        return "Z"
con = sqlite3.connect('dict-revised.sqlite3')
#con.text_factory = 'big5'
for i in range(1,165830):
    cursor = con.execute("""SELECT `bopomofo` from heteronyms WHERE id=?""",(i,))
    bopomofo = cursor.fetchone()
    if bopomofo[0] != None:
        listBuf = splitBopomofo(bopomofo[0])
        strBuf = ""
        for bopomofo in listBuf:
            strBuf += typeAEncode(bopomofo) + " "
        if strBuf[-1:] == " ":
            strBuf = strBuf[:-1]
        cursor = con.execute("""UPDATE heteronyms SET bopomofoAEncode=? WHERE id=?""", [strBuf,i])
        print("UPDATE heteronyms SET bopomofoAEncode=? WHERE id=?", (strBuf, i))
con.commit()
cursor = con.execute("""SELECT `bopomofo` from heteronyms WHERE id=?""",(165830,))
bopomofo = cursor.fetchone()
print(bopomofo)
