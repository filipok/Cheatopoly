class Bank(object):
    '''
    In standard editions of Monopoly the Bank has USD 15,140.
    Source: http://boardgames.about.com/od/monopolyfaq/f/bank_money.htm
    '''
    def __init__(self, money):
        self.money = money

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
    Also, there is a mortgage value.
    '''
    def __init__(self, name, price, rent0, rent1, rent2, rent3, rent4, rentH, mortgage, houseCost, hotelCost):
        self.name = name
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
    def newOwner(self, player):
        #change street owner
        self.ownedBy = player
    
class Railroad(Place):
    '''
    Railroad rents depend on the number of railroads owned.
    There is also a mortgage value.
    The rents and mortgae values are identical for all railroads.
    They are still defined in __init__().
    '''
    def __init__(self, rent1, rent2, rent3, rent4, mortgage):
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
    def __init__(self, name, mortgage):
        self.name = name
        self.mortgage = mortgage

class ComunityChests(Place):
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
    - give you an out-of-jail ticket.
    '''
    def __init__(self, text, movement, cash, jailcard):
        self.text = text
        self.movement = movement #int
        self.cash = cash
        self.jailcard = jailcard #0 or 1?

class ChanceCard(object):
    '''
    Chance cards are generally similar to community chest cards, with several exceptions:
    - you advance to the neareast railroad and pay twice the rental or buy it from the bank;
    - you make general repairs (USD 25 per house, USD 100 per hotel);
    - take a ride on the Reading; if you pass go, collect 200.
    '''
    def __init__(self, text, movement, cash, jailcard, rail, repairs, reading):
        self.text = text
        self.movement = movement #int
        self.cash = cash
        self.jailcard = jailcard #0 or 1?
        self.rail = rail #boolean
        self.repairs = repairs #boolean
        self.reading = reading #boolean
