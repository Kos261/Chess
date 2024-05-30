#Ta klasa odpowiada za obecny stan gry oraz poprawne ruchy.

class GameState():
    def __init__(self, GUI):
        #Pierwsza litera kolor, druga rodzaj R-rook, N-knight, B-bishop, Q-queen, K-king "--" puste
        # self.board = [
        #     ["bR","bN","bB","bQ","bK","bB","bN","bR"],
        #     ["bp","bp","bp","bp","bp","bp","bp","bp"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["wp","wp","wp","wp","wp","wp","wp","wp"],
        #     ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        
        self.board = [
          ["--","--","--","--","--","--","bB","bR"],
          ["--","--","--","--","--","--","--","--"],
          ["--","--","--","--","bK","--","--","--"],
          ["--","--","bp","--","--","--","--","--"],
          ["--","--","--","--","wK","--","--","--"],
          ["--","--","--","--","--","--","--","--"],
          ["--","--","--","--","--","--","--","--"],
          ["--","--","--","--","--","--","--","--"]]

        self.GUI = GUI
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.moveLog = []

        self.moveFunctions = {'p':self.getPawnMoves, 'R':self.getRookMoves, 'N': self.getKnightMoves, 
                              'B':self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}
        self.WhiteToMove = True
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wKs,self.currentCastlingRight.bKs,
                                             self.currentCastlingRight.wQs,self.currentCastlingRight.bQs)]
            
    def makeMove(self, move, AIPlaying = False):
        #To bierze ruch jako parameter (nie działa dla roszady i en-passante)
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #Zapisujemy historię ruchów
        self.WhiteToMove = not self.WhiteToMove #Zmiana gracza
        if move.pieceMoved[1] == 'K':
            if move.pieceMoved[0] == 'b':
                self.blackKingLocation = (move.endRow, move.endCol)
            if move.pieceMoved[0] == 'w':
                self.whiteKingLocation = (move.endRow, move.endCol)

        if move.pawnPromotion:

            if not AIPlaying:
                while True:
                    try:
                        promotedPiece = str(input("Promote to Q, R, B or N: ") .upper())
                        if promotedPiece in ['Q','R','B','N']:
                            break
                        else:
                            print("Error! give proper letter for figure")
                    except ValueError:
                        print("Wprowadzono zły znak")
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

            elif AIPlaying:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
            

        #en passante
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'

        #updating enpassant square location
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2,move.endCol)   #Square beetwen is enpassant
        else:
            self.enpassantPossible = ()

        #updating castling rights - when king or rook move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  #King side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves rook
                self.board[move.endRow][move.endCol+1] = '--'
            else: #Queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wKs,self.currentCastlingRight.bKs,
                                             self.currentCastlingRight.wQs,self.currentCastlingRight.bQs))
        
        self.enpassantPossibleLog.append(self.enpassantPossible)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.WhiteToMove = not self.WhiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow , move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow , move.startCol)

            #Undo enpassant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]


            #Undo castling
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:    #King side castle
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #Queen side castle
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self,move):

        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wKs = False
            self.currentCastlingRight.wQs = False

        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bKs = False
            self.currentCastlingRight.bQs = False

        elif move.pieceMoved == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wQs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wKs = False

        elif move.pieceMoved == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bQs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bKs = False

        #Captured rook 
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wQs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wKs = False

        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bQs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bKs = False

    def getValidMoves(self):
        moves = []
        if self.WhiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
            allyColor = 'w'
            enemyColor = 'b'
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
            allyColor = 'b'
            enemyColor = 'w'
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks(kingRow,kingCol,allyColor, enemyColor)
        

        
        if self.inCheck:
            if len(self.checks) == 1: #Jeden szach, można się ruszyć albo zablokować
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N': 
                    validSquares = [(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                
                #Wywalam wszystkie złe ruchy które nie blokują szacha albo ruszają króla
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != 'K': #Jeśli ruch nie przemieszcza króla, musi zbić albo zasłonić
                        if not (moves[i].endRow,moves[i].endCol) in validSquares: #Ruch nie zasłania ani nie zbija
                            moves.remove(moves[i])
            
            else:   #Podwójny szach
                self.getKingMoves(kingRow,kingCol,moves)

        else:
            moves = self.getAllPossibleMoves()

        # Win condintion
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    def checkForPinsAndChecks(self, startRow, startCol, allyColor, enemyColor):
        pins = []
        checks = []
        inCheck = False
        
        #Teraz sprawdzam wszystkie pins i szachy, jeśli zapinowany to śledzę figurę
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,1),(1,-1))
        for j in range(len(directions)):
            oneDir = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + oneDir[0] * i
                endCol = startCol + oneDir[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K' :
                        if possiblePin == ():   #Pierwsza figura zapinowana
                            possiblePin = (endRow, endCol, oneDir[0], oneDir[1])
                        else:                   #Druga sojusznicza figura, nie ma pinu
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        # Przypadki
                        #   Wieża na prostej
                        #   Goniec na przekątnej
                        #   1 pole na przekątnej pion
                        #   Królowa gdziekolwiek
                        #   Skoczek
                        #   Król przeciwnika
                        if (0 <= j <= 3 and pieceType == 'R') or (4 <= j <= 7 and pieceType == 'B') or \
                        (i == 1 and pieceType == 'p' and \
                        (enemyColor == 'w' and (oneDir == (-1,-1) or oneDir == (-1,1))) or \
                        (enemyColor == 'b' and (oneDir == (1,-1) or oneDir == (1,1))))  or \
                        (pieceType == 'Q') or (i == 1 and pieceType == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow,endCol,oneDir[0],oneDir[1]))
                                break
                            else:   #Figura zasłania
                                pins.append(possiblePin)
                                break
                        else:   #Brak szacha
                            break
                else:   #poza planszą
                    break

        knightMoves = ((-1,-2),(-2,-1),(-2,1),(1,-2),(-1,2),(2,-1),(2,1),(1,2))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow,endCol,move[0],move[1]))
        
        return inCheck, pins, checks

    def getAllPossibleMoves(self, checkingCastling = False): 
        moves = []
        #Castling
        if not checkingCastling:
            if self.WhiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
            
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]                  #pierwsza litera w/b
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    piece = self.board[row][col][1]             #druga litera to figura
                    self.moveFunctions[piece](row, col, moves)  #wywołanie odpowiedniej funkcji dla figury
        return moves

    def scanBoard(self):
        figs = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                square = self.board[row][col]
                if square != '--':
                    figs.append(square)
        if len(figs) == 2:
            self.staleMate = True

        #Sprawdzanie czy król jest na planszy
        if ('wK' not in figs) or ('bK' not in figs):
            return False 
        else:
            return True

    def printBoard(self):
        for row in self.board:
            print(f"{row} \n")

    def getPawnMoves(self,row,col,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.WhiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
            kingCol, kingRow = self.blackKingLocation

        pawnPromotion = False
        
        if self.board[row+moveAmount][col] == '--':
            if not piecePinned or pinDirection == (moveAmount,0):
                if row+moveAmount == backRow:
                    pawnPromotion = True
                moves.append(Move((row,col),(row+moveAmount,col),self.board, pawnPromotion = pawnPromotion))
                if row == startRow and self.board[row+2*moveAmount][col] == '--':
                    moves.append(Move((row,col),(row+2*moveAmount,col),self.board))



        if col-1 >= 0:
            if not piecePinned or pinDirection == (moveAmount,-1):
                if self.board[row+moveAmount][col-1][0] == enemyColor:
                    if row+moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((row,col),(row+moveAmount,col-1), self.board, pawnPromotion = pawnPromotion))
                if (row+moveAmount, col-1) == self.enpassantPossible:
                    #This block handles issues when after enpassante there is free way to kill king
                    attackingPiece = False
                    blockingPiece = False

                    if kingRow == row:
                        if kingCol < col:   #king is on the left of the pawn
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)

                        else:
                             insideRange = range(kingCol - 1, col, -1)
                             outsideRange = range(col - 2, -1, -1)

                        for i in insideRange:
                            if self.board[row][i] != '--':  #Some other piece besides enpassante pawn blocks
                                blockingPiece = True
                        
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row,col),(row+moveAmount,col-1), self.board, isEnPassantMove=True))

        if col+1 <= 7:
            if not piecePinned or pinDirection == (moveAmount,1):
                if self.board[row+moveAmount][col+1][0] == enemyColor:
                    if row+moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((row,col),(row+moveAmount,col+1), self.board, pawnPromotion = pawnPromotion))
                if (row+moveAmount, col-1) == self.enpassantPossible:
                    #This block handles issues when after enpassante there is free way to kill king
                    attackingPiece = False
                    blockingPiece = False

                    if kingRow == row:
                        if kingCol < col:   #king is on the left of the pawn
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)

                        else:
                             insideRange = range(kingCol - 1, col + 1, -1)
                             outsideRange = range(col - 1, -1, -1)

                        for i in insideRange:
                            if self.board[row][i] != '--':  #Some other piece besides enpassante pawn blocks
                                blockingPiece = True
                        
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row,col),(row+moveAmount,col+1), self.board, isEnPassantMove=True))

    def getRookMoves(self,row,col,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,0),(1,0),(0,-1),(0,1)) #Góra Dół Lewo Prawo
        enemy = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((row,col),(endRow,endCol),self.board))
                        elif endPiece[0] == enemy:
                            moves.append(Move((row,col),(endRow,endCol),self.board))
                            break
                        else:   #Twoja figura
                            break
                else:       #Poza planszą
                    break
                
    def getKnightMoves(self,row,col,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-2),(-2,-1),(-2,1),(1,-2),(-1,2),(2,-1),(2,1),(1,2))
        allyColor = 'w' if self.WhiteToMove else 'b'
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((row,col),(endRow,endCol),self.board))

    def getBishopMoves(self,row,col,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1),(1,1),(1,-1),(-1,1)) #Na skos
        enemy = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((row,col),(endRow,endCol),self.board))
                        elif endPiece[0] == enemy:
                            moves.append(Move((row,col),(endRow,endCol),self.board))
                            break
                        else:   #Twoja figura
                            break
                else:       #Poza planszą
                    break

    def smallScanAroundKing(self, row, col, allyColor, enemyColor):
        directions = ((-1,-1),(1,1),(1,-1),(-1,1),(-1,0),(1,0),(0,-1),(0,1))
        for i in range(8):
            endRow = row + directions[i][0] 
            endCol = col + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy  
                inCheck, _, _ = self.checkForPinsAndChecks(endRow, endCol, allyColor, enemyColor) 
                endPiece = self.board[endRow][endCol]
                if (endPiece[0] != allyColor):
                    if endPiece[1] == 'p' and  col != endCol:
                        return True
                    if endPiece[1] == 'K':
                        return True
                else:
                    inCheck = False
        return inCheck

            



    def getKingMoves(self,row,col,moves):
        
        if self.WhiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1,-1),(1,1),(1,-1),(-1,1),(-1,0),(1,0),(0,-1),(0,1)) #Wszystko
        
        for i in range(8):
            endRow = row + directions[i][0] 
            endCol = col + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    
                    inCheck, pins, checks = self.checkForPinsAndChecks(startRow, startCol, allyColor, enemyColor)
                    inCheck = self.smallScanAroundKing(endRow, endCol, allyColor, enemyColor)
                    
                    if not inCheck:
                        moves.append(Move((row,col),(endRow,endCol),self.board))

                    if allyColor == 'w':
                        self.whiteKingLocation = (row,col)
                    else:
                        self.blackKingLocation = (row,col) 

         

    def getQueenMoves(self,row,col,moves):
        # self.getBishopMoves(row,col,moves)
        # self.getRookMoves(row,col,moves)
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1),(1,1),(1,-1),(-1,1),(-1,0),(1,0),(0,-1),(0,1)) #Wszystko
        enemy = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((row,col),(endRow,endCol),self.board))
                        elif endPiece[0] == enemy:
                            moves.append(Move((row,col),(endRow,endCol),self.board))
                            break
                        else:   #Twoja figura
                            break
                else:       #Poza planszą
                    break

    def squareUnderAttack(self,row,col):
        self.WhiteToMove = not self.WhiteToMove             #Tura przeciwnika
        oppMoves = self.getAllPossibleMoves(checkingCastling=True)
        self.WhiteToMove = not self.WhiteToMove             #Odwracamy z powrotem
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:   #Pole pod ostrzałem                                
                return True
        return False

    def getCastleMoves(self,row,col,moves):
        if (self.WhiteToMove and self.currentCastlingRight.wKs) or (not self.WhiteToMove and self.currentCastlingRight.bKs):
            self.getKingSideCastleMoves(row,col,moves)
        if  (self.WhiteToMove and self.currentCastlingRight.wQs) or (not self.WhiteToMove and self.currentCastlingRight.bQs):
            self.getQueenSideCastleMoves(row,col,moves)

    def getKingSideCastleMoves(self,row,col,moves):
        # print(self.board[row][col+1],self.board[row][col+2])
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            if not self.squareUnderAttack(row,col+1) and not self.squareUnderAttack(row,col+2):
                moves.append(Move((row,col), (row,col+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self,row,col,moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            if not self.squareUnderAttack(row,col-1) and not self.squareUnderAttack(row,col-2) and not self.squareUnderAttack(row,col-3):
                moves.append(Move((row,col), (row,col-2), self.board, isCastleMove=True))


class Move():
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0} #key:value
    rowsToRanks = {v:k for k,v in ranksToRows.items()}                     #value:key
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board,isEnPassantMove = False, pawnPromotion = False, isCastleMove = False):
        self.board = board
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0] 
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.pawnPromotion = pawnPromotion
        self.isCapture = self.pieceCaptured != '--'
        
        #Castling
        self.isCastleMove = isCastleMove

        #en passant true/false
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        
    def __eq__(self,other):
        if isinstance(other,Move):
            return  self.moveID == other.moveID
        return False
    
    def __str__(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O" 
        
        else:
            if self.isCapture:
                tekst = f"{self.pieceMoved} {self.getRankFile(self.startRow,self.startCol)} x {self.getRankFile(self.endRow,self.endCol)}"
                
            else:
                tekst = f"{self.pieceMoved} {self.getRankFile(self.startRow,self.startCol)} > {self.getRankFile(self.endRow,self.endCol)}"
            return tekst         

    def getChessNotation(self):
        tekst = f"{self.pieceMoved} {self.getRankFile(self.startRow,self.startCol)} -> {self.getRankFile(self.endRow,self.endCol)}"
        return tekst

    def getRankFile(self,row,col):
        return self.colsToFiles[col]+self.rowsToRanks[row]
    

class CastleRights():
    def __init__(self,wKs,bKs,wQs,bQs):
        #White King side, black king side, white queen side, black queen side
        self.wKs = wKs
        self.bKs = bKs
        self.wQs = wQs
        self.bQs = bQs
        