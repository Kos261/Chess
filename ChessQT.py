import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
from ChessEngine_Advanced import GameState, Move
import random

BOARD_WIDTH = BOARD_HEIGHT = 600
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 20
IMAGES = {}


class ChessGraphicsQT(QWidget):
    def __init__(self):
        super().__init__()
        self.loadImages()
        self.gs = GameState()
        self.validMoves = self.gs.getValidMoves()
        random.shuffle(self.validMoves)
        self.moveMade = False            
        self.animate = False
        self.sqSelected = ()
        self.playerClicks = [] 
        self.gameOver = False
        self.playerOne = True          #If player is playing or AI
        self.playerTwo = True
        self.AIThinking = False
        self.moveFinderProcess = None
        self.moveUndone = False
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

    def drawGameState(self):
        # drawGameState odpowiada za całą grafikę w obecnym stanie gry
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        # self.drawBoard()
        # highlightSquares(screen, gs, validMoves, sqSelected)
        # drawPieces(screen,gs.board)
        # drawMoveLog(screen, gs, moveLogFont)

    def paintEvent(self,event):
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

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
        self.painter.end()

    def updateGameState(self):
        self.update()  # Wywołuje paintEvent i odświeża widok
        
    
    def keyPressEvent(self, event):
        if event.isAccepted():
            print("Zdarzenie zostało zaakceptowane.")
        else:
            print("Zdarzenie nie zostało zaakceptowane.")
        print(f"Naciśnięto klawisz: {event.text()}")
               
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.gameOver:
                col = event.pos().x()//SQ_SIZE
                row = event.pos().y()//SQ_SIZE
                print(f"Lokalizacja kursora myszy: {col}, {row}")
                if self.sqSelected == (row,col) or col >= 8:  #Gracz wybrał to samo pole 2 razy
                    self.sqSelected = ()          #deselect
                    self.playerClicks = []
                else:
                    self.sqSelected = (row,col)
                    self.playerClicks.append(self.sqSelected)
                if len(self.playerClicks) == 2 and self.humanTurn:
                    print("Działa")
                    move = Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
                    print(move)

                    for i in range(len(self.validMoves)):
                        if move == self.validMoves[i]:
                            #print(move.getChessNotation())
                            self.gs.makeMove(self.validMoves[i])
                            self.gs.printBoard()
                            self.moveMade = True
                            self.animate = True
                            self.sqSelected = ()
                            self.playerClicks = []
                        if not self.moveMade:
                            self.playerClicks = [self.sqSelected]

        elif event.button() == Qt.RightButton:
            print("Kliknięto prawym przyciskiem myszy")



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QMainWindow()
    chessboard = ChessGraphicsQT()
    window.setCentralWidget(chessboard)
    window.setGeometry(750, 250, BOARD_WIDTH, BOARD_HEIGHT)
    window.show()

    sys.exit(app.exec_())
