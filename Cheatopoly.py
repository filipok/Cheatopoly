import sys
from random import shuffle
from CheatopolyClasses import *

# Pygame initialization
pygame.init()
# GUI settings
HEIGHT = 600
WIDTH = 800
GRAY = (192, 192, 192)
LINE_HEIGHT = 7
FONT_SIZE = 11
DISPLAYSURF = pygame.display.set_mode((WIDTH, HEIGHT))
DISPLAYSURF.fill(GRAY)
pygame.display.set_caption('Cheatopoly')

#Create game
thisGame = Game(HEIGHT, WIDTH, GRAY, DISPLAYSURF, LINE_HEIGHT, FONT_SIZE)
thisGame.load('data.txt')  # Process data.txt
thisGame.bank = Bank(thisGame)  # Initialize bank
#Randomize community chest and chance cards
shuffle(thisGame.chances)
shuffle(thisGame.community_chest)
# Set place coordinates
thisGame.set_places()

#Welcome screen
for item in thisGame.board:
    item.draw(thisGame)
message(thisGame.display, "************************", thisGame.background,
        min(thisGame.width, thisGame.height)/2, thisGame.height/4 + 20)
message(thisGame.display, "WELCOME TO CHEATOPOLY!!!", thisGame.background,
        min(thisGame.width, thisGame.height)/2, thisGame.height/4 + 40)
message(thisGame.display, "You can play Cheatopoly in up to 6 players",
        thisGame.background, min(thisGame.width, thisGame.height)/2,
        thisGame.height/4 + 60)
message(thisGame.display, "************************", thisGame.background,
        min(thisGame.width, thisGame.height)/2, thisGame.height/4 + 80)
pygame.display.update()
pygame.time.wait(2000)
thisGame.click_n_cover()

#Initialize players
ans = thisGame.yes_no("Play interactively?[yes/no] ", 40)
if ans == "yes":
    thisGame.initialize_players()
else:
    thisGame.mock_players()

#Player turns are generated in a while loop
while thisGame.bank.money > 0 and len(thisGame.players) > 1:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw board with places, players and stats
    thisGame.visual_refresh()

    myPlayer = thisGame.players[thisGame.current_player]  # Shorthand

    #Start player turn; test for teleportation with Chance card
    #Dice roll and jail check happen only when not teleporting
    if myPlayer.teleport == 0:
        if not isinstance(myPlayer, Cheatoid):
            thisGame.start_turn(myPlayer)
        dice = thisGame.roll_dice(myPlayer)

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
        if not myPlayer.in_jail and not myPlayer.jail_doubles:
            #Update random position variation
            myPlayer.x_rand = random.randint(-6, 6)
            myPlayer.y_rand = random.randint(-6, 6)
            myPlayer.location = (myPlayer.location + dice[0] + dice[1]) % \
                len(thisGame.board)
            thisGame.visual_refresh()
            text = myPlayer.name + " advances to " + str(myPlayer.location) + \
                " (" + thisGame.board[myPlayer.location].name + ")."
            thisGame.cover_n_central(text)
            #Did we pass Go? +start_wage/2*start_wage
            if myPlayer.location == 0:
                thisGame.bank.move_money(2*thisGame.start_wage, myPlayer)
                text = myPlayer.name + " is a lucky punk and gets $" + \
                    str(2*thisGame.start_wage) + "."
                thisGame.cover_n_central(text)
            elif myPlayer.location - dice[0] - dice[1] < 0:
                thisGame.bank.move_money(thisGame.start_wage, myPlayer)
                text = myPlayer.name + " gets $" + str(thisGame.start_wage) + \
                    "."
                thisGame.cover_n_central(text)
        elif myPlayer.jail_doubles:
            myPlayer.jail_doubles = False

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
            text = "You (" + myPlayer.name + ") already own " + \
                   thisPlace.name + "."
            thisGame.cover_n_central(text)
        else:
            #Finally, you pay rent (if not mortgaged)
            myPlayer.pay_rent(thisPlace, thisGame)

    #Free Parking
    if isinstance(thisPlace, FreeParking):
        thisGame.move_table(myPlayer)

    #Go To Jail
    if isinstance(thisPlace, GoToJail):
        myPlayer.move_to_jail(thisGame)

    #Pay taxes:
    if isinstance(thisPlace, Tax):
        myPlayer.pay_tax(thisPlace, thisGame)

    #Community Chest
    if isinstance(thisPlace, CommunityChest):
        text = myPlayer.name + ", you have drawn this Community Chest card: "
        thisGame.cover_n_central(text)
        thisGame.cover_n_central(
            thisGame.community_chest[thisGame.current_comm].text)
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
        text = myPlayer.name + ", you have drawn this Chance card: "
        thisGame.cover_n_central(text)
        thisGame.cover_n_central(
            thisGame.chances[thisGame.current_chance].text)
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
    if myPlayer.cash < 0:
        thisGame.cover_n_central(
            "YOU MUST SELL ASSETS OR YOU GET OUT OF THE GAME!")
    choose = ''
    while choose not in ["u", "d", "m", "d", "e", "n"]:
        choose = myPlayer.choose_action(thisGame)
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
    #save/load game from disk
    # add turn counter and print it at the end

    #Turn end: remove from game if cash < 0 and increment current player
    thisGame.check_eliminate(myPlayer)

thisGame.game_end()  # Game end
