def Dice():
    import random
    a = random.randint(1, 6)
    b = random.randint(1, 6)
    return [a, b]

def TaxRate(option, player, board):
        '''
        A function to calculate taxes for a certain player and one tax system.
        It returns None when fed with the "None" option.
        '''
        if option[-1] == "%":
            taxrate = int(option[:-1])
            payment = player.cash * taxrate/100.0 #add percentage of cash
            for item in board:
                if item.ownedBy == player:
                    payment += item.price * taxrate/100.0
                    payment += item.hotels * item.hotelCost + item.houses * item.houseCost
            return int(payment)
        elif option == "None":
            return None
        else:
            return int(option)

def Repairs(houseCost, hotelCost, player, game):
    repairCost = 0
    for item in game.board:
        if item.ownedBy == player:
            repairCost += item.houses * houseCost + item.hotels * hotelCost
    player.cash -= repairCost
    game.bank.cardPayments += repairCost #money goes to table
    print "Your repair costs have amounted to $" + str(repairCost) + "."

def MoveMoney(amount, player, bank):
    #move money from/to player to/from bank
    player.cash += amount
    bank.money -= amount

def MoveMoneyToTable(amount, player, bank):
    #move money from player to table
    player.cash += amount
    bank.cardPayments -= amount

def PlusOne(location, length):
    return (location + 1) % length

def MoveTable(player, bank):
    #player gets money on the table
    print "Congratulations, " + player.name + "! You have landed on Free Parking!"
    print "You get $" + str(bank.cardPayments) + " from the community and chance card payments."
    player.cash += bank.cardPayments
    bank.cardPayments = 0

def choose_int(fro, to):
    choose = -1
    while choose < fro or choose > to:
        try:
            choose = int(raw_input("Enter number [" + str(fro) + " - "+ str(to) + "]: ")) #human
        except ValueError:
            print "Oops!  That was no valid number.  Try again..."
    return choose

def choose_yes_no(string):
    choose = ''
    while choose not in ["yes", "no"]:
        choose = raw_input(string).lower() #human
    return choose
                

def isOwnedAndMortgaged(item, player, condition):
    return item.ownedBy == player and item.mortgaged == condition
    
def BankAllowsUpgrade(item, bank):
    return (item.houses < 4 and bank.houses > 0) or \
    (item.houses == 4 and bank.hotels > 0)

def IsUpgradeable(item, myPlayer):
    return item.ownedBy == myPlayer and item.minUpgrade == item.houses and \
    item.hotels == 0 and \
    ((item.houses == 4 and item.hotelCost <= myPlayer.cash) or \
    (item.houses < 4 and item.houseCost <= myPlayer.cash))

def AllUpgradeConditions(item, bank, myPlayer):
    return IsUpgradeable(item, myPlayer) and BankAllowsUpgrade(item, bank)
    
def BankAllowsDowngrade(item, bank):
    return (item.hotels == 1 and bank.houses >= 4) or (item.hotels == 0 and bank.houses > 0)

def DowngradeHotel(player, item, bank):
    item.hotels = 0
    bank.houses -= 4
    bank.hotels += 1
    MoveMoney(item.hotelCost/2, player, bank)

def DowngradeHouse(player, item, bank):
    item.houses -= 1
    bank.houses += 1
    MoveMoney(item.houseCost/2, player, bank)
    
def UpgradeHouse(player, item, bank):
    item.houses += 1
    bank.houses -= 1
    MoveMoney(-item.houseCost, player, bank)

def UpgradeHotel(player, item, bank):
    item.hotels = 1
    bank.hotels -= 1
    bank.houses += 4
    MoveMoney(-item.hotelCost, player, bank)

def FlagUpgradeableLocations(player, neighborhoods):
    '''
    Flag upgradeable locations
    '''
    for neighborhood in neighborhoods.values():
        minUpgrade = 5
        for street in neighborhood:
            if street.ownedBy != player  or street.mortgaged:
                #restore to 5
                for street in neighborhood:
                    street.minUpgrade = 5
                minUpgrade = 5
                break
            else:
                if street.hotels == 0:
                    minUpgrade = min(minUpgrade, street.houses)
        for street in neighborhood:
            if street.ownedBy == player:
                street.minUpgrade = minUpgrade

def ReturnCardAndIncrement(cardSet, position, card):
        cardSet.insert(position, card)
        return PlusOne(position, len(cardSet))