# -*- coding: utf_8 -*-
import sys, untitle, sqlite3 
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
    def	on_text_changed(self):
        # print unicode(self.textEdit.toPlainText(),"utf8")
        word_id = self.findWord(self.textEdit.toPlainText() + " ", 1)
        cursor = self.con.execute("""SELECT bopomofo from heteronyms WHERE entry_id = ?""", (word_id,))
        self.label.setText(str(cursor.fetchone()[0]).decode("utf8"))
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.textEdit.setText('請輸入文字')
        self.textEdit.textChanged.connect(self.on_text_changed)

if __name__ == "__main__":
    app = untitle.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())