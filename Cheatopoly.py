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
ans = thisGame.choose_yes_no("Play interactively?[yes/no] ")
if ans == "yes":
    thisGame.initialize_players()
else:
    thisGame.mock_players()

# Game window size
HEIGHT = 480
WIDTH = 640
# Colors
GRAY = (192, 192, 192)
# Frames per second
FPS = 2
fpsClock = pygame.time.Clock()
#Pygame initialization
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cheatopoly')
DISPLAYSURF.fill(GRAY)

thisGame.set_places(WIDTH, HEIGHT)

#Player turns are generated in a while loop
while thisGame.bank.money > 0 and len(thisGame.players) > 1:

    #draw board with places
    thisGame.draw_board(DISPLAYSURF)

    pygame.display.update()
    fpsClock.tick(FPS)

    myPlayer = thisGame.players[thisGame.current_player]  # Shorthand

    #Start player turn; test for teleportation with Chance card
    #Dice roll and jail check happen only when not teleporting
    if myPlayer.teleport == 0:
        if not isinstance(myPlayer, Cheatoid):
            raw_input("Hello, " + myPlayer.name + "! You have $" +
                      str(myPlayer.cash) + ". Press Enter to start turn.")
        dice = thisGame.dice()  # Roll dice
        print "Dice roll for " + myPlayer.name + ": " + str(dice[0]) + " " + \
              str(dice[1])

        ## Resolve jail status
        myPlayer.check_jail(thisGame, dice)

        #Check how many doubles in a row
        if dice[0] == dice[1]:
            myPlayer.doubles_in_a_row += 1
            if myPlayer.doubles_in_a_row == 3:
                myPlayer.move_to_jail(thisGame)
        else:
            myPlayer.doubles_in_a_row = 0

        #If not in jail, advance to new position
        if not myPlayer.in_jail:
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
                print myPlayer.name + " gets $" + str(thisGame.start_wage) + \
                    "."

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
        #Specific procedure
        myPlayer.check_specific_comm(thisGame)
        # Common procedure
        myPlayer.check_common_cards(thisGame, thisGame.community_chest,
                                    thisGame.chest_repairs[0],
                                    thisGame.chest_repairs[1],
                                    thisGame.current_comm, "comm")
        #increment community chest card index
        thisGame.current_comm = thisGame.add_one(thisGame.current_comm,
                                                 len(thisGame.community_chest))

    #Chance cards
    if isinstance(thisPlace, Chance):
        print myPlayer.name + ", you have drawn this Chance card: ",
        print thisGame.chances[thisGame.current_chance].text
        # Specific procedure
        myPlayer.check_specific_chance(thisGame)
        # Common procedure
        myPlayer.check_common_cards(thisGame, thisGame.chances,
                                    thisGame.chance_repairs[0],
                                    thisGame.chance_repairs[1],
                                    thisGame.current_chance, "chance")
        # Increment chance card index
        thisGame.current_chance = thisGame.add_one(thisGame.current_chance,
                                                   len(thisGame.chances))
        if myPlayer.teleport == 1:
            continue  # Player teleports.

    #Upgrade/downgrade houses/hotels, mortgage properties
    print ""
    print myPlayer.name + ", you have the following properties:"
    for item in thisGame.board:
        if item.owned_by == myPlayer:
            print item
    if myPlayer.cash < 0:
        print "YOU MUST SELL ASSETS OR YOU GET OUT OF THE GAME!"
    print ""
    choose = ''
    while choose not in ["u", "d", "m", "d", "e", "n"]:
        print "Now " + myPlayer.name + " has $" + str(myPlayer.cash) + "."
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

    #Negotiate with other players
    #Update display
    #save/load game from disk
    # add turn counter and print it at the end

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    #Turn end: remove from game if cash < 0 and increment current player
    thisGame.check_eliminate(myPlayer)

    #Print turn end status
    thisGame.turn_end()

thisGame.game_end()  # Game end
