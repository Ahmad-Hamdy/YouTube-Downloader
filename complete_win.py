from PyQt5 import QtCore, QtGui, QtWidgets, uic
from os import startfile, system
from requests import get
from pafy import new


class download_complete(QtWidgets.QMainWindow):
    def __init__(self, data):
        super(download_complete, self).__init__()
        uic.loadUi('downlad_complete.ui', self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.path = data['path']
        self.location.setText(self.path)
        #pixmap = QtGui.QPixmap()
        #pixmap.loadFromData(data["image"])
        #self.thumbnail.setPixmap(pixmap.scaled(171, 171))
        self.title.setText(data['title'])
        self.category.setText(f"Category: {data['category']}")
        self.rating.setText(f"Rating: {data['rating']}")
        self.views.setText(f"views: {data['views']}")
        self.duration.setText(f"{data['duration']}")
        self.setupUi()

    def setupUi(self):
    	self.exit.clicked.connect(self.close)
    	self.open_location.clicked.connect(lambda :startfile(self.path))
    	self.open.clicked.connect(lambda :system('"{}/{}"'.format(self.path, self.title.text())))
    	self.location.setText(self.path)

if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = download_complete({
			        "title" : "Shortest Video on Youtube EVER! 0 seconds nearly 1 (fastest).webm",
			        "category" : "sample category",
			        "rating" : f"{4.48494:.2}",
			        "views" : f"{12511:,}",
			        "duration" : "00:00:15",
			        "path" : r"E:/"})
	window.show()
	sys.exit(app.exec_())