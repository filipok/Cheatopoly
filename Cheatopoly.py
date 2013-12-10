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
    placeLocation = None #location of each place

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

class Player(object):
    '''
    Each player is initialized with an amount of money and a starting position.
    '''
    def __init__ (self, cash, location):
        self.cash = cash
        self.location = location

class Street(Place):
    '''
    Each street is a place and has a name and a price.
    The rent depends on the number of houses (0-4, plus a hotel) .
    The costs of the houses and hotels is specific to the street
    Also, there is a mortgage value and the street belongs to a neighborhood.
    '''
    def __init__(self, name, placeType, price, rent0, rent1, rent2, rent3, rent4, rentH, mortgage, houseCost, hotelCost, neighborhood):
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
        print self.name + "\n"
        print "Neighborhood: " + self.neighborhood + "\n"
        print "Rent: " + str(self.rent0) + "\n"
        print "With 1 House: " + str(self.rent1) + "\n"
        print "With 2 Houses: " + str(self.rent2) + "\n"
        print "With 3 Houses: " + str(self.rent3) + "\n"
        print "With 4 Houses: " + str(self.rent4) + "\n"
        print "With Hotel: " + str(self.rentH) + "\n"
        print "Mortgage Value: " + str(self.mortgage) + "\n"
        print "Houses Cost " + str(self.houseCost) + " each." + "\n"
        print "Hotels, " + str(self.houseCost) + " plus 4 houses" + "\n"
        return self.name + ", " + self.neighborhood
    
class Railroad(Place):
    '''
    Railroad rents depend on the number of railroads owned.
    There is also a mortgage value.
    The rents and mortgae values are identical for all railroads.
    They are still defined in __init__().
    '''
    def __init__(self, name, placeType, rent1, rent2, rent3, rent4, mortgage):
        self.name = name
        self.placeType = placeType
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.mortgage = mortgage
    
class Utility(Place):
    '''
    Utility rents depend on the dice values:
        - if one utility is owned, four times the dice value;
        - if both utilities are owned, 10 times the dice value.
    They also have a mortgage value.
    '''
    def __init__(self, name, placeType, mortgage):
        self.name = name
        self.placeType = placeType
        self.mortgage = mortgage

class CommunityChests(Place):
    '''
    No specific data.
    '''
    pass

class Chances(Place):
    '''
    No specific data.
    '''
    pass

class Taxes(Place):
    def __init__(self, name, option1, option2):
        '''
        Each tax location has a name or one or two taxation options, as
        some tax locations allow you to choose one of two alternatives.
        '''
        self.name = name
        self.option1 = option1
        self.option2 = option2

class Jail(Place):
    '''
    This is the jail
    '''
    pass

class GoToJail(Place):
     '''
     Here you go to jail.
     '''
     pass

class FreeParking(Place):
    '''
    This is the free parking corner.
    '''
    pass

class Start(Place):
    '''
    This is the starting corner.
    '''
    pass

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
        
# import data from data.txt
import os
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
ff = open(os.path.join(__location__, 'data.txt'));
with ff as f:
    content = f.readlines()

places = {}
for i in range(len(content)):
    line = content[i].rstrip().split("\t")
    if line[0] == "street":
        name = "pos" + str(i)
        places[name] = Street(line[12], line[0], int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8]), int(line[9]), int(line[10]), line[11])
        