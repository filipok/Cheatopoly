def Dice():
    import random
    a = random.randint(1, 6)
    b = random.randint(1, 6)
    return [a, b]

def PlusOne(location, length):
    return (location + 1) % length

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
    bank.MoveMoney(item.hotelCost/2, player)

def DowngradeHouse(player, item, bank):
    item.houses -= 1
    bank.houses += 1
    bank.MoveMoney(item.houseCost/2, player)
    
def UpgradeHouse(player, item, bank):
    item.houses += 1
    bank.houses -= 1
    bank.MoveMoney(-item.houseCost, player)

def UpgradeHotel(player, item, bank):
    item.hotels = 1
    bank.hotels -= 1
    bank.houses += 4
    bank.MoveMoney(-item.hotelCost, player)

def ReturnCardAndIncrement(cardSet, position, card):
        cardSet.insert(position, card)
        return PlusOne(position, len(cardSet))