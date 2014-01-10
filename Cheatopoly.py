from random import shuffle
from CheatopolyClasses import *

# Import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                             os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'))
with ff as f:
    content = f.readlines()

#Create game
thisGame = Game()
thisGame.bank = Bank(thisGame)  # Initialize bank
thisGame.load(content)  # Process data.txt
#Randomize community chest and chance cards
shuffle(thisGame.chances)
shuffle(thisGame.community_chest)

print "************************"
print "WELCOME TO CHEATOPOLY!!!"
print "You can play Cheatopoly in up to 6 players."
print "************************"

#Initialize players
#thisGame.initialize_players()
thisGame.mock_players()

currentPlayer = 0  # Initialize current player
#Player turns are generated in a while loop
while thisGame.bank.money > 0 and len(thisGame.players) > 1:
    myPlayer = thisGame.players[currentPlayer]  # Shorthand
    #Start player turn; test for teleportation with Chance card
    #Roll dice and jail check happen only when not teleporting
    if myPlayer.teleport == 0:
        if not isinstance(myPlayer, Cheatoid):
            raw_input("Hello, " + myPlayer.name + "! You have $" +
                      str(myPlayer.cash) + ". Press Enter to start turn.")
        dice = thisGame.dice()  # Roll dice
        print "Dice roll for " + myPlayer.name + ": " + str(dice[0]) + " " + \
              str(dice[1])
        # Resolve jail status
        if myPlayer.in_jail:  # Check for doubles while in jail
            if dice[0] == dice[1]:
                myPlayer.reset_jail()
                print myPlayer.name + " has got a double: " + str(dice[0]) + \
                    " " + str(dice[1]) + "."
            else:
                myPlayer.time_in_jail += 1
        #Else use a get ouf of jail card
        if myPlayer.in_jail and \
                max(myPlayer.jail_comm_cards, myPlayer.jail_chance_cards) > 0:
            choose = myPlayer.use_jail_card(thisGame)
            if choose == 'yes':
                myPlayer.return_card_leave_jail(thisGame)
        #Else pay
        if myPlayer.in_jail and myPlayer.cash >= thisGame.jail_fine:
            choose = myPlayer.pay_jail_fine(thisGame)
            if choose == 'yes':
                thisGame.bank.move_money(-thisGame.jail_fine, myPlayer)
                myPlayer.reset_jail()
                print myPlayer.name + " pays $" + str(thisGame.jail_fine) + \
                    " to get out of jail."
        #Else if already three turns in jail:
        if myPlayer.time_in_jail == 3:
            thisGame.bank.move_money(-thisGame.jail_fine, myPlayer)
            myPlayer.reset_jail()
            print myPlayer.name + " pays anyway $" + str(thisGame.jail_fine) +\
                " to get out of jail after three turns."
        #Check if still in jail
        if myPlayer.in_jail:
            currentPlayer = thisGame.add_one(currentPlayer,
                                             len(thisGame.players))
            continue  # End of turn
        #Check how many doubles in a row
        if dice[0] == dice[1]:
            myPlayer.doubles_in_a_row += 1
            if myPlayer.doubles_in_a_row == 3:
                myPlayer.move_to_jail(thisGame)
                currentPlayer = thisGame.add_one(currentPlayer,
                                                 len(thisGame.players))
                continue
        else:
            myPlayer.doubles_in_a_row = 0
        #So,we are definitely not in jail. Advance to new position
        myPlayer.location = (myPlayer.location + dice[0] + dice[1]) % \
            len(thisGame.board)
        print myPlayer.name + " advances to " + str(myPlayer.location) + \
            " (" + thisGame.board[myPlayer.location].name + ")."
        #Did we pass Go? +start_wage/2*start_wage
        if myPlayer.location == 0:
            thisGame.bank.move_money(2*thisGame.start_wage, myPlayer)
            print myPlayer.name + " is a lucky punk and gets $" + \
                str(2*thisGame.start_wage) + "."
        elif myPlayer.location - dice[0] - dice[1] < 0:
            thisGame.bank.move_money(thisGame.start_wage, myPlayer)
            print myPlayer.name + " gets $" + str(thisGame.start_wage) + "."
    #reset teleport counter now
    myPlayer.teleport = 0
    thisPlace = thisGame.board[myPlayer.location]  # Shorthand
    # if player lands on street, rail or utility:
    if isinstance(thisPlace, (Street, Railroad, Utility)):
        if thisPlace.owned_by is None:
            #You can buy the place
            choose = myPlayer.buy(thisGame)  # Make a choice
            thisGame.buy_or_auction(choose, myPlayer, thisPlace)
        elif thisPlace.owned_by == myPlayer:
            #If you already own that place
            print "You (" + myPlayer.name + ") already own " + \
                  thisPlace.name + "."
        else:
            #Finally, you pay rent (if not mortgaged)
            myPlayer.pay_rent(thisPlace, thisGame)
    #Free Parking
    if isinstance(thisPlace, FreeParking):
        thisGame.bank.move_table(myPlayer)
    #Go To Jail
    if isinstance(thisPlace, GoToJail):
        myPlayer.move_to_jail(thisGame)
    #Pay taxes:
    if isinstance(thisPlace, Tax):
        myPlayer.pay_tax(thisPlace, thisGame)
    #Community Chest
    if isinstance(thisPlace, CommunityChest):
        print myPlayer.name + ", you have drawn this Community Chest card: ",
        print thisGame.community_chest[thisGame.current_comm].text
        if thisGame.community_chest[thisGame.current_comm].go_start == 1:
            myPlayer.move_to_start(thisGame)
        elif thisGame.community_chest[thisGame.current_comm].cash != 0:
            myPlayer.pay_card_money(
                thisGame.community_chest[thisGame.current_comm].cash, thisGame)
        elif thisGame.community_chest[thisGame.current_comm].jail_card == 1:
            myPlayer.jail_comm_cards += 1
            #remove card & decrease index,to compensate for increase after IF
            thisGame.community_chest.pop(thisGame.current_comm)
            thisGame.current_comm = (thisGame.current_comm +
                                     len(thisGame.community_chest) - 1) % \
                len(thisGame.community_chest)
        elif thisGame.community_chest[thisGame.current_comm].go_to_jail == 1:
            myPlayer.move_to_jail(thisGame)
        elif thisGame.community_chest[thisGame.current_comm].collect == 1:
            for person in thisGame.players:
                if person != myPlayer:
                    person.cash -= thisGame.collect_fine
                    myPlayer.cash += thisGame.collect_fine
                    print person.name + " pays $" + \
                        str(thisGame.collect_fine) + " to " + myPlayer.name + \
                        "."
        elif thisGame.community_chest[thisGame.current_comm].repairs == 1:
            thisGame.repairs(thisGame.chest_repairs[0],
                             thisGame.chest_repairs[1], myPlayer)
        #increment community chest card index
        thisGame.current_comm = thisGame.add_one(thisGame.current_comm,
                                                 len(thisGame.community_chest))
    #Chance cards
    if isinstance(thisPlace, Chance):
        print myPlayer.name + ", you have drawn this Chance card: ",
        print thisGame.chances[thisGame.current_chance].text
        if thisGame.chances[thisGame.current_chance].cash != 0:
            myPlayer.pay_card_money(
                thisGame.chances[thisGame.current_chance].cash, thisGame)
        elif thisGame.chances[thisGame.current_chance].jail_card == 1:
            myPlayer.jail_chance_cards += 1
            #remove card & decrease index,to compensate for increase after IF
            thisGame.chances.pop(thisGame.current_chance)
            thisGame.current_chance = (thisGame.current_chance +
                                       len(thisGame.chances) - 1) % \
                len(thisGame.chances)
        elif thisGame.chances[thisGame.current_chance].go_to_jail == 1:
            myPlayer.move_to_jail(thisGame)
        elif thisGame.chances[thisGame.current_chance].repairs == 1:
            thisGame.repairs(thisGame.chance_repairs[0],
                             thisGame.chance_repairs[1], myPlayer)
        elif thisGame.chances[thisGame.current_chance].reading == 1:
            #find Reading location
            for item in thisGame.board:
                if item.name == "Reading Railroad":
                    destination = item.location  # FIXME What if not found?
                    break
            if destination < myPlayer.location:
                print "You pass Go and collect $" + str(thisGame.start_wage) +\
                      "."
                thisGame.bank.move_money(thisGame.start_wage, myPlayer)
            myPlayer.location = destination
            print "You move to Reading Railroad, at location " + \
                  str(destination) + "."
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.current_chance].movement != 0:
            myPlayer.location = (myPlayer.location +
                                 len(thisGame.board) +
                                 thisGame.chances[
                                     thisGame.current_chance].movement) % \
                len(thisGame.board)
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.current_chance].rail == 1:
            while not isinstance(thisPlace, Railroad):
                #FIXME: infinite loop if no rail!
                myPlayer.location = thisGame.add_one(myPlayer.location,
                                                     len(thisGame.board))
                thisPlace = thisGame.board[myPlayer.location]  # Updt shorthand
            print "You have moved to the next railroad: " + thisPlace.name + \
                  ", at pos " + str(myPlayer.location) + "."
            myPlayer.doubleRent = 2
            myPlayer.teleport = 1
            continue
        elif thisGame.chances[thisGame.current_chance].go_to != 0:
            if thisGame.chances[thisGame.current_chance].go_to == "1":
                myPlayer.move_to_start(thisGame)
            else:
                for item in thisGame.board:
                    if item.name == thisGame.chances[
                            thisGame.current_chance].go_to:
                        #you get $200 if you pass Go.
                        if myPlayer.location > item.location:
                            thisGame.bank.move_money(thisGame.start_wage,
                                                     myPlayer)
                            print "You get $" + str(thisGame.start_wage)
                        myPlayer.location = item.location
                        break
                print "You move to " + thisPlace.name + " at pos " + \
                      str(myPlayer.location) + "."
                myPlayer.teleport = 1
                continue
        #increment chance card index
        thisGame.current_chance = thisGame.add_one(thisGame.current_chance,
                                                   len(thisGame.chances))
    #Upgrade/downgrade houses/hotels, mortgage properties
    print ""
    print myPlayer.name + ", you have the following properties:"
    for item in thisGame.board:
        if item.owned_by == myPlayer:
            print item
    print myPlayer.name + " has $" + str(myPlayer.cash) + ".",
    if myPlayer.cash < 0:
        print "YOU MUST SELL ASSETS OR YOU GET OUT OF THE GAME!"
    print ""
    choose = ''
    while choose not in ["u", "d", "m", "d", "e", "n"]:
        choose = myPlayer.choose_action()
        if choose == "u":
            myPlayer.upgrade(thisGame)  # Upgrade
        elif choose == "d":
            myPlayer.downgrade(thisGame)  # Downgrade
        elif choose == "m":
            myPlayer.mortgage(thisGame)  # Mortgage
        elif choose == "e":
            myPlayer.demortgage(thisGame)  # Demortgage
        elif choose == "n":  # Exit loop
            break
        choose = ""
        print "Now " + myPlayer.name + " has $" + str(myPlayer.cash) + "."

    #Negotiate with other players
    #Update display
    #stylecheck
    #no possibility to upgrade while in jail?
    #save/load game from disk
    # add turn counter and print it at the end
    
    #Turn end: remove from game if cash < 0
    if myPlayer.cash < 0:
        print myPlayer.name + " HAS BEEN ELIMINATED!"
        for item in thisGame.board:
            if isinstance(item, (Street, Railroad, Utility)) and \
                    item.owned_by == myPlayer:
                item.owned_by = None
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
        currentPlayer = thisGame.add_one(currentPlayer, len(thisGame.players))

    #Print current financial status
    print ""
    print "***"
    for player in thisGame.players:
        print player.name + " has $" + str(player.cash)
    print "The bank has got $" + str(thisGame.bank.money) + \
          " left. There are " + str(thisGame.bank.houses) + " houses and " + \
          str(thisGame.bank.hotels) + " hotels available."
    print "There are $" + str(thisGame.bank.card_payments) + \
          " left on the table."
    print "***"
    print ""


if len(thisGame.players) == 1:
    print thisGame.players[0].name + " HAS WON THE GAME"
else:
    best_score = 0
    best_player = None
    for person in thisGame.players:
        if person.cash > best_score:
            best_player = person
            best_score = person.cash
    if best_player is not None:
        print best_player.name + " HAS WON THE GAME"
    else:
        print "INCREDIBLE BUNCH OF LOSERS."