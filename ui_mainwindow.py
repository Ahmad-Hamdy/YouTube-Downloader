import yt_dlp
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from requests import get
from downloader import DownLoader
from ui_download_complete import download_complete

window = None  # For DownLoader reference

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
        global window
        window = self

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

        # Load stylesheet from external file
        try:
            with open("style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load stylesheet: {e}")

        self.downloader = DownLoader()
        self.thread = QtCore.QThread(self)
        self.thread.start()
        self.downloader.moveToThread(self.thread)

        self.pathEntry.editingFinished.connect(self.get_streams)
        self.type.currentIndexChanged.connect(self.type_changed)
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
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(self.URL, download=False)
            self.yt_info = info
            self.Streams = [
                f for f in info['formats']
                if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none'
            ]
            self.Streams.sort(key=lambda f: f.get('height', 0), reverse=True)
        except Exception as e:
            print(f"Error in get_streams for URL {self.URL}: {e}")
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("URL Error")
            msg.setInformativeText(f"Couldn't find the video for the given URL\n{e}")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        pixmap = QtGui.QPixmap()
        self.image = get(info['thumbnail']).content
        pixmap.loadFromData(self.image)
        self.thumbnail.setPixmap(pixmap.scaled(171, 171))
        self.title.setText(f"{info['title']}")
        self.category.setText(f"Category: {info.get('categories', ['N/A'])[0]}")
        self.rating.setText(f"Rating: {info.get('average_rating', 'N/A')}")
        self.views.setText(f"views: {info.get('view_count', 'N/A')}")
        duration_sec = info.get('duration', 0)
        self.duration.setText(f"{duration_sec // 60}:{duration_sec % 60:02d}")

        resolutions = [
            f"{f.get('height', 'audio')}p {f.get('ext', '')}"
            for f in self.Streams
        ]
        self.resolutions.clear()
        self.resolutions.insertItems(0, resolutions)
        if self.resolutions.count() > 0:
            self.resolutions.setCurrentIndex(0)
            self.selected_resolution = self.resolutions.currentText()
        if self.type.count() > 0:
            self.type.setCurrentIndex(0)


    def type_changed(self, t):
        try:
            video = self.yt_video
            if t == "Video only":
                self.Streams = video.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc()
            elif t == "Audio only":
                self.Streams = video.streams.filter(only_audio=True).order_by('abr').desc()
            elif t == "Video + Audio":
                self.Streams = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("URL Error")
            msg.setInformativeText(f"Couldn't find the video for the given URL\n{e}")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            # msg.exec_()
            return
        pass

    def change_resolution(self, resolution):
        self.selected_resolution = resolution

    def get_download_path(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self)
        if folder:
            # Use video title if available, else default
            title = getattr(self, 'yt_info', {}).get('title', 'video')
            # Clean title for filesystem
            safe_title = "".join(c for c in title if c.isalnum() or c in " ._-").rstrip()
            filename = f"{safe_title}.mp4"
            full_path = QtCore.QDir(folder).filePath(filename)
            self.destination_path.setText(full_path)

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

        selected_stream = None
        for idx, stream in enumerate(self.Streams):
            label = f"{stream.get('height', 'audio')}p {stream.get('ext', '')}"
            if label == self.selected_resolution:
                selected_stream = stream
                break

        # Use the full path (including filename) from destination_path
        save_path = self.destination_path.text()
        if save_path and selected_stream:
            self.downloader.start_download(selected_stream, save_path)
            self.download.setEnabled(False)
            self.setStatusTip("Downloading...")

    @QtCore.pyqtSlot()
    def on_finished(self):
        self.download.setEnabled(True)
        complete = download_complete({
            "image" : self.image,
            "title" : self.title.text(),
            "category" : self.category.text(),
            "rating" : self.rating.text(),
            "views" : self.views.text(),
            "duration" : self.duration.text(),
            "path" : self.path})
        complete.show()
        self.showMinimized()
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