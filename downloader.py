from PyQt5 import QtCore
import os
import requests

class DownLoader(QtCore.QObject):
    ratioSignal = QtCore.pyqtSignal(int)
    recvdSignal = QtCore.pyqtSignal(str)
    rateSignal = QtCore.pyqtSignal(str)
    etaSignal = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(object, str)
    def start_download(self, stream, filepath):
        from ui_mainwindow import window  # Import here to avoid circular import
        window.progress_label.show()
        window.progressBar.show()
        window.download_size_label.show()
        window.download_size.show()
        window.download_eta_label.show()
        window.download_eta.show()
        window.rate_label.show()
        window.rate.show()
        url = stream['url']
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(chunk_size=1024*1024):
                f.write(data)
                downloaded += len(data)
                ratio = downloaded / total if total else 0
                self.ratioSignal.emit(int(ratio * 100))
        self.finished.emit()