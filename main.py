import sys, untitle
from untitle import Ui_MainWindow
from PyQt4.QtGui import QMainWindow
 
class MainWindow(QMainWindow, Ui_MainWindow):
    def	on_text_changed(self):
		self.label.setText(self.textEdit.toPlainText())
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.textEdit.setText('aaaaaaaaaa')
        self.textEdit.textChanged.connect(self.on_text_changed)
 
if __name__ == "__main__":
    app = untitle.QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())