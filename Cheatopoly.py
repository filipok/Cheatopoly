class Bank(object):
    '''
    In standard editions of Monopoly the Bank has USD 15,140.
    Source: http://boardgames.about.com/od/monopolyfaq/f/bank_money.htm
    There is also a limited number of houses and hotels.[how many?]
    '''
    def __init__(self, money, houses, hotels):
        self.money = money
        self.houses = houses
        self.hotels = hotels

class Place(object):
    '''
    There are several types of places on the Monopoly board:
        - streets
        - railroads
        - utilities
        - community chests
        - chances
        - taxes
        - jail
        - go to jail
        - free parking
        - Start
    '''
    placeType = None #type of place
    placeLocation = None #location of each place #useless when using lists?

class Neighborhood(object):
    '''
    Each neighborhood has a name.
    '''
    ownedBy = None #initially owned by nobody
    
    def __init__(self, name):
        self.name = name
    def newOwner(self, player):
        #change neighborhood owner
        self.ownedBy = player

class Street(Place):
    '''
    Each street is a place and has a name and a price.
    The rent depends on the number of houses (0-4, plus a hotel) .
    The costs of the houses and hotels is specific to the street
    Also, there is a mortgage value and the street belongs to a neighborhood.
    '''
    #initially there are no houses or hotels on the street
    houses = 0
    hotels = 0
    ownedBy = None
    
    def __init__(self, name, placeType, price, rent0, rent1, rent2, rent3, \
    rent4, rentH, mortgage, houseCost, hotelCost, neighborhood):
        self.name = name
        self.placeType = placeType
        self.price = price
        self.rent0 = rent0
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.rentH = rentH
        self.mortgage = mortgage
        self.houseCost = houseCost
        self.hotelCost = hotelCost
        self.neighborhood = neighborhood
    def newOwner(self, player):
        #change street owner
        self.ownedBy = player
    def __repr__(self):
        return self.name + ", " + self.neighborhood + " at pos " + \
        str(self.location) + ", price: " + str(self.price) + ", rents: " + \
        str(self.rent1) + " " + str(self.rent2) + " " + str(self.rent3) + " " +\
        str(self.rent4) + " " + str(self.rentH) + ", mortgage: " + \
        str(self.mortgage) + ", house cost: " +  str(self.houseCost) + \
        ", hotel cost: " + str(self.hotelCost) + " plus 4 houses"
    
class Railroad(Place):
    '''
    Railroad rents depend on the number of railroads owned.
    There is also a mortgage value.
    The rents and mortgae values are identical for all railroads.
    They are still defined in __init__().
    '''
    def __init__(self, name, placeType, price, rent1, rent2, rent3, rent4, \
    mortgage):
        self.name = name
        self.placeType = placeType
        self.price = price
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.mortgage = mortgage
    def __repr__(self):
        return self.name + " at pos " + str(self.location) + ", price: " + \
        str(self.price) + ", rents: " + str(self.rent1) + " " +  \
        str(self.rent2) + " " + str(self.rent3) + " " + str(self.rent4) + \
        ", mortgage: " + str(self.mortgage)
    
class Utility(Place):
    '''
    Utility rents depend on the dice values:
        - if one utility is owned, four times the dice value;
        - if both utilities are owned, 10 times the dice value.
    They also have a mortgage value.
    '''
    def __init__(self, name, placeType, price, mortgage):
        self.name = name
        self.placeType = placeType
        self.price = price
        self.mortgage = mortgage
    def __repr__(self):
        return self.name +  " at pos " + str(self.location) + ", price: " + \
        str(self.price) + ", mortgage: " + str(self.mortgage)

class CommunityChest(Place):
    '''
    No specific data.
    '''
    def __repr__(self):
        return "Community Chest at pos " + str(self.location)

class Chance(Place):
    '''
    No specific data.
    '''
    def __repr__(self):
        return "Chance at pos " + str(self.location)

class Tax(Place):
    def __init__(self, name, placeType, option1, option2, text):
        '''
        Each tax location has a name or one or two taxation options, as
        some tax locations allow you to choose one of two alternatives.
        '''
        self.name = name
        self.placeType = placeType
        self.option1 = option1
        self.option2 = option2
        self.text = text
    def __repr__(self):
        return self.name + " at pos " + str(self.location)

class Jail(Place):
    '''
    This is the jail
    '''
    def __repr__(self):
        return "Jail at pos " + str(self.location)

class GoToJail(Place):
     '''
     Here you go to jail.
     '''
     def __repr__(self):
        return "Go To Jail at pos " + str(self.location)

class FreeParking(Place):
    '''
    This is the free parking corner.
    '''
    def __repr__(self):
        return "Free Parking at pos " + str(self.location)

class Start(Place):
    '''
    This is the starting corner.
    '''
    def __repr__(self):
        return "Start at pos " + str(self.location)

class CommunityCard(object):
    '''
    All comunity chest cards have a text description.
    These cards:
    - give or take cash from you; or 
    - move you to a new location; or
    - order you to make general repairs (USD 25 per house, USD 100 per hotel);
    - give you an out-of-jail ticket.
    '''
    def __init__(self, text, cardType, goStart, cash, jailcard, repairs, collect, goToJail):
        self.text = text
        self.cardType = cardType #?
        self.goStart = goStart # 0 or 1
        self.cash = cash # positive or negative int
        self.jailcard = jailcard # 0 or 1
        self.repairs = repairs # 0 or 1
        self.collect = collect # 0 or 1
        self.goToJail = goToJail # 0 or 1
    def __repr__(self):
        return "Community Card: " + self.text

class ChanceCard(object):
    '''
    Chance cards are generally similar to community chest cards, with several exceptions:
    - you advance to the neareast railroad and pay twice the rental or buy it from the bank;
    - take a ride on the Reading; if you pass go, collect 200.
    '''
    def __init__(self, text, cardType, movement, cash, jailcard, rail, repairs, goToJail, reading, goTo):
        self.text = text
        self.cardType = cardType #?
        self.movement = movement # int
        self.cash = cash
        self.jailcard = jailcard #0 or 1?
        self.rail = rail #boolean
        self.repairs = repairs #0 or 1
        self.goToJail = goToJail # 0 or 1
        self.reading = reading #0 or 1
        self.goTo = goTo # 0 or 1 if Start or string
    def __repr__(self):
        return "Chance Card: " + self.text
        
class Player(object):
    '''
    Each player is initialized with an amount of money and a starting position.
    '''
    location = 0
    doubles = 0 #how many doubles in a row
    inJail = False
    timeInJail = 0
    jailCommCards = 0
    jailChanceCards = 0
    def __init__ (self, name, cash, human = True):
        self.name = name
        self.cash = cash
        self.human = human
    def __repr__(self):
        return "Player " + self.name + ", human: " + str(self.human)

def Dice():
    import random
    a = random.randint(1, 6)
    b = random.randint(1, 6)
    return [a, b]

# import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'));
with ff as f:
    content = f.readlines()

#places = {}
board = []
communityChest = []
chances = []
currentComm = 0
currentChance = 0

for i in range(len(content)):
    line = content[i].rstrip().split("\t")
    if line[0] == "street":
        board.append(Street(line[12], line[0], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8]), int(line[9]), int(line[10]), line[11]))
    elif line[0] == "start":
        board.append(Start())
        board[i].placeType = line[0]
    elif line[0] == "chestL":
        board.append(CommunityChest())
        board[i].placeType = line[0]
    elif line[0] == "tax":
        board.append(Tax(line[3], line[0], line[1], line[2], line[4]))
    elif line[0] == "rail":
        board.append(Railroad(line[7], line[0], line[1], line[2], line[3], line[4], line[5], line[6]))
    elif line[0] == "chanceL":
        board.append(Chance())
        board[i].placeType = line[0]
    elif line[0] == "jail":
        board.append(Jail())
        board[i].placeType = line[0]
    elif line[0] == "utility":
        board.append(Utility(line[3], line[0], line[1], line[2]))
    elif line[0] == "park":
        board.append(FreeParking())
        board[i].placeType = line[0]
    elif line[0] == "gotojail":
        board.append(GoToJail())
        board[i].placeType = line[0]
    elif line[0] == "chest":
        communityChest.append(CommunityCard(line[7], line[0], line[1], line[2], line[3], line[4], line[5], line[6]))
    elif line[0] == "chance":
        chances.append(ChanceCard(line[9], line[0], line[1], line [2], line[3], line[4], line[5], line[6], line[7], line[8]))
    if line[0] in ["street", "start", "chestL", "tax", "rail", "chanceL", "jail", "utility", "park", "gotojail"]:
        board[i].location = i #useless?
        
    
#test: output  board, community cards and chance cards to output.txt
f = open(os.path.join(__location__, 'output.txt'), "w")
for i in range(len(board)):
    f.write(str(board[i]) + "\n")
for i in range(len(communityChest)):
    f.write(str(communityChest[i]) + "\n")
for i in range(len(chances)):
    f.write(str(chances[i]) + "\n")
f.close()

'''
Cheatopoly Game creation
'''

print "WELCOME TO CHEATOPOLY!!!"
print "You can play Cheatopoly in up to 6 players."
numberPlayers = 0
playerCash = 1500 #initial amount received by each player
while numberPlayers < 2 or numberPlayers > 6:
    try:
        numberPlayers = int(raw_input("Please enter a number of players between 2 and 6: "))
    except ValueError:
        print "Oops!  That was no valid number.  Try again..."

#Initialize players
players = []
for i in range(numberPlayers):
    name =  raw_input("Please enter the name of player " + str(i+1) + ": ")
    human = ''
    while human not in ["yes", "no"]:
        human = raw_input("Is the player human [yes/no]: ").lower()
    if human == "yes":
        human = True
    else:
        human = False
    players.append(Player(name, playerCash, human))

#Initialize bank
money = 15140 #although some rules say infinite money: https://en.wikibooks.org/wiki/Monopoly/Official_Rules
houses = 32 # https://en.wikibooks.org/wiki/Monopoly/Official_Rules
hotels = 12 # https://en.wikibooks.org/wiki/Monopoly/Official_Rules
bank =  Bank(money, houses, hotels)

currentPlayer = 0 # indicates current player
startWage = 200

while bank.money > 0 and len(players) > 1:
    #Roll dice
    dice = Dice()
    print "Dice roll for " + ": " +  str(dice[0]) + " " + str(dice[1])
    # resolve jail status (and advance to next position)
    if players[currentPlayer].inJail:
        if dice[0] == dice[1]:
            players[currentPlayer].inJail = False
            players[currentPlayer].timeInJail = 0
            players[currentPlayer].location = (players[currentPlayer].location + dice[0] + dice[1])% len(board)
            print players[currentPlayer].name + " has got a double: " + str(dice[0]) + " " +str(dice[1]) + ". Advance to position " + str(players[currentPlayer].location) + "."
        else:
            players[currentPlayer].timeInJail += 1
            choose = ''
            while choose not in ["yes", "no"]:
                choose = raw_input("Do you want to use a 'Get Out Of Jail' card? [yes/no] ").lower() #human
            if choose == 'yes':
                if players[currentPlayer].jailCommCards > 0 or players[currentPlayer].jailChanceCards > 0:
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
                   players[currentPlayer].inJail = False
                   players[currentPlayer].timeInJail = 0
                   players[currentPlayer].location = (players[currentPlayer].location + dice[0] + dice[1])% len(board)
                   print players[currentPlayer].name + " gets out of jail and advances to " + str(players[currentPlayer].location) + "."
                else:
                    print "Sorry, you have no 'Get Out Of Jail'cards."
                    choose = ''
                    while choose not in ["yes", "no"]:
                        choose = raw_input("Do you want to pay $50 to get out of jail[yes/no] ").lower() #human
                    if choose == 'yes':
                        if players[currentPlayer].cash >= 50:
                           players[currentPlayer].cash -= 50
                           players[currentPlayer].inJail = False
                           players[currentPlayer].timeInJail = 0
                           players[currentPlayer].location = (players[currentPlayer].location + dice[0] + dice[1])% len(board)
                           print players[currentPlayer].name + " pays $50 to get out of jail and advances to " + str(players[currentPlayer].location) + "."
                        else:
                            print "Sorry, you do not have enough cash to get out of jail."
            if players[currentPlayer].timeInJail == 3:
                players[currentPlayer].cash -= 50
                players[currentPlayer].inJail = False
                players[currentPlayer].timeInJail = 0
                players[currentPlayer].location = (players[currentPlayer].location + dice[0] + dice[1])% len(board)
                print players[currentPlayer].name + " pays $50 to get out of jail and advances to " + str(players[currentPlayer].location) + "."
    else:
        players[currentPlayer].location = (players[currentPlayer].location + dice[0] + dice[1])% len(board)
        print players[currentPlayer].name + " advances to " + str(players[currentPlayer].location) + "."
    #crossing start, +startWage/2*startWage
    if players[currentPlayer].location - dice[0] - dice[1] < 0:
        players[currentPlayer].cash += startWage
        print players[currentPlayer].name + " gets $" + str(startWage) + "."
    elif players[currentPlayer].location - dice[0] - dice[1] == 0:
        players[currentPlayer].cash += 2*startWage
        print players[currentPlayer].name + " is a lucky punk and gets $" + str(2*startWage) + "."
    # if lands on street, rail or utility:
    if board[players[currentPlayer].location].placeType in ["street", "rail", "utility"]:
        if board[players[currentPlayer].location].ownedBy == None:
            choose = ''
            while choose not in ["yes", "no"]:
                choose = raw_input(board[players[currentPlayer].location].name + " is currently available. Do you want to buy it? Summary: " + board[players[currentPlayer].location] + " [yes/no] ").lower() #human
            if choose == "yes" and players[currentPlayer].cash > board[players[currentPlayer].location].price:
                board[players[currentPlayer].location].newOwner(players[currentPlayer]) #assign new owner
                players[currentPlayer].cash -= board[players[currentPlayer].location].price
                bank.money += board[players[currentPlayer].location].price
                print "Congratulations, " + players[currentPlayer].name + " has bought: " +  board[players[currentPlayer].location] + "."
        else:
            pass #it is owned by someone!!!
    
    #- buy
    #- pay rent
    #-do nothing
    #if chest/chance/tax/jail/gotojail/freeparking, do required actions
    #Upgrade/downgrade houses/hotels
    #Negotiate with other players
    #Turn end: check if positive balance. if not, remove from game
    #Update display
    #currentPlayer += 1
    
    