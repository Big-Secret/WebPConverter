import traceback
import threading
import webbrowser
from time import sleep
from threading import Thread
import urllib.request
from selenium import webdriver
import pyautogui
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import praw
import sys
import os
import random
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
import vlc
os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'


class RedditApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(RedditApp, self).__init__(*args, **kwargs)
        self.version = 0.03
        self.currentURL = ""
        self.currentTitle = ""
        self.randomRisingList = []
        self.randomBestList = []
        self.randomHotList = []
        self.randomTopList = []
        self.currentSub = ""
        self.currentSubUser = ""
        self.logs = []
        self.videoPosition = 1
        self.previousPosition = 0
        self.playing = False
        self.lastFunction = "random post"
        self.playerStarted = False
        self.count = 0

        width = 1000
        height = 800

        ################      UI
        self.setWindowTitle(f"Dutty v{self.version}")

        # REDDIT LAYOUTS
        self.mainRedditLayout = QVBoxLayout()
        self.titleRedditLayout = QHBoxLayout()
        self.lowerControlsLayout = QHBoxLayout()
        self.contentRedditLayout = QVBoxLayout()
        self.footerRedditLayout = QHBoxLayout()

        self.contentDetails = QVBoxLayout()
        self.contentDetailsLabel = QLabel()
        self.contentDetailsLabel.setText("Details")
        self.contentDetailsLabel.setFixedHeight(30)
        self.contentDetailsLabel.setAlignment(Qt.AlignCenter)
        self.contentDetailsLabel.setWordWrap(True)
        self.contentDetailsLabel.setStyleSheet("font-size: 15px")
        self.contentDetails.addWidget(self.contentDetailsLabel)

        self.commandCenter = QVBoxLayout()
        self.mainButtons = QHBoxLayout()
        self.lowerButtons = QHBoxLayout()
        self.commandCenter.addLayout(self.mainButtons)
        self.commandCenter.addLayout(self.lowerButtons)
        self.commandCenter.addLayout(self.lowerControlsLayout)
        self.contentDetails.addLayout(self.commandCenter)

        self.randomImageButton = QPushButton()
        self.randomImageButton.setText("IMG")
        self.randomImageButton.clicked.connect(self.getRandomPost)
        self.randomImageButton.setFixedSize(QSize(100, 50))

        self.bestImageButton = QPushButton()
        self.bestImageButton.setText("BEST IMG")
        self.bestImageButton.clicked.connect(self.getBestPost)
        self.bestImageButton.setFixedSize(QSize(100, 50))

        self.randomHotButton = QPushButton()
        self.randomHotButton.setText("HOT IMG")
        self.randomHotButton.clicked.connect(self.getRandomHot)
        self.randomHotButton.setFixedSize(QSize(100, 50))

        self.randomTopButton = QPushButton()
        self.randomTopButton.setText("Top Today")
        self.randomTopButton.clicked.connect(self.getRandomTop)
        self.randomTopButton.setFixedSize(QSize(100, 50))

        self.randomRisingImageButton = QPushButton()
        self.randomRisingImageButton.setText("Rising IMG")
        self.randomRisingImageButton.clicked.connect(self.getRandomRisingPost)
        self.randomRisingImageButton.setFixedSize(QSize(100, 50))

        self.openURLButton = QPushButton()
        self.openURLButton.setText("Open URL")
        self.openURLButton.clicked.connect(self.openURL)
        self.openURLButton.setFixedSize(QSize(100, 50))

        self.sameSubButton = QPushButton()
        self.sameSubButton.setText("Same Sub")
        self.sameSubButton.clicked.connect(self.sameSubPost)
        self.sameSubButton.setFixedSize(QSize(100, 50))

        self.saveImageButton = QPushButton()
        self.saveImageButton.setText("Save IMG")
        self.saveImageButton.clicked.connect(self.saveImage)
        self.saveImageButton.setFixedSize(QSize(100, 50))

        # self.saveHButton = QPushButton()
        # self.saveHButton.setText("Save H")
        # self.saveHButton.clicked.connect(self.saveImageH)
        # self.saveHButton.setFixedSize(QSize(100, 50))

        self.sameButton = QPushButton()
        self.sameButton.setText("Again")
        self.sameButton.clicked.connect(self.sameAction)
        self.sameButton.setFixedSize(QSize(100, 50))

        self.nextButton = QPushButton()
        self.nextButton.setText("Next")
        self.nextButton.clicked.connect(self.nextAction)
        self.nextButton.setFixedSize(QSize(100, 50))

        # self.playRedditButton = QPushButton()
        # self.playRedditButton.setText("Start")
        # self.playRedditButton.setFixedSize(QSize(50, 50))
        # self.playRedditButton.clicked.connect(self.startRedditSlideshow)

        self.pickSubredditWidget = QComboBox()
        self.pickSubredditWidget.setFixedSize(QSize(400, 25))
        self.patternMode = QPushButton()
        self.patternMode.setText("Pattern")
        self.patternMode.setFixedSize(QSize(100, 25))
        self.patternMode.clicked.connect(self.patternAction)
        self.openUser = QPushButton()
        self.openUser.setText("Open User")
        # self.openUser.clicked.connect()

        self.mainButtons.addStretch()
        self.mainButtons.addWidget(self.randomImageButton)
        self.mainButtons.addWidget(self.bestImageButton)
        self.mainButtons.addWidget(self.randomHotButton)
        self.mainButtons.addWidget(self.randomTopButton)
        self.mainButtons.addWidget(self.randomRisingImageButton)
        self.mainButtons.addStretch()
        self.lowerButtons.addStretch()
        self.lowerButtons.addWidget(self.openURLButton)
        self.lowerButtons.addWidget(self.sameButton)
        self.lowerButtons.addWidget(self.sameSubButton)
        self.lowerButtons.addWidget(self.nextButton)
        self.lowerButtons.addWidget(self.saveImageButton)
        self.lowerButtons.addStretch()
        # self.lowerControlsLayout.addWidget(self.saveHButton)
        self.lowerControlsLayout.addStretch()
        # self.lowerControlsLayout.addWidget(self.playRedditButton)
        self.lowerControlsLayout.addWidget(self.pickSubredditWidget)
        self.lowerControlsLayout.addWidget(self.patternMode)
        self.lowerControlsLayout.addWidget(self.openUser)
        self.lowerControlsLayout.addStretch()
        self.setMinimumWidth(width)
        # self.setMaximumWidth(width)
        self.setMinimumHeight(height)
        self.setGeometry(2365, 25, 1002, 1440)
        # self.setMaximumHeight(height)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))
        self.contentRedditLayout.addWidget(self.browser)
        self.contentRedditLayout.addLayout(self.contentDetails)

        # ADD LAYOUTS
        self.mainRedditLayout.addLayout(self.titleRedditLayout)
        self.mainRedditLayout.addLayout(self.contentRedditLayout)
        self.mainRedditLayout.addLayout(self.footerRedditLayout)

        # DESKTOP LAYOUTS

        self.desktopLayout = QVBoxLayout()
        self.desktopLayout_content = QVBoxLayout()
        self.desktopLayout_controls = QHBoxLayout()
        self.desktopLayout_controls_2 = QHBoxLayout()

        # MEDIA PLAYER
        # header
        self.mediaPlayerLabel = QLabel()
        self.mediaPlayerLabel.setText("Media Player")

        self.vlc_instance = vlc.Instance()
        self.mediaPlayer = self.vlc_instance.media_player_new()

        self.mediaFrame = QFrame()
        self.mediaFrame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        # self.mediaFrame.setFixedSize(QSize(1280, 720))
        self.palette = self.mediaFrame.palette()
        self.palette.setColor(QPalette.Window, QColor(130, 130, 130))
        self.mediaFrame.setPalette(self.palette)
        self.mediaFrame.setAutoFillBackground(True)

        self.progressBar = QLabel()
        self.progressBar.setText("/")
        self.progressBar.setAlignment(Qt.AlignCenter)

        # self.video = QVideoWidget()
        # self.video.resize(300, 300)
        # self.video.move(0, 0)
        # self.player = QMediaPlayer()
        # self.player.setVideoOutput(self.video)
        # self.player.setMedia(QMediaContent(QUrl.fromLocalFile("D:\\Projects\\Moto Rides\\050921.mp4")))

        # self.video = QVideoWidget()
        # self.video.resize(300, 300)
        # self.video.move(0, 0)
        # self.player = QMediaPlayer()
        # self.player.setVideoOutput(self.video)
        # self.player.setMedia(QMediaContent(QUrl.fromLocalFile("D:\\Projects\\Moto Rides\\050921.mp4")))

        self.playButton = QPushButton()
        self.playButton.setText("Play Random WebM")
        self.playButton.clicked.connect(self.playRandomVid)

        self.cpuImageButton = QPushButton()
        self.cpuImageButton.setText("Random Photo")
        self.cpuImageButton.clicked.connect(self.showRandomPictureFromCPU)

        self.stopVidButton = QPushButton()
        self.stopVidButton.setText("Stop")
        self.stopVidButton.clicked.connect(self.stopVidAction)

        self.volumeControlSlider = QSlider(Qt.Horizontal)
        self.volumeControlSlider.setValue(90)
        self.volumeControlSlider.valueChanged[int].connect(self.setVideoVolume)

        self.desktopLayout_content.addWidget(self.mediaPlayerLabel)
        self.desktopLayout_content.addWidget(self.mediaFrame)
        self.desktopLayout_content.addWidget(self.progressBar)
        # self.desktopLayout_content.addWidget(self.video)

        self.backward_10_Seconds = QPushButton()
        self.backward_10_Seconds.setText("<-10")
        self.backward_10_Seconds.clicked.connect(lambda: self.forwardSeek(-10))

        self.forward_5_Seconds = QPushButton()
        self.forward_5_Seconds.setText("2->")
        self.forward_5_Seconds.clicked.connect(lambda: self.forwardSeek(2))

        self.forward_15_Seconds = QPushButton()
        self.forward_15_Seconds.setText("15->")
        self.forward_15_Seconds.clicked.connect(lambda: self.forwardSeek(15))

        self.forward_30_Seconds = QPushButton()
        self.forward_30_Seconds.setText("30->")
        self.forward_30_Seconds.clicked.connect(lambda: self.forwardSeek(30))

        # self.desktopLayout_controls.addStretch()
        self.desktopLayout_controls.addWidget(self.playButton)
        self.desktopLayout_controls.addWidget(self.cpuImageButton)
        self.desktopLayout_controls.addWidget(self.stopVidButton)
        self.desktopLayout_controls.addWidget(self.volumeControlSlider)
        self.desktopLayout_controls.addStretch()

        self.desktopLayout_controls_2.addWidget(self.backward_10_Seconds)
        self.desktopLayout_controls_2.addWidget(self.forward_5_Seconds)
        self.desktopLayout_controls_2.addWidget(self.forward_15_Seconds)
        self.desktopLayout_controls_2.addWidget(self.forward_30_Seconds)
        self.desktopLayout_controls_2.addStretch()

        self.desktopLayout.addLayout(self.desktopLayout_content)
        self.desktopLayout.addLayout(self.desktopLayout_controls)
        self.desktopLayout.addLayout(self.desktopLayout_controls_2)

        ## Tab system
        # Create Tabs

        self.tabbedLayout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.redditTab = QWidget()
        self.pcTab = QWidget()
        # self.tabs.resize(300,200)

        self.tabs.addTab(self.redditTab, "Reddit")
        self.tabs.addTab(self.pcTab, "Desktop")

        self.redditTab.setLayout(self.mainRedditLayout)
        self.pcTab.setLayout(self.desktopLayout)
        self.tabbedLayout.addWidget(self.tabs)

        # FINALIZE
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.tabbedLayout)
        self.setCentralWidget(self.mainWidget)

        self.show()

        self.connectToReddit()
        self.createMultiReddit()

        class ConvertImages():
            def __init__(self, inputPath):
                self.outputFolder = "D:\Projects\Crypto Priks\CreateWebP\webp"
                self.inputFolder = inputPath

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
    window = RedditApp()
    window.show()
    # monitorQueue()
    app.exec_()
    traceback.print_exc()