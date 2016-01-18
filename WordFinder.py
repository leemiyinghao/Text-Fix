# -*- coding: utf_8 -*-
import sys, sqlite3, copy, random, time, codecs
class CodedWordFinder():
    con = sqlite3.connect('dict-revised.sqlite3')
    con.text_factory = str
    def findWord(self,string, index):
        cursor = self.con.execute("""SELECT * FROM entries where title LIKE ?;""", (str('%'+string[(-1 - index):-1]+'%'),))
        # print len(cursor.fetchall())
        if len(cursor.fetchall()) > 0 and index < len(string):
            result = self.findWord(string, index+1)
            if result == None:
                cursor = self.con.execute("""SELECT * FROM entries where title LIKE ?;""", (str('%'+string[(-1 - index):-1]+'%'),))
                firstRow = cursor.fetchone()
                print firstRow[0]
                return firstRow[0]
            else:
                return result
        else:
            return None
    def wordCountByAEncode(self,phList):
        strTemp = ""
        for item in phList:
            strTemp += item + " "
        strTemp = strTemp[:-1]
        cursor = self.con.execute("""SELECT COUNT(bopomofoAEncode) FROM heteronyms WHERE bopomofoAEncode LIKE ?;""", (str('%'+strTemp+'%'),))
        return cursor.fetchone()[0]

    def findAllPhoneticInAEncode(self, ch):
        cursor = self.con.execute("""SELECT `id` from entries WHERE title = ?;""", (ch, ))
        charId = cursor.fetchone()
        if charId != None:
            charId = charId[0]
            cursor = self.con.execute("""SELECT `bopomofoAEncode` from heteronyms WHERE entry_id = ?""", (charId, ))
            lis = cursor.fetchall()
            retList = list()
            for item in lis:
                if item[0] == None:
                    break
                if item[0].decode("utf8") in retList:
                    continue
                retList.append(item[0].decode("utf8"))
            return retList
        else:
            return (" ",)
    def expendAllPhonticCombination(self, phoneticLists, index):
        tempList = list()
        if index+1 < len(phoneticLists):
            nextChar = self.expendAllPhonticCombination(phoneticLists, index+1)
            for phonetic in phoneticLists[index]:
                nextCharCopy = copy.deepcopy(nextChar)
                for nextCharCopyitem in nextCharCopy:
                    nextCharCopyitem.insert(0, phonetic)
                tempList.extend(nextCharCopy)
        else:
            for phonetic in phoneticLists[index]:
                tempList.append([phonetic,])
        return tempList
class WordFinder():
    con = sqlite3.connect('dict-revised.sqlite3')
    con.text_factory = str
    def findWord(self,string, index):
        cursor = self.con.execute("""SELECT * FROM entries where title LIKE ?;""", (str('%'+string[(-1 - index):-1]+'%'),))
        # print len(cursor.fetchall())
        if len(cursor.fetchall()) > 0 and index < len(string):
            result = self.findWord(string, index+1)
            if result == None:
                cursor = self.con.execute("""SELECT * FROM entries where title LIKE ?;""", (str('%'+string[(-1 - index):-1]+'%'),))
                firstRow = cursor.fetchone()
                print firstRow[0]
                return firstRow[0]
            else:
                return result
        else:
            return None
    def findAllPhonetic(self, ch):
        cursor = self.con.execute("""SELECT `id` from entries WHERE title = ?;""", (ch, ))
        charId = cursor.fetchone()
        if charId != None:
            charId = charId[0]
            cursor = self.con.execute("""SELECT `bopomofo` from heteronyms WHERE entry_id = ?""", (charId, ))
            lis = cursor.fetchall()
            retList = list()
            for item in lis:
                retList.append(item[0].decode("utf8"))
            return retList
        else:
            return (" ",)
    def expendAllPhonticCombination(self, phoneticLists, index):
        tempList = list()
        if index+1 < len(phoneticLists):
            nextChar = self.expendAllPhonticCombination(phoneticLists, index+1)
            for phonetic in phoneticLists[index]:
                nextCharCopy = copy.deepcopy(nextChar)
                for nextCharCopyitem in nextCharCopy:
                    nextCharCopyitem.insert(0, phonetic)
                tempList.extend(nextCharCopy)
        else:
            for phonetic in phoneticLists[index]:
                tempList.append([phonetic,])
        return tempList
    def expendApproxPhonetics(self, phonetic):
        #resolve vowel and consonant
        consonantList = u"ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
        halfVowelList = u"一ㄨㄩ"
        vowelsList = u"ㄚㄛㄜㄝㄞㄟㄠㄢㄣㄤㄥㄦ"
        consonant = u""
        halfVowel = u""
        vowel = u""
        for phoneticChar in phonetic:
            if phoneticChar in consonantList:
                consonant = phoneticChar
            elif phoneticChar in halfVowelList:
                halfVowel = phoneticChar
            elif phoneticChar in vowelsList:
                vowel = phoneticChar
        approxVowels = [halfVowel + vowel,]
        approxConsonants = [consonant,]
        approxPhonetics = list()
        cursor = self.con.execute("""SELECT `approx_phonetic` from approximate_tone WHERE phonetic = ?""", (halfVowel + vowel,))
        for approxVowel in cursor.fetchall():
            approxVowels.append(approxVowel[0].decode('utf8'))
        #TODO: fetch approx consonant
        for approxVowel in approxVowels:
            for approxConsonant in approxConsonants:
                approxPhonetics.append(approxConsonant + approxVowel)
                approxPhonetics.append(approxConsonant + approxVowel + u"ˊ")
                approxPhonetics.append(approxConsonant + approxVowel + u"ˇ")
                approxPhonetics.append(approxConsonant + approxVowel + u"ˋ")
                approxPhonetics.append(approxConsonant + approxVowel + u"˙")
        return approxPhonetics
finder = CodedWordFinder()
oldFinder = WordFinder()
for j in range(1000):
    cursor = finder.con.execute("""SELECT `title` from entries WHERE id=?""",(random.randint(1946,163094),))
    phoneticLists = list()
    inputString = cursor.fetchone()[0].decode("utf8")
    print inputString
    searchList = list()
    searchTemp = ""
    tStart = time.time()
    for ch in inputString:
        phoneticLists.append(finder.findAllPhoneticInAEncode(ch))
    searchList = finder.expendAllPhonticCombination(phoneticLists,0)
    for comb in searchList:
        strTemp = ""
        for item in comb:
            strTemp += item + " "
        searchTemp += "bopomofoAEncode="+strTemp+"OR "
    searchTemp += "0"
    cursor = finder.con.execute("""SELECT `entry_id` from heteronyms WHERE ?""", (strTemp,))
    entry_ids = cursor.fetchall()
    tEnd = time.time()
    newTime = (tEnd - tStart)
    tStart = time.time()
    phoneticLists = list()
    searchList = list()
    finalPhoneticLists = list()
    for ch in inputString:
        phoneticList = oldFinder.findAllPhonetic(ch)
        approxPhoneticList = list()
        for phonetic in phoneticList:
            approxPhoneticList.extend(oldFinder.expendApproxPhonetics(phonetic))
        phoneticLists.append(approxPhoneticList)
    searchList = oldFinder.expendAllPhonticCombination(phoneticLists,0)
    searchTemp = u""
    for comb in searchList:
        strTemp = ""
        for item in comb:
            strTemp += item + " "
        searchTemp += "bopomofo="+strTemp+"OR "
    searchTemp += "0"
    cursor = oldFinder.con.execute("""SELECT `entry_id` from heteronyms WHERE ?""", (searchTemp,))
    entry_ids = cursor.fetchall()
    tEnd = time.time()
    oldTime = (tEnd - tStart)
    print "%f, %f" % (oldTime, newTime)
    f = codecs.open('test.csv', 'a', 'utf-8')
    f.write(u"%s, %f, %f\n" % (inputString, oldTime, newTime))
    f.close()