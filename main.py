from PyQt5 import QtWidgets
from ui_mainwindow import Ui

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())