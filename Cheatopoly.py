import random
from random import shuffle
from CheatopolyClasses import *
from CheatopolyFunctions import *

# Import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'));
with ff as f:
    content = f.readlines()

#Create game
thisGame = Game()
thisGame.bank =  Bank(thisGame) #initialize bank
thisGame.ReadData(content) #process data.txt
#randomize community chest and chance cards
shuffle(thisGame.chances)
shuffle(thisGame.communityChest)

print "************************"
print "WELCOME TO CHEATOPOLY!!!"
print "You can play Cheatopoly in up to 6 players."
print "************************"

#Initialize players
thisGame.InitializePlayers()

currentPlayer = 0 # initialize current player
#Player turns are generated in a while loop
while thisGame.bank.money > 0 and len(thisGame.players) > 1:
    myPlayer = thisGame.players[currentPlayer] #shorthand
    #Start player turn; test for teleportation with Chance card
    #Roll dice and jail check happen only when not teleporting
    print "check teleport"
    if myPlayer.teleport == 0:
        if not isinstance(myPlayer, Cheatoid):
            raw_input("Hello, " + myPlayer.name +  "! You have $" + \
            str(myPlayer.cash) + ". Press Enter to start turn.")
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
            choose = myPlayer.UseJailCard(thisGame)
            if choose == 'yes':
                myPlayer.ReturnCardLeaveJail(thisGame)
        #Else pay
        if myPlayer.inJail and myPlayer.cash >= thisGame.jailFine:
            choose = myPlayer.PayJailFine(thisGame)
            if choose == 'yes':
                MoveMoney(-thisGame.jailFine, myPlayer, thisGame.bank)
                myPlayer.ResetJail()
                print myPlayer.name + " pays $" + str(thisGame.jailFine) + \
                " to get out of jail."
        #Else if already three turns in jail:
        if myPlayer.timeInJail == 3:
            MoveMoney(-thisGame.jailFine, myPlayer, thisGame.bank)
            myPlayer.ResetJail()
            print myPlayer.name + " pays anyway $" + str(thisGame.jailFine) + " to get out of jail after three turns."
        #Check if still in jail
        if myPlayer.inJail:
            currentPlayer = PlusOne(currentPlayer, len(thisGame.players))
            continue #end of turn
        #Check how many doubles in a row
        if dice[0] == dice[1]:
            myPlayer.doublesInARow += 1
            if myPlayer.doublesInARow == 3:
                myPlayer.MoveToJail(thisGame.board)
                currentPlayer = PlusOne(currentPlayer, len(thisGame.players))
                continue
        else:
            myPlayer.doublesInARow = 0
        #So,we are definitely not in jail. Advance to new position
        myPlayer.location = (myPlayer.location + dice[0] + dice[1]) % len(thisGame.board)
        print myPlayer.name + " advances to " + str(myPlayer.location) + \
        " (" + thisGame.board[myPlayer.location].name + ")."
        #Did we pass Go? +startWage/2*startWage
        if myPlayer.location == 0:
            MoveMoney(2*thisGame.startWage, myPlayer, thisGame.bank)
            print myPlayer.name + " is a lucky punk and gets $" + str(2*thisGame.startWage) + "."
        elif myPlayer.location - dice[0] - dice[1] < 0:
            MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
            print myPlayer.name + " gets $" + str(thisGame.startWage) + "."
    #reset teleport counter now
    myPlayer.teleport = 0
    thisPlace = thisGame.board[myPlayer.location] #shorthand
    # if player lands on street, rail or utility:
    if isinstance(thisPlace, (Street, Railroad, Utility)):
        if thisPlace.ownedBy == None:
            #You can buy the place
            choose = myPlayer.Buy(thisGame.board) #make a choice
            thisGame.NewOwnerOrAuction(choose, myPlayer, thisPlace)
        elif thisPlace.ownedBy == myPlayer:
            #If you already own that place
            print "You (" + myPlayer.name + ") already own " + thisPlace.name + "."
        else:
            #Finally, you pay rent (if not mortgaged)
            myPlayer.PayRent(thisPlace, thisGame)
    #Free Parking
    if isinstance(thisPlace, FreeParking):
        MoveTable(myPlayer,thisGame.bank)
    #Go To Jail
    if isinstance(thisPlace, GoToJail):
        myPlayer.MoveToJail(thisGame.board)    
    #Pay taxes: 
    if isinstance(thisPlace, Tax):
        myPlayer.PayTax(thisPlace, thisGame)
    #Community Chest
    if isinstance(thisPlace, CommunityChest):
        print myPlayer.name + ", you have drawn this Community Chest card: ",
        print thisGame.communityChest[thisGame.currentComm].text
        if thisGame.communityChest[thisGame.currentComm].goStart == 1:
            myPlayer.MoveToStart(thisGame)
        elif thisGame.communityChest[thisGame.currentComm].cash != 0:
            myPlayer.PayCardMoney(thisGame.communityChest[thisGame.currentComm].cash, thisGame)
        elif thisGame.communityChest[thisGame.currentComm].jailcard == 1:
            myPlayer.jailCommCards += 1
            #remove card & decrease index,to compensate for increase after IF
            thisGame.communityChest.pop(thisGame.currentComm)
            thisGame.currentComm = (thisGame.currentComm + \
            len(thisGame.communityChest) - 1) % len(thisGame.communityChest)
        elif thisGame.communityChest[thisGame.currentComm].goToJail == 1:
            myPlayer.MoveToJail(thisGame.board)
        elif thisGame.communityChest[thisGame.currentComm].collect == 1:
            for person in thisGame.players:
                if person != myPlayer:
                    person.cash -= thisGame.collectFine
                    myPlayer.cash += thisGame.collectFine
                    print person.name + " pays $" + str(thisGame.collectFine) +" to " + myPlayer.name + "."
        elif thisGame.communityChest[thisGame.currentComm].repairs == 1:
            Repairs(thisGame.chestRepairs[0], thisGame.chestRepairs[1], myPlayer, thisGame)
        #increment community chest card index
        thisGame.currentComm = PlusOne(thisGame.currentComm, len(thisGame.communityChest))
    #Chance cards
    if isinstance(thisPlace, Chance):
        print myPlayer.name + ", you have drawn this Chance card: ",
        print thisGame.chances[thisGame.currentChance].text
        if thisGame.chances[thisGame.currentChance].cash != 0:
            myPlayer.PayCardMoney(thisGame.chances[thisGame.currentChance].cash, thisGame)
        elif thisGame.chances[thisGame.currentChance].jailcard == 1:
            myPlayer.jailChanceCards += 1
            #remove card & decrease index,to compensate for increase after IF
            thisGame.chances.pop(thisGame.currentChance)
            thisGame.currentChance = (thisGame.currentChance + \
            len(thisGame.chances) - 1) % len(thisGame.chances)
        elif thisGame.chances[thisGame.currentChance].goToJail == 1:
            myPlayer.MoveToJail(thisGame.board)
        elif thisGame.chances[thisGame.currentChance].repairs == 1:
            Repairs(thisGame.chanceRepairs[0],thisGame.chanceRepairs[1], myPlayer, thisGame)
        elif thisGame.chances[thisGame.currentChance].reading == 1:
            #find Reading location
            for item in thisGame.board:
                if item.name == "Reading Railroad":
                    destination = item.location #what if not found?
                    break
            if destination < myPlayer.location:
                print "You pass Go and collect $" + str(thisGame.startWage) + "."
                MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
            myPlayer.location = destination
            print "You move to Reading Railroad, at location " + str(destination) + "."
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.currentChance].movement != 0:
            myPlayer.location = (myPlayer.location + len(thisGame.board) + thisGame.chances[thisGame.currentChance].movement) % len(thisGame.board)
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.currentChance].rail == 1:
            while not isinstance(thisPlace, Railroad):
                #FIXME: infinite loop if no rail!
                myPlayer.location = PlusOne(myPlayer.location, len(thisGame.board))
            print "You have moved to the next railroad: " + thisPlace.name + ", at pos " + str(myPlayer.location) + "."
            myPlayer.doubleRent = 2
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.currentChance].goTo != 0:
            if thisGame.chances[thisGame.currentChance].goTo == "1":
                myPlayer.MoveToStart(thisGame)
            else:
                for item in thisGame.board:
                    if item.name == thisGame.chances[thisGame.currentChance].goTo:
                        #you get $200 if you pass Go.
                        if myPlayer.location > item.location:
                            MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
                            print "You get $" + str(thisGame.startWage)
                        myPlayer.location = item.location
                        break
                print "You move to " + thisPlace.name + " at pos " + str(myPlayer.location) + "."
                myPlayer.teleport = 1
                continue
        #increment chance card index
        thisGame.currentChance = PlusOne(thisGame.currentChance, len(thisGame.chances))
    #Upgrade/downgrade houses/hotels, mortgage properties
    print ""
    print myPlayer.name + ", you have the following properties:"
    for item in thisGame.board:
        if item.ownedBy == myPlayer:
            print item
    print myPlayer.name + " has $"+ str(myPlayer.cash) + ".",
    if myPlayer.cash < 0:
        print "YOU MUST SELL ASSETS OR YOU GET OUT OF THE GAME!"
    print ""
    choose = ''
    while choose not in ["u", "d", "m","d", "e", "n"]:
        choose = myPlayer.ChooseAction(thisGame.board, thisGame.bank, thisGame.neighborhoods)
        if choose == "u":
            myPlayer.Upgrade(thisGame.neighborhoods, thisGame.board, thisGame.bank) #upgrade
        elif choose == "d":
            myPlayer.Downgrade(thisGame.board, thisGame.bank) #downgrade
        elif choose == "m":
            myPlayer.Mortgage(thisGame.board, thisGame.bank) #mortgage
        elif choose == "e":
            myPlayer.Demortgage(thisGame.board, thisGame.bank) #demortgage
        elif choose == "n": #exit loop
            break
        choose = ""
        print "Now " + myPlayer.name + " has $"+ str(myPlayer.cash) + "."
    
    #Negotiate with other players
    #Update display
    #stylecheck
    #no possibility to upgrade while in jail?
    #save/load game from disk
    
    #Turn end: remove from game if cash < 0
    if myPlayer.cash < 0:
        print myPlayer.name + " HAS BEEN ELIMINATED!"
        for item in thisGame.board:
            if isinstance(item, (Street, Railroad, Utility)) and item.ownedBy == myPlayer:
                item.ownedBy = None
                if item.hotels == 1:
                    item.hotels = 0
                    thisGame.bank.hotels += 1
                    item.houses = 0
                else:
                    thisGame.bank.houses += item.houses
                    item.houses = 0
        thisGame.players.pop(currentPlayer)
        #no need to increment currentPlayer, but set to zero as needed
        if currentPlayer == len(thisGame.players):
            currentPlayer = 0
    else:
        #currentPlayer += 1
        currentPlayer = PlusOne(currentPlayer, len(thisGame.players))

    #Print current financial status
    print ""
    print "***"
    for player in thisGame.players:
        print player.name + " has $" +str(player.cash)
    print "The bank has got $" + str(thisGame.bank.money) + " left. There are "+ str(thisGame.bank.houses) + " houses and " + str(thisGame.bank.hotels) + " hotels available."
    print "There are $" + str(thisGame.bank.cardPayments) + " left on the table."
    print "***"
    print ""
    
    
if len(thisGame.players) == 1:
    print thisGame.players[0].name + " HAS WON THE GAME"
else:
    bestscore = 0
    bestPlayer = None
    for person in thisGame.players:
        if person.cash > bestscore:
            bestPlayer = person
            bestscore = person.cash
    if bestPlayer != None:
        print bestPlayer.name + " HAS WON THE GAME"
    else:
        print "INCREDIBLE BUNCH OF LOSERS."
    