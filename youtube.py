# test cases: https://www.youtube.com/watch?v=7-qGKqveZaM       short video
#             https://www.youtube.com/watch?v=1fOBgosDo7s

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from requests import get
from pafy import new


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('youtube.ui', self)
        self.setMaximumWidth(900)
        self.setMaximumHeight(750)
        self.Streams = None
        self.URL = ""
        self.selected_resolution = self.resolutions.currentText()
        self.setupUi()

    def setupUi(self):
        self.progress_label.hide()
        self.progressBar.hide()
        self.download_size_label.hide()
        self.download_size.hide()
        self.download_eta_label.hide()
        self.download_eta.hide()
        self.rate_label.hide()
        self.rate.hide()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.downloader = DownLoader()
        self.thread = QtCore.QThread(self)
        self.thread.start()
        self.downloader.moveToThread(self.thread)

        self.pathEntry.editingFinished.connect(self.get_streams)
        self.type.currentTextChanged.connect(lambda t: self.type_changed(t))
        self.resolutions.textActivated.connect(lambda text: self.change_resolution(text))
        self.destination_path.editingFinished.connect(self.update_download_path)
        self.browse.clicked.connect(self.get_download_path)
        self.download.clicked.connect(self.start_download)

        self.downloader.ratioSignal.connect(self.progressBar.setValue)
        self.downloader.recvdSignal.connect(self.download_size.setText)
        self.downloader.rateSignal.connect(self.rate.setText)
        self.downloader.etaSignal.connect(self.download_eta.setText)
        self.downloader.finished.connect(self.on_finished)

    def get_streams(self): 
        self.URL = self.pathEntry.text()

        if not self.URL:
            return False

        try:
            video = new(self.URL)
            self.Streams = video.streams
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("self.URL Error")
            msg.setInformativeText("Couldn't find the video self.URL given")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(get(video.bigthumb).content)
        self.thumbnail.setPixmap(pixmap.scaled(150, 150))
        self.title.setText(f"{video.title}")
        self.category.setText(f"Category: {video.category}")
        self.rating.setText(f"Rating: {video.rating}")
        self.views.setText(f"views: {video.viewcount}")
        self.duration.setText(f"{video.duration}")

        resolutions = [f"{video.quality} {video.extension}" for video in self.Streams]
        self.resolutions.clear()
        self.resolutions.insertItems(0, resolutions)

    def type_changed(self, t):
        try:
            if t == "Video only":
                self.Streams = new(self.URL).videostreams
            elif t == "Audio only":
                self.Streams = new(self.URL).audiostreams
            elif t == "Video + Audio":
                self.Streams = new(self.URL).streams
        except:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("self.URL Error")
            msg.setInformativeText("Couldn't find the video URL given")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        resolutions = [f"{video.quality} {video.extension}" for video in self.Streams]
        # update resolutions combo box with list
        self.resolutions.clear()
        self.resolutions.insertItems(0, resolutions)

    def change_resolution(self, resolution):
    	self.selected_resolution = resolution

    def get_download_path(self):
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self)
        self.destination_path.setText(self.path)

    def update_download_path(self):
        self.path = self.destination_path.text()

    def start_download(self):
        if not self.pathEntry.text():
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("self.URL Error")
            msg.setInformativeText("Video self.URL field is empty")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        video = None
        for stream in self.Streams:
        	if f"{stream.quality} {stream.extension}" == self.selected_resolution:
        		video = stream
        		break

        if self.path:
            QtCore.QMetaObject.invokeMethod(self.downloader, "start_download",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(object, video),
                QtCore.Q_ARG(str, self.path))
        self.download.setEnabled(False)
        self.setStatusTip("Downloading...")

    @QtCore.pyqtSlot()
    def on_finished(self):
        self.download.setEnabled(True)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText("Download complete successfully")
        msg.setInformativeText("Video saved at: " + self.path)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

        self.progress_label.hide()
        self.progressBar.hide()
        self.download_size_label.hide()
        self.download_size.hide()
        self.download_eta_label.hide()
        self.download_eta.hide()
        self.rate_label.hide()
        self.rate.hide()

        self.setStatusTip("Download Complete")

    def closeEvent(self, event):
        self.thread.terminate()
        
class DownLoader(QtCore.QObject):
    ratioSignal = QtCore.pyqtSignal(int)
    recvdSignal = QtCore.pyqtSignal(str)
    rateSignal = QtCore.pyqtSignal(str)
    etaSignal = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(object, str)
    def start_download(self, video, path):
        window.progress_label.show()
        window.progressBar.show()
        window.download_size_label.show()
        window.download_size.show()
        window.download_eta_label.show()
        window.download_eta.show()
        window.rate_label.show()
        window.rate.show()
        video.download(filepath = path, quiet=True, callback= self.on_progress)

    def on_progress(self, total, recvd, ratio, rate, eta):
        self.ratioSignal.emit(int(ratio * 100))
        self.recvdSignal.emit("{:.2f}/{:.2f} MBs".format(int(recvd)/1000000, int(total)/1000000))
        self.rateSignal.emit(f"{rate} Kb/s")
        self.etaSignal.emit(str(eta) + " Seconds")
        if recvd == total:
            self.finished.emit()

if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Ui()
	window.show()
	sys.exit(app.exec_())