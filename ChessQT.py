import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,QFileDialog, QDialog, QMessageBox, QTextEdit,QStyleFactory
from PyQt5.QtGui import QPainter, QPixmap, QColor, QIcon, QFont, QPalette
from PyQt5.QtCore import Qt, QTimer
from multiprocessing import Process, Queue
import threading

from ChessEngine_Advanced import GameState, Move
import SmartMoveFinder
import random
import pygame

BOARD_WIDTH = BOARD_HEIGHT = 600
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 20
IMAGES = {}


class MainGame(QDialog):
    def __init__(self, playerOne, playerTwo):
        super().__init__()
        self.playerOne = playerOne
        self.playerTwo = playerTwo
        self.layout = QHBoxLayout(self)
        self.setFixedSize(int(1.7*BOARD_WIDTH), BOARD_HEIGHT+40)
        self.center()
        self.darkMode()
        self.createButtons()

        # Dodaj niestandardowy widget do układu
        self.chessboard = ChessGraphicsQT(self, self.playerOne, self.playerTwo)
        self.chessboard.setFixedSize(BOARD_WIDTH, BOARD_HEIGHT)
        self.layout.addWidget(self.chessboard)
        self.chessboard.setFocus()
    
        #Text edit
        self.text_edit = QTextEdit()
        font = self.text_edit.currentFont()
        font.setPointSize(13)
        self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)  # Ustaw tryb tylko do odczytu
        self.text_edit.setFixedSize(200,BOARD_HEIGHT)
        self.layout.addWidget(self.text_edit)

        self.setLayout(self.layout)
        self.center()

    def darkMode(self):
        # Tworzenie ciemnego motywu
        
        self.dark_palette = QPalette()
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        self.dark_palette.setColor(QPalette.Text, Qt.white)
        self.dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Ustawianie ciemnego motywu
        self.setPalette(self.dark_palette)

        # Ustawianie ciemnego stylu
        QApplication.setStyle(QStyleFactory.create('Fusion'))

    def createButtons(self):
        self.button_size = 150
        self.button = QPushButton("TEST", self)
        self.button.setFixedSize(self.button_size, self.button_size)
        #self.button.clicked.connect()
        self.layout.addWidget(self.button)

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
        self.loadImages()
        self.GUI = GUI
        self.gs = GameState()
        self.validMoves = self.gs.getValidMoves()
        random.shuffle(self.validMoves)

        self.playerOne = playerOne
        self.playerTwo = playerTwo   

        self.animate = False
        self.sqSelected = ()
        self.playerClicks = [] 
        self.gameOver = False
        self.AIThinking = False
        self.moveFinderProcess = None
        self.moveUndone = False
        self.moveMade = False  
        self.humanTurn = (self.gs.WhiteToMove and self.playerOne) or (not self.gs.WhiteToMove and self.playerTwo)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGameState)
        self.timer.start(int(1000 / MAX_FPS))

    def AIMoveLogic(self):
        if not self.gameOver and not self.humanTurn and not self.moveUndone:
            if not self.AIThinking:
                self.AIThinking = True
                print("Thinking...")
                returnQueue = Queue()   #Used to pass data between threads  
                self.moveFinderProcess = Process(target=SmartMoveFinder.negaMaxAlphaBetaCaller_, 
                                            args = (self.gs, self.validMoves, returnQueue))
                self.moveFinderProcess.start() #Call findBestMove(gs,validMoves,returnQueue)

        elif not self.moveFinderProcess.is_alive():
                print("Done thinking")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(self.validMoves)
                self.gs.makeMove(AIMove,AIPlaying=True)
                self.moveMade = True
                self.animate = True  
                self.AIThinking = False

    def loadImages(self):
        pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
        for piece in pieces:
            # Figury od razu w skali planszy
            pixmap = QPixmap("Figury_HD/" + piece + ".png")
            pixmap = pixmap.scaled(SQ_SIZE, SQ_SIZE)
            label = QLabel()
            label.setPixmap(pixmap)
            IMAGES[piece] = label

    def drawBoard(self):
        global colors
        colors = [QColor(180,180,150), QColor(40,40,50)]

        for row in range(DIMENSION):
            for col in range(DIMENSION):
                color = colors[((row + col) % 2)]
                
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
            self.animate = False
            self.moveUndone = False
            self.sqSelected = ()         
            self.playerClicks = []  
            self.validMoves = self.gs.getValidMoves()  
        
        if not self.gameOver and not self.humanTurn and not self.moveUndone:
            self.AIMoveLogic()

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
            if self.animate:
                self.animateMove()
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
        if event.key() == Qt.Key_Z:
            self.gs.undoMove()   #Undo move
            self.sqSelected = ()
            self.playerClicks = []
            self.gameOver = False
            self.moveMade = True
            self.animate = False
            # if AIThinking:
            #     moveFinderProcess.terminate()
            # AIThinking = False
            self.moveUndone = True
            self.validMoves = self.gs.getValidMoves()

        if event.key() == Qt.Key_R:  #Reset game
            self.gs = GameState()
            self.validMoves = self.gs.getValidMoves()
            self.sqSelected = ()
            self.playerClicks = []
            self.gameOver = False
            self.moveMade = True
            self.animate = False
            # if AIThinking:
            #     moveFinderProcess.terminate()
            #     AIThinking = False
            self.moveUndone = True
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: 
            if not self.gameOver:
                col = event.pos().x() // SQ_SIZE
                row = event.pos().y() // SQ_SIZE

                if self.sqSelected == (row, col) or col >= 8:
                    # Gracz wybrał to samo pole 2 razy
                    self.sqSelected = ()  # deselect
                    self.playerClicks = []
                else:
                    self.sqSelected = (row, col)
                    self.playerClicks.append(self.sqSelected)
                                        
                                        #TU ZMIENIŁEM ==
                if len(self.playerClicks) == 2 and self.humanTurn:
                    self.move = Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
    
                    if self.move in self.validMoves:
                        self.gs.makeMove(self.move)
                        self.humanTurn = (self.gs.WhiteToMove and self.playerOne) or (not self.gs.WhiteToMove and self.playerTwo)
                        
                        self.GUI.append_text(str(self.gs.moveLog[-1]))
                        self.moveMade = True
                        self.animate = True
                        self.sqSelected = ()
                        self.playerClicks = []
                        self.validMoves = self.gs.getValidMoves()
                    else:
                        self.sqSelected = ()
                        self.playerClicks = []


        elif event.button() == Qt.RightButton:
            pass




class StartScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.playerOne = None
        self.playerTwo = None
        self.layout = QVBoxLayout(self)
        self.darkMode()
        self.createButtons()

    def createButtons(self):
        self.label = QLabel("Super Chess")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 25)
        font2 = QFont("Arial", 12)
        self.label.setFont(font)

        self.button1 = QPushButton("Player1 vs Player2")
        self.button1.setFont(font2)
        self.button1.clicked.connect(self.clickedPVP)

        self.button2 = QPushButton("Player vs AI")
        self.button2.setFont(font2)
        self.button2.clicked.connect(self.clickedPVAi)
        
        self.button3 = QPushButton("AI1 vs AI2")
        self.button3.setFont(font2)
        self.button3.clicked.connect(self.clickedAiVAi)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.button3)

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

    def startGame(self):
        if (self.playerOne != None) and (self.playerTwo != None):
            self.close()
            Game = MainGame(self.playerOne, self.playerOne)
            Game.setGeometry(750, 250, BOARD_WIDTH+500, BOARD_HEIGHT+100)
            Game.exec_()
        else:
            self.label.setText("Wybierz tryb gry")

    def darkMode(self):
        # Tworzenie ciemnego motywu
        self.dark_palette = QPalette()
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        self.dark_palette.setColor(QPalette.Text, Qt.white)
        self.dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Ustawianie ciemnego motywu
        self.setPalette(self.dark_palette)

        # Ustawianie ciemnego stylu
        QApplication.setStyle(QStyleFactory.create('Fusion'))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # window = MainGame(True, True)
    # window.setGeometry(750, 250, BOARD_WIDTH+500, BOARD_HEIGHT+100)
    # window.show()

    window = StartScreen()
    window.setGeometry(750, 250, 340, 300)
    window.show()

    sys.exit(app.exec_())
