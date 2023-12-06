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
        
        self.moveFunctions = {'p':self.getPawnMoves, 'R':self.getRookMoves, 'N': self.getKnightMoves, 
                              'B':self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}
        self.WhiteToMove = True
        self.checkMate = False
        self.staleMate = False
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.moveLog = []
        self.enpassantPossible = ()

    def makeMove(self, move):
        #To bierze ruch jako parameter (nie działa dla roszady i en-passante)
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #Zapisujemy historię ruchów
        self.WhiteToMove = not self.WhiteToMove #Zmiana gracza
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow , move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow , move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +'Q'

        #en passante
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'

        #updating enpassant square location
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2,move.endCol)   #Pole pomiędzy jest enpassant
        else:
            self.enpassantPossible = ()
        
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
                self.enpassantPossible = (move.endRow,move.endCol)

            #Undo 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

    def getValidMoves(self):
        #1) wygeneruj wszystkie ruchy
        #2) dla każdego ruchu, wykonaj go
        #3) wygeneruj wszystkie ruchy przeciwnika
        #4) dla każdego z nich sprawdź czy atakuje króla
        #5) jeśli tak, to nie jest prawidłowy ruch dla ciebie
        tempEnPassant = self.enpassantPossible
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.WhiteToMove = not self.WhiteToMove
            if self.inCheck():          #Tu powinno być white king loc i czemu KRÓL NIE MOŻE SIE RUSZYĆ
                moves.remove(moves[i])
            self.WhiteToMove = not self.WhiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        self.enpassantPossible = tempEnPassant
        return moves

    def inCheck(self):
        if self.WhiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    def squareUnderAttack(self,row,col):
        self.WhiteToMove = not self.WhiteToMove             #Tura przeciwnika
        oppMoves = self.getAllPossibleMoves()
        self.WhiteToMove = not self.WhiteToMove             #Odwracamy z powrotem
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:   #Pole pod ostrzałem                                
                return True
        return False
        

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
        if self.WhiteToMove:   #Białe
            if self.board[row-1][col] == "--":                               #Pole przed pionem puste
                moves.append(Move((row,col),(row-1,col),self.board))
                if self.board[row-2][col] == "--" and row == 6:              #2 puste i pozycja startowa
                    moves.append(Move((row,col),(row-2,col),self.board))
            if col-1 >= 0:
                if self.board[row-1][col-1][0] == "b":                       #Czarna figura
                    moves.append(Move((row,col),(row-1,col-1),self.board))   #Zbijamy po skosie lewo
                elif (row-1,col-1) == self.enpassantPossible:
                    moves.append(Move((row,col),(row-1,col-1),self.board,isEnPassantMove=True))


            if col+1 < 7:
                if self.board[row-1][col+1][0] == "b":                       #Czarna figura
                    moves.append(Move((row,col),(row-1,col+1),self.board))   #Zbijamy po skosie prawo
                elif (row-1,col+1) == self.enpassantPossible:
                    moves.append(Move((row,col),(row-1,col+1),self.board,isEnPassantMove=True))

        else:                   #Czarne
            if self.board[row+1][col] == "--":
                moves.append(Move((row,col),(row+1,col),self.board))
                if self.board[row+2][col] == "--" and row == 1:              #2 puste i pozycja startowa
                    moves.append(Move((row,col),(row+2,col),self.board))
            if col-1 >= 0:
                if self.board[row+1][col-1][0] == "w":                       #Biała figura
                    moves.append(Move((row,col),(row+1,col-1),self.board))   #Zbijamy po skosie lewo
                elif (row+1,col-1) == self.enpassantPossible:
                    moves.append(Move((row,col),(row+1,col-1),self.board,isEnPassantMove=True))

            if col+1 < 7:
                if self.board[row+1][col+1][0] == "w":                       #Biała figura
                    moves.append(Move((row,col),(row+1,col+1),self.board))   #Zbijamy po skosie prawo
                elif (row+1,col+1) == self.enpassantPossible:
                   moves.append(Move((row,col),(row+1,col+1),self.board,isEnPassantMove=True))

    def getRookMoves(self,row,col,moves):
        directions = ((-1,0),(1,0),(0,-1),(0,1)) #Góra Dół Lewo Prawo
        enemy = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
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
        directions = ((-1,-2),(-2,-1),(-2,1),(1,-2),(-1,2),(2,-1),(2,1),(1,2))
        allyColor = 'w' if self.WhiteToMove else 'b'
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((row,col),(endRow,endCol),self.board))

    def getBishopMoves(self,row,col,moves):
        directions = ((-1,-1),(1,1),(1,-1),(-1,1)) #Na skos
        enemy = 'b' if self.WhiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
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
        ally = 'w' if self.WhiteToMove else 'b'
        for i in range(8):
            endRow = row + directions[i][0] 
            endCol = col + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ally:
                    moves.append(Move((row,col),(endRow,endCol),self.board))
            else:   #Poza planszą
                break

    def getQueenMoves(self,row,col,moves):
        self.getBishopMoves(row,col,moves)
        self.getRookMoves(row,col,moves)
        # directions = ((-1,-1),(1,1),(1,-1),(-1,1),(-1,0),(1,0),(0,-1),(0,1)) #Wszystko
        # enemy = 'b' if self.WhiteToMove else 'w'
        # for d in directions:
        #     for i in range(1,8):
        #         endRow = row + d[0] * i
        #         endCol = col + d[1] * i
        #         if 0 <= endRow < 8 and 0 <= endCol < 8: #Na planszy
        #             endPiece = self.board[endRow][endCol]
        #             if endPiece == '--':
        #                 moves.append(Move((row,col),(endRow,endCol),self.board))
        #             elif endPiece[0] == enemy:
        #                 moves.append(Move((row,col),(endRow,endCol),self.board))
        #                 break
        #             else:   #Twoja figura
        #                 break
        #         else:       #Poza planszą
        #             break


class Move():
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0} #key:value
    rowsToRanks = {v:k for k,v in ranksToRows.items()}                     #value:key
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self,startSq,endSq,board,isEnPassantMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0] 
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        #en passant true/false
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'


        #Promotion
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self,other):
        if isinstance(other,Move):
            return  self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,row,col):
        return self.colsToFiles[col]+self.rowsToRanks[row]