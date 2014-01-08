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
    
def ReturnCardAndIncrement(cardSet, position, card):
        cardSet.insert(position, card)
        return PlusOne(position, len(cardSet))