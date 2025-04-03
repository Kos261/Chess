import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,QFileDialog, QDialog, QMessageBox, QTextEdit,QStyleFactory, QComboBox, QGridLayout, QSlider
from PyQt5.QtGui import QPainter, QPixmap, QColor, QIcon, QFont, QPalette
from PyQt5.QtCore import Qt, QTimer, QSize, QByteArray, QBuffer, QIODevice

from multiprocessing import Process, Queue
from threading import Thread

from Themes_and_animations import *
from ChessEngine import GameState, Move
import SmartMoveFinder
import random
import pygame
import os

BOARD_WIDTH = BOARD_HEIGHT = 600
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 20
IMAGES = {}
THEMES = {}

class MainGame(QDialog):
    def __init__(self, playerOne, playerTwo, theme_func):
        super().__init__()

        self.playerOne = playerOne
        self.playerTwo = playerTwo
        self.MainLayout = QHBoxLayout(self)
        self.setFixedSize(int(1.7*BOARD_WIDTH), BOARD_HEIGHT+40)
        self.chessboard_colors = None
        self.theme = theme_func(self)
        self.theme_func = theme_func
        self.createButtons()
        self.text_edit = QTextEdit()

        # Dodaj niestandardowy widget do układu
        self.chessboard = ChessGraphicsQT(self, self.playerOne, self.playerTwo)
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
        self.chessboard = ChessGraphicsQT(self, self.playerOne, self.playerTwo)
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

class ChessGraphicsQT(QWidget):
    def __init__(self, GUI, playerOne, playerTwo):
        super().__init__()
        self.chessboard_color = GUI.chessboard_color
        self.loadImages()
        self.GUI = GUI
        self.gs = GameState(self.GUI)
        self.validMoves = self.gs.getValidMoves()
        random.shuffle(self.validMoves)

        self.playerOne = playerOne
        self.playerTwo = playerTwo   

        self.sqSelected = () 
        self.playerClicks = [] 
        self.gameOver = False
        self.AIThinking = False
        self.moveFinderProcess = None
        self.moveMade = False  
        self.humanTurn = self.playerOne if self.gs.WhiteToMove else self.playerTwo

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGameState)
        self.timer.start(int(1000 / MAX_FPS))

    def AIMoveLogic(self):
        if not self.gameOver and not self.humanTurn:
            if not self.AIThinking:
                self.AIThinking = True
                self.GUI.append_text("Thinking...")
                self.returnQueue = Queue()   #Used to pass data between threads 
               
                self.moveFinderProcess = Thread(
                                target=SmartMoveFinder.negaMaxAlphaBetaCaller_, 
                                args = (self.gs, self.validMoves, self.returnQueue),
                                daemon=True)
                self.moveFinderProcess.start()

        if not self.moveFinderProcess.is_alive():
            print("Done thinking")
            AIMove = self.returnQueue.get()
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(self.validMoves)
            self.gs.makeMove(AIMove,AIPlaying=True)
            
            self.moveMade = True 
            self.AIThinking = False
            self.humanTurn =  self.playerOne if self.gs.WhiteToMove else self.playerTwo

    def loadImages(self):
        pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
        image_path = os.path.join(os.path.dirname(__file__), '..', 'Figury')
        for piece in pieces:
            pixmap = QPixmap(image_path + "/" + piece + ".png")
            pixmap = pixmap.scaled(SQ_SIZE, SQ_SIZE)
            if pixmap.isNull():
                raise Exception(f"Figure {piece} is not loaded properly")

            ChessStartBoard = QLabel()
            ChessStartBoard.setPixmap(pixmap)
            IMAGES[piece] = ChessStartBoard

    def drawBoard(self):
        
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                color = self.chessboard_color[((row + col) % 2)]
                
                if (row + col) % 2 == 0:
                    self.painter.fillRect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE, color)
                else:
                    self.painter.fillRect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE, color)

                piece = self.gs.board[row][col]
                if piece != "--": #Nie jest puste pole
                    pixmap = IMAGES[piece].pixmap()
                    self.painter.drawPixmap(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE, pixmap)

    def updateGameState(self):
        
        if self.moveMade:
            self.moveMade = False
            self.sqSelected = ()         
            self.playerClicks = []  
            self.validMoves = self.gs.getValidMoves()  
        
        if not self.gameOver and not self.humanTurn:
            self.AIMoveLogic()
        
        #TUTAJ BLOKADA GDY AI SYMULUJE RUCHY Ale średnio działa
        if not self.AIThinking:
            self.gs.scanBoard()
            self.update()

        if self.gs.checkMate or self.gs.staleMate:
            self.gameOver = True
            if self.gs.staleMate:
                self.Wintext = 'Stalemate'
            else:
                self.Wintext = 'White wins' if not self.gs.WhiteToMove else 'Black wins'
            self.GUI.append_text(self.Wintext)
            
            self.update()
            self.timer.stop()

    def paintEvent(self,event):
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        if not self.gameOver: 
            self.drawBoard()
            self.highlightSquares()

        else:
            self.drawBoard()
            self.drawEndText(self.Wintext)
        self.painter.end()

    def highlightSquares(self):
        if self.sqSelected != ():
            yellow = QColor(100,100,0,100)
            blue = QColor(0,0,220,50)
            row, col = self.sqSelected
            if self.gs.board[row][col][0] == ('w' if self.gs.WhiteToMove else 'b'):
                self.painter.fillRect(col*SQ_SIZE, row * SQ_SIZE, SQ_SIZE,SQ_SIZE,blue)

                for move in self.validMoves:
                    if move.startRow == row and move.startCol == col:
                        self.painter.fillRect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE,SQ_SIZE, yellow)

    def animateMove(self):
        #DO POPRAWY
        global colors
        dRow = self.move.endRow - self.move.startRow
        dCol = self.move.endCol - self.move.startCol
        endRow = self.move.endRow * SQ_SIZE
        endCol = self.move.endCol * SQ_SIZE

        framesPerSquare = 10
        frameCount = (abs(dRow) + abs(dCol)) * framesPerSquare
        pixPieceMoving = IMAGES[self.move.pieceMoved].pixmap()

        for frame in range(frameCount + 1):
            row, col = (self.move.startRow + dRow * frame / frameCount, self.move.startCol + dCol * frame / frameCount)

            # Clear previous frame
            

            # Erase the piece moved from its ending square
            color = colors[(self.move.endRow + self.move.endCol) % 2]
            self.painter.fillRect(self.move.endCol * SQ_SIZE, self.move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE, color)

            # Draw captured piece
            if self.move.pieceCaptured != '--' and not self.move.isEnPassantMove:
                pixPieceCaptured = IMAGES[self.move.pieceCaptured].pixmap()
                self.painter.drawPixmap(endCol, endRow, SQ_SIZE, SQ_SIZE, pixPieceCaptured)

            # Draw moving piece 
            self.painter.drawPixmap(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE, pixPieceMoving)
            self.update()
            # Update the widget
        self.painter.end()

    def drawEndText(self,text):
        font = QFont("Arial", 40)
        self.painter.setFont(font)
        self.painter.setPen(Qt.red)
        x = BOARD_WIDTH//2
        y = BOARD_HEIGHT//2

        bounding_rect = self.painter.boundingRect(x, y, 0, 0, Qt.TextDontPrint, text)
        text_width = bounding_rect.width()
        text_height = bounding_rect.height()

        self.painter.drawText(x-text_width//2, y-text_height//2 , text)

        self.painter.setPen(Qt.yellow)
        self.painter.drawText(x-text_width//2+3, y-text_height//2+3 , text)

        self.painter.setPen(Qt.blue)
        self.painter.drawText(x-text_width//2+6, y-text_height//2+6 , text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:  #Reset game
            self.gs = GameState(self)
            self.validMoves = self.gs.getValidMoves()
            self.sqSelected = ()
            self.playerClicks = []
            self.gameOver = False
            self.moveMade = True
            
            if self.AIThinking:
                self.moveFinderProcess.terminate()
                self.AIThinking = False
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: 
            if not self.gameOver:
                col = event.pos().x() // SQ_SIZE
                row = event.pos().y() // SQ_SIZE

                if self.sqSelected == (row, col) or col >= 8:
                    self.sqSelected = ()  
                    self.playerClicks = []
                else:
                    self.sqSelected = (row, col)
                    self.playerClicks.append(self.sqSelected)
                                        
                                        #TU ZMIENIŁEM == self.humanTurn
                if len(self.playerClicks) == 2:
                    self.move = Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
    
                    if self.move in self.validMoves:
                        self.gs.makeMove(self.move)
                        self.humanTurn =  self.playerOne if self.gs.WhiteToMove else self.playerTwo
                        # self.GUI.append_text(f"Teraz gra człowiek - {self.humanTurn}")
                        self.GUI.append_text(str(self.gs.moveLog[-1]))
                        self.moveMade = True
                    
                        self.sqSelected = ()
                        self.playerClicks = []
                        self.validMoves = self.gs.getValidMoves()
                    else:
                        self.sqSelected = ()
                        self.playerClicks = []


        elif event.button() == Qt.RightButton:
            pass

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
        # self.Settings.setGeometry(750, 250, 340, 300)
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

    '''
    pyinstaller --onefile --windowed --add-data "Figury;Figury" --onefile --add-data "Figury;Figury" --add-data "Images;Images" ChessQT.py
    '''

    sys.exit(app.exec_())
