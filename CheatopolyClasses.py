from CheatopolyFunctions import *

class Bank(object):
    '''
    In standard editions of Monopoly the Bank has USD 15,140.
    Source: http://boardgames.about.com/od/monopolyfaq/f/bank_money.htm
    There is also a limited number of houses and hotels.[how many?]
    '''
    #payments made by players as defined in community/chance cards are 
    #cumulated into this account and are paid to the first player getting to
    #Free Parking
    cardPayments = 0
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
    location = None
    ownedBy = None
    mortgaged = False
    houses = 0
    hotels = 0
    hotelCost = 0
    houseCost = 0


class Street(Place):
    '''
    Each street is a place and has a name and a price.
    The rent depends on the number of houses (0-4, plus a hotel) .
    The costs of the houses and hotels is specific to the street
    Also, there is a mortgage value and the street belongs to a neighborhood.
    '''
    #initially there are no houses or hotels on the street
    minUpgrade = 5
    def __init__(self, name, price, rent0, rent1, rent2, rent3, \
    rent4, rentH, mortgage, houseCost, hotelCost, neighborhood):
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
        self.neighborhood = neighborhood
    def newOwner(self, player):
        #change street owner
        self.ownedBy = player
    def rent(self,neighborhoods,board):
        if self.hotels == 1:
            return self.rentH
        elif self.houses == 4:
            return self.rent4
        elif self.houses == 3:
            return self.rent3
        elif self.houses == 2:
            return self.rent2
        elif self.houses == 1:
            return self.rent1
        else:
            #no hotels,no houses:
            #check for ownership of entire neighborhood
            for item in neighborhoods[self.neighborhood]:
                if item.ownedBy != self.ownedBy:
                    return self.rent0
            return 2*self.rent0
            
    def __repr__(self):
        return self.name + ", " + self.neighborhood + " (" + \
        str(self.location) + "), $: " + str(self.price) + ", r: " + \
        str(self.rent1) + ", " + str(self.rent2) + ", " + str(self.rent3) + \
        ", " + str(self.rent4) + ", " + str(self.rentH) + ", m: " + \
        str(self.mortgage) + ", h+: " +  str(self.houseCost) + \
        ", H+: " + str(self.hotelCost) + ", h: " + str(self.houses) + \
        ", H: " + str(self.hotels)
    
class Railroad(Place):
    '''
    Railroad rents depend on the number of railroads owned.
    There is also a mortgage value.
    The rents and mortgage values are identical for all railroads.
    They are still defined in __init__().
    '''
    def __init__(self, name, price, rent1, rent2, rent3, rent4, \
    mortgage):
        self.name = name
        self.price = price
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.mortgage = mortgage
    def newOwner(self, player):
        #change railroad owner
        self.ownedBy = player
    def rent(self,neighborhoods, board):
        counter = 0
        for item in board:
            if isinstance(item, Railroad) and item.ownedBy == self.ownedBy:
                counter += 1
        if counter == 4:
            return self.rent4
        elif counter == 3:
            return self.rent3
        elif counter == 2:
            return self.rent2
        else:
            return self.rent1
    def __repr__(self):
        return self.name + " (" + str(self.location) + "), price: " + \
        str(self.price) + ", rents: " + str(self.rent1) + " " +  \
        str(self.rent2) + " " + str(self.rent3) + " " + str(self.rent4) + \
        ", mortgage: " + str(self.mortgage) + "; demortgage: " + \
        str(int(self.mortgage * 1.1))
    
class Utility(Place):
    '''
    Utility rents depend on the dice values:
        - if one utility is owned, four times the dice value;
        - if both utilities are owned, 10 times the dice value.
    They also have a mortgage value.
    '''
    def __init__(self, name, price, mortgage):
        self.name = name
        self.price = price
        self.mortgage = mortgage
    def newOwner(self, player):
        #change utility owner
        self.ownedBy = player
    def rent(self,neighborhoods, board):
        print "Let us roll the dice for rent!"
        dice = Dice()
        print "Dice: " +  str(dice[0]) + " " + str(dice[1])
        counter = 0
        for item in board:
            if isinstance(item, Utility) and item.ownedBy == self.ownedBy:
                counter += 1
        if counter == 1:
            return 4 * (dice[0] + dice[1])
        else:
            return 10 * (dice[0] + dice[1])
    def __repr__(self):
        return self.name +  " (" + str(self.location) + "), price: " + \
        str(self.price) + ", mortgage: " + str(self.mortgage) + \
        "; demortgage: " + str(int(self.mortgage * 1.1))

class CommunityChest(Place):
    '''
    No specific data.
    '''
    name = "Community Chest"
    def __repr__(self):
        return "Community Chest at pos " + str(self.location)

class Chance(Place):
    '''
    No specific data.
    '''
    name = "Chance"
    def __repr__(self):
        return "Chance at pos " + str(self.location)

class Tax(Place):
    def __init__(self, name, option1, option2, text):
        '''
        Each tax location has a name or one or two taxation options, as
        some tax locations allow you to choose one of two alternatives.
        '''
        self.name = name
        self.option1 = option1
        self.option2 = option2
        self.text = text
    def __repr__(self):
        return self.name + " at pos " + str(self.location)

class Jail(Place):
    '''
    This is the jail
    '''
    name = "Jail"
    def __repr__(self):
        return "Jail at pos " + str(self.location)

class GoToJail(Place):
     '''
     Here you go to jail.
     '''
     name = "Go To Jail"
     def __repr__(self):
        return "Go To Jail at pos " + str(self.location)

class FreeParking(Place):
    '''
    This is the free parking corner.
    '''
    name = "Free Parking"
    def __repr__(self):
        return "Free Parking at pos " + str(self.location)

class Start(Place):
    '''
    This is the starting corner.
    '''
    name = "Start"
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
    def __init__(self, text, goStart, cash, jailcard, repairs, collect, goToJail):
        self.text = text
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
    def __init__(self, text, movement, cash, jailcard, rail, repairs, goToJail, reading, goTo):
        self.text = text
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
    doublesInARow = 0
    doubleRent = 1# 1 or 2; flag for the chance card sending to next R.R.
    teleport =0 #indicates if the player was sent over by a Chance card
    inAuction = False #used for auctions
    
    def __init__ (self, name, cash, human = True):
        self.name = name
        self.cash = cash
        self.human = human
    
    def MoveToJail(self, board):
            print self.name + " goes to JAIL!"
            #find next jail (you can have several, if you ask me)
            searchJail = self.location
            while not isinstance(board[searchJail], Jail):
                searchJail = (searchJail + 1) % len(board)
            self.location = searchJail
            self.inJail = True
    
    def Mortgage(self, board, bank):
        print "List of properties that you can mortgage:"
        for item in board:
            if isOwnedAndMortgaged(item, self, False) and item.houses == 0:
                print item
        choose = choose_int(0, len(board) - 1) #human
        if isOwnedAndMortgaged(board[choose], self, False) and board[choose].houses == 0:
            MoveMoney(board[choose].mortgage, self, bank)
            board[choose].mortgaged = True
            print "You have successfully mortgaged " + board[choose].name + "."
    
    def Demortgage(self, board, bank):
        print "List of properties that you can demortgage:"
        for item in board:
            if isOwnedAndMortgaged(item, self, True):
                print item
        choose = choose_int(0, len(board) - 1) #human
        if isOwnedAndMortgaged(board[choose], self, True) and \
        self.cash >= int(board[choose].mortgage * 1.1):
            MoveMoney(-int(board[choose].mortgage * 1.1), self, bank)
            board[choose].mortgaged = False
            print "You have successfully demortgaged " + board[choose].name + "."
    
    def Downgrade(self, board, bank):
        print "List of properties that you can downgrade:"
        for item in board:
            if isOwnedAndMortgaged(item, self, False) and \
            item.houses > 0 and BankAllowsDowngrade(item, bank):
                print item
        choose = choose_int(0, len(board) - 1) #human        
        if isOwnedAndMortgaged(board[choose], self, False) and \
        board[choose].houses > 0 and BankAllowsDowngrade(board[choose], bank):
            if board[choose].hotels == 1:
                board[choose].hotels = 0
                bank.houses -= 4
                bank.hotels += 1
                MoveMoney(board[choose].hotelCost/2, self, bank)
            else:
                board[choose].houses -= 1
                bank.houses += 1
                MoveMoney(board[choose].houseCost/2, self, bank)
            print "You have downgraded " + board[choose].name + "."
    
    def Upgrade(self, neighborhoods, board, bank):
        #Flag the upgradeable locations
        for neighborhood in neighborhoods.values():
            minUpgrade = 5
            for street in neighborhood:
                if street.ownedBy != self  or street.mortgaged:
                    #restore to 5
                    for street in neighborhood:
                        street.minUpgrade = 5
                    minUpgrade = 5
                    break
                else:
                    if street.hotels == 0:
                        minUpgrade = min(minUpgrade, street.houses)
            for street in neighborhood:
                if street.ownedBy == self:
                    street.minUpgrade = minUpgrade
        #Print the upgradeable locations
        print "Hey , " + self.name + "! These are the locations you can upgrade now:"
        for item in board:
            if isinstance(item, Street) and AllUpgradeConditions(item, bank, self):
                print item
        choose = choose_int(0, len(board) - 1) #human
        if  isinstance(board[choose], Street) and AllUpgradeConditions(board[choose], bank, self):
            if board[choose].houses < 4:
                board[choose].houses += 1
                bank.houses -= 1
                MoveMoney(-board[choose].houseCost, self, bank)
            else:
                board[choose].hotels = 1
                bank.hotels -= 1
                bank.houses += 4
                MoveMoney(-board[choose].hotelCost, self, bank)
            print "You have successfully upgraded " + board[choose].name + "."
        #restore to 5
        for item in board:
            if isinstance(item, Street):
                item.minUpgrade = 5

    def ChooseAction(self):
        return raw_input("Do you want to [u]pgrade/[d]owngrade/[m]ortgage/d[e]mortgage/do [n]othing? ").lower() #human
    
    def ReplyToAuction(self, player, board, auctionPrice, money):
        print "Hello,"+ self.name + "! " + player.name + " did not buy " + board[player.location].name + ". Do you want to buy it instead? Last price is " + str(auctionPrice) + ". Enter your price below."
        return choose_int(0, max(self.cash, 0))#money=max bank money
    
    def StartAuction(self, players, board, money, bank):
        #set auction flag
        print "Starting auction..."
        for person in players:
            person.inAuction = True
        self.inAuction = False
        auctionRunning = True
        auctionPrice = 0 # the auction starts from zero
        bestCandidate = None
        while auctionRunning:
            stillInPlay = 0
            for person in players:
                if person.inAuction and person != bestCandidate:
                    choose = person.ReplyToAuction(self, board, auctionPrice, money)
                    if choose > auctionPrice:
                        bestCandidate = person
                        auctionPrice = choose
                        stillInPlay += 1
                    else:
                        person.inAuction = False
            if stillInPlay == 0:
                auctionRunning = False
        if bestCandidate == None:
            print "Sadly, nobody wants that place."
        else:
            print "Congratulations, " + bestCandidate.name + "! You have bought " + board[self.location].name + " for $" + str(auctionPrice) + "."
            MoveMoney(-auctionPrice, bestCandidate, bank)
            board[self.location].newOwner(bestCandidate)#assign new owner
 
    def Buy(self, board):
        message = "Hey, {}! {} is currently available and you have ${}. Do you want to buy it? Summary: {} [yes/no] ".format(self.name, board[self.location].name, str(self.cash), str(board[self.location]))
        return choose_yes_no(message)
    
    def UseJailCard(self):
        return choose_yes_no("Do you want to use a 'Get Out Of Jail' card? [yes/no] ")
    
    def PayJailFine(self, jailFine):
        return choose_yes_no("Do you want to pay $" + str(jailFine) + " to get out of jail[yes/no] ")
    
    def __repr__(self):
        return "Player " + self.name + ", human: " + str(self.human)
