#Ta klasa odpowiada za user input i za grę
import pygame as p
import ChessEngine_Advanced,ChessEngine_Naive, SmartMoveFinder
import random
from multiprocessing import Process, Queue

import sys
import re
import time
import os
import shutil


from PyQt5.QtCore import QDir, Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QMessageBox, QTextEdit, QStyleFactory


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 20
IMAGES = {}

def loadImages():
    pieces = ["bR","bN","bB","bQ","bK","bp","wR","wN","wB","wQ","wK","wp"]
    for piece in pieces:
        #Figury od razu w skali planszy
        IMAGES[piece] = p.transform.scale(p.image.load("Figury/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))

def drawGameState(screen,gs,validMoves,sqSelected, moveLogFont):
    #drawGameState odpowiada za całą grafikę w obecnym stanie gry
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board)
    drawMoveLog(screen, gs, moveLogFont)

def drawBoard(screen):
    #Rysowanie planszy
    global colors
    colors = [p.Color("white"),(150,150,150)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row+col) % 2)]
            p.draw.rect(screen,color, p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))



            #TRZEBA ZAMIENIĆ LITERY Z CYFRAMUI
    numbers = ['8', '7', '6', '5', '4', '3', '2', '1']
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    font = p.font.Font(None, 36)
    for i in range(DIMENSION):
        text = font.render(numbers[i], True, p.Color('grey'))
        screen.blit(text, (0, i * SQ_SIZE + SQ_SIZE / 2 - text.get_height() / 2))
    
    # Dodawanie liczb do dolnej krawędzi
    
    for i in range(DIMENSION):
        text = font.render(letters[i], True, p.Color('grey'))
        screen.blit(text, (i * SQ_SIZE + SQ_SIZE / 2 - text.get_width() / 2, 0))

def drawPieces(screen,board):
    #Rysowanie figur w obecnym stanie gry
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": #Nie jest puste pole
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawMoveLog(screen, gs, font):
    
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = moveLog #LAter change
    padding = 20
    textY = padding
    line_spacing = 2 

    for i in range(len(moveTexts)):
        text = f"{i+1}. " + str(moveTexts[i])
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject,textLocation)
        textY += textObject.get_height() + line_spacing

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.WhiteToMove else 'b'):
            #Highlighting tiles
            surface = p.Surface((SQ_SIZE,SQ_SIZE))
            surface.set_alpha(100) #0 Transparent 255 opaque
            surface.fill(p.Color('blue'))
            screen.blit(surface, (col*SQ_SIZE,row*SQ_SIZE))
            surface.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(surface, (SQ_SIZE*move.endCol,SQ_SIZE*move.endRow))

def animateMove(move, screen, board, clock):
    global colors
    dRow = move.endRow - move.startRow
    dCol = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dRow) + abs(dCol)) * framesPerSquare
    for frame in range(frameCount+1):
        row, col = (move.startRow + dRow * frame/frameCount,move.startCol + dCol * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece
        if move.pieceCaptured != '--' and move.isEnPassantMove == False:
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw moving piece 
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32 , True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_BOARD_WIDTH()/2, BOARD_HEIGHT/2 - textObject.get_BOARD_HEIGHT()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject,textLocation.move(2,2))

def drawPawnPromotion(screen):
    pass



def main(): 
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT)) 
    screen.fill(p.Color("White"))
    moveLogFont = p.font.SysFont("Helvetica", 20, False, False)
    clock = p.time.Clock()
    gs = ChessEngine_Advanced.GameState()
    validMoves = gs.getValidMoves()
    random.shuffle(validMoves)
    moveMade = False            
    animate = False
    loadImages()
    running = True
    sqSelected = ()             #Na razie żaden nie jest wybrany. Zapamiętuje ostatnie kliknięcie (tuple: (row,col))
    playerClicks = []           #Zapamiętuje kliknięcia (2 tuples np: (6,4),(4,4))
    gameOver = False
    playerOne = True          #If player is playing or AI
    playerTwo = False
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while running:
        humanTurn = (gs.WhiteToMove and playerOne) or (not gs.WhiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Obsługa myszki
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) myszki
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >= 8:  #Gracz wybrał to samo pole 2 razy
                        sqSelected = ()          #deselect
                        playerClicks = []        #wyczyszczenie pamięci kliknięć
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine_Advanced.Move(playerClicks[0],playerClicks[1],gs.board)
                        
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                # print(move.getChessNotation())
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #Obsługa klawiszy
            elif e.type == p.KEYDOWN:

                if e.key == p.K_z:
                    gs.undoMove()   #Undo move
                    sqSelected = ()
                    playerClicks = []
                    gameOver = False
                    moveMade = True
                    animate = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

                if e.key == p.K_r:  #Reset game
                    gs = ChessEngine_Advanced.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    gameOver = False
                    moveMade = True
                    animate = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True


        # AI logic
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("Thinking...")
                returnQueue = Queue()   #Used to pass data between threads  
                moveFinderProcess = Process(target=SmartMoveFinder.negaMaxAlphaBetaCaller_, 
                                            args = (gs, validMoves, returnQueue))
                moveFinderProcess.start() #Call findBestMove(gs,validMoves,returnQueue)
                
            if not moveFinderProcess.is_alive():
                print("Done thinking")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove,AIPlaying=True)
                moveMade = True
                animate = True  
                AIThinking = False


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            random.shuffle(validMoves)
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                text = 'Stalemate'
            else:
                text = 'White wins by checkmate' if not gs.WhiteToMove else 'Black wins by checkmate'
                
            drawEndGameText(screen, text)
            

        clock.tick(MAX_FPS)
        p.display.flip()




class ChessGraphicsQT(QWidget):
    def __init__(self):
        super().__init__()



if __name__ == '__main__':
    main()