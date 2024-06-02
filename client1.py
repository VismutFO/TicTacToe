# -*- coding: utf-8 -*-
import http.client
import time
import sys, select

def printPosition(gamePosition: str):
    print(gamePosition[0:3])
    print(gamePosition[3:6])
    print(gamePosition[6:9])

print("Hello! Type \"start\" to connect to server and start a game.")
print("If you need instruction before, type \"help\".")

while (True):
    temp = input("Type your command: ")
    if (temp == "help"):
        print("You will be seeing a map in console, type you moves as x y, where 1 <= x <= 3, 1 <= y <= 3.")
        print("Type your moves in 30s after getting updated map, or you will be considered disconnected.")
        continue
    if (temp == "start"):
        break
    print("Invalid command, try again")


connection = http.client.HTTPConnection("localhost", 8000) #TODO

connection.request("GET", "/initNewPlayer")
response = connection.getresponse()
response.read()
response.close()

playerId = response.getheader("playerId")
if (response.status != 200):
    print("Couldn't connect, try again later, please")
    print("Status: {} and reason: {}".format(response.status, response.reason))
    connection.close()
    exit(0)
#
while (True):
    connection.request("GET", "/getInformation?playerId="+str(playerId));
    response = connection.getresponse()
    response.read()
    response.close()
    if (response.status != 200):
        print("Server error, sorry")
        break    
    
    if (response.getheader("gameStatus") == "notInGame"):
        print("Waiting for start...")
        time.sleep(5)
        continue
    
    print("Current winrate: " + response.getheader("winrate"))
    #elif (response.getheader("gameStatus") == "waitingOtherPlayer"):
        #print("Waiting for other player's move...")
        #time.sleep(5)
        #continue
    printPosition(response.getheader("gamePosition"));
    
    while(True):
        i = input("Type your move: ")
        i = i.replace(' ', '_')
        # i, o, e = select.select([sys.stdin], [], [], 25)
        if (i is None):
            print("You wasted your time, disconnecting from server...")
            connection.close()
            exit(0)
        connection.request("GET", "/playerMove?playerId=" + str(playerId) + "&playerMove=" + i)
        response = connection.getresponse()
        if (response.status == 200):
            result = response.getheader("moveStatus")
            response.read()
            response.close()
            if (result == "OK"):
                break
            elif (result == "Invalid move"):
                print(result)
                print("Try again, please")
                continue
            elif (result == "Not your move"):
                print(result)
                print("Wait and try again, please")
                time.sleep(5)
                continue
            else:
                print(result)
                print("You got disconnected, relaunch client, please")
                connection.close()
                exit(0)
        else:
            print("Server error, sorry")
connection.close()
