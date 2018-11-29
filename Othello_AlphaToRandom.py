import os, copy
import random

n = 8  # board size (even)
board = [['0' for x in range(n)] for y in range(n)]
# 8 directions
dirx = [-1, 0, 1, -1, 1, -1, 0, 1]
diry = [-1, -1, -1, 0, 0, 1, 1, 1]

opt = 2
depth = 4

def InitBoard():
    if n % 2 == 0:  # if board size is even
        z = int((n - 2) / 2)
        board[z][z] = '2'
        board[n - 1 - z][z] = '1'
        board[z][n - 1 - z] = '1'
        board[n - 1 - z][n - 1 - z] = '2'


def PrintBoard():
    m = len(str(n - 1))
    for y in range(n):
        row = ''
        for x in range(n):
            row += board[y][x]
            row += ' ' * m
        print(row + ' ' + str(y))
    print
    row = ''
    for x in range(n):
        row += str(x).zfill(m) + ' '
    print(row + '\n')


def MakeMove(board, x, y, player):  # assuming valid move
    totctr = 0  # total number of opponent pieces taken
    board[y][x] = player
    for d in range(8):  # 8 directions
        ctr = 0
        for i in range(n):
            dx = x + dirx[d] * (i + 1)
            dy = y + diry[d] * (i + 1)
            if dx < 0 or dx > n - 1 or dy < 0 or dy > n - 1:
                ctr = 0;
                break
            elif board[dy][dx] == player:
                break
            elif board[dy][dx] == '0':
                ctr = 0;
                break
            else:
                ctr += 1
        for i in range(ctr):
            dx = x + dirx[d] * (i + 1)
            dy = y + diry[d] * (i + 1)
            board[dy][dx] = player
        totctr += ctr
    return (board, totctr)

def AlphaBeta(board, player, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or IsTerminalNode(board, player):
        return EvalBoard(board, player)
    if maximizingPlayer:
        v = minEvalBoard
        for y in range(n):
            for x in range(n):
                if ValidMove(board, x, y, player):
                    (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                    v = max(v, AlphaBeta(boardTemp, player, depth - 1, alpha, beta, False))
                    alpha = max(alpha, v)
                    if beta <= alpha:
                        break # beta cut-off
        return v
    else: # minimizingPlayer
        v = maxEvalBoard
        for y in range(n):
            for x in range(n):
                if ValidMove(board, x, y, player):
                    (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                    v = min(v, AlphaBeta(boardTemp, player, depth - 1, alpha, beta, True))
                    beta = min(beta, v)
                    if beta <= alpha:
                        break # alpha cut-off
        return v

def AlphaBetaSN(board, player, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or IsTerminalNode(board, player):
        return EvalBoard(board, player)
    sortedNodes = GetSortedNodes(board, player)
    if maximizingPlayer:
        v = minEvalBoard
        for boardTemp in sortedNodes:
            v = max(v, AlphaBetaSN(boardTemp, player, depth - 1, alpha, beta, False))
            alpha = max(alpha, v)
            if beta <= alpha:
                break # beta cut-off
        return v
    else: # minimizingPlayer
        v = maxEvalBoard
        for boardTemp in sortedNodes:
            v = min(v, AlphaBetaSN(boardTemp, player, depth - 1, alpha, beta, True))
            beta = min(beta, v)
            if beta <= alpha:
                break # alpha cut-off
        return v

def Negamax(board, player, depth, color):
    if depth == 0 or IsTerminalNode(board, player):
        return color * EvalBoard(board, player)
    bestValue = minEvalBoard
    for y in range(n):
        for x in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                v = -Negamax(boardTemp, player, depth - 1, -color)
                bestValue = max(bestValue, v)
    return bestValue

def NegamaxAB(board, player, depth, alpha, beta, color):
    if depth == 0 or IsTerminalNode(board, player):
        return color * EvalBoard(board, player)
    bestValue = minEvalBoard
    for y in range(n):
        for x in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                v = -NegamaxAB(boardTemp, player, depth - 1, -beta, -alpha, -color)
                bestValue = max(bestValue, v)
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
    return bestValue

def NegamaxABSN(board, player, depth, alpha, beta, color):
    if depth == 0 or IsTerminalNode(board, player):
        return color * EvalBoard(board, player)
    sortedNodes = GetSortedNodes(board, player)
    bestValue = minEvalBoard
    for boardTemp in sortedNodes:
        v = -NegamaxABSN(boardTemp, player, depth - 1, -beta, -alpha, -color)
        bestValue = max(bestValue, v)
        alpha = max(alpha, v)
        if alpha >= beta:
            break
    return bestValue

def Negascout(board, player, depth, alpha, beta, color):
    if depth == 0 or IsTerminalNode(board, player):
        return color * EvalBoard(board, player)
    firstChild = True
    for y in range(n):
        for x in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                if not firstChild:
                    score = -Negascout(boardTemp, player, depth - 1, -alpha - 1, -alpha, -color)
                    if alpha < score and score < beta:
                        score = -Negascout(boardTemp, player, depth - 1, -beta, -score, -color)
                else:
                    firstChild = False
                    score = -Negascout(boardTemp, player, depth - 1, -beta, -alpha, -color)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
    return alpha

def NegascoutSN(board, player, depth, alpha, beta, color):
    if depth == 0 or IsTerminalNode(board, player):
        return color * EvalBoard(board, player)
    sortedNodes = GetSortedNodes(board, player)
    firstChild = True
    for boardTemp in sortedNodes:
        if not firstChild:
            score = -NegascoutSN(boardTemp, player, depth - 1, -alpha - 1, -alpha, -color)
            if alpha < score and score < beta:
                score = -NegascoutSN(boardTemp, player, depth - 1, -beta, -score, -color)
        else:
            firstChild = False
            score = -NegascoutSN(boardTemp, player, depth - 1, -beta, -alpha, -color)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return alpha

def ValidMove(board, x, y, player):
    if x < 0 or x > n - 1 or y < 0 or y > n - 1:
        return False
    if board[y][x] != '0':
        return False
    (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
    if totctr == 0:
        return False
    return True


minEvalBoard = -1  # min - 1
maxEvalBoard = n * n + 4 * n + 4 + 1  # max + 1


def EvalBoard(board, player):
    tot = 0
    for y in range(n):
        for x in range(n):
            if board[y][x] == player:
                if (x == 0 or x == n - 1) and (y == 0 or y == n - 1):
                    tot += 4  # corner
                elif (x == 0 or x == n - 1) or (y == 0 or y == n - 1):
                    tot += 2  # side
                else:
                    tot += 1
    return tot


def IsTerminalNode(board, player):
    for y in range(n):
        for x in range(n):
            if ValidMove(board, x, y, player):
                return False
    return True

def BestMove(board, player):
    maxPoints = 0
    mx = -1; my = -1
    for y in range(n):
        for x in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                points = AlphaBeta(board, player, depth, minEvalBoard, maxEvalBoard, True)
                if points > maxPoints:
                    maxPoints = points
                    mx = x; my = y
    return (mx, my)

def GetSortedNodes(board, player):
    sortedNodes = []
    for y in range(n):
        for x in range(n):
            if ValidMove(board, x, y, player):
                (boardTemp, totctr) = MakeMove(copy.deepcopy(board), x, y, player)
                sortedNodes.append((boardTemp, EvalBoard(boardTemp, player)))
    sortedNodes = sorted(sortedNodes, key=lambda node: node[1], reverse=True)
    sortedNodes = [node[0] for node in sortedNodes]
    return sortedNodes

InitBoard()
while True:
    for p in range(2):
        print
        PrintBoard()
        player = str(p + 1)
        print('PLAYER: ' + player)
        if IsTerminalNode(board, player):
            print('Player cannot play! Game ended!')
            print('RL AI : ' + str(EvalBoard(board, '1')))
            print('AlPHA AI  : ' + str(EvalBoard(board, '2')))
            os._exit(0)

        if player == '1': #computer1's turn
            while True:
                validlist = []
                for x in range(8):
                    for y in range(8):
                        if ValidMove(board, x, y, player):
                            validlist.append([x,y])
                random.shuffle(validlist)
                (x,y) = validlist.pop()
                x = int(x)
                y = int(y)
                (board, totctr) = MakeMove(board, x, y, player)
                print('# of pieces taken: ' + str(totctr))
                break

            if not (x == -1 and y == -1):
                (board, totctr) = MakeMove(board, x, y, player)
                print('player2 played (X Y): ' + str(x) + ' ' + str(y))
                print('# of pieces taken: ' + str(totctr))
                PrintBoard()

        else:  # computer2's turn (Alpha Beta)
            (x, y) = BestMove(board, player)
            if not (x == -1 and y == -1):
                (board, totctr) = MakeMove(board, x, y, player)
                print('AI played (X Y): ' + str(x) + ' ' + str(y))
                print('# of pieces taken: ' + str(totctr))