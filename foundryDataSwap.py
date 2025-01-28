from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon
from platform import system
import os
import shutil
import sys
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        app_icon = QIcon("d20.ico")
        self.setWindowIcon(app_icon)
        self.setWindowTitle("Foundry Data Swapper")
        self.setFixedSize(QSize(650, 375))

        self.destinationFileStruct = QLabel(
'''Destination Folder Structure:
''')
        self.destinationFileStruct.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.sourceFileStruct = QLabel(
'''Source Folder Structure:
''')
        self.sourceFileStruct.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.sourceLabel = QLabel("Select the 'source' data directory:")
        self.sourceLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        font = self.sourceLabel.font()
        font.setPointSize(10)
        font.setBold(True)
        self.sourceLabel.setFont(font)

        self.destinationLabel = QLabel("Select the 'destination' data directory:")
        self.destinationLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        font = self.destinationLabel.font()
        font.setPointSize(10)
        font.setBold(True)
        self.destinationLabel.setFont(font)

        sourceButton = QPushButton("Browse Folder")
        sourceButton.clicked.connect(self.browseSourceFolder)

        destinationButton = QPushButton("Browse Folder")
        destinationButton.clicked.connect(self.browseDestinationFolder)

        self.submitButton = QPushButton("Copy Data")
        self.submitButton.clicked.connect(self.submitButtonClicked)
        self.submitButton.setFixedWidth(100)
        self.submitButton.setEnabled(False)


        mainLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        bottomLayout = QHBoxLayout()
        submissionLayout = QHBoxLayout()
        sourceContainerLayout = QVBoxLayout()
        destinationContainerLayout = QVBoxLayout()

        horizontalLayout.addWidget(self.sourceFileStruct)
        horizontalLayout.addWidget(self.destinationFileStruct)

        sourceContainerLayout.addWidget(self.sourceLabel)
        sourceContainerLayout.addWidget(sourceButton)
        destinationContainerLayout.addWidget(self.destinationLabel)
        destinationContainerLayout.addWidget(destinationButton)
        bottomLayout.addLayout(sourceContainerLayout)
        bottomLayout.addLayout(destinationContainerLayout)

        submissionLayout.addWidget(self.submitButton)
        submissionLayout.setContentsMargins(0, 20, 0, 0)

        mainLayout.addLayout(horizontalLayout)
        mainLayout.addLayout(bottomLayout)
        mainLayout.addLayout(submissionLayout)

        container = QWidget()
        container.setLayout(mainLayout)
        container.layout
        self.setCentralWidget(container)

        self.sourceDirectory: str = ''
        self.destinationDirectory: str = ''
        with open('meta.json', 'a+') as f:
            if os.path.getsize('./meta.json') == 0:
                json.dump({"sourceDirectory": '', "destinationDirectory": ''}, f, indent=4)
                return
            f.seek(0)
            data = json.load(f)
            self.sourceDirectory = data['sourceDirectory']
            self.destinationDirectory = data['destinationDirectory']
            self.formatFolderStructLabel('Source', self.sourceDirectory.split('/')[1:])
            self.formatFolderStructLabel('Destination', self.destinationDirectory.split('/')[1:])

    def submitButtonClicked(self):
        directory = os.path.dirname(self.destinationDirectory)
        sep = '\\'
        if system() == 'Linux':
            sep = '/'
        backupPath = directory + sep + 'backupFoundryData'
        os.makedirs(directory + sep + 'backupFoundryData', exist_ok=True)

        shutil.copytree(self.destinationDirectory, backupPath, dirs_exist_ok=True)
        shutil.rmtree(self.destinationDirectory)
        shutil.copytree(self.sourceDirectory, self.destinationDirectory, dirs_exist_ok=True)

        self.submitButton.setText("Submitted!")
        self.submitButton.setEnabled(False)

    def formatFolderStructLabel(self, folderType: str, directory):
        if directory[-1] != 'data':
            self.selectValidDirectoryLabelText(f'{folderType.lower()}Folder', error='notDataFolder')
            return
        
        with open('meta.json', 'r+') as f:
            data = json.load(f)
            data[f'{folderType.lower()}Directory'] = f'C:/{'/'.join(directory)}'
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)

        result = f'{folderType} Folder Structure:\n'
        for n, folderName in enumerate(directory):
            tabs = n*'    '
            result = result + f'{tabs}-> {folderName}\n'
        result = result + '    '*(len(directory)) + '^'*(len(directory[-1]))
        self.sourceFileStruct.setText(result) if folderType=='Source' else self.destinationFileStruct.setText(result)
        if self.sourceDirectory != '' and self.destinationDirectory != '':
            self.submitButton.setEnabled(True)

    def browseSourceFolder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", self.sourceDirectory)
        if directory:
            self.sourceDirectory = directory
            directory = directory.split('/')[1:]
            self.formatFolderStructLabel("Source", directory)
        else:
            self.selectValidDirectoryLabelText('sourceFolder')

    def browseDestinationFolder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", self.destinationDirectory)
        if directory:
            self.destinationDirectory = directory
            directory = directory.split('/')[1:]
            self.formatFolderStructLabel("Destination", directory)
        else:
            self.selectValidDirectoryLabelText('destinationFolder')

    def selectValidDirectoryLabelText(self, folderType, **kwargs):
        label = self.sourceLabel if folderType=='sourceFolder' else self.destinationLabel
        text = 'Select a folder named "data"!' if kwargs and kwargs['error'] =='notDataFolder' else 'Select a valid directory!'
        label.setText(text)
        font = label.font()

        font.setUnderline(True)
        font.setPointSize(15)
        label.setFont(font)
        QTimer.singleShot(2000, self.normalizeLabelText)

    def normalizeLabelText(self):
        sourceLabel = self.sourceLabel
        destinationLabel = self.destinationLabel
        sourceLabel.setText("Search for data directory:")
        font = sourceLabel.font()
        font.setUnderline(False)
        font.setPointSize(10)
        sourceLabel.setFont(font)
        destinationLabel.setText("Search for data directory:")
        font = destinationLabel.font()
        font.setUnderline(False)
        font.setPointSize(10)
        destinationLabel.setFont(font)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())