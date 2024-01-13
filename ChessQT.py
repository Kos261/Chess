import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
from ChessEngine_Advanced import GameState, Move
import random
import pygame

BOARD_WIDTH = BOARD_HEIGHT = 600
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 1
IMAGES = {}


class ChessGraphicsQT(QWidget):
    def __init__(self):
        super().__init__()
        self.loadImages()
        self.gs = GameState()
        self.validMoves = self.gs.getValidMoves()
        random.shuffle(self.validMoves)
                  
        self.animate = False
        self.sqSelected = ()
        self.playerClicks = [] 
        self.gameOver = False
        self.playerOne = True
        self.playerTwo = True
        self.AIThinking = False
        self.moveFinderProcess = None
        self.moveUndone = False
        self.moveMade = False  
        self.humanTurn = (self.gs.WhiteToMove and self.playerOne) or (not self.gs.WhiteToMove and self.playerTwo)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGameState)
        self.timer.start(int(1000 / MAX_FPS))

    def loadImages(self):
        pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
        for piece in pieces:
            # Figury od razu w skali planszy
            pixmap = QPixmap("Figury/" + piece + ".png")
            pixmap = pixmap.scaled(SQ_SIZE, SQ_SIZE)
            label = QLabel()
            label.setPixmap(pixmap)
            IMAGES[piece] = label

    def drawBoard(self):
        global colors
        colors = [QColor(150,150,150), QColor(50,50,50)]

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
        print(self.sqSelected,self.playerClicks)
        if self.moveMade:
            self.moveMade = False
            self.animate = False
            self.moveUndone = False
            print(self.sqSelected,self.playerClicks)
            self.sqSelected = ()         
            self.playerClicks = []      #TO DODAŁEM TERAZ  
                    
        self.gs.scanBoard()

        if self.gs.checkMate or self.gs.staleMate:
            self.gameOver = True
            if self.gs.staleMate:
                text = 'Stalemate'
            else:
                text = 'White wins by checkmate' if not self.gs.WhiteToMove else 'Black wins by checkmate'
            print(text)
        self.update() 

    def paintEvent(self,event):
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing)
        if self.animate:
            self.animateMove()
        else:
            self.drawBoard()
        self.painter.end()

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



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QMainWindow()
    chessboard = ChessGraphicsQT()
    window.setCentralWidget(chessboard)
    window.setGeometry(750, 250, BOARD_WIDTH, BOARD_HEIGHT)
    chessboard.setFocus()
    window.show()

    sys.exit(app.exec_())
