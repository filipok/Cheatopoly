from CheatopolyClasses import *
from CheatopolyFunctions import *
from CheatopolyReadData import *

#Create game
thisGame = Game()
thisGame.bank =  Bank(thisGame) #initialize bank

# Import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'));
with ff as f:
    content = f.readlines()
CheatopolyReadData(content, thisGame)
#randomize community chest and chance cards
from random import shuffle
shuffle(thisGame.chances)
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
        thisGame.players.append(Player(name, thisGame.playerCash, True))
    else:
        thisGame.players.append(Cheatoid(name, thisGame.playerCash,False))
    list_of_names.append(name)



#The player turns are generated in a while loop
currentPlayer = 0 # initialize current player
while thisGame.bank.money > 0 and len(thisGame.players) > 1:
    myPlayer = thisGame.players[currentPlayer] #shorthand
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
            choose = myPlayer.UseJailCard(thisGame.board, thisGame.players, thisGame.bank)
            if choose == 'yes':
                if myPlayer.jailCommCards > myPlayer.jailChanceCards:
                    myPlayer.jailCommCards -= 1
                    #return community card back to the pile
                    thisGame.communityChest.insert(thisGame.currentComm,CommunityCard("Get out of jail, free", 0, 0, 1, 0, 0, 0))
                    thisGame.currentComm = PlusOne(thisGame.currentComm, len(thisGame.communityChest))
                else:
                    myPlayer.jailChanceCards -= 1
                    #return chance card back to the pile
                    thisGame.chances.insert(thisGame.currentChance,ChanceCard("Get out of jail free", 0, 0, 1, 0, 0, 0, 0, 0))
                    thisGame.currentChance = PlusOne(thisGame.currentChance, len(thisGame.chances))
                myPlayer.ResetJail()
                print myPlayer.name + " gets out of jail."
        if myPlayer.inJail and myPlayer.cash >= thisGame.jailFine: #Else pay
            choose = myPlayer.PayJailFine(thisGame.jailFine, thisGame.board, thisGame.players, thisGame.bank)
            if choose == 'yes':
                MoveMoney(-thisGame.jailFine, myPlayer, thisGame.bank)
                myPlayer.ResetJail()
                print myPlayer.name + " pays $" + str(thisGame.jailFine) + " to get out of jail."
        if myPlayer.timeInJail == 3: #Else if already three turns in jail:
            MoveMoney(-thisGame.jailFine, myPlayer, thisGame.bank)
            myPlayer.ResetJail()
            print myPlayer.name + " pays anyway $" + str(thisGame.jailFine) + " to get out of jail after three turns."
        if myPlayer.inJail: #Check if still in jail
            currentPlayer = PlusOne(currentPlayer, len(thisGame.players))
            continue #end of turn
        if dice[0] == dice[1]: #Check how many doubles in a row
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
        if myPlayer.location == 0: #Did we pass Go? +startWage/2*startWage
            MoveMoney(2*thisGame.startWage, myPlayer, thisGame.bank)
            print myPlayer.name + " is a lucky punk and gets $" + str(2*thisGame.startWage) + "."
        elif myPlayer.location - dice[0] - dice[1] < 0:
            MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
            print myPlayer.name + " gets $" + str(thisGame.startWage) + "."
    #reset teleport counter now
    myPlayer.teleport = 0
    # if player lands on street, rail or utility:
    if isinstance(thisGame.board[myPlayer.location], (Street, Railroad, Utility)):
        if thisGame.board[myPlayer.location].ownedBy == None:
            choose = myPlayer.Buy(thisGame.board) #You can buy the place
            if choose == "yes":
                if myPlayer.cash > thisGame.board[myPlayer.location].price:
                    thisGame.board[myPlayer.location].newOwner(myPlayer) #assign new owner
                    MoveMoney(-thisGame.board[myPlayer.location].price, myPlayer, thisGame.bank)
                    print "Congratulations, " + myPlayer.name + "! You have bought: " +  str(thisGame.board[myPlayer.location]) + "."
                else:
                    print "Sorry, you do not have the required funds!"
                    import random
                    a = random.randint(1, 4)
                    if a == 1:
                        print "Beggar...!"
                    myPlayer.StartAuction(thisGame.players, thisGame.board, thisGame.neighborhoods, thisGame.bank) #launch auction
            else:
                myPlayer.StartAuction(thisGame.players, thisGame.board, thisGame.neighborhoods, thisGame.bank) #launch auction
        elif thisGame.board[myPlayer.location].ownedBy == myPlayer:
            #If you already own that place
            print "You (" + myPlayer.name + ") already own " + thisGame.board[myPlayer.location].name + "."
        else:
            #Finally, you pay rent (if not mortgaged)
            rentDue = thisGame.board[myPlayer.location].rent(thisGame.neighborhoods, thisGame.board)
            if myPlayer.doubleRent == 2:
                rentDue *= 2 #rent is doubled when sent by Chance card to a R.R.
                myPlayer.doubleRent = 1
            if not thisGame.board[myPlayer.location].mortgaged:
                print thisGame.board[myPlayer.location].name +  " is owned by " + thisGame.board[myPlayer.location].ownedBy.name + ", you (" + myPlayer.name + ") must pay rent amounting to: " + str(rentDue) + "."
                myPlayer.cash -= rentDue
                thisGame.board[myPlayer.location].ownedBy.cash += rentDue
            else:
                print thisGame.board[myPlayer.location].name +  " is owned by " + thisGame.board[myPlayer.location].ownedBy.name + ", but is mortgaged and you pay nothing."
    #Free Parking
    if isinstance(thisGame.board[myPlayer.location], FreeParking):
        MoveTable(myPlayer,thisGame.bank)
    #Go To Jail
    if isinstance(thisGame.board[myPlayer.location], GoToJail):
        myPlayer.MoveToJail(thisGame.board)    
    #Pay taxes: you can pay either a lump sum or a percentage of total assets.
    #Sometimes,the second option can be "None"
    if isinstance(thisGame.board[myPlayer.location], Tax):
        tax1 = TaxRate(thisGame.board[myPlayer.location].option1, myPlayer, thisGame.board)
        tax2 = TaxRate(thisGame.board[myPlayer.location].option2, myPlayer, thisGame.board)
        if tax1 == None or tax2 == None:
            tax = max(tax1,tax2)
        else:
            tax = min(tax1,tax2)
        print "Well done, " + myPlayer.name + ", you pay taxes amounting to: $" + str(tax)
        MoveMoneyToTable(-tax, myPlayer, thisGame.bank)
    #Community Chest
    if isinstance(thisGame.board[myPlayer.location], CommunityChest):
        print "Well, " + myPlayer.name + ", you have drawn this card: ",
        print thisGame.communityChest[thisGame.currentComm].text
        if thisGame.communityChest[thisGame.currentComm].goStart == 1:
            myPlayer.location = 0
            MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
            print "You go to Start and only receive $" + str(thisGame.startWage)
        elif thisGame.communityChest[thisGame.currentComm].cash != 0:
            if thisGame.communityChest[thisGame.currentComm].cash > 0:
                MoveMoney(thisGame.communityChest[thisGame.currentComm].cash, myPlayer, thisGame.bank)
            else:
                MoveMoneyToTable(thisGame.communityChest[thisGame.currentComm].cash, myPlayer, thisGame.bank)
        elif thisGame.communityChest[thisGame.currentComm].jailcard == 1:
            myPlayer.jailCommCards += 1
            #remove card from community chest
            thisGame.communityChest.pop(thisGame.currentComm)
            #decrease index,to compensate for the general increase after IF
            thisGame.currentComm = (thisGame.currentComm + len(thisGame.communityChest) - 1) % len(thisGame.communityChest)
        elif thisGame.communityChest[thisGame.currentComm].goToJail == 1:
            myPlayer.MoveToJail(thisGame.board)
        elif thisGame.communityChest[thisGame.currentComm].collect == 1:
            for person in thisGame.players:
                if person != myPlayer:
                    person.cash -= thisGame.collectFine
                    myPlayer.cash += thisGame.collectFine
                    print person.name + " pays $" + str(thisGame.collectFine) +" to " + myPlayer.name + "."
        elif thisGame.communityChest[thisGame.currentComm].repairs == 1:
            Repairs(thisGame.chestRepairs[0], thisGame.chestRepairs[1], myPlayer, thisGame.board, thisGame.bank)
        #increment community chest card index
        thisGame.currentComm = PlusOne(thisGame.currentComm, len(thisGame.communityChest))
    #Chance cards
    if isinstance(thisGame.board[myPlayer.location], Chance):
        print "Well, " + myPlayer.name + ", you have drawn this card: ",
        print thisGame.chances[thisGame.currentChance].text
        if thisGame.chances[thisGame.currentChance].cash != 0:
            if thisGame.chances[thisGame.currentChance].cash > 0:
                MoveMoney(thisGame.chances[thisGame.currentChance].cash, myPlayer, thisGame.bank)
            else:
                MoveMoneyToTable(thisGame.chances[thisGame.currentChance].cash, myPlayer, thisGame.bank)
        elif thisGame.chances[thisGame.currentChance].jailcard == 1:
            myPlayer.jailChanceCards += 1
            #remove card from community chest
            thisGame.chances.pop(thisGame.currentChance)
            #decrease index,to compensate for the general increase after IF
            thisGame.currentChance = (thisGame.currentChance + len(thisGame.chances) - 1) % len(thisGame.chances)
        elif thisGame.chances[thisGame.currentChance].goToJail == 1:
            myPlayer.MoveToJail(thisGame.board)
        elif thisGame.chances[thisGame.currentChance].repairs == 1:
            Repairs(thisGame.chanceRepairs[0],thisGame.chanceRepairs[1], myPlayer, thisGame.board, thisGame.bank)
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
            while not isinstance(thisGame.board[myPlayer.location], Railroad):
                #FIXME: infinite loop if no rail!
                myPlayer.location = PlusOne(myPlayer.location, len(thisGame.board))
            print "You have moved to the next railroad: " + thisGame.board[myPlayer.location].name + ", at pos " + str(myPlayer.location) + "."
            myPlayer.doubleRent = 2
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.currentChance].goTo != 0:
            if thisGame.chances[thisGame.currentChance].goTo == "1":
                myPlayer.location = 0
                MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
                print "You move to Go and only get $" + str(thisGame.startWage) + "."
            else:
                for item in thisGame.board:
                    if item.name == thisGame.chances[thisGame.currentChance].goTo:
                        #you get $200 if you pass Go.
                        if myPlayer.location > item.location:
                            MoveMoney(thisGame.startWage, myPlayer, thisGame.bank)
                            print "You get $" + str(thisGame.startWage)
                        myPlayer.location = item.location
                        break
                print "You move to " + thisGame.board[myPlayer.location].name + " at pos " + str(myPlayer.location) + "."
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
    
    #if player has no money and still tries to buy, then auction
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
    