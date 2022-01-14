import traceback
import threading
import os
import sys
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class convertToWebP(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(convertToWebP, self).__init__(*args, **kwargs)
        self.version = 1.0


        # UI
        self.setWindowTitle(f"WebP Converter by Big Secret | v{self.version}")
        self.setMinimumSize(500, 350)


        # LAYOUTS
        self.mainLayout = QVBoxLayout()
        self.topBarLayout = QHBoxLayout()
        self.settingsLayout = QVBoxLayout()
        self.statusBarLayout = QHBoxLayout()



        # FINALIZE
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.show()


        try:
            os.mkdir(self.outputFolder)
        except:
            pass

    def convertWebP(self, imageName):
        imagePath = f"{self.inputFolder}\{imageName}"
        imageName = imageName.split(".")[0]
        print(f"Converting {imageName} from {imagePath}")
        image = Image.open(imagePath)
        image = image.convert("RGBA")
        imgInfo = image.info
        image.save(f"{self.outputFolder}\{imageName}.webp", format='webp', lossless=False, quality=80, method=6,
                   **imgInfo)
        print(f"{imageName} saved as {imageName}.webp @ {self.outputFolder}\{imageName}.webp")

    def readDirectory(self):
        self.dir = os.listdir(self.inputFolder)
        for item in self.dir:
            if "." in item:
                self.convertWebP(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = convertToWebP()
    window.show()
    # monitorQueue()
    app.exec_()
    traceback.print_exc()