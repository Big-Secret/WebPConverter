import traceback
import threading
import os
import sys
from PIL import Image, UnidentifiedImageError
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class convertToWebP(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(convertToWebP, self).__init__(*args, **kwargs)
        self.version = 1.3

        self.inputPath = ""
        self.usingFolder = False
        self.fileCount = 0
        self.imagesConvertedCount = 0
        self.losslessStatus = False
        self.exportQuality = 80
        self.exportMethod = 4
        self.saveToInputDirectory = False
        self.outputPath = ""
        self.filesToConvert = []
        self.fileCount = 0
        self.inputDirectory = ""
        self.outputFolderSet = False

        # UI
        self.setWindowTitle(f"WebP Converter by Big Secret | v{self.version}")
        self.setMinimumSize(500, 350)
        self.setFont(QFont("Arial", 10))

        # LAYOUTS
        self.mainLayout = QVBoxLayout()
        self.headerLayout = QHBoxLayout()
        self.topBarLayout = QHBoxLayout()
        self.settingsFrame = QFrame()
        self.settingsLayout = QVBoxLayout()
        self.settingsLayout.setAlignment(Qt.AlignHCenter)
        self.settingsFrame.setFrameShape(QFrame.StyledPanel)
        self.settingsFrame.setLineWidth(5)
        self.settingsFrame.setLayout(self.settingsLayout)
        self.statusBarLayout = QHBoxLayout()

        # WIDGETS
        # TOP BAR
        self.locateFilesLabel = QLabel()
        self.locateFilesLabel.setText("Locate File(s):")
        self.buyMeCoffee = QLabel()
        self.buyMeCoffee.setText("<a href='https://www.paypal.com/donate/?hosted_button_id=KMU4WDWUUVK4C'>Buy me a coffee</a>")
        self.buyMeCoffee.setFont(QFont("Arial", 8))
        self.buyMeCoffee.setTextFormat(Qt.RichText)
        self.buyMeCoffee.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.buyMeCoffee.setOpenExternalLinks(True)

        self.headerLayout.addWidget(self.locateFilesLabel)
        self.headerLayout.addStretch()
        self.headerLayout.addWidget(self.buyMeCoffee)

        self.selectFileButton = QPushButton()
        self.selectFileButton.setText("Select File(s)")
        self.selectFileButton.clicked.connect(self.selectFile)
        self.selectFolderButton = QPushButton()
        self.selectFolderButton.setText("Select Folder")
        self.selectFolderButton.clicked.connect(self.selectFolder)

        self.resetAllButton = QPushButton()
        self.resetAllButton.setText("Reset All")
        self.resetAllButton.clicked.connect(self.initializeSettings)

        # PLACE INTO LAYOUT
        self.topBarLayout.addWidget(self.selectFileButton)
        self.topBarLayout.addWidget(self.selectFolderButton)
        self.topBarLayout.addStretch()
        self.topBarLayout.addWidget(self.resetAllButton)

        # SETTINGS BAR
        self.settingsLabel = QLabel()
        self.settingsLabel.setText("Convert to WebP Settings")
        self.settingsLabel.setFont(QFont("Arial", 13))

        self.losslessCheckbox = QCheckBox()
        self.losslessCheckbox.setText("Lossless Format")
        self.losslessCheckbox.stateChanged.connect(self.updateLosslessCheckbox)


        # QUALITY
        self.qualityDefault = 80
        self.qualityNameLabel = QLabel()
        self.qualityNameLabel.setText("Quality: ")
        self.qualityNumberLabel = QLineEdit()
        self.qualityNumberLabel.setFixedWidth(25)
        self.qualityNumberLabel.setText(f"{self.qualityDefault}")
        self.qualityNumberLabel.textChanged.connect(self.updateQualityEntry)
        self.qualitySlider = QSlider()
        self.qualitySlider.setValue(self.qualityDefault)
        self.qualitySlider.setOrientation(Qt.Horizontal)
        self.qualitySlider.setMaximum(100)
        self.qualitySlider.setMinimum(1)
        self.qualitySlider.setSizeIncrement(1, 0)
        self.qualitySlider.valueChanged.connect(self.updateQualitySlider)
        self.qualityDescriptionLabel = QLabel()
        self.qualityDescriptionLabel.setText(
            "1-100, Defaults to 80.\nFor lossy, 0 gives the smallest size and 100 the largest. For lossless, this parameter is the amount of effort put into the compression: 0 is the fastest, but gives larger files compared to the slowest, but best, 100.")
        self.qualityDescriptionLabel.setFont(QFont("Arial", 8))
        self.qualityDescriptionLabel.setWordWrap(True)

        # Create H Layout for these Quality Widgets
        self.qualityLayout = QHBoxLayout()
        self.qualityLayout.addWidget(self.qualityNameLabel)
        self.qualityLayout.addWidget(self.qualityNumberLabel)
        self.qualityLayout.addWidget(self.qualitySlider)

        # METHOD
        self.methodDefault = 4
        self.methodLabel = QLabel()
        self.methodLabel.setText("Method: ")
        self.methodNumberLabel = QLineEdit()
        self.methodNumberLabel.setText(str(self.methodDefault))
        self.methodNumberLabel.setFixedWidth(25)
        self.methodNumberLabel.textChanged.connect(self.updateMethodEntry)
        self.methodSlider = QSlider()
        self.methodSlider.setOrientation(Qt.Horizontal)
        self.methodSlider.setMinimum(0)
        self.methodSlider.setMaximum(6)
        self.methodSlider.setValue(self.methodDefault)
        self.methodSlider.valueChanged.connect(self.updateMethodSlider)
        self.methodDescriptionLabel = QLabel()
        self.methodDescriptionLabel.setText("Quality vs Speed Tradeoff. Defaults to 4.\n0 = Fast, 6 = Slower, Better.")
        self.methodDescriptionLabel.setFont(QFont("Arial", 8))
        self.methodDescriptionLabel.setWordWrap(True)
        self.saveCurrentSettingsCheckbox = QCheckBox()
        self.saveCurrentSettingsCheckbox.setText("Save Settings")
        self.saveCurrentSettingsCheckbox.setDisabled(True)

        # CREATE H LAYOUT FOR METHOD WIDGETS
        self.methodLayout = QHBoxLayout()
        self.methodLayout.addWidget(self.methodLabel)
        self.methodLayout.addWidget(self.methodNumberLabel)
        self.methodLayout.addWidget(self.methodSlider)

        # OUTPUT
        self.sameAsInputCheckbox = QCheckBox()
        self.sameAsInputCheckbox.setText("Save to Input Directory")
        self.sameAsInputCheckbox.setCheckState(True)
        self.sameAsInputCheckbox.setDisabled(True)
        self.sameAsInputCheckbox.stateChanged.connect(self.updateOutputCheckbox)
        self.setOutFolderButton = QPushButton()
        self.setOutFolderButton.setText("Select Output Folder")
        self.setOutFolderButton.setFixedWidth(140)
        self.setOutFolderButton.setDisabled(True)
        self.setOutFolderButton.clicked.connect(self.selectOutputFolder)

        # PLACE INTO LAYOUT
        self.settingsLayout.addWidget(self.settingsLabel)
        self.settingsLayout.addWidget(self.losslessCheckbox)
        self.settingsLayout.addLayout(self.qualityLayout)
        self.settingsLayout.addWidget(self.qualityDescriptionLabel)
        self.settingsLayout.addLayout(self.methodLayout)
        self.settingsLayout.addWidget(self.methodDescriptionLabel)
        self.settingsLayout.addWidget(self.saveCurrentSettingsCheckbox)
        self.settingsLayout.addStretch()

        # STATUS BAR
        self.statusBarText = QLabel()
        self.statusBarText.setText("State: Ready")
        self.statusBarText.setWordWrap(True)
        self.statusBarText.setFont(QFont('Arial',8))
        self.statusBarText.setFixedWidth(round(self.width()*.75))

        self.convertImagesButton = QPushButton()
        self.convertImagesButton.setText("Convert to WebP ▶")
        self.convertImagesButton.setDisabled(True)
        self.convertImagesButton.clicked.connect(self.createConvertThread)

        # PLACE INTO LAYOUT
        self.statusBarLayout.addWidget(self.statusBarText)
        self.statusBarLayout.addStretch()
        self.statusBarLayout.addWidget(self.convertImagesButton)

        # ORDER LAYOUTS
        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addLayout(self.topBarLayout)
        self.mainLayout.addWidget(self.settingsFrame)
        self.mainLayout.addWidget(self.sameAsInputCheckbox)
        self.mainLayout.addWidget(self.setOutFolderButton)
        self.mainLayout.addLayout(self.statusBarLayout)

        # FINALIZE UI
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.show()
        self.setFixedSize(self.width(), self.height())

        # INITIALIZE SETTINGS

    def initializeSettings(self):
        self.inputPath = ""
        self.usingFolder = False
        self.fileCount = 0
        self.imagesConvertedCount = 0
        self.losslessStatus = False
        self.exportQuality = 80
        self.exportMethod = 4
        self.saveToInputDirectory = False
        self.outputPath = ""
        self.filesToConvert = []
        self.fileCount = 0
        self.inputDirectory = ""
        self.outputFolderSet = False
        self.qualityNumberLabel.setText(str(self.qualityDefault))
        self.methodNumberLabel.setText(str(self.methodDefault))
        self.losslessCheckbox.setCheckState(0)
        self.saveCurrentSettingsCheckbox.setCheckState(0)
        self.sameAsInputCheckbox.setCheckState(0)
        self.convertImagesButton.setDisabled(True)
        self.setOutFolderButton.setDisabled(True)
        self.sameAsInputCheckbox.setDisabled(True)
        self.setStatusText("Everything Reset!")

    def setStatusText(self, text):
        self.statusBarText.setText(f"Status: {text}")
        print(f"Status: {text}")

        # VALUE SLIDER SETTINGS FOR QUALITY

    def updateQualitySlider(self, value):
        self.qualityNumberLabel.setText(str(value))
        self.exportQuality = int(value)

    def updateQualityEntry(self, value):
        if value == "":
            return
        elif len(value) > 0:
            if int(value) > 100:
                value = 100
            elif int(value) == 0:
                value = self.qualityDefault
            else:
                value = int(value)
            self.qualityNumberLabel.setText(str(value))
            self.qualitySlider.setValue(value)
            self.exportQuality = int(value)
        else:
            self.qualitySlider.setValue(self.qualityDefault)

        # VALUE SLIDER SETTINGS FOR METHOD

    def updateMethodEntry(self, value):
        if value == "":
            return
        elif int(value) > 6:
            self.methodNumberLabel.setText(str(6))
            value = 6
        else:
            value = int(value)
        self.methodSlider.setValue(value)
        self.exportMethod = int(value)

    def updateMethodSlider(self, value):
        self.methodNumberLabel.setText(str(value))
        self.exportMethod = int(value)

        # EXPORT CHECKBOX SETTINGS

    def updateLosslessCheckbox(self,value):
        if value == 2:
            self.losslessStatus = True
        elif value == 0:
            self.losslessStatus = False

    def updateOutputCheckbox(self, value):
        if value > 0:
            self.setOutFolderButton.setDisabled(True)
            self.saveToInputDirectory = True
        elif value == 0:
            self.setOutFolderButton.setDisabled(False)
            self.saveToInputDirectory = False

    def selectFile(self):
        self.inputPath, check = QFileDialog.getOpenFileNames(None, "Select an Image File", "C:\\", "All Files (*)")
        if len(self.inputPath) > 0:
            inputDirectory = self.inputPath[0].split("/")
            inputDirectory.pop(-1)
            for i in inputDirectory:
                if self.inputDirectory == "":
                    self.inputDirectory = i
                else:
                    self.inputDirectory = f"{self.inputDirectory}/{i}"
            if check:
                for x in self.inputPath:
                    self.fileCount += 1
                    self.filesToConvert.append(x)
                    self.setStatusText(f"Added {x}")
                self.setStatusText(f"{self.fileCount} files loaded from {self.inputDirectory}.")
                self.inputPath = self.inputDirectory
                self.outputPath = self.inputPath
                self.convertImagesButton.setDisabled(False)
                self.setOutFolderButton.setDisabled(False)
                self.sameAsInputCheckbox.setDisabled(False)

    def selectFolder(self):
        self.inputPath = QFileDialog.getExistingDirectory(None, "Select a Folder", "C:\\")
        self.outputPath = self.inputPath
        if self.inputPath:
            for file in os.listdir(self.inputPath):
                if "." in file:
                    self.filesToConvert.append(f"{self.inputPath}/{file}")
            self.fileCount = len(self.filesToConvert)
            self.setStatusText(f"{self.fileCount} files loaded from {self.inputPath}.")
            self.convertImagesButton.setDisabled(False)
            self.setOutFolderButton.setDisabled(False)
            self.sameAsInputCheckbox.setDisabled(False)

    def selectOutputFolder(self):
        self.outputPath = QFileDialog.getExistingDirectory(None, "Select a Folder", self.inputPath)
        if len(self.outputPath) > 0:
            if self.inputDirectory == self.outputPath:
                self.sameAsInputCheckbox.setCheckState(True)
                self.setStatusText(f"{self.outputPath} same as input directory.")
            else:
                self.setStatusText(f"{self.outputPath} set as output directory.")
                self.sameAsInputCheckbox.setCheckState(False)
            self.outputFolderSet = True

    def convertWebP(self):
        self.setDisabled(True)
        self.statusBarText.setDisabled(False)
        self.buyMeCoffee.setDisabled(False)
        for file in self.filesToConvert:
            self.convertThisImage(file)
        self.initializeSettings()
        self.setStatusText("Conversion Complete")
        self.setDisabled(False)


    def createConvertThread(self):
        print(f"STARTING CONVERSION PROCESS WITH THE FOLLOWING SETTINGS:\n"
              f"Lossless: {self.losslessStatus}\n"
              f"Export Quality: {self.exportQuality}\n"
              f"Export Method: {self.exportMethod}\n")
        self.convertImagesButton.setDisabled(True)
        self.x = threading.Thread(target=self.convertWebP)
        self.x.start()

    def convertThisImage(self, imagePath):
        self.setStatusText(f"Converting {imagePath}")
        try:
            image = Image.open(imagePath)
            image = image.convert("RGBA")
            if self.saveToInputDirectory:
                outputDirectory = self.inputPath
            else:
                outputDirectory = self.outputPath
            filename = imagePath.split("/")[-1]
            filename = filename.split(".")[0] + ".webp"
            finalPath = f"{outputDirectory}/{filename}"
            imgInfo = image.info
            image.save(finalPath, format='webp', lossless=self.losslessStatus, quality=self.exportQuality,
                       method=self.exportMethod, **imgInfo)
            self.imagesConvertedCount += 1
            self.setStatusText(f"{self.imagesConvertedCount}/{self.fileCount} converted & saved as {finalPath}")
        except UnidentifiedImageError:
            self.setStatusText(f"!!!!! ERROR: {imagePath} not supported !!!!!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = convertToWebP()
    window.show()
    # monitorQueue()
    app.exec_()
    traceback.print_exc()
