from CheatopolyClasses import *
from CheatopolyFunctions import *
from CheatopolyReadData import *

#Create basic data structure
thisGame = Game()

board = []
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
CheatopolyReadData(content, board, chances, thisGame)
#randomize community chest and chance cards
from random import shuffle
shuffle(chances)
shuffle(thisGame.communityChest)

#Cheatopoly Game creation
print "************************"
print "WELCOME TO CHEATOPOLY!!!"
print "You can play Cheatopoly in up to 6 players."
print "************************"

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
    if human == "yes":
        players.append(Player(name, thisGame.playerCash, True))
    else:
        players.append(Cheatoid(name, thisGame.playerCash,False))
    list_of_names.append(name)

#Initialize bank
bank =  Bank(thisGame.money, thisGame.houses, thisGame.hotels)

#The player turns are generated in a while loop
currentPlayer = 0 # initialize current player
while bank.money > 0 and len(players) > 1:
    myPlayer = players[currentPlayer]
    #Start player turn; test for teleportation with Chance card
    #Roll dice and jail check happen only when not teleporting
    if myPlayer.teleport == 0:
        if not isinstance(myPlayer, Cheatoid):
            raw_input("Hello, " + myPlayer.name +  "! You have $" + str(myPlayer.cash) + ". Press Enter to start turn.")
        dice = Dice() #Roll dice
        print "Dice roll for " + myPlayer.name + ": " +  str(dice[0]) + " " + str(dice[1])
        # Resolve jail status
        if myPlayer.inJail: #Check for doubles while in jail
            if dice[0] == dice[1]:
                myPlayer.ResetJail()
                print myPlayer.name + " has got a double: " + str(dice[0]) + " " +str(dice[1]) + "."
            else:
                myPlayer.timeInJail += 1
        #Else use a get ouf of jail card
        if myPlayer.inJail and max(myPlayer.jailCommCards, myPlayer.jailChanceCards) > 0:
            choose = myPlayer.UseJailCard(board, players, bank)
            if choose == 'yes':
                if myPlayer.jailCommCards > myPlayer.jailChanceCards:
                    myPlayer.jailCommCards -= 1
                    #return community card back to the pile
                    thisGame.communityChest.insert(currentComm,CommunityCard("Get out of jail, free", 0, 0, 1, 0, 0, 0))
                    currentComm = PlusOne(currentComm, len(thisGame.communityChest))
                else:
                    myPlayer.jailChanceCards -= 1
                    #return chance card back to the pile
                    chances.insert(currentChance,ChanceCard("Get out of jail free", 0, 0, 1, 0, 0, 0, 0, 0))
                    currentChance = PlusOne(currentChance, len(chances))
                myPlayer.ResetJail()
                print myPlayer.name + " gets out of jail."
        if myPlayer.inJail and myPlayer.cash >= thisGame.jailFine: #Else pay
            choose = myPlayer.PayJailFine(thisGame.jailFine, board, players, bank)
            if choose == 'yes':
                MoveMoney(-thisGame.jailFine, myPlayer, bank)
                myPlayer.ResetJail()
                print myPlayer.name + " pays $" + str(thisGame.jailFine) + " to get out of jail."
        if myPlayer.timeInJail == 3: #Else if already three turns in jail:
            MoveMoney(-thisGame.jailFine, myPlayer, bank)
            myPlayer.ResetJail()
            print myPlayer.name + " pays anyway $" + str(thisGame.jailFine) + " to get out of jail after three turns."
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
            MoveMoney(2*thisGame.startWage, myPlayer, bank)
            print myPlayer.name + " is a lucky punk and gets $" + str(2*thisGame.startWage) + "."
        elif myPlayer.location - dice[0] - dice[1] < 0:
            MoveMoney(thisGame.startWage, myPlayer, bank)
            print myPlayer.name + " gets $" + str(thisGame.startWage) + "."
    #reset teleport counter now
    myPlayer.teleport = 0
    # if player lands on street, rail or utility:
    if isinstance(board[myPlayer.location], (Street, Railroad, Utility)):
        if board[myPlayer.location].ownedBy == None:
            choose = myPlayer.Buy(board) #You can buy the place
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
                    myPlayer.StartAuction(players, board, thisGame.neighborhoods, bank) #launch auction
            else:
                myPlayer.StartAuction(players, board, thisGame.neighborhoods, bank) #launch auction
        elif board[myPlayer.location].ownedBy == myPlayer:
            #If you already own that place
            print "You (" + myPlayer.name + ") already own " + board[myPlayer.location].name + "."
        else:
            #Finally, you pay rent (if not mortgaged)
            rentDue = board[myPlayer.location].rent(thisGame.neighborhoods,board)
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
        print "Well, " + myPlayer.name + ", you have drawn this card: ",
        print thisGame.communityChest[currentComm].text
        if thisGame.communityChest[currentComm].goStart == 1:
            myPlayer.location = 0
            MoveMoney(thisGame.startWage, myPlayer, bank)
            print "You go to Start and only receive $" + str(thisGame.startWage)
        elif thisGame.communityChest[currentComm].cash != 0:
            if thisGame.communityChest[currentComm].cash > 0:
                MoveMoney(thisGame.communityChest[currentComm].cash, myPlayer, bank)
            else:
                MoveMoneyToTable(thisGame.communityChest[currentComm].cash, myPlayer, bank)
        elif thisGame.communityChest[currentComm].jailcard == 1:
            myPlayer.jailCommCards += 1
            #remove card from community chest
            thisGame.communityChest.pop(currentComm)
            #decrease index,to compensate for the general increase after IF
            currentComm = (currentComm + len(thisGame.communityChest) - 1) % len(thisGame.communityChest)
        elif thisGame.communityChest[currentComm].goToJail == 1:
            myPlayer.MoveToJail(board)
        elif thisGame.communityChest[currentComm].collect == 1:
            for person in players:
                if person != myPlayer:
                    person.cash -= thisGame.collectFine
                    myPlayer.cash += thisGame.collectFine
                    print person.name + " pays $" + str(thisGame.collectFine) +" to " + myPlayer.name + "."
        elif thisGame.communityChest[currentComm].repairs == 1:
            Repairs(thisGame.chestRepairs[0], thisGame.chestRepairs[1], myPlayer, board, bank)
        #increment community chest card index
        currentComm = PlusOne(currentComm, len(thisGame.communityChest))
    #Chance cards
    if isinstance(board[myPlayer.location], Chance):
        print "Well, " + myPlayer.name + ", you have drawn this card: ",
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
            Repairs(thisGame.chanceRepairs[0],thisGame.chanceRepairs[1], myPlayer, board, bank)
        elif chances[currentChance].reading == 1:
            #find Reading location
            for item in board:
                if item.name == "Reading Railroad":
                    destination = item.location #what if not found?
                    break
            if destination < myPlayer.location:
                print "You pass Go and collect $" + str(thisGame.startWage) + "."
                MoveMoney(thisGame.startWage, myPlayer, bank)
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
                MoveMoney(thisGame.startWage, myPlayer, bank)
                print "You move to Go and only get $" + str(thisGame.startWage) + "."
            else:
                for item in board:
                    if item.name == chances[currentChance].goTo:
                        #you get $200 if you pass Go.
                        if myPlayer.location > item.location:
                            MoveMoney(thisGame.startWage, myPlayer, bank)
                            print "You get $" + str(thisGame.startWage)
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
    print myPlayer.name + " has $"+ str(myPlayer.cash) + ".",
    if myPlayer.cash < 0:
        print "YOU MUST SELL ASSETS OR YOU GET OUT OF THE GAME!"
    print ""
    choose = ''
    while choose not in ["u", "d", "m","d", "e", "n"]:
        choose = myPlayer.ChooseAction(board, bank, thisGame.neighborhoods)
        if choose == "u":
            myPlayer.Upgrade(thisGame.neighborhoods, board, bank) #upgrade
        elif choose == "d":
            myPlayer.Downgrade(board, bank) #downgrade
        elif choose == "m":
            myPlayer.Mortgage(board, bank) #mortgage
        elif choose == "e":
            myPlayer.Demortgage(board, bank) #demortgage
        elif choose == "n": #exit loop
            break
        choose = ""
        print "Now " + myPlayer.name + " has $"+ str(myPlayer.cash) + "."
    
    #if player has no money and still tries to buy, then auction
    #Negotiate with other players
    
    #Update display
    
    
    
    #stylecheck
    
    #no possibility to upgrade while in jail?
    
    #move hardcoded constants to txt file
    #maxhotels, maxhouses hardcoded or not?
    #save/load game from disk
    
    #create Game object with all data
    
    #Turn end: remove from game if cash < 0
    if myPlayer.cash < 0:
        print myPlayer.name + " HAS BEEN ELIMINATED!"
        for item in board:
            if isinstance(item, (Street, Railroad, Utility)) and item.ownedBy == myPlayer:
                item.ownedBy = None
                if item.hotels == 1:
                    item.hotels = 0
                    bank.hotels += 1
                    item.houses = 0
                else:
                    bank.houses += item.houses
                    item.houses = 0
        players.pop(currentPlayer)
        #no need to increment currentPlayer, but set to zero as needed
        if currentPlayer == len(players):
            currentPlayer = 0
    else:
        #currentPlayer += 1
        currentPlayer = PlusOne(currentPlayer, len(players))


    #Print current financial status
    print ""
    print "***"
    for player in players:
        print player.name + " has $" +str(player.cash)
    print "The bank has got $" + str(bank.money) + " left. There are "+ str(bank.houses) + " houses and " + str(bank.hotels) + " hotels available."
    print "There are $" + str(bank.cardPayments) + " left on the table."
    print "***"
    print ""
    
    
if len(players) == 1:
    print players[0].name + " HAS WON THE GAME"
else:
    bestscore = 0
    bestPlayer = None
    for person in players:
        if person.cash > bestscore:
            bestPlayer = person
            bestscore = person.cash
    if bestPlayer != None:
        print bestPlayer.name + " HAS WON THE GAME"
    else:
        print "INCREDIBLE BUNCH OF LOSERS."
    