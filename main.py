# -*- coding: utf_8 -*-
import sys, untitle, sqlite3, copy, random, time
from untitle import Ui_MainWindow
from PyQt4.QtGui import QMainWindow
sys.setdefaultencoding('utf_8')
class MainWindow(QMainWindow, Ui_MainWindow):
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
    def findAllPhoneticInAEncode(self, ch):
        cursor = self.con.execute("""SELECT `id` from entries WHERE title = ?;""", (ch, ))
        charId = cursor.fetchone()
        if charId != None:
            charId = charId[0]
            cursor = self.con.execute("""SELECT `bopomofoAEncode` from heteronyms WHERE entry_id = ?""", (charId, ))
            lis = cursor.fetchall()
            retList = list()
            for item in lis:
                if item[0].decode("utf8") in retList:
                    continue
                retList.append(item[0].decode("utf8"))
            return retList
        else:
            return (" ",)
    def expendApproxPhonetics(self, phonetic):
        #resolve vowel and consonant
        consonantList = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
        halfVowelList = "一ㄨㄩ"
        vowelsList = "ㄚㄛㄜㄝㄞㄟㄠㄢㄣㄤㄥㄦ"
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
                approxPhonetics.append(approxConsonant + approxVowel + "ˊ")
                approxPhonetics.append(approxConsonant + approxVowel + "ˇ")
                approxPhonetics.append(approxConsonant + approxVowel + "ˋ")
                approxPhonetics.append(approxConsonant + approxVowel + "˙")
        return approxPhonetics
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
    def onButtonPressed(self):
        tempStr = u""
        phoneticLists = list()
        inputString = str(self.textEdit.toPlainText()).decode('utf8')
        searchList = list()
        displayBuf = ""
        for ch in reversed(inputString):
            if ch == None or ch == '\n':
                continue
            phoneticLists.insert(0,self.findAllPhoneticInAEncode(ch))
            searchList = self.expendAllPhonticCombination(phoneticLists,0)
            countResult = 0
            for comb in searchList:
                countResult += self.wordCountByAEncode(comb)
            if countResult == 0:
                firstChr = phoneticLists[0]
                phoneticLists = phoneticLists[1:]
                searchList = self.expendAllPhonticCombination(phoneticLists,0)
                for comb in searchList:
                    strTemp = ""
                    for item in comb:
                        strTemp += item + " "
                    strTemp = strTemp[:-1]
                    print strTemp
                    cursor = self.con.execute("""SELECT `entry_id` from heteronyms WHERE bopomofoAEncode = ?""", (strTemp,))
                    entry_ids = cursor.fetchall()
                    for entry_id in entry_ids:
                        cursor = self.con.execute("""SELECT `title` from entries WHERE id = ?""", (entry_id[0],))
                        tempStr += cursor.fetchone()[0] + " "
                phoneticLists = list()
                phoneticLists.append(firstChr)
                tempStr += "\n"
        searchList = self.expendAllPhonticCombination(phoneticLists,0)
        for comb in searchList:
            strTemp = ""
            for item in comb:
                strTemp += item + " "
            strTemp = strTemp[:-1]
            print strTemp
            cursor = self.con.execute("""SELECT `entry_id` from heteronyms WHERE bopomofoAEncode = ?""", (strTemp,))
            entry_ids = cursor.fetchall()
            for entry_id in entry_ids:
                cursor = self.con.execute("""SELECT `title` from entries WHERE id = ?""", (entry_id[0],))
                tempStr += cursor.fetchone()[0] + " "
        phoneticLists = list()
        tempStr += "\n"
        self.textEdit_2.setText(tempStr)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.textEdit.setText('Words')
        self.textEdit_2.setText("Phonetic")
        self.pushButton.clicked.connect(self.onButtonPressed)
        #TEST MODE NEW
        for j in range(5):
            tStart = time.time()
            for i in range(10):
                cursor = self.con.execute("""SELECT `title` from entries WHERE id=?""",(random.randint(1946,163094),))
                phoneticLists = list()
                inputString = cursor.fetchone()[0].decode("utf8")
                searchList = list()
                searchTemp = ""
                for ch in inputString:
                    phoneticLists.append(self.findAllPhoneticInAEncode(ch))
                searchList = self.expendAllPhonticCombination(phoneticLists,0)
                for comb in searchList:
                    strTemp = ""
                    for item in comb:
                        strTemp += item + " "
                    searchTemp += "bopomofoAEncode="+strTemp+"OR "
                searchTemp += "0"
                cursor = self.con.execute("""SELECT `entry_id` from heteronyms WHERE ?""", (strTemp,))
                entry_ids = cursor.fetchall()
                self.textEdit_2.setText(searchTemp)
            tEnd = time.time()
            print "It cost %f sec" % (tEnd - tStart)
        print "OLD:"
        #TEST MODE NEW
        #TEST MODE OLD
        for j in range(5):
            tStart = time.time()
            for i in range(10):
                cursor = self.con.execute("""SELECT `title` from entries WHERE id=?""",(random.randint(1946,163094),))
                phoneticLists = list()
                inputString = cursor.fetchone()[0].decode("utf8")
                searchList = list()
                finalPhoneticLists = list()
                for ch in inputString:
                    phoneticList = self.findAllPhonetic(ch)
                    approxPhoneticList = list()
                    for phonetic in phoneticList:
                        approxPhoneticList.extend(self.expendApproxPhonetics(phonetic))
                    phoneticLists.append(approxPhoneticList)
                searchList = self.expendAllPhonticCombination(phoneticLists,0)
                searchTemp = u""
                for comb in searchList:
                    strTemp = ""
                    for item in comb:
                        strTemp += item + " "
                    searchTemp += "bopomofo="+strTemp+"OR "
                searchTemp += "0"
                cursor = self.con.execute("""SELECT `entry_id` from heteronyms WHERE ?""", (searchTemp,))
                entry_ids = cursor.fetchall()
                self.textEdit_2.setText(searchTemp)
            tEnd = time.time()
            print "It cost %f sec" % (tEnd - tStart)
        raw_input()
        #TEST MODE OLD
if __name__ == "__main__":
    app = untitle.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
#TODO: OOP