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
                    if item.placeType == "street":
                        payment += item.hotels * item.hotelCost + item.houses * item.houseCost
            return int(payment)
        elif option == "None":
            return None
        else:
            return int(option)

def MoveToJail(player, board):
            print player.name + " goes to JAIL!"
            #find next jail (you can have several, if you ask me)
            searchJail = player.location
            while board[searchJail].placeType !="jail":
                searchJail = (searchJail + 1) % len(board)
            player.location = searchJail
            player.inJail = True

def Repairs(houseCost, hotelCost, player, board, bank):
    repairCost = 0
    for item in board:
        if item.ownedBy == player and item.placeType == "street":
            repairCost += item.houses * houseCost + item.hotels * hotelCost
    player.cash -= repairCost
    bank.cardPayments += repairCost #money goes to table
    print "Your repair costs have amounted to $" + str(repairCost) + "."

def MoveMoney(amount, player, bank):
    #move money from/to player to/from bank
    player.cash += amount
    bank.money -= amount

def MoveMoneyToTable(amount, player, bank):
    #move money from player to table
    player.cash += amount
    bank.cardPayments -= amount

def MoveTable(player, bank):
    #player gets money on the table
    print "Congratulations, " + player.name + "! You have landed on Free Parking!"
    print "You get $" + str(bank.cardPayments) + " from the community and chance card payments."
    player.cash += bank.cardPayments
    bank.cardPayments = 0


def ResetJail(player):
    player.inJail = False
    player.timeInJail = 0
    player.doublesInARow = 0