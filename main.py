# -*- coding: utf_8 -*-
import sys, untitle, sqlite3, copy
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
    def findAllPhonetic(self, ch):
        print ch
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
    def onButtonPressed(self):
        tempStr = u""
        phoneticLists = list()
        inputString = str(self.textEdit.toPlainText()).decode('utf8')
        for ch in inputString:
            print ch
            if ch == None or ch == '\n':
                continue
            phoneticList = self.findAllPhonetic(ch)
            phoneticLists.append(phoneticList)
        tempList = self.expendAllPhonticCombination(phoneticLists,0)
        print tempList
        for item in tempList:
            for i in item:
                tempStr += i
                tempStr += " "
            tempStr += "\n"
        self.label.setText(tempStr)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.textEdit.setText('Words')
        self.label.setText("Phonetic")
        self.pushButton.clicked.connect(self.onButtonPressed)

if __name__ == "__main__":
    app = untitle.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())