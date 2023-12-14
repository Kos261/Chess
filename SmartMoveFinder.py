import random

pieceScore = {"K":0, "Q":10, "R":5, "N":3, "B":3, "p":1 }
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
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
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE


    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def greedyAlgorithm(gs, validMoves):
    turnMultiplier = 1 if gs.WhiteToMove else -1
    bestMove = None
    maxScore = -CHECKMATE

    for playerMove in validMoves:
        gs.makeMove(playerMove)
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
    random.shuffle(validMoves)
    
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        if gs.staleMate:
            opponentMaxScore = STALEMATE

        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE

        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
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
def minMaxRecursiveCaller_(gs, validMoves, depth, whiteToMove):
    global nextMove
    nextMove = None
    minMaxRecursive(gs, validMoves, DEPTH, gs.WhiteToMove)
    return nextMove

def minMaxRecursive(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board) #ScoreBoard?
    
    random.shuffle(validMoves)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
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
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = minMaxRecursive(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
    return minScore


