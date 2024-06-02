# -*- coding: utf-8 -*-
from fastapi import FastAPI, Response
import random
import time
import uvicorn

    
class GameState():
    gamePosition: str
    firstPlayerId: int
    secondPlayerId: int
    firstPlayerWins: int
    secondPlayerWins: int
    firstPlayersMove: bool
    firstPlayerLastTime: int
    secondPlayerLastTime: int
    
    def __init__(self, firstId, secondId, position = ".........", firstWins = 0, secondWins = 0, firstMove = True):
        self.gamePosition = position
        self.firstPlayerId = firstId
        self.secondPlayerId = secondId
        self.firstPlayerWins = firstWins
        self.secondPlayerWins = secondWins
        self.firstPlayersMove = firstMove
        self.firstPlayerLastTime = int(time.time())
        self.secondPlayerLastTime = int(time.time())


# = {}
playerDict = {}
gameDict = {}
globalPlayerId = 0
globalGameId = 0
lastUnmatched = -1

app = FastAPI()

def printPosition(gamePosition: str):
    print(gamePosition[0:3])
    print(gamePosition[3:6])
    print(gamePosition[6:9])

def isValidMove(playerMove: str, gamePosition: str):
    try:
        x, y = map(int, playerMove.split('_'))
    except ValueError:
        return False
    if (y < 1) or (y > 3) or (x < 1) or (x > 3):
        return False
    index = (3 - y) * 3 + (x - 1)
    return gamePosition[index] == '.'

def indexForPosition(playerMove: str):
    try:
        x, y = map(int, playerMove.split('_'))
    except ValueError:
        return -1
    return (3 - y) * 3 + (x - 1)

def getNewPosition(gamePosition: str, index: int, symbol: str):
    return gamePosition[:index] + symbol + gamePosition[index+1:]

def isGameEnded(gamePos: str):
    # 0 - it's not, 1 - first player won, 2 - second, -1 - draw.
    if (gamePos[0] == gamePos[1] and gamePos[1] == gamePos[2] and gamePos[0] != '.'):
        return (1 if gamePos[0] == 'X' else 2)
    
    if (gamePos[3] == gamePos[4] and gamePos[4] == gamePos[5] and gamePos[3] != '.'):
        return (1 if gamePos[3] == 'X' else 2)
    
    if (gamePos[6] == gamePos[7] and gamePos[7] == gamePos[8] and gamePos[6] != '.'):
        return (1 if gamePos[6] == 'X' else 2)
    
    
    
    if (gamePos[0] == gamePos[3] and gamePos[3] == gamePos[6] and gamePos[0] != '.'):
        return (1 if gamePos[0] == 'X' else 2)
    
    if (gamePos[1] == gamePos[4] and gamePos[4] == gamePos[7] and gamePos[1] != '.'):
        return (1 if gamePos[1] == 'X' else 2)
    
    if (gamePos[2] == gamePos[5] and gamePos[5] == gamePos[8] and gamePos[2] != '.'):
        return (1 if gamePos[2] == 'X' else 2)
    
    
    if (gamePos[0] == gamePos[4] and gamePos[4] == gamePos[8] and gamePos[0] != '.'):
        return (1 if gamePos[0] == 'X' else 2)
    
    if (gamePos[2] == gamePos[4] and gamePos[4] == gamePos[6] and gamePos[2] != '.'):
        return (1 if gamePos[2] == 'X' else 2)
    
    for c in gamePos:
        if c == '.':
            return 0
    return -1
    
@app.get("/initNewPlayer")
async def initNewPlayer(response: Response):
    global globalPlayerId
    global globalGameId
    global lastUnmatched
    
    response.headers["playerId"] = str(globalPlayerId)
    
    if (lastUnmatched == -1):
        lastUnmatched = globalPlayerId
        playerDict[globalPlayerId] = -1
    else:
        playerDict[globalPlayerId] = globalGameId
        playerDict[lastUnmatched] = globalGameId
        
        firstPlayer = random.choice([globalPlayerId, lastUnmatched])
        
        gameDict[globalGameId] = GameState(firstPlayer, globalPlayerId + lastUnmatched - firstPlayer)
        
        lastUnmatched = -1
        globalGameId += 1
        
    globalPlayerId = globalPlayerId + 1
    return "{}\r\n"

@app.get("/getInformation")
async def getInformation(playerId: str, response: Response):
    #print("---------------- " + playerId)
    try:
        playerIdInt = int(playerId)
    except ValueError:
        response.headers["gameStatus"] = "notInGame"
        #response.headers["whoWon"] = "-1"
        return {}
    
    gameId = playerDict.get(playerIdInt)
    
    if ((gameId is None) or (gameId == -1)):
        response.headers["gameStatus"] = "notInGame"
        #response.headers["whoWon"] = "-1"
        return {}
    #print ("point1")
    
    gameInfo = gameDict.get(gameId)
    
    #print ("point2")
    
    if ((gameInfo is None) or (gameInfo == -1)):
        # error?
        #print ("point3")
        response.headers["gameStatus"] = "notInGame"
        #response.headers["whoWon"] = "-1"
        return {}
    
    #print ("point4")
    
    if (int(time.time()) - gameInfo.firstPlayerLastTime >= 30 or
        int(time.time()) - gameInfo.secondPlayerLastTime >= 30):
        print ("point5")
        response.headers["gameStatus"] = "disconnected"
        #response.headers["whoWon"] = "-1"
        return {}
    
    #print ("point6")
    
    winrate = ""
    if (gameInfo.firstPlayerId == playerIdInt):
        gameInfo.firstPlayerLastTime = int(time.time())
        gameDict[gameId] = gameInfo
        winrate += str(gameInfo.firstPlayerWins)
        winrate += ":"
        winrate += str(gameInfo.secondPlayerWins)
    else:
        gameInfo.secondPlayerLastTime = int(time.time())
        gameDict[gameId] = gameInfo
        winrate += str(gameInfo.secondPlayerWins)
        winrate += ":"
        winrate += str(gameInfo.firstPlayerWins)
    
    #print ("point7")
    response.headers["winrate"] = winrate
    printPosition(gameInfo.gamePosition)
    #print(gameInfo.whoWon)
    response.headers["gamePosition"] = gameInfo.gamePosition
    #response.headers["whoWon"] = str(gameInfo.whoWon)
    response.headers["gameStatus"] = "inGame"
    #print ("point8")
    return {}


@app.get("/playerMove")
async def playerMove(playerId: str, playerMove: str, response: Response):
    try:
        playerIdInt = int(playerId)
    except ValueError:
        response.headers["moveStatus"] = "Invalid playerId"
        return {}
    
    gameId = playerDict.get(playerIdInt)
    
    if ((gameId is None) or (gameId == -1)):
        response.headers["moveStatus"] = "No finded game id for current playerId"
        return {}
    
    gameInfo = gameDict.get(gameId)
    
    if ((gameInfo is None) or (gameInfo == -1)):
        response.headers["moveStatus"] = "No finded game for current game id"
        return {}
    
    if (int(time.time()) - gameInfo.firstPlayerLastTime >= 30 or
        int(time.time()) - gameInfo.secondPlayerLastTime >= 30):
        response.headers["moveStatus"] = "disconnected"
        return {}
    
    if (gameInfo.firstPlayerId == playerIdInt):
        gameInfo.firstPlayerLastTime = int(time.time())
        gameDict[gameId] = gameInfo
    else:
        gameInfo.secondPlayerLastTime = int(time.time())
        gameDict[gameId] = gameInfo
    
    if (isValidMove(playerMove, gameInfo.gamePosition) == False):
        response.headers["moveStatus"] = "Invalid move"
        return {}
    
    if ((gameInfo.firstPlayersMove == True and playerIdInt == gameInfo.secondPlayerId) or
        (gameInfo.firstPlayersMove == False and playerIdInt == gameInfo.firstPlayerId)):
        response.headers["moveStatus"] = "Not your move"
        return {}
    
    response.headers["moveStatus"] = "OK"
    indexInGame = indexForPosition(playerMove)
    if (indexInGame < 0 or indexInGame >= 9):
        response.headers["moveStatus"] = "Internal error at calculating position"
        return {}
    
    if (gameInfo.firstPlayersMove == True):
        gameInfo.gamePosition = getNewPosition(gameInfo.gamePosition, indexInGame, 'X')
    else:
        gameInfo.gamePosition = getNewPosition(gameInfo.gamePosition, indexInGame, 'O')
    gameInfo.firstPlayersMove = (gameInfo.firstPlayersMove == False)
    
    # check on game end also TODO
    resultGame = isGameEnded(gameInfo.gamePosition)
    if (resultGame != 0): # just starting over, watch winrate for info
        gameInfo.gamePosition = "........."
    if (resultGame == 1):
        #gameInfo.whoWon = gameInfo.firstPlayerId
        gameInfo.firstPlayerWins += 1
    elif (resultGame == 2):
        #gameInfo.whoWon = gameInfo.secondPlayerId
        gameInfo.secondPlayerWins += 1
    
    gameDict[gameId] = gameInfo
    
    return {}

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='127.0.0.1')
