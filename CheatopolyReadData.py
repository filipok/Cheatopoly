def CheatopolyReadData(content, board, neighborhoods,chances, communityChest):
    from CheatopolyClasses import *
    #Process data.txt
    for i in range(len(content)):
        line = content[i].rstrip().split("\t")
        if line[0] == "street":
            board.append(Street(line[12], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8]), int(line[9]), int(line[10]), line[11]))
            if line[11] in neighborhoods:
                neighborhoods[line[11]].append(board[-1])
            else:
                neighborhoods[line[11]] = [board[-1]]
        elif line[0] == "start":
            board.append(Start())
        elif line[0] == "chestL":
            board.append(CommunityChest())
        elif line[0] == "tax":
            board.append(Tax(line[3], line[1], line[2], line[4]))
        elif line[0] == "rail":
            board.append(Railroad(line[7], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])))
        elif line[0] == "chanceL":
            board.append(Chance())
        elif line[0] == "jail":
            board.append(Jail())
        elif line[0] == "utility":
            board.append(Utility(line[3], int(line[1]), int(line[2])))
        elif line[0] == "park":
            board.append(FreeParking())
        elif line[0] == "gotojail":
            board.append(GoToJail())
        elif line[0] == "chest":
            communityChest.append(CommunityCard(line[7], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])))
        elif line[0] == "chance":
            chances.append(ChanceCard(line[9], int(line[1]), int(line [2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), line[8]))
        if line[0] in ["street", "start", "chestL", "tax", "rail", "chanceL", "jail", "utility", "park", "gotojail"]:
            board[i].location = i

        #test: output  board, community cards and chance cards to output.txt
        import os
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, 'output.txt'), "w")
        for i in range(len(board)):
            f.write(str(board[i]) + "\n")
        for i in range(len(communityChest)):
            f.write(str(communityChest[i]) + "\n")
        for i in range(len(chances)):
            f.write(str(chances[i]) + "\n")
        f.close()