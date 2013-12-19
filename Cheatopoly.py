from CheatopolyClasses import *
from CheatopolyFunctions import *
from CheatopolyReadData import *

#Create basic data structure
neighborhoods = {}
board = []
communityChest = []
chances = []
currentComm = 0
currentChance = 0
players = []

# Import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'));
with ff as f:
    content = f.readlines()
CheatopolyReadData(content, board, neighborhoods,chances, communityChest)
#randomize community chest and chance cards
from random import shuffle
shuffle(chances)
shuffle(communityChest)

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
print "Please enter a number of players between 2 and 6:"
numberPlayers = choose_int(2, 6)

#Initialize players
list_of_names = ['']
for i in range(numberPlayers):
    name  = ''
    while name in list_of_names:
        name =  raw_input("Please enter a unique name for player " + str(i+1) + ": ")
    human = choose_yes_no("Is the player human [yes/no]: ")
    dic = {"yes": True, "no": False}
    players.append(Player(name, playerCash, dic[human]))
    list_of_names.append(name)

#Initialize bank
bank =  Bank(money, houses, hotels)

#The player turns are generated in a while loop
currentPlayer = 0 # initialize current player
while bank.money > 0 and len(players) > 1:
    myPlayer = players[currentPlayer]
    #Start player turn; test for teleportation with Chance card
    #Roll dice and jail check happen only when not teleporting
    if myPlayer.teleport == 0:
        raw_input("Hello, " + myPlayer.name +  "! You have $" + str(myPlayer.cash) + ". Press Enter to start turn.")
        dice = Dice() #Roll dice
        print "Dice roll for " + myPlayer.name + ": " +  str(dice[0]) + " " + str(dice[1])
        # Resolve jail status
        if myPlayer.inJail: #Check for doubles while in jail
            if dice[0] == dice[1]:
                ResetJail(myPlayer)
                print myPlayer.name + " has got a double: " + str(dice[0]) + " " +str(dice[1]) + "."
            else:
                myPlayer.timeInJail += 1
        #Else use a get ouf of jail card
        if myPlayer.inJail and max(myPlayer.jailCommCards, myPlayer.jailChanceCards) > 0:
            choose = myPlayer.UseJailCard()
            if choose == 'yes':
                if myPlayer.jailCommCards > myPlayer.jailChanceCards:
                    myPlayer.jailCommCards -= 1
                    #return community card back to the pile
                    communityChest.insert(currentComm,CommunityCard("Get out of jail, free", 0, 0, 1, 0, 0, 0))
                    currentComm = PlusOne(currentComm, len(communityChest))
                else:
                    myPlayer.jailChanceCards -= 1
                    #return chance card back to the pile
                    chances.insert(currentChance,ChanceCard("Get out of jail free", 0, 0, 1, 0, 0, 0, 0, 0))
                    currentChance = PlusOne(currentChance, len(chances))
                ResetJail(myPlayer)
                print myPlayer.name + " gets out of jail."
        if myPlayer.inJail and myPlayer.cash >= jailFine: #Else pay
            choose = myPlayer.PayJailFine(JailFine)
            if choose == 'yes':
                MoveMoney(-jailFine, myPlayer, bank)
                ResetJail(myPlayer)
                print myPlayer.name + " pays $" + str(jailFine) + " to get out of jail."
        if myPlayer.timeInJail == 3: #Else if already three turns in jail:
            MoveMoney(-jailFine, myPlayer, bank)
            ResetJail(myPlayer)
            print myPlayer.name + " pays anyway $" + str(jailFine) + " to get out of jail after three turns."
        if myPlayer.inJail: #Check if still in jail
            currentPlayer = PlusOne(currentPlayer, len(players))
            continue #end of turn
        if dice[0] == dice[1]: #Check how many doubles in a row
            myPlayer.doublesInARow += 1
            if myPlayer.doublesInARow == 3:
                myPlayer.MoveToJail(board)
                currentPlayer = PlusOne(currentPlayer, len(players))
                continue
        else:
            myPlayer.doublesInARow = 0
        #So,we are definitely not in jail. Advance to new position
        myPlayer.location = (myPlayer.location + dice[0] + dice[1]) % len(board)
        print myPlayer.name + " advances to " + str(myPlayer.location) + \
        " (" + board[myPlayer.location].name + ")."
        if myPlayer.location == 0: #Did we pass Go? +startWage/2*startWage
            MoveMoney(2*startWage, myPlayer, bank)
            print myPlayer.name + " is a lucky punk and gets $" + str(2*startWage) + "."
        elif myPlayer.location - dice[0] - dice[1] < 0:
            MoveMoney(startWage, myPlayer, bank)
            print myPlayer.name + " gets $" + str(startWage) + "."
    #reset teleport counter now
    myPlayer.teleport = 0
    # if player lands on street, rail or utility:
    if isinstance(board[myPlayer.location], (Street, Railroad, Utility)):
        if board[myPlayer.location].ownedBy == None:
            choose = myPlayer.Buy(self, board) #You can buy the place
            if choose == "yes":
                if myPlayer.cash > board[myPlayer.location].price:
                    board[myPlayer.location].newOwner(myPlayer) #assign new owner
                    MoveMoney(-board[myPlayer.location].price, myPlayer, bank)
                    print "Congratulations, " + myPlayer.name + "! You have bought: " +  str(board[myPlayer.location]) + "."
                else:
                    print "Sorry, you do not have the required funds!"
                    import random
                    a = random.randint(1, 4)
                    if a == 1:
                        print "Beggar...!"
                    myPlayer.StartAuction(players, board, money, bank) #launch auction
            else:
                myPlayer.StartAuction(players, board, money, bank) #launch auction
        elif board[myPlayer.location].ownedBy == myPlayer:
            #If you already own that place
            print "You (" + myPlayer.name + ") already own " + board[myPlayer.location].name + "."
        else:
            #Finally, you pay rent (if not mortgaged)
            rentDue = board[myPlayer.location].rent(neighborhoods,board)
            if myPlayer.doubleRent == 2:
                rentDue *= 2 #rent is doubled when sent by Chance card to a R.R.
                myPlayer.doubleRent = 1
            if not board[myPlayer.location].mortgaged:
                print board[myPlayer.location].name +  " is owned by " + board[myPlayer.location].ownedBy.name + ", you (" + myPlayer.name + ") must pay rent amounting to: " + str(rentDue) + "."
                myPlayer.cash -= rentDue
                board[myPlayer.location].ownedBy.cash += rentDue
            else:
                print board[myPlayer.location].name +  " is owned by " + board[myPlayer.location].ownedBy.name + ", but is mortgaged and you pay nothing."
    #Free Parking
    if isinstance(board[myPlayer.location], FreeParking):
        MoveTable(myPlayer,bank)
    #Go To Jail
    if isinstance(board[myPlayer.location], GoToJail):
        myPlayer.MoveToJail(board)    
    #Pay taxes: you can pay either a lump sum or a percentage of total assets.
    #Sometimes,the second option can be "None"
    if isinstance(board[myPlayer.location], Tax):
        tax1 = TaxRate(board[myPlayer.location].option1, myPlayer,board)
        tax2 = TaxRate(board[myPlayer.location].option2, myPlayer,board)
        if tax1 == None or tax2 == None:
            tax = max(tax1,tax2)
        else:
            tax = min(tax1,tax2)
        print "Well done, " + myPlayer.name + ", you pay taxes amounting to: $" + str(tax)
        MoveMoneyToTable(-tax, myPlayer, bank)
    #Community Chest
    if isinstance(board[myPlayer.location], CommunityChest):
        print "Well, " + myPlayer.name + ", you have drawn this card:"
        print communityChest[currentComm].text
        if communityChest[currentComm].goStart == 1:
            myPlayer.location = 0
            MoveMoney(startWage, myPlayer, bank)
            print "You go to Start and only receive $" + str(startWage)
        elif communityChest[currentComm].cash != 0:
            if communityChest[currentComm].cash > 0:
                MoveMoney(communityChest[currentComm].cash, myPlayer, bank)
            else:
                MoveMoneyToTable(communityChest[currentComm].cash, myPlayer, bank)
        elif communityChest[currentComm].jailcard == 1:
            myPlayer.jailCommCards += 1
            #remove card from community chest
            communityChest.pop(currentComm)
            #decrease index,to compensate for the general increase after IF
            currentComm = (currentComm + len(communityChest) - 1) % len(communityChest)
        elif communityChest[currentComm].goToJail == 1:
            myPlayer.MoveToJail(board)
        elif communityChest[currentComm].collect == 1:
            for person in players:
                if person != myPlayer:
                    person.cash -= collectFine
                    myPlayer.cash += collectFine
                    print person.name + " pays $" + str(collectFine) +" to " + myPlayer.name + "."
        elif communityChest[currentComm].repairs == 1:
            Repairs(chestRepairs[0],chestRepairs[1], myPlayer, board, bank)
        #increment community chest card index
        currentComm = PlusOne(currentComm, len(communityChest))
    #Chance cards
    if isinstance(board[myPlayer.location], Chance):
        print "Well, " + myPlayer.name + ", you have drawn this card:"
        print chances[currentChance].text
        if chances[currentChance].cash != 0:
            if chances[currentChance].cash > 0:
                MoveMoney(chances[currentChance].cash, myPlayer, bank)
            else:
                MoveMoneyToTable(chances[currentChance].cash, myPlayer, bank)
        elif chances[currentChance].jailcard == 1:
            myPlayer.jailChanceCards += 1
            #remove card from community chest
            chances.pop(currentChance)
            #decrease index,to compensate for the general increase after IF
            currentChance = (currentChance + len(chances) - 1) % len(chances)
        elif chances[currentChance].goToJail == 1:
            myPlayer.MoveToJail(board)
        elif chances[currentChance].repairs == 1:
            Repairs(chanceRepairs[0],chanceRepairs[1], myPlayer, board, bank)
        elif chances[currentChance].reading == 1:
            #find Reading location
            for item in board:
                if item.name == "Reading Railroad":
                    destination = item.location #what if not found?
                    break
            if destination < myPlayer.location:
                print "You pass Go and collect $" + str(startWage) + "."
                MoveMoney(startWage, myPlayer, bank)
            myPlayer.location = destination
            print "You move to Reading Railroad, at location " + str(destination) + "."
            myPlayer.teleport = 1
            continue
        elif chances[currentChance].movement != 0:
            myPlayer.location = (myPlayer.location + len(board) + chances[currentChance].movement) % len(board)
            myPlayer.teleport = 1
            continue
        elif chances[currentChance].rail == 1:
            while not isinstance(board[myPlayer.location], Railroad):
                #FIXME: infinite loop if no rail!
                myPlayer.location = PlusOne(myPlayer.location, len(board))
            print "You have moved to the next railroad: " + board[myPlayer.location].name + ", at pos " + str(myPlayer.location) + "."
            myPlayer.doubleRent = 2
            myPlayer.teleport = 1
            continue
        elif chances[currentChance].goTo != 0:
            if chances[currentChance].goTo == "1":
                myPlayer.location = 0
                MoveMoney(startWage, myPlayer, bank)
                print "You move to Go and only get $" + str(startWage) + "."
            else:
                for item in board:
                    if item.name == chances[currentChance].goTo:
                        #you get $200 if you pass Go.
                        if myPlayer.location > item.location:
                            MoveMoney(startWage, myPlayer, bank)
                            print "You get $" + str(startWage)
                        myPlayer.location = item.location
                        break
                print "You move to " + board[myPlayer.location].name + " at pos " + str(myPlayer.location) + "."
                myPlayer.teleport = 1
                continue
        #increment chance card index
        currentChance = PlusOne(currentChance, len(chances))
    #Upgrade/downgrade houses/hotels, mortgage properties
    print ""
    print myPlayer.name + ", you have the following properties:"
    for item in board:
        if item.ownedBy == myPlayer:
            print item
    choose = ''
    while choose not in ["u", "d", "m","d", "e", "n"]:
        choose = myPlayer.ChooseAction()
        if choose == "u":
            myPlayer.Upgrade(neighborhoods, board, bank) #upgrade
        elif choose == "d":
            myPlayer.Downgrade(board, bank) #downgrade
        elif choose == "m":
            myPlayer.Mortgage(board, bank) #mortgage
        elif choose == "e":
            myPlayer.Demortgage(board, bank) #demortgage
        elif choose == "n": #exit loop
            break
        choose = ""
    
    #if player has no money and still tries to buy, then auction
    #Negotiate with other players
    
    #Update display
    
    #save/load game from disk
    
    #stylecheck
    
    #Turn end: check if positive balance. if not, remove from game
    #should consistently check for player funds

    #Print current financial status
    print ""
    print "***"
    for player in players:
        print player.name + " has $" +str(player.cash)
    print "The bank has got $" + str(bank.money) + " left. There are "+ str(bank.houses) + " houses and " + str(bank.hotels) + " hotels available."
    print "There are $" + str(bank.cardPayments) + " left on the table."
    print "***"
    print ""
    #currentPlayer += 1
    currentPlayer = PlusOne(currentPlayer, len(players))
    
    