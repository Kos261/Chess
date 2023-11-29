#Ta klasa odpowiada za obecny stan gry oraz poprawne ruchy.

class GameState():
    def __init__(self):
        #Pierwsza litera kolor, druga rodzaj R-rook, N-knight, B-bishop, Q-queen, K-king "--" puste
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        
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
        
    def makeMove(self, move):
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

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.WhiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

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

        return moves
    
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
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
        knightMoves = ((-1,-1),(1,1),(1,-1),(-1,1),(-1,0),(1,0),(0,-1),(0,1))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow,endCol,move[0],move[1]))
        
        return inCheck, pins, checks

    def getAllPossibleMoves(self): 
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]                  #pierwsza litera w/b
                if (turn == 'w' and self.WhiteToMove) or (turn == 'b' and not self.WhiteToMove):
                    piece = self.board[row][col][1]             #druga litera to figura
                    self.moveFunctions[piece](row, col, moves)  #wywołanie odpowiedniej funkcji dla figury
        return moves

    def getPawnMoves(self,row,col,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.WhiteToMove: #Białe
            if self.board[row-1][col] == "--": #Pole przed pionem puste
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((row,col),(row-1,col),self.board))
                    if self.board[row-2][col] == "--" and row == 6:             #2 puste i pozycja startowa
                        moves.append(Move((row,col),(row-2,col),self.board))

            if col-1 >= 0:
                if self.board[row-1][col-1][0] == "b":
                    if not piecePinned or pinDirection == (-1,-1):                   
                        moves.append(Move((row,col),(row-1,col-1),self.board))  #Zbijamy po skosie lewo
            if col+1 < 7:
                if self.board[row-1][col+1][0] == "b":
                    if not piecePinned or pinDirection == (-1,1):               #Czarna figura
                        moves.append(Move((row,col),(row-1,col+1),self.board))  #Zbijamy po skosie prawo

        else:                   #Czarne
            if self.board[row+1][col] == "--":
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((row,col),(row+1,col),self.board))
                    if self.board[row+2][col] == "--" and row == 1:              #2 puste i pozycja startowa
                        moves.append(Move((row,col),(row+2,col),self.board))


            if col-1 >= 0:
                if self.board[row+1][col-1][0] == "w":    
                    if not piecePinned or pinDirection == (1,-1):                #Biała figura
                        moves.append(Move((row,col),(row+1,col-1),self.board))   #Zbijamy po skosie lewo
            if col+1 < 7:
                if self.board[row+1][col+1][0] == "w":  
                    if not piecePinned or pinDirection == (1,1):                 #Biała figura
                        moves.append(Move((row,col),(row+1,col+1),self.board))   #Zbijamy po skosie prawo

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

    def getKingMoves(self,row,col,moves):
        directions = ((-1,-1),(1,1),(1,-1),(-1,1),(-1,0),(1,0),(0,-1),(0,1)) #Wszystko
        allyColor = 'w' if self.WhiteToMove else 'b'
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
                    
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    print(inCheck,pins,checks)
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

class Move():
    #Tu jest kurwa machlojka niezła z zamianą pól (row,col) na te z szachownicy
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0} #key:value
    rowsToRanks = {v:k for k,v in ranksToRows.items()}                     #value:key
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board):
        self.board = board
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0] 
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromotion = True


        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)

    def __eq__(self,other):
        if isinstance(other,Move):
            return  self.moveID == other.moveID
        return False

    def getChessNotation(self):
        figura = self.board[self.startRow][self.startCol]
        tekst = f"{figura}\t{self.getRankFile(self.startRow,self.startCol)} -> {self.getRankFile(self.endRow,self.endCol)}"
        return tekst

    def getRankFile(self,row,col):
        return self.colsToFiles[col]+self.rowsToRanks[row]