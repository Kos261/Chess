# import sys
import random
# import pygame
import os
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QPixmap, QColor, QFont, QPalette
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QThreadPool
     # QSize, QByteArray, QBuffer, QIODevice

from multiprocessing import Process, Queue
from threading import Thread

from Themes_and_animations import *
from ChessEngine import GameState, Move
import SmartMoveFinder

BOARD_WIDTH = BOARD_HEIGHT = 600
MAX_FPS = 20
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
IMAGES = {}
THEMES = {}

class Chessboard(QWidget):
    def __init__(self, GUI, playerOne, playerTwo):
        super().__init__()
        self.t = QThread(self)
        self.chessboard_color = GUI.chessboard_color
        self.loadImages()
        self.GUI = GUI
        self.gs = GameState(self.GUI)
        self.validMoves = self.gs.getValidMoves()
        random.shuffle(self.validMoves)

        self.playerOne = playerOne
        self.playerTwo = playerTwo   

        self.pawnPromotionActive = False
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
            # last_move = self.gs.moveLog[-1]
            # if last_move:
            #     if last_move.pawnPromotion:
            #         self.pawnPromotionActive = True

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

    def pawn_promotion_screen(self):
        size_scaled = int(SQ_SIZE * 1.2)
        self.pawn_promotionPieces = ['wQ', 'wR', 'wB', 'wN']

        board_width = 8 * SQ_SIZE
        total_width = 4 * size_scaled
        x_offset = (board_width - total_width) // 2
        y = 30

        base_color = self.chessboard_color[1]
        shadow_color = QColor(
            max(0, base_color.red() - 40),
            max(0, base_color.green() - 40),
            max(0, base_color.blue() - 40)
        )
        shadow_color.setAlpha(150)

        self.painter.fillRect(x_offset + 10, y + 10,
                            size_scaled * 4 + 20,
                            size_scaled + 20,
                            shadow_color)

        self.painter.fillRect(x_offset - 10, y - 10,
                            size_scaled * 4 + 20,
                            size_scaled + 20,
                            self.chessboard_color[1])

        for col in range(4):
            color = self.chessboard_color[(col % 2)]
            x = x_offset + col * size_scaled
            self.painter.fillRect(x, y, size_scaled, size_scaled, color)
            pixmap = IMAGES[self.pawn_promotionPieces[col]].pixmap()

            scaled_pixmap = pixmap.scaled(size_scaled, size_scaled, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.painter.drawPixmap(x, y, size_scaled, size_scaled, scaled_pixmap)

    def paintEvent(self, event):
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing)

        if not self.gameOver: 
            self.drawBoard()
            self.highlightSquares()
            if self.pawnPromotionActive:
                self.pawn_promotion_screen()
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
                if self.pawnPromotionActive:
                    x = event.pos().x()
                    y = event.pos().y()

                    size_scaled = int(SQ_SIZE * 1.2)
                    promo_width = 4 * size_scaled
                    x_offset = (BOARD_WIDTH - promo_width) // 2
                    panel_y = 30

                    if x_offset <= x < x_offset + promo_width and \
                    panel_y <= y < panel_y + size_scaled:
                        selected_col = int((x - x_offset) // size_scaled)
                        selected_piece = self.pawn_promotionPieces[selected_col]    
                        print("Wybrano figurę do promocji:", selected_piece)



                else:
                    col = event.pos().x() // SQ_SIZE
                    row = event.pos().y() // SQ_SIZE

                    if self.sqSelected == (row, col) or col >= 8:
                        self.sqSelected = ()  
                        self.playerClicks = []
                    else:
                        self.sqSelected = (row, col)
                        self.playerClicks.append(self.sqSelected)
                                            
                    if len(self.playerClicks) == 2:
            
                        self.move = Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
                        #There is no check if move is pawn promotion!!!!
                        if self.move in self.validMoves:

                            self.gs.makeMove(self.move)
                            self.humanTurn =  self.playerOne if self.gs.WhiteToMove else self.playerTwo
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
