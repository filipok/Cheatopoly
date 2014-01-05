import os
from CheatopolyClasses import *

def CheatopolyReadData(content, game):
    #Process data.txt
    for i in range(len(content)):
        line = content[i].rstrip().split("\t")
        if line[0] == "street":
            game.board.append(Street(line[12], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8]), int(line[9]), int(line[10]), line[11]))
            if line[11] in game.neighborhoods:
                game.neighborhoods[line[11]].append(game.board[-1])
            else:
                game.neighborhoods[line[11]] = [game.board[-1]]
        elif line[0] == "start":
            game.board.append(Start())
        elif line[0] == "chestL":
            game.board.append(CommunityChest())
        elif line[0] == "tax":
            game.board.append(Tax(line[3], line[1], line[2], line[4]))
        elif line[0] == "rail":
            game.board.append(Railroad(line[7], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])))
        elif line[0] == "chanceL":
            game.board.append(Chance())
        elif line[0] == "jail":
            game.board.append(Jail())
        elif line[0] == "utility":
            game.board.append(Utility(line[3], int(line[1]), int(line[2])))
        elif line[0] == "park":
            game.board.append(FreeParking())
        elif line[0] == "gotojail":
            game.board.append(GoToJail())
        elif line[0] == "chest":
            game.communityChest.append(CommunityCard(line[7], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])))
        elif line[0] == "chance":
            game.chances.append(ChanceCard(line[9], int(line[1]), int(line [2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), line[8]))
        elif line[0] == "const":
            if line[1] == "playerCash":
                game.playerCash = int(line[2])
            elif line[1] == "money":
                game.money = int(line[2])
            elif line[1] == "houses":
                game.houses =  int(line[2])
            elif line[1] == "hotels":
                game.hotels = int(line[2])
            elif line[1] == "startWage":
                game.startWage = int(line[2])
            elif line[1] == "jailFine":
                game.jailFine = int(line[2])
            elif line[1] == "collectFine":
                game.collectFine = int(line[2])
            elif line[1] == "chanceRepairsMin":
                game.chanceRepairs = [int(line[2])]
            elif line[1] == "chanceRepairsMax":
                game.chanceRepairs.append(int(line[2]))
            elif line[1] == "chestRepairsMin":
                game.chestRepairs = [int(line[2])]
            elif line[1] == "chestRepairsMax":
                game.chestRepairs.append(int(line[2]))
        if line[0] in ["street", "start", "chestL", "tax", "rail", "chanceL", "jail", "utility", "park", "gotojail"]:
            game.board[i].location = i

        #test: output  board, community cards and chance cards to output.txt
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, 'output.txt'), "w")
        for i in range(len(game.board)):
            f.write(str(game.board[i]) + "\n")
        for i in range(len(game.communityChest)):
            f.write(str(game.communityChest[i]) + "\n")
        for i in range(len(game.chances)):
            f.write(str(game.chances[i]) + "\n")
        f.close()