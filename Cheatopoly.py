from CheatopolyClasses import *
from CheatopolyFunctions import *

# Import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'));
with ff as f:
    content = f.readlines()

#Create basic data structure
neighborhoods = {}
board = []
communityChest = []
chances = []
currentComm = 0
currentChance = 0
players = []

#Process data.txt
for i in range(len(content)):
    line = content[i].rstrip().split("\t")
    if line[0] == "street":
        board.append(Street(line[12], line[0], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8]), int(line[9]), int(line[10]), line[11]))
        if line[11] in neighborhoods:
            neighborhoods[line[11]].append(board[-1])
        else:
            neighborhoods[line[11]] = [board[-1]]
    elif line[0] == "start":
        board.append(Start())
        board[i].placeType = line[0]
    elif line[0] == "chestL":
        board.append(CommunityChest())
        board[i].placeType = line[0]
    elif line[0] == "tax":
        board.append(Tax(line[3], line[0], line[1], line[2], line[4]))
    elif line[0] == "rail":
        board.append(Railroad(line[7], line[0], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])))
    elif line[0] == "chanceL":
        board.append(Chance())
        board[i].placeType = line[0]
    elif line[0] == "jail":
        board.append(Jail())
        board[i].placeType = line[0]
    elif line[0] == "utility":
        board.append(Utility(line[3], line[0], int(line[1]), int(line[2])))
    elif line[0] == "park":
        board.append(FreeParking())
        board[i].placeType = line[0]
    elif line[0] == "gotojail":
        board.append(GoToJail())
        board[i].placeType = line[0]
    elif line[0] == "chest":
        communityChest.append(CommunityCard(line[7], line[0], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])))
    elif line[0] == "chance":
        chances.append(ChanceCard(line[9], line[0], int(line[1]), int(line [2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), line[8]))
    if line[0] in ["street", "start", "chestL", "tax", "rail", "chanceL", "jail", "utility", "park", "gotojail"]:
        board[i].location = i

#randomize community chest and chance cards
from random import shuffle
shuffle(chances)
shuffle(communityChest)

#test: output  board, community cards and chance cards to output.txt
f = open(os.path.join(__location__, 'output.txt'), "w")
for i in range(len(board)):
    f.write(str(board[i]) + "\n")
for i in range(len(communityChest)):
    f.write(str(communityChest[i]) + "\n")
for i in range(len(chances)):
    f.write(str(chances[i]) + "\n")
f.close()



#Cheatopoly Game creation
print "************************"
print "WELCOME TO CHEATOPOLY!!!"
print "You can play Cheatopoly in up to 6 players."
print "************************"

#Hard-coded constants
playerCash = 1500 #initial amount received by each player
money = 15140 #although some rules say infinite bank money: https://en.wikibooks.org/wiki/Monopoly/Official_Rules
houses = 32 # https://en.wikibooks.org/wiki/Monopoly/Official_Rules
hotels = 12 # https://en.wikibooks.org/wiki/Monopoly/Official_Rules
startWage = 200 # what you get when you pass Go
jailFine = 50 # cost to get out of jail
collectFine = 50 #amount to collect from each player with the Collect card
chanceRepairs = [25, 100]
chestRepairs = [45,115]

#Get number of players
numberPlayers = 0
while numberPlayers < 2 or numberPlayers > 6:
    try:
        numberPlayers = int(raw_input("Please enter a number of players between 2 and 6: "))
    except ValueError:
        print "Oops!  That was no valid number.  Try again..."

#Initialize players
for i in range(numberPlayers):
    sameName = True
    while sameName:
        sameName = False
        name =  raw_input("Please enter a unique name for player " + str(i+1) + ": ")
        if len(name) == 0:
            sameName = True
        for person in players:
            if person.name == name:
                sameName = True
    human = ''
    while human not in ["yes", "no"]:
        human = raw_input("Is the player human [yes/no]: ").lower()
    if human == "yes":
        human = True
    else:
        human = False
    players.append(Player(name, playerCash, human))

#Initialize bank
bank =  Bank(money, houses, hotels)


#The player turns are generated in a while loop
currentPlayer = 0 # initialize current player
while bank.money > 0 and len(players) > 1:
    #Start player turn; test for teleportation with Chance card
    #Roll dice and jail check happen only when not teleporting
    if players[currentPlayer].teleport == 0:
        raw_input("Hello, " + players[currentPlayer].name +  "! You have $" + str(players[currentPlayer].cash) + ". Press Enter to start turn.")
        #Roll dice
        dice = Dice()
        print "Dice roll for " + players[currentPlayer].name + ": " +  str(dice[0]) + " " + str(dice[1])
        # Resolve jail status
        #Check for doubles while in jail
        if players[currentPlayer].inJail:
            if dice[0] == dice[1]:
                ResetJail(players[currentPlayer])
                print players[currentPlayer].name + " has got a double: " + str(dice[0]) + " " +str(dice[1]) + "."
            else:
                players[currentPlayer].timeInJail += 1
        #Else use a get ouf of jail card
        if players[currentPlayer].inJail and (players[currentPlayer].jailCommCards > 0 or players[currentPlayer].jailChanceCards > 0):
            choose = ''
            while choose not in ["yes", "no"]:
                choose = raw_input("Do you want to use a 'Get Out Of Jail' card? [yes/no] ").lower() #human
            if choose == 'yes':
                if players[currentPlayer].jailCommCards > players[currentPlayer].jailChanceCards:
                    players[currentPlayer].jailCommCards -= 1
                    #return community card back to the pile
                    communityChest.insert(currentComm,CommunityCard("Get out of jail, free", "chest", 0, 0, 1, 0, 0, 0))
                    currentComm = (currentComm + 1) % len(communityChest)
                else:
                    players[currentPlayer].jailChanceCards -= 1
                    #return chance card back to the pile
                    chances.insert(currentChance,ChanceCard("Get out of jail free", "chance", 0, 0, 1, 0, 0, 0, 0, 0))
                    currentChance = (currentChance + 1) % len(chances)
                ResetJail(players[currentPlayer])
                print players[currentPlayer].name + " gets out of jail."
        #Else pay
        if players[currentPlayer].inJail and players[currentPlayer].cash >= jailFine:
            choose = ''
            while choose not in ["yes", "no"]:
                choose = raw_input("Do you want to pay $" + str(jailFine) + " to get out of jail[yes/no] ").lower() #human
            if choose == 'yes':
                MoveMoney(-jailFine, players[currentPlayer], bank)
                ResetJail(players[currentPlayer])
                print players[currentPlayer].name + " pays $" + str(jailFine) + " to get out of jail."
        #Else if already three turns in jail:
        if players[currentPlayer].timeInJail == 3:
            MoveMoney(-jailFine, players[currentPlayer], bank)
            ResetJail(players[currentPlayer])
            print players[currentPlayer].name + " pays anyway $" + str(jailFine) + " to get out of jail after three turns."
        #Check if still in jail
        if players[currentPlayer].inJail:
            currentPlayer = (currentPlayer + 1) % len(players)
            continue #end of turn
        #Check how many doubles in a row
        if dice[0] == dice[1]:
            players[currentPlayer].doublesInARow += 1
            if players[currentPlayer].doublesInARow == 3:
                MoveToJail(players[currentPlayer],board)
                currentPlayer = (currentPlayer + 1) % len(players)
                continue
        else:
            players[currentPlayer].doublesInARow = 0
        #So,we are definitely not in jail. Advance to new position
        players[currentPlayer].location = (players[currentPlayer].location + dice[0] + dice[1])% len(board)
        print players[currentPlayer].name + " advances to " + str(players[currentPlayer].location) + " (" + board[players[currentPlayer].location].name + ")."
        #Did we pass Go? +startWage/2*startWage
        if players[currentPlayer].location == 0:
            MoveMoney(2*startWage, players[currentPlayer], bank)
            print players[currentPlayer].name + " is a lucky punk and gets $" + str(2*startWage) + "."
        elif players[currentPlayer].location - dice[0] - dice[1] < 0:
            MoveMoney(startWage, players[currentPlayer], bank)
            print players[currentPlayer].name + " gets $" + str(startWage) + "."
    #reset teleport counter now
    players[currentPlayer].teleport = 0
    # if player lands on street, rail or utility:
    if board[players[currentPlayer].location].placeType in ["street", "rail", "utility"]:
        if board[players[currentPlayer].location].ownedBy == None:
            #You can buy the place
            choose = ''
            while choose not in ["yes", "no"]:
                choose = raw_input("Hey, " + players[currentPlayer].name + "! " + board[players[currentPlayer].location].name + " is currently available and you have $" + str(players[currentPlayer].cash) + ". Do you want to buy it? Summary: " + str(board[players[currentPlayer].location]) + " [yes/no] ").lower() #human
            if choose == "yes":
                if players[currentPlayer].cash > board[players[currentPlayer].location].price:
                    board[players[currentPlayer].location].newOwner(players[currentPlayer]) #assign new owner
                    MoveMoney(-board[players[currentPlayer].location].price, players[currentPlayer], bank)
                    print "Congratulations, " + players[currentPlayer].name + " has bought: " +  str(board[players[currentPlayer].location]) + "."
                else:
                    print "Sorry, you do not have the required funds!"
                    import random
                    a = random.randint(1, 4)
                    if a == 1:
                        print "Beggar...!"
            else:
                #auction!
                #set auction flag
                print "Starting auction..."
                for person in players:
                    person.inAuction = True
                players[currentPlayer].inAuction = False
                auctionRunning = True
                auctionPrice = 0 # the auction starts from zero
                bestCandidate = None
                while auctionRunning:
                    stillInPlay = 0
                    for person in players:
                        if person.inAuction and person != bestCandidate:
                            print "Hello,"+ person.name + "! " + players[currentPlayer].name + " did not buy " + board[players[currentPlayer].location].name + ". Do you want to buy it instead? Last price is " + str(auctionPrice) + "."
                            choose = -1
                            while choose == -1:
                                try:
                                    choose = int(raw_input("Please enter your price: ")) #human
                                except ValueError:
                                    print "Oops!  That was no valid number.  Try again..."
                            if choose > auctionPrice:
                                bestCandidate = person
                                auctionPrice = choose
                                stillInPlay += 1
                            else:
                                person.inAuction = False
                    if stillInPlay == 0:
                        auctionRunning = False
                if bestCandidate == None:
                    print "Sadly, nobody wants that place."
                else:
                    print "Congratulations, " + bestCandidate.name + "! You have bought " + board[players[currentPlayer].location].name + " for $" + str(auctionPrice) + "."
                    MoveMoney(-auctionPrice, bestCandidate, bank)
                    board[players[currentPlayer].location].newOwner(bestCandidate)#assign new owner
        elif board[players[currentPlayer].location].ownedBy == players[currentPlayer]:
            #If you already own that place
            print "You (" + players[currentPlayer].name + ") own " + board[players[currentPlayer].location].name + "!"
        else:
            #Finally, you pay rent (if not mortgaged)
            rentDue = board[players[currentPlayer].location].rent(neighborhoods,board)
            if players[currentPlayer].doubleRent == 2:
                rentDue *= 2 #rent is doubled when sent by Chance card to a R.R.
                players[currentPlayer].doubleRent = 1
            if board[players[currentPlayer].location].mortgaged == False:
                print board[players[currentPlayer].location].name +  " is owned by " + board[players[currentPlayer].location].ownedBy.name + ", you (" + players[currentPlayer].name + ") must pay rent amounting to: " + str(rentDue) + "."
                players[currentPlayer].cash -= rentDue
                board[players[currentPlayer].location].ownedBy.cash += rentDue
            else:
                print board[players[currentPlayer].location].name +  " is owned by " + board[players[currentPlayer].location].ownedBy.name + ", but is mortgaged and you pay nothing."
    #Free Parking
    if board[players[currentPlayer].location].placeType == "park":
        MoveTable(players[currentPlayer],bank)
    #Go To Jail
    if board[players[currentPlayer].location].placeType == "gotojail":
        MoveToJail(players[currentPlayer], board)    
    #Pay taxes: you can pay either a lump sum or a percentage of total assets.
    #Sometimes,the second option can be "None"
    if board[players[currentPlayer].location].placeType == "tax":
        tax1 = TaxRate(board[players[currentPlayer].location].option1, players[currentPlayer],board)
        tax2 = TaxRate(board[players[currentPlayer].location].option2, players[currentPlayer],board)
        if tax1 == None or tax2 == None:
            tax = max(tax1,tax2)
        else:
            tax = min(tax1,tax2)
        print "Well done, " + players[currentPlayer].name + ", you pay taxes amounting to: $" + str(tax)
        MoveMoneyToTable(-tax, players[currentPlayer], bank)
    #Community Chest
    if board[players[currentPlayer].location].placeType == "chestL":
        print "Well, " + players[currentPlayer].name + ", you have drawn this card:"
        print communityChest[currentComm].text
        if communityChest[currentComm].goStart == 1:
            players[currentPlayer].location = 0
            MoveMoney(startWage, players[currentPlayer], bank)
            print "You go to Start and only receive $" + str(startWage)
        elif communityChest[currentComm].cash != 0:
            if communityChest[currentComm].cash > 0:
                MoveMoney(communityChest[currentComm].cash, players[currentPlayer], bank)
            else:
                MoveMoneyToTable(communityChest[currentComm].cash, players[currentPlayer], bank)
        elif communityChest[currentComm].jailcard == 1:
            players[currentPlayer].jailCommCards += 1
            #remove card from community chest
            communityChest.pop(currentComm)
            #decrease index,to compensate for the general increase after IF
            currentComm = (currentComm + len(communityChest) - 1) % len(communityChest)
        elif communityChest[currentComm].goToJail == 1:
            MoveToJail(players[currentPlayer],board)
        elif communityChest[currentComm].collect == 1:
            for person in players:
                if person != players[currentPlayer]:
                    person.cash -= collectFine
                    players[currentPlayer].cash += collectFine
                    print person.name + " pays $" + str(collectFine) +" to " + players[currentPlayer].name + "."
        elif communityChest[currentComm].repairs == 1:
            Repairs(chestRepairs[0],chestRepairs[1], players[currentPlayer], board, bank)
        #increment community chest card index
        currentComm = (currentComm + 1) % len(communityChest)
    #Chance cards
    if board[players[currentPlayer].location].placeType == "chanceL":
        print "Well, " + players[currentPlayer].name + ", you have drawn this card:"
        print chances[currentChance].text
        if chances[currentChance].cash != 0:
            if chances[currentChance].cash > 0:
                MoveMoney(chances[currentChance].cash, players[currentPlayer], bank)
            else:
                MoveMoneyToTable(chances[currentChance].cash, players[currentPlayer], bank)
        elif chances[currentChance].jailcard == 1:
            players[currentPlayer].jailChanceCards += 1
            #remove card from community chest
            chances.pop(currentChance)
            #decrease index,to compensate for the general increase after IF
            currentChance = (currentChance + len(chances) - 1) % len(chances)
        elif chances[currentChance].goToJail == 1:
            MoveToJail(players[currentPlayer],board)
        elif chances[currentChance].repairs == 1:
            Repairs(chanceRepairs[0],chanceRepairs[1], players[currentPlayer], board, bank)
        elif chances[currentChance].reading == 1:
            #find Reading location
            for item in board:
                if item.name == "Reading Railroad":
                    destination = item.location
                    break
            if destination < players[currentPlayer].location:
                print "You pass Go and collect $" + str(startWage) + "."
                MoveMoney(startWage, players[currentPlayer], bank)
            players[currentPlayer].location = destination
            print "You move to Reading Railroad, at location " + str(destination) + "."
            players[currentPlayer].teleport = 1
            continue
        elif chances[currentChance].movement != 0:
            players[currentPlayer].location = (players[currentPlayer].location + len(board) + chances[currentChance].movement) % len(board)
            players[currentPlayer].teleport = 1
            continue
        elif chances[currentChance].rail == 1:
            while board[players[currentPlayer].location].placeType != "rail":
                #FIXME: infinite loop if no rail!
                players[currentPlayer].location = (players[currentPlayer].location + 1) % len(board)
            print "You have moved to the next railroad: " + board[players[currentPlayer].location].name + ", at pos " + str(players[currentPlayer].location) + "."
            players[currentPlayer].doubleRent = 2
            players[currentPlayer].teleport = 1
            continue
        elif chances[currentChance].goTo != 0:
            if chances[currentChance].goTo == "1":
                players[currentPlayer].location = 0
                MoveMoney(startWage, players[currentPlayer], bank)
                print "You move to Go and only get $" + str(startWage) + "."
            else:
                for item in board:
                    if item.name == chances[currentChance].goTo:
                        #you get $200 if you pass Go.
                        if players[currentPlayer].location > item.location:
                            MoveMoney(startWage, players[currentPlayer], bank)
                            print "You get $" + str(startWage)
                        players[currentPlayer].location = item.location
                        break
                print "You move to " + board[players[currentPlayer].location].name + " at pos " + str(players[currentPlayer].location) + "."
                players[currentPlayer].teleport = 1
                continue
        #increment chance card index
        currentChance = (currentChance + 1) % len(chances)
    #Upgrade/downgrade houses/hotels, mortgage properties
    print ""
    print players[currentPlayer].name + ", you have the following properties:"
    for item in board:
        if item.ownedBy == players[currentPlayer]:
            if item.placeType == "street":
                print item.name + ", " + item.neighborhood +  ": " + str(item.houses) + " houses " + str(item.hotels) + " hotels."
            else:
                print item.name + ": " + item.placeType + "."
    choose = ''
    while choose not in ["u", "d", "m","d", "e", "n"]:
        choose = raw_input("Do you want to [u]pgrade/[d]owngrade/[m]ortgage/d[e]mortgage/do [n]othing? ").lower() #human
        if choose == "u":
            #upgrade
            #first flag the upgradeable locations
            for neighborhood in neighborhoods.values():
                minUpgrade = 5
                for street in neighborhood:
                    #inefficient...
                    if street.ownedBy != players[currentPlayer]  or street.mortgaged:
                        #restore to 5
                        for street in neighborhood:
                            street.minUpgrade = 5
                        minUpgrade = 5
                        break
                    else:
                        if street.hotels == 0:
                            minUpgrade = min(minUpgrade, street.houses)
                for street in neighborhood:
                    if street.ownedBy == players[currentPlayer]:
                        street.minUpgrade = minUpgrade
            print "Hey , " + players[currentPlayer].name + "! These are the locations you can upgrade now:"
            for item in board: #this loop should become a function
                if isinstance(item, Street) and item.ownedBy == players[currentPlayer] and item.minUpgrade == item.houses and item.hotels == 0:
                    print item.name + "(" + str(item.location) +")" + ", " + item.neighborhood +  ": " + str(item.houses) + " houses " + str(item.hotels) + " hotels. House price: " + str(item.houseCost) + ". Hotel price: " + str(item.hotelCost) + "."

            choose = ""
            while choose == "":
                try:
                    choose = int(raw_input("Enter code of property to upgrade: ")) #human
                except ValueError:
                    print "Oops!  That was no valid number.  Try again..."
            #or set a canUpgrade flag?
            if  1 <= choose <= len(board)-1 and isinstance(board[choose], Street) and board[choose].ownedBy == players[currentPlayer] and board[choose].minUpgrade == board[choose].houses:
                if board[choose].houses < 4:
                    if board[choose].houseCost <= players[currentPlayer].cash:
                        board[choose].houses += 1
                        MoveMoney(-board[choose].houseCost, players[currentPlayer], bank)
                        print "You have successfully upgraded " + board[choose].name + "."
                    else:
                        print "Sorry,  not enough cash."
                else:
                    if board[choose].hotelCost <= players[currentPlayer].cash:
                        board[choose].hotels = 1
                        MoveMoney(-board[choose].hotelCost, players[currentPlayer], bank)
                        print "You have successfully upgraded " + board[choose].name + "."
                    else:
                        print "Sorry,  not enough cash."
                
            #restore to 5
            for item in board:
                if item.placeType == "street":
                    item.minUpgrade = 5
            choose = "" 
        elif choose == "d":
            #downgrade
            print "List of properties that you can downgrade:"
            for item in board: #this loop should become a function
                if isinstance(item, Street)and item.ownedBy == players[currentPlayer] and item.houses > 0:
                    print item.name + "(" + str(item.location) +")" + ", " + item.neighborhood +  ": " + str(item.houses) + " houses " + str(item.hotels) + " hotels. House return price: " + str(item.houseCost/2) + ". Hotel return price: " + str(item.hotelCost/2) + "."
            choose = ""
            while choose == "":
                try:
                    choose = int(raw_input("Enter code of property to downgrade: ")) #human
                except ValueError:
                    print "Oops!  That was no valid number.  Try again..."        
            if 1 <= choose <= len(board)-1 and \
            isinstance(board[choose],Street) and \
            board[choose].ownedBy == players[currentPlayer] and \
            board[choose].houses > 0:
                if board[choose].hotels == 1:
                    board[choose].hotels = 0
                    MoveMoney(board[choose].hotelCost/2, players[currentPlayer], bank)
                else:
                    board[choose].houses -= 1
                    MoveMoney(board[choose].houseCost/2, players[currentPlayer], bank)
                print "You have successfully downgraded " + board[choose].name + ": currently " + str(board[choose].houses) + " houses and " + str(board[choose].hotels) + " hotels."
            choose = ""
            pass
        elif choose == "m":
            #mortgage
            print "List of properties that you can mortgage:"
            for item in board: #this loop should become a function
                if item.ownedBy == players[currentPlayer] and item.mortgaged == False and item.houses == 0:
                    if item.placeType == "street":
                        print item.name + "(" + str(item.location) +")" + ", " + item.neighborhood +  ": " + str(item.houses) + " houses " + str(item.hotels) + " hotels. Mortgage price: " + str(item.mortgage) + "."
                    else:
                        print item.name + "(" + str(item.location) +")" + ": " + item.placeType + ". Mortgage price: " + str(item.mortgage) + "."
                    
            choose = int(raw_input("Enter code of property to mortgage: ")) #human
            if 1 <= choose <= len(board)-1 and \
            board[choose].placeType in ["street","rail","utility"] and \
            board[choose].ownedBy == players[currentPlayer] and \
            board[choose].mortgaged == False and board[choose].houses == 0:
                MoveMoney(board[choose].mortgage, players[currentPlayer], bank)
                board[choose].mortgaged = True
                print "You have successfully mortgaged " + board[choose].name + "."
            choose = ""
        elif choose == "e":
            #demortgage
            print "List of properties that you can demortgage:"
            for item in board:
                if item.ownedBy == players[currentPlayer] and item.mortgaged == True:
                    if item.placeType == "street":
                        print item.name + "(" + str(item.location) +")" + ", " + item.neighborhood +  ": " + str(item.houses) + " houses " + str(item.hotels) + " hotels. Demortgage cost (mortgage +10%): " + str(int(item.mortgage * 1.1)) + "."
                    else:
                        print item.name + "(" + str(item.location) +")" + ": " + item.placeType + ". Demortgage cost (mortgage +10%): " + str(int(item.mortgage*1.1)) + "."
                    
            choose = int(raw_input("Enter code of property to demortgage: ")) #human
            if 1 <= choose <= len(board)-1 and \
            board[choose].placeType in ["street","rail","utility"] and \
            board[choose].ownedBy == players[currentPlayer] and \
            board[choose].mortgaged == True and \
            players[currentPlayer].cash >= int(board[choose].mortgage * 1.1):
                MoveMoney(-int(board[choose].mortgage * 1.1), players[currentPlayer], bank)
                board[choose].mortgaged = False
                print "You have successfully demortgaged " + board[choose].name + "."
            choose = ""
        elif choose == "n":
            break
    

    #Return hotels and houses to the bank for half their purchase price
    #? Whenever a mortgaged property changes hands between players, either through a trade, sale or by bankruptcy, the new owner must immediately pay 10% interest on the mortgage and at their option may pay the principal or hold the property. If the player holds the property and later wishes to lift the mortgage they must pay the 10% interest again as well as the principal.
    #?[nope]If a property is mortgaged, a sale of this property can be forced by another player by offering the bank a some more than the mortgaged price. Thereby forcing the person mortgaging the property to buy it back at that time or relinquish the property to the bank which may then be purchased for sale for offered price.
    #?[nope]If more players decide to build more houses at the same time than there are houses in the bank, the houses are auctioned off one at a time to the highest bidder.?
    #upgrade if in jail?
    
    #Negotiate with other players
    #Turn end: check if positive balance. if not, remove from game
    #Update display
    #stylecheck
    #turn 'choose' into a player method
    #placeType? check for class?
    #what if "choose" not an int
    #should consistently check for player funds


    
    #Print current financial status
    print ""
    print "***"
    for player in players:
        print player.name + " has $" +str(player.cash)
    print "The bank has got $" + str(bank.money) + " left."
    print "There are $" + str(bank.cardPayments) + " left on the table."
    print "***"
    print ""
    #currentPlayer += 1
    currentPlayer = (currentPlayer + 1) % len(players)
    
    