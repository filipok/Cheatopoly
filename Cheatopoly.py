from random import shuffle
from CheatopolyClasses import *

#Create game
thisGame = Game()
thisGame.load('data.txt')  # Process data.txt
thisGame.bank = Bank(thisGame)  # Initialize bank
#Randomize community chest and chance cards
shuffle(thisGame.chances)
shuffle(thisGame.community_chest)

print "************************"
print "WELCOME TO CHEATOPOLY!!!"
print "You can play Cheatopoly in up to 6 players."
print "************************"

#Initialize players
thisGame.initialize_players()
#thisGame.mock_players()

thisGame.current_player = 0  # Initialize current player
#Player turns are generated in a while loop
while thisGame.bank.money > 0 and len(thisGame.players) > 1:
    myPlayer = thisGame.players[thisGame.current_player]  # Shorthand
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
            thisGame.current_player = thisGame.add_one(thisGame.current_player,
                                                       len(thisGame.players))
            continue  # End of turn
        #Check how many doubles in a row
        if dice[0] == dice[1]:
            myPlayer.doubles_in_a_row += 1
            if myPlayer.doubles_in_a_row == 3:
                myPlayer.move_to_jail(thisGame)
                thisGame.current_player = thisGame.add_one(
                    thisGame.current_player, len(thisGame.players))
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
        # Common procedure
        myPlayer.check_common_cards(thisGame, thisGame.community_chest,
                                    thisGame.chest_repairs[0],
                                    thisGame.chest_repairs[1],
                                    thisGame.current_comm, "comm")
        #Specific procedure
        if thisGame.community_chest[thisGame.current_comm].collect == 1:
            for person in thisGame.players:
                if person != myPlayer:
                    person.cash -= thisGame.collect_fine
                    myPlayer.cash += thisGame.collect_fine
                    print person.name + " pays $" + \
                        str(thisGame.collect_fine) + " to " + myPlayer.name + \
                        "."
        elif thisGame.community_chest[thisGame.current_comm].go_start == 1:
            myPlayer.move_to_start(thisGame)
        #increment community chest card index
        thisGame.current_comm = thisGame.add_one(thisGame.current_comm,
                                                 len(thisGame.community_chest))
    #Chance cards
    if isinstance(thisPlace, Chance):
        print myPlayer.name + ", you have drawn this Chance card: ",
        print thisGame.chances[thisGame.current_chance].text
        # Common procedure
        myPlayer.check_common_cards(thisGame, thisGame.chances,
                                    thisGame.chance_repairs[0],
                                    thisGame.chance_repairs[1],
                                    thisGame.current_chance, "chance")
        if thisGame.chances[thisGame.current_chance].reading == 1:
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
        elif thisGame.chances[thisGame.current_chance].go_to != "0":
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

    #should check ifthisGame already in memory before running
    #Negotiate with other players
    #Update display
    #stylecheck
    #no possibility to upgrade while in jail?
    #save/load game from disk
    # add turn counter and print it at the end

    #Turn end: remove from game if cash < 0
    thisGame.check_eliminate(myPlayer)

    #Print turn end status
    thisGame.turn_end()

thisGame.game_end()  # Game end
