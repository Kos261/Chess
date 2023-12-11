#Ta klasa odpowiada za user input i za grę
import pygame as p
import ChessEngine_Advanced,ChessEngine_Naive

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ["bR","bN","bB","bQ","bK","bp","wR","wN","wB","wQ","wK","wp"]
    for piece in pieces:
        #Figury od razu w skali planszy
        IMAGES[piece] = p.transform.scale(p.image.load("Figury/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))

def drawGameState(screen,gs,validMoves,sqSelected):
    #drawGameState odpowiada za całą grafikę w obecnym stanie gry
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board)

def drawBoard(screen):
    #Rysowanie planszy
    global colors
    colors = [p.Color("white"),(150,150,150)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row+col) % 2)]
            p.draw.rect(screen,color, p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

     # Dodawanie liter do lewej krawędzi
    letters = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
    font = p.font.Font(None, 36)
    for i in range(DIMENSION):
        text = font.render(letters[i], True, p.Color('grey'))
        screen.blit(text, (0, i * SQ_SIZE + SQ_SIZE / 2 - text.get_height() / 2))
    
    # Dodawanie liczb do dolnej krawędzi
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    for i in range(DIMENSION):
        text = font.render(numbers[i], True, p.Color('grey'))
        screen.blit(text, (i * SQ_SIZE + SQ_SIZE / 2 - text.get_width() / 2, 0))

def drawPieces(screen,board):
    #Rysowanie figur w obecnym stanie gry
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": #Nie jest puste pole
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

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



def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32 , True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject,textLocation.move(2,2))


def main(): 
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT)) 
    screen.fill(p.Color("White"))
    clock = p.time.Clock()
    gs = ChessEngine_Advanced.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False            
    animate = False
    loadImages()
    running = True
    sqSelected = ()             #Na razie żaden nie jest wybrany. Zapamiętuje ostatnie kliknięcie (tuple: (row,col))
    playerClicks = []           #Zapamiętuje kliknięcia (2 tuples np: (6,4),(4,4))
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Obsługa myszki
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) myszki
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col):  #Gracz wybrał to samo pole 2 razy
                        sqSelected = ()          #deselect
                        playerClicks = []        #wyczyszczenie pamięci kliknięć
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks)==2:
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
                    moveMade = True
                    animate = False

                if e.key == p.K_r:  #Reset game
                    gs = ChessEngine_Advanced.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen,gs,validMoves,sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.WhiteToMove:
                drawText(screen, 'Black wins by checkmate')
                print("Black wins by checkmate")
            else:
                drawText(screen, 'White wins by checkmate')
                print('White wins by checkmate')

        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')
            print("Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()




if __name__ == '__main__':
    main()