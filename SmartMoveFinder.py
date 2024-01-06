import random

pieceScore = {"K":0, "Q":10, "R":5, "N":3, "B":3, "p":1 }

knightScores = [[1,1,1,1,1,1,1,1],
                [1,2,2,2,2,2,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [1,1,1,1,1,1,1,1]]

bishopScores = [[4,3,2,1,1,2,3,4],
                [3,4,3,2,2,3,4,3],
                [2,3,4,3,3,4,3,2],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [2,3,4,3,3,4,3,2],
                [3,4,3,2,2,3,4,3],
                [4,3,2,1,1,2,3,4]]

rookScores =   [[4,3,3,4,4,3,3,4],
                [1,2,2,2,2,2,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [4,3,3,4,4,3,3,4]]

queenScores =  [[4,4,4,4,4,4,4,4],
                [3,4,3,2,2,3,4,3],
                [2,3,4,3,3,4,3,2],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [2,3,4,3,3,4,3,2],
                [3,4,3,2,2,3,4,3],
                [4,4,4,4,4,4,4,4]]

wPawnScores =  [[8,8,8,8,8,8,8,8],
                [5,6,6,7,7,6,6,5],
                [1,2,4,5,5,4,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [2,2,2,3,3,2,2,2],
                [1,1,1,0,0,1,1,1],
                [0,0,0,0,0,0,0,0]]


bPawnScores =  [[0,0,0,0,0,0,0,0],
                [1,1,1,0,0,1,1,1],
                [2,2,2,3,3,2,2,2],
                [1,2,3,4,4,3,2,1],
                [1,2,3,4,4,3,2,1],
                [1,2,4,5,5,4,2,1],
                [5,6,6,7,7,6,6,5],
                [8,8,8,8,8,8,8,8]]

piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores, "R": rookScores, "bp": bPawnScores, "wp": wPawnScores}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
'''
A positive score is good for white, a negative score is good for black
'''

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score

def scoreBoard(gs):
    # for example pawn protecting piece is stronger than pawn that doesn't do that
    if gs.checkMate:
        if gs.WhiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE


    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != '--':
                #Score positionally
                piecePositionScore = 0

                if square[1] != 'K':
                    if square[1] == 'p':
                        piecePositionScore = piecePositionScores[square][row][col] 
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col] 



                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * 0.5

                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * 0.5
    return score


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def greedyAlgorithm(gs, validMoves):
    turnMultiplier = 1 if gs.WhiteToMove else -1
    bestMove = None
    maxScore = -CHECKMATE

    for playerMove in validMoves:
        gs.makeMove(playerMove, AIPlaying = True)
        if gs.checkMate:
            score = CHECKMATE
        elif gs.staleMate:
            score = STALEMATE
        else:
            score = turnMultiplier * scoreMaterial(gs.board)
        if score > maxScore:
            maxScore = score 
            bestMove = playerMove
        gs.undoMove()

    return bestMove

def minMaxAlgorithm2depth(gs, validMoves):
    #Algorithm is looking for best opponent moves, and then minimize them and maximize AI adventage
    turnMultiplier = 1 if gs.WhiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    
    for playerMove in validMoves:
        gs.makeMove(playerMove, AIPlaying = True)
        opponentMoves = gs.getValidMoves()
        if gs.staleMate:
            opponentMaxScore = STALEMATE

        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE

        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove, AIPlaying = True)
                gs.getValidMoves()

                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score =  -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score 
                gs.undoMove()

        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()

    return bestPlayerMove


#Helper method to make first recursive call
def minMaxRecursiveCaller_(gs, validMoves):
    global nextMove
    nextMove = None
    minMaxRecursive(gs, validMoves, DEPTH, gs.WhiteToMove)
    return nextMove

def minMaxRecursive(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board) #ScoreBoard?
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move, AIPlaying = True)
            nextMoves = gs.getValidMoves()
            score = minMaxRecursive(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move, AIPlaying = True)
            nextMoves = gs.getValidMoves()
            score = minMaxRecursive(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
    return minScore



#Helper method to make first recursive call
def negaMaxCaller_(gs, validMoves):
    global nextMove, counter
    counter = 0
    nextMove = None
    negaMax(gs, validMoves, DEPTH, 1 if gs.WhiteToMove else -1)
    print("Simulated moves:", counter)
    counter = 0
    return nextMove

def negaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs) 

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, AIPlaying = True)
        nextMoves = gs.getValidMoves()
        score = -negaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore



#Helper method to make first recursive call
def negaMaxAlphaBetaCaller_(gs, validMoves, returnQueue):
    global nextMove, counter
    counter = 0
    nextMove = None
    negaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.WhiteToMove else -1)
    print("Simulated moves:", counter)
    counter = 0
    returnQueue.put(nextMove)

def negaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs) 

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, AIPlaying = True)
        nextMoves = gs.getValidMoves()
        score = -negaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                #print(move,score)
        gs.undoMove()

        #Pruning useless moves
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    return maxScore


