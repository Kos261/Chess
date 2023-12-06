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

def drawGameState(screen,gs):
    #drawGameState odpowiada za całą grafikę w obecnym stanie gry
    drawBoard(screen)
    drawPieces(screen,gs.board)

def drawBoard(screen):
    #Rysowanie planszy
    colors = [p.Color("white"),p.Color("pink")]
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



if __name__ == '__main__':
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT)) 
    screen.fill(p.Color("White"))
    clock = p.time.Clock()
    gs = ChessEngine_Advanced.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False            #Zmienna flagowa żeby nie generować ruchów za każdym razem
    loadImages()
    running = True
    sqSelected = ()             #Na razie żaden nie jest wybrany. Zapamiętuje ostatnie kliknięcie (tuple: (row,col))
    playerClicks = []           #Zapamiętuje kliknięcia (2 tuples np: (6,4),(4,4))
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Obsługa myszki
            elif e.type == p.MOUSEBUTTONDOWN:
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
                            print(move.getChessNotation())
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            #Obsługa klawiszy
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()   #Undo move
                    moveMade = True


        if moveMade:
            # if gs.WhiteToMove: 
            #     print("White")
            # else: 
            #     print("Block")
            validMoves = gs.getValidMoves()
            for move in validMoves:
                print(move.getChessNotation())
            moveMade = False

        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()