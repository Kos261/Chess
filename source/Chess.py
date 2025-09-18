import sys
import random
import pygame
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton,QFileDialog, QDialog, QMessageBox, QTextEdit,
    QStyleFactory, QComboBox, QGridLayout, QSlider)
from PyQt5.QtGui import QPainter, QPixmap, QColor, QIcon, QFont, QPalette
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QThreadPool
     # QSize, QByteArray, QBuffer, QIODevice

# from multiprocessing import Process, Queue
# from threading import Thread

from Themes_and_animations import *
# from ChessEngine import GameState, Move
from Chessboard import Chessboard, BOARD_HEIGHT, BOARD_WIDTH
# import SmartMoveFinder

MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT


class MainGame(QDialog):
    def __init__(self, playerOne, playerTwo, theme_func):
        super().__init__()
        # self.setup_UI()
        self.playerOne = playerOne
        self.playerTwo = playerTwo
        self.MainLayout = QHBoxLayout(self)
        self.setFixedSize(int(1.7*BOARD_WIDTH), BOARD_HEIGHT+40)
        self.chessboard_colors = None
        self.theme = theme_func(self)
        self.theme_func = theme_func
        self.createButtons()
        self.text_edit = QTextEdit()

    
        self.chessboard = Chessboard(self, self.playerOne, self.playerTwo)
        self.chessboard.setFixedSize(BOARD_WIDTH, BOARD_HEIGHT)
        self.MainLayout.addWidget(self.chessboard)
        self.chessboard.setFocus()
    
        #Text edit
        font = self.text_edit.currentFont()
        font.setPointSize(13)
        self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)  # Ustaw tryb tylko do odczytu
        self.text_edit.setFixedSize(200, BOARD_HEIGHT)
        self.MainLayout.addWidget(self.text_edit)
        self.center()

    def createButtons(self):
        self.buttonLayout = QVBoxLayout()  # Utwórz układ pionowy dla przycisków
        self.button_size = 150

        self.button = QPushButton("Main Menu", self)
        self.button.setFixedSize(self.button_size, self.button_size)
        self.button.setStyleSheet(self.theme)
        self.button.clicked.connect(self.confirmMainMenu)
        self.buttonLayout.addWidget(self.button)

        self.new_game_butt = QPushButton("Nowa gra", self)
        self.new_game_butt.setFixedSize(self.button_size, self.button_size)
        self.new_game_butt.setStyleSheet(self.theme)
        self.new_game_butt.clicked.connect(self.confirmNewGame)
        self.buttonLayout.addWidget(self.new_game_butt)


        self.MainLayout.addLayout(self.buttonLayout)  # Dodaj układ pionowy do głównego układu poziomego

    def confirmNewGame(self):
        reply = self.createStyledMessageBox('New game', 'Are you sure you want to start a new game?', 
                                            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.text_edit.clear()
            self.startNewGame()

    def startNewGame(self):
        self.MainLayout.removeWidget(self.chessboard)
        self.chessboard.deleteLater()
        self.chessboard = Chessboard(self, self.playerOne, self.playerTwo)
        self.MainLayout.insertWidget(1, self.chessboard)

    def confirmMainMenu(self):
        reply = self.createStyledMessageBox('Menu', 'Are you sure you want to exit?', 
                                            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.mainMenu()

    def mainMenu(self):
        self.main_menu_window = StartScreen(self.theme_func)
        self.main_menu_window.setGeometry(750, 250, 340, 300)
        self.main_menu_window.show()
        self.close()

    def createStyledMessageBox(self, title, text, buttons):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(title)
        msgBox.setText(text)
        msgBox.setStandardButtons(buttons)
        msgBox.setStyleSheet(self.theme)
        return msgBox.exec_()
        
    def append_text(self, text):
        self.text_edit.append(text)

    def center(self):
        # Ustaw okno na środku ekranu
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

class StartScreen(QWidget):
    def __init__(self, theme_func = darkMode):
        super().__init__()
        self.playerOne = None
        self.playerTwo = None
        self.setFixedSize(550, 750)
        
        self.Layout = QVBoxLayout(self)
        self.theme_func = theme_func
        self.theme = theme_func(self)
        
        self.createButtons()
        self.changeTheme(theme_func)
        
    def createButtons(self):
        self.ChessStartBoard =  StartScreenBoard()
        
        font = QFont("Arial", 25)
        font2 = QFont("Arial", 12)

        # self.theme_combo = QComboBox()
        # self.theme_combo.addItem("Light Mode")
        # self.theme_combo.addItem("Dark Mode")
        # self.theme_combo.addItem("Green Neon")
        # self.theme_combo.addItem("BridgerTone")
        # self.theme_combo.currentIndexChanged.connect(self.changeTheme)

        image_path = os.path.join(os.path.dirname(__file__), '..', 'Assets')
        self.settings = QPushButton()
        self.settings.setFixedSize(32, 32)
        self.settings.setIcon(QIcon(image_path + "/Gear.png"))
        self.settings.clicked.connect(self.clickedSettings)

        self.button0 = QPushButton("New gamemode soon...")
        self.button0.setFont(font2)
        self.button0.setStyleSheet(self.theme)
        # self.button0.clicked.connect(self.clickedOnline)

        self.button1 = QPushButton("Player1 vs Player2")
        self.button1.setFont(font2)
        self.button1.setStyleSheet(self.theme)
        self.button1.clicked.connect(self.clickedPVP)

        self.button2 = QPushButton("Player vs AI")
        self.button2.setFont(font2)
        self.button2.setStyleSheet(self.theme)
        self.button2.clicked.connect(self.clickedPVAi)
        
        self.button3 = QPushButton("AI1 vs AI2")
        self.button3.setFont(font2)
        self.button3.setStyleSheet(self.theme)
        self.button3.clicked.connect(self.clickedAiVAi)

        # self.Layout.addWidget(self.theme_combo)
        self.Layout.addWidget(self.settings)
        self.Layout.addWidget(self.ChessStartBoard)
        self.Layout.addWidget(self.button0)
        self.Layout.addWidget(self.button1)
        self.Layout.addWidget(self.button2)
        self.Layout.addWidget(self.button3)

    def changeTheme(self, index):
        if index == 0:
            self.theme_func = lightMode
            self.theme = lightMode(self)
        elif index == 1:
            self.theme_func = darkMode
            self.theme = darkMode(self)
        elif index == 2:
            self.theme_func = neonMode
            self.theme = neonMode(self)
        elif index == 3:
            self.theme_func = bridgerToneMode
            self.theme = bridgerToneMode(self)

        self.ChessStartBoard.chessboard_color = self.chessboard_color
        self.button0.setStyleSheet(self.theme)
        self.button1.setStyleSheet(self.theme)
        self.button2.setStyleSheet(self.theme)
        self.button3.setStyleSheet(self.theme)

    def clickedPVP(self):
        self.playerOne = True
        self.playerTwo = True
        self.startGame()

    def clickedPVAi(self):
        self.playerOne = True
        self.playerTwo = False
        self.startGame()

    def clickedAiVAi(self):
        self.playerOne = False
        self.playerTwo = False
        self.startGame()

    def clickedOnline(self):
        self.playerOne = False
        self.playerTwo = False
        self.startGame()

    def clickedSettings(self):
        self.Settings = SettingsScreen(self, self.theme_func)
        self.Settings.setGeometry(750, 250, 340, 300)
        self.Settings.show()

    def startGame(self):
        if (self.playerOne != None) and (self.playerTwo != None):
            self.close()
            Game = MainGame(self.playerOne, self.playerTwo, self.theme_func)
            Game.setGeometry(750, 250, BOARD_WIDTH+500, BOARD_HEIGHT+100)
            Game.exec_()
        else:
            self.ChessStartBoard.setText("Wybierz tryb gry")

class OnlineScreen(QWidget):
    def __init__(self):
        super().__init__()
        darkMode(self)

class SettingsScreen(QWidget):
    def __init__(self, Startscreen, theme_func) -> None:
        super().__init__()
        self.Layout = QGridLayout(self)
        
        font2 = QFont("Arial", 12)
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light Mode")
        self.theme_combo.addItem("Dark Mode")
        self.theme_combo.addItem("Green Neon")
        self.theme_combo.addItem("BridgerTone")
        self.theme_combo.currentIndexChanged.connect(Startscreen.changeTheme)
        
        self.difficulty = 1
        self.label2 = QLabel(f"Difficulty level: {self.difficulty}")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickInterval(5)
        self.slider.setMinimum(1)
        self.slider.setMaximum(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setStyleSheet(slider_stylesheet)
        self.slider.valueChanged.connect(self.value_changed)

        self.Layout.addWidget(self.theme_combo, 0, 0)
        self.Layout.addWidget(self.label2,1,0)
        self.Layout.addWidget(self.slider, 2,0)
        
    def value_changed(self):
        self.difficulty = self.slider.value()
        self.label2.setText(f"Difficulty level: {self.difficulty}")





if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = StartScreen()
    window.setGeometry(750, 250, 340, 300)
    window.show()
    sys.exit(app.exec_())
