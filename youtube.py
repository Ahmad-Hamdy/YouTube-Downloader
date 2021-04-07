# test cases: https://www.youtube.com/watch?v=7-qGKqveZaM       short video
#             https://www.youtube.com/watch?v=1fOBgosDo7s

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from pafy import new
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('youtube.ui', self)
        self.setupUi()

    def setupUi(self):
        self.downloader = DownLoader()
        self.thread = QtCore.QThread(self)
        self.thread.start()
        self.downloader.moveToThread(self.thread)
        self.pathEntry.editingFinished.connect(self.get_streams)
        self.destination_path.editingFinished.connect(self.update_download_path)
        self.browse.clicked.connect(self.get_download_path)
        self.download.clicked.connect(self.start_download)
        self.downloader.ratioSignal.connect(self.progressBar.setValue)
        self.downloader.recvdSignal.connect(self.download_size.setText)
        self.downloader.etaSignal.connect(self.download_eta.setText)
        self.downloader.finished.connect(self.on_finished)

    def get_streams(self): 
        global Streams
        Streams = None
        URL = self.pathEntry.text()

        if not URL:
            return False

        Streams = new(URL).streams

        resolutions = [video.dimensions[1] for video in Streams]
        if 144 in resolutions:
            self.res_144.setEnabled(True)
        if 240 in resolutions:
            self.res_240.setEnabled(True)
        if 360 in resolutions:
            self.res_360.setEnabled(True)
        if 480 in resolutions:
            self.res_480.setEnabled(True)
        if 720 in resolutions:
            self.res_720.setEnabled(True)

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
            msg.setText("URL Error")
            msg.setInformativeText("Video URL field is empty")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return
        
        selected_resolution = [resolution.text() for resolution in [self.res_144, self.res_240, self.res_360, self.res_480, self.res_720] if resolution.isChecked()]
        if selected_resolution:
            selected_resolution = int(selected_resolution[0][:-1])
        elif not Streams:
            return
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("No resolution provided")
            msg.setInformativeText("Please select one of the available resolutions")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        video = None
        for stream in Streams:
        	if stream.dimensions[1] == selected_resolution:
        		video = stream
        		break

        if self.path:
            QtCore.QMetaObject.invokeMethod(self.downloader, "start_download",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(object, video),
                QtCore.Q_ARG(str, self.path))

    @QtCore.pyqtSlot()
    def on_finished(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Success")
        msg.setText("Download complete successfully")
        msg.setInformativeText("Video saved at: " + self.path)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):
        self.thread.terminate()


class DownLoader(QtCore.QObject):
    ratioSignal = QtCore.pyqtSignal(int)
    recvdSignal = QtCore.pyqtSignal(str)
    etaSignal = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(object, str)
    def start_download(self, video, path):
        video.download(filepath = path, quiet=True, callback= self.on_progress)

    def on_progress(self, total, recvd, ratio, rate, eta):
        self.ratioSignal.emit(int(ratio * 100))
        self.recvdSignal.emit(f"{int(recvd)/1000}/{int(total)/1000} MBs")
        self.etaSignal.emit(str(eta) + " Seconds")
        if recvd == total:
            self.finished.emit()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
sys.exit(app.exec_())