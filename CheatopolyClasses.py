import random
import os
import pygame
import sys
from pygame.locals import *


class Game(object):
    """
    This class contains all game constants.
    """

    #Default values
    player_cash = 1500  # Initial amount received by each player
    money = 15140  # See https://en.wikibooks.org/wiki/Monopoly/Official_Rules
    houses = 32  # See https://en.wikibooks.org/wiki/Monopoly/Official_Rules
    hotels = 12  # See https://en.wikibooks.org/wiki/Monopoly/Official_Rules
    start_wage = 200  # What you get when you pass Go
    jail_fine = 50  # Cost to get out of jail
    collect_fine = 50  # Amount to collect from players with the Collect card
    chance_repairs = [25, 100]  # Cost of Chance repairs
    chest_repairs = [45, 115]  # Cost of Community Chest repairs

    #Counters
    current_comm = 0
    current_chance = 0
    current_player = 0  # current player index

    #Bank
    bank = None

    #Display
    square_side = 0
    height = 0
    width = 0
    background = None
    display = None

    #Player colors
    player_cols = [(255, 51, 51), (255, 153, 51), (255, 51, 153),
                   (153, 255, 51), (51, 255, 153, ), (51, 153, 255)]

    def __init__(self, height, width, background, display):
        self.neighborhoods = {}
        self.community_chest = []
        self.chances = []
        self.players = []
        self.board = []
        self.height = height
        self.width = width
        self.background = background
        self.display = display

    def load(self, file_name):

        """ Process file_name txt file

        @param file_name: the file name
        """
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        ff = open(os.path.join(__location__, file_name))
        with ff as f:
            content = f.readlines()
        for i in range(len(content)):
            line = content[i].rstrip().split("\t")
            if line[0] == "street":
                self.board.append(
                    Street(line[12], int(line[1]), int(line[2]), int(line[3]),
                           int(line[4]), int(line[5]), int(line[6]),
                           int(line[7]), int(line[8]), int(line[9]),
                           int(line[10]), line[11]))
                if line[11] in self.neighborhoods:
                    self.neighborhoods[line[11]].append(self.board[-1])
                else:
                    self.neighborhoods[line[11]] = [self.board[-1]]
            elif line[0] == "start":
                self.board.append(Start())
            elif line[0] == "chestL":
                self.board.append(CommunityChest())
            elif line[0] == "tax":
                self.board.append(Tax(line[3], line[1], line[2], line[4]))
            elif line[0] == "rail":
                self.board.append(
                    Railroad(line[7], int(line[1]), int(line[2]), int(line[3]),
                             int(line[4]), int(line[5]), int(line[6])))
            elif line[0] == "chanceL":
                self.board.append(Chance())
            elif line[0] == "jail":
                self.board.append(Jail())
            elif line[0] == "utility":
                self.board.append(Utility(line[3], int(line[1]), int(line[2])))
            elif line[0] == "park":
                self.board.append(FreeParking())
            elif line[0] == "gotojail":
                self.board.append(GoToJail())
            elif line[0] == "chest":
                self.community_chest.append(
                    CommunityCard(line[7], int(line[1]), int(line[2]),
                                  int(line[3]), int(line[4]), int(line[5]),
                                  int(line[6])))
            elif line[0] == "chance":
                self.chances.append(
                    ChanceCard(line[9], int(line[1]), int(line[2]),
                               int(line[3]), int(line[4]), int(line[5]),
                               int(line[6]), int(line[7]), line[8]))
            elif line[0] == "const":
                if line[1] == "playerCash":
                    self.player_cash = int(line[2])
                elif line[1] == "money":
                    self.money = int(line[2])
                elif line[1] == "houses":
                    self.houses = int(line[2])
                elif line[1] == "hotels":
                    self.hotels = int(line[2])
                elif line[1] == "startWage":
                    self.start_wage = int(line[2])
                elif line[1] == "jailFine":
                    self.jail_fine = int(line[2])
                elif line[1] == "collectFine":
                    self.collect_fine = int(line[2])
                elif line[1] == "chanceRepairsMin":
                    self.chance_repairs = [int(line[2])]
                elif line[1] == "chanceRepairsMax":
                    self.chance_repairs.append(int(line[2]))
                elif line[1] == "chestRepairsMin":
                    self.chest_repairs = [int(line[2])]
                elif line[1] == "chestRepairsMax":
                    self.chest_repairs.append(int(line[2]))
            if line[0] in ["street", "start", "chestL", "tax", "rail",
                           "chanceL", "jail", "utility", "park", "gotojail"]:
                self.board[i].location = i

    def initialize_players(self):
        print "Please enter a number of players between 2 and 6:"
        num_players = self.choose_int(2, 6)
        list_of_names = ['']
        for i in range(num_players):
            name = ''
            while name in list_of_names:
                name = raw_input(
                    "Please enter a unique name for player {0}: ".format(
                        str(i + 1)))
            human = self.choose_yes_no("Is the player human [yes/no]: ")
            if human == "yes":
                self.players.append(Player(name, self.player_cash, True,
                                           self.player_cols[i]))
            else:
                self.players.append(Cheatoid(name, self.player_cash, False,
                                             self.player_cols[i]))
            list_of_names.append(name)

    def mock_players(self):
        print "Please enter a number of Borg players between 2 and 6:"
        num_players = self.choose_int(2, 6)
        for i in range(num_players):
            name = "Borg{0}".format(str(i + 1))
            print "Adding " + name + "..."
            self.players.append(Cheatoid(name, self.player_cash, False,
                                         self.player_cols[i]))
        print self.players

    def buy_or_auction(self, choose, player, place):
        if choose == "yes":
            if player.cash > place.price:
                place.new_owner(player)  # Assign new owner
                self.bank.move_money(-place.price, player)
                print "Congratulations, " + player.name + \
                      "! You have bought: " + str(place) + "."
            else:
                print "Sorry, you do not have the required funds!"
                a = random.randint(1, 4)
                if a == 1:
                    print "Beggar...!"
                player.start_auction(self)  # Launch auction
        else:
            player.start_auction(self)  # Launch auction

    def flag_upgradeable_places(self, player):
        """ Flag upgradeable locations

        """
        for neighborhood in self.neighborhoods.values():
            min_upgrade = 5
            for street in neighborhood:
                if street.owned_by != player or street.mortgaged:
                    #restore to 5
                    for street in neighborhood:
                        street.min_upgrade = 5
                    min_upgrade = 5
                    break
                else:
                    if street.hotels == 0:
                        min_upgrade = min(min_upgrade, street.houses)
            for street in neighborhood:
                if street.owned_by == player:
                    street.min_upgrade = min_upgrade

    def tax_rate(self, option, player):
        """Function to calculate taxes for a certain player and one tax system
        It returns None when fed with the "None" option.

        """
        if option[-1] == "%":
            tax_percent = int(option[:-1])
            payment = player.cash * tax_percent / 100.0  # Add % of cash
            for item in self.board:
                if item.owned_by == player:
                    payment += item.price * tax_percent / 100.0
                    payment += item.hotels * item.hotel_cost + \
                        item.houses * item.house_cost
            return int(payment)
        elif option == "None":
            return None
        else:
            return int(option)

    def repairs(self, house_cost, hotel_cost, player):
        repair_cost = 0
        for item in self.board:
            if item.owned_by == player:
                repair_cost += item.houses * house_cost + \
                    item.hotels * hotel_cost
        player.cash -= repair_cost
        self.bank.card_payments += repair_cost  # Money goes to table
        print "Your repair costs have amounted to $" + str(repair_cost) + "."

    def check_eliminate(self, player):
        if player.cash < 0:
            print player.name + " HAS BEEN ELIMINATED!"
            for item in self.board:
                if isinstance(item, (Street, Railroad, Utility)) and \
                        item.owned_by == player:
                    item.owned_by = None
                    if item.hotels == 1:
                        item.hotels = 0
                        self.bank.hotels += 1
                        item.houses = 0
                    else:
                        self.bank.houses += item.houses
                        item.houses = 0
            self.players.pop(self.current_player)
            #no need to increment currentPlayer, but set to zero as needed
            if self.current_player == len(self.players):
                self.current_player = 0
        else:
            #currentPlayer += 1
            self.current_player = self.add_one(self.current_player,
                                               len(self.players))
    
    def turn_end(self):
        print ""
        print "***"
        for player in self.players:
            print player.name + " has $" + str(player.cash)
        print "The bank has got $" + str(self.bank.money) + \
            " left. There are " + str(self.bank.houses) + " houses and " + \
            str(self.bank.hotels) + " hotels available."
        print "There are $" + str(self.bank.card_payments) + \
            " left on the table."
        print "***"
        print ""        
    
    def game_end(self):
        if len(self.players) == 1:
            print self.players[0].name + " HAS WON THE GAME"
        else:
            best_score = 0
            best_player = None
            for person in self.players:
                if person.cash > best_score:
                    best_player = person
                    best_score = person.cash
            if best_player is not None:
                print best_player.name + " HAS WON THE GAME"
            else:
                print "INCREDIBLE BUNCH OF LOSERS."
    
    def set_places(self):
        # Find the length of the side of the board
        remainder = len(self.board) % 4
        if remainder == 0:
            side = len(self.board) / 4 + 1
        else:
            # increase the side of the square, with some empty places
            side = (len(self.board) + remainder)/4 + 1

        # Calculate place square size
        self.square_side = min(self.width, self.height) / side

        # Assign top/left positions for each Place
        left = 0
        up = 0
        orientation = "right"
        counter = 0
        for item in self.board:
                item.x = left
                item.y = up
                counter += 1
                if counter == side:
                    orientation = "down"
                elif counter == 2 * side - 1:
                    orientation = "left"
                elif counter == 3 * side - 2:
                    orientation = "up"
                if orientation == "right":
                    left += self.square_side
                elif orientation == "down":
                    up += self.square_side
                elif orientation == "left":
                    left -= self.square_side
                elif orientation == "up":
                    up -= self.square_side
        black = (0, 0, 0)
        white = (255, 255, 255)
        red = (255, 0, 0)
        green = (0, 255, 0)
        blue = (0, 0, 255)
        purple = (204, 0, 255)
        teal = (0, 128, 128)
        pink = (253, 221, 230)
        orange = (255, 165, 0)
        yellow = (255, 255, 0)
        brown = (150, 113, 23)
        army_green = (75, 83, 32)
        dark_green = (0, 100, 0)
        coldict = {'Black': black, 'White': white, 'Red': red, 'Green': green,
                   'Blue': blue, 'Purple': purple, 'Teal': teal, 'Pink': pink,
                   'Orange': orange, 'Yellow': yellow, 'Brown': brown,
                   'Army green': army_green, 'Dark_green': dark_green}
        for item in self.board:
            if isinstance(item, Street):
                item.col = coldict[item.neighborhood]
            elif isinstance(item, Railroad):
                item.col = brown
            elif isinstance(item, Utility):
                item.col = army_green
            elif isinstance(item, FreeParking):
                item.col = dark_green
            elif isinstance(item, GoToJail):
                item.col = dark_green
            else:
                item.col = white

    def draw_board(self):
        for item in self.board:
            item.draw(self.display, self)
        for player in self.players:
            player.draw(self.display, self)

    def roll_dice(self, player):
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        text = "Dice roll for " + player.name + ": " + str(a) + " " + str(b)
        message(self.display, text, self.background, min(self.height, self.width)/2, min(self.height, self.width)/2)
        return [a, b]


    def write_left(self, display, font_size, text, font_color, background,
                   center_tuple, left):
        font_obj = pygame.font.Font(None, font_size)
        text_surface_obj = font_obj.render(text, True, font_color, background)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = center_tuple
        text_rect_obj.left = left
        display.blit(text_surface_obj, text_rect_obj)

    def draw_stats(self):
        if self.width > self.height:
            i = 0
            #Draw player stats
            for player in self.players:
                if player.in_jail:
                    self.draw_doughnut(self.display, (0,0, 0), (0, 0, 0),
                                       self.height + 10, 10 + i*30, 10, 5, 1)
                self.write_left(self.display, 25,
                                player.name + ": $" + str(player.cash),
                                player.col, self.background,
                                (self.height + 80, 10 + i*30), self.height + 25)
                i += 1
            # Draw bank
            i += 1
            self.write_left(self.display, 20, "Bank: $" + str(self.bank.money),
                (0, 0, 0), self.background, (self.height + 80, 10 + i*30),
                self.height + 25)
            i += 1
            self.write_left(self.display, 20, "Houses: " + str(self.bank.houses),
                (0, 0, 0), self.background, (self.height + 80, 10 + i*30),
                self.height + 25)
            i += 1
            self.write_left(self.display, 20, "Hotels: " + str(self.bank.hotels),
                (0, 0, 0), self.background, (self.height + 80, 10 + i*30),
                self.height + 25)
            # Money on table
            i += 1
            self.write_left(self.display, 20, "On table: " +
                                         str(self.bank.card_payments),
                            (0, 0, 0), self.background, (self.height + 80, 10 + i*30),
                            self.height + 25)

    def draw_cards(self, card_set, ind, display, background):
        for i in range(len(card_set)):
            self.write_left(display, 14, card_set[i].text, (0, 0, 0),
                            background, (self.square_side + 20,
                                         self.square_side + 10 + i*12),
                            self.square_side + 20)
        pygame.draw.circle(display, (255, 0, 0),
                           (self.square_side + 5,
                            self.square_side + 10 + ind*12),
                           5, 0)

    def draw_doughnut(self, display, fill_col, edge_col, x, y, diam, thick_1,
                      thick_2):
        pygame.draw.circle(display, fill_col, (x, y), diam, thick_1)
        pygame.draw.circle(display, edge_col, (x, y), diam, thick_2)

    def start_turn(self, player):
        mouse_click = False
        message(self.display, "Hello, " + player.name +
                              ", click to begin turn",
                     (255, 0, 255), self.height/2, self.height/2)
        pygame.display.update()
        self.click_n_cover()


    def click_n_cover(self):
        mouse_click = False
        remainder = len(self.board) % 4
        side = (len(self.board) + remainder)/4 - 1
        while True:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONUP:
                        mouse_click = True
                if mouse_click:
                    pygame.draw.rect(self.display, self.background,
                                     (self.square_side, self.square_side,
                                      side*self.square_side,
                                      side*self.square_side))
                    pygame.display.update()
                    break

    def add_one(self, location, length):
        return (location + 1) % length

    def choose_int(self, fro, to):
        """Choose an integer number within an interval

        @rtype : int
        """
        choose = -1
        while choose < fro or choose > to:
            try:
                choose = int(raw_input(
                    "Enter number [{0} - {1}]: ".format(str(fro), str(
                        to))))
            except ValueError:
                print "Oops!  That was no valid number.  Try again..."
        return choose

    def yes_no(self, text, button_size):
        red = (255, 0, 0)
        green = (0, 255, 0)
        x = min(self.width, self.height)/2
        y = x
        #draw yes/no boxes
        message(self.display, text, self.background, x, y + 20)
        yes_box = pygame.draw.rect(self.display, green, (x - int(button_size*1.5),
                                                    y + 40, button_size,
                                                    button_size))
        no_box = pygame.draw.rect(self.display, red, (x + int(button_size*0.5),
                                                 y + 40, button_size,
                                                 button_size))
        pygame.display.update()
        #detect click
        mouse_x = 0
        mouse_y = 0
        while True:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONUP:
                        mouse_x, mouse_y = event.pos
                        #check click
                        if yes_box.collidepoint(mouse_x, mouse_y):
                            return "yes"
                        if no_box.collidepoint(mouse_x, mouse_y):
                            return "no"



    def choose_yes_no(self, string):
        choose = ''
        while choose not in ["yes", "no"]:
            choose = raw_input(string).lower()
        return choose

    def return_card_and_add(self, card_set, position, card):
        card_set.insert(position, card)
        return self.add_one(position, len(card_set))


class Bank(object):
    """
    In standard editions of Monopoly the Bank has USD 15,140.
    Source: http://boardgames.about.com/od/monopolyfaq/f/bank_money.htm
    """

    #payments made by players as defined in community/chance cards are
    #cumulated into this account and are paid to the first player getting to
    #Free Parking
    card_payments = 0

    def __init__(self, game):
        self.money = game.money
        self.houses = game.houses
        self.hotels = game.hotels

    def move_money(self, amount, player):
        #move money from/to player to/from bank
        player.cash += amount
        self.money -= amount

    def move_money_to_table(self, amount, player):
        #move money from player to table
        player.cash += amount
        self.card_payments -= amount

    def move_table(self, player):
        #player gets money on the table
        print "Congratulations, " + player.name + \
              "! You have landed on Free Parking!"
        print "You get ${0} from the community & chance card payments.".format(
            str(self.card_payments))
        player.cash += self.card_payments
        self.card_payments = 0


class Place(object):
    """
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
    """
    location = None
    owned_by = None
    mortgaged = False
    houses = 0
    hotels = 0
    hotel_cost = 0
    house_cost = 0
    x = 0
    y = 0
    col = None
    txt = ""

    def write(self, text, font_size, col, background, lines, line_height,
              display, game):
        font_obj = pygame.font.Font(None, font_size)
        text_surface_obj = font_obj.render(text, True, col, background)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = (self.x + game.square_side/2,
                                self.y + lines*line_height)
        display.blit(text_surface_obj, text_rect_obj)

    def draw(self, display, game):
        # Draw place rectangle
        pygame.draw.rect(display, self.col,
                         (self.x, self.y, game.square_side, game.square_side))
        # Draw street owner color, if any
        if self.owned_by is not None and isinstance(self, Street):
            pygame.draw.rect(display, self.owned_by.col,
                             (self.x,
                              self.y + game.square_side - game.square_side/2,
                              game.square_side, game.square_side/2))
        # Draw central text
        col = (0, 0, 0)
        if isinstance(self, GoToJail) or isinstance(self, Jail) or \
                isinstance(self, Chance):
            col = (255, 0, 0)
        if isinstance(self, Railroad) or isinstance(self, Utility):
            y_pos = game.square_side/2 + 5
        else:
            y_pos = game.square_side/2
        self.write(self.txt, 40, col, self.col, 1, y_pos, display, game)
        # Draw railroad/utility owner color, if any
        if self.owned_by is not None and isinstance(self, (Railroad, Utility)):
            pygame.draw.rect(display, self.owned_by.col,
                             (self.x,
                              self.y + game.square_side - game.square_side/4,
                              game.square_side, game.square_side/4))

        # Draw community chest symbol
        if isinstance(self, CommunityChest):
            pygame.draw.circle(display, (255, 247, 0),
                               (self.x + game.square_side/2,
                                self.y + game.square_side/2),
                               game.square_side/2, game.square_side/2)
        # Draw place names and split it as necessary
        background = self.col
        if self.owned_by is not None:
            col = (255, 255, 255)
        if isinstance(self, Street) or isinstance(self, Utility) or \
                isinstance(self, Railroad):
            name_split = self.name.split(" ")
            name_end = name_split[-1]
            name_begin = " ".join(name_split[:-1])
            line_height = 5
            lines = 1
            if len(name_begin) != 0:
                self.write(name_begin, 10, col, background, lines, line_height,
                           display, game)
                lines += 1
            self.write(name_end, 10, col, background, lines, line_height,
                       display, game)
        # Draw street houses and hotels
        if isinstance(self, Street):
            for i in range(4):
                if self.houses >= i + 1:
                    col = (111, 255, 255)  # Indigo
                else:
                    col = (0, 0, 0)
                pygame.draw.rect(display, col, (self.x + i*game.square_side/4,
                                                self.y + game.square_side -
                                                game.square_side/4,
                                                game.square_side/4 - 1,
                                                game.square_side/4 - 1))
            if self.hotels == 1:
                col = (111, 255, 255)  # Indigo
            else:
                col = (0, 0, 0)
            pygame.draw.rect(display, col, (self.x,
                                            self.y + game.square_side -
                                            game.square_side/2,
                                            game.square_side,
                                            game.square_side/4 - 1))

    def new_owner(self, player):
        #change place owner
        self.owned_by = player

    def owned_and_mortgaged_by(self, player):
        return self.owned_by == player and self.mortgaged

    def owned_and_not_mortgaged_by(self, player):
        return self.owned_by == player and not self.mortgaged


class Street(Place):
    """Each street is a place and has a name and a price.
    The rent depends on the number of houses (0-4, plus a hotel) .
    The costs of the houses and hotels is specific to the street
    Also, there is a mortgage value and the street belongs to a neighborhood.
    Initially there are no houses or hotels on the street.

    """

    min_upgrade = 5

    def __init__(self, name, price, rent0, rent1, rent2, rent3, rent4, rent_h,
                 mortgage, house_cost, hotel_cost, neighborhood):
        self.name = name
        self.price = price
        self.rent0 = rent0
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.rent_h = rent_h
        self.mortgage = mortgage
        self.house_cost = house_cost
        self.hotel_cost = hotel_cost
        self.neighborhood = neighborhood

    def rent(self, game):
        if self.hotels == 1:
            return self.rent_h
        elif self.houses == 4:
            return self.rent4
        elif self.houses == 3:
            return self.rent3
        elif self.houses == 2:
            return self.rent2
        elif self.houses == 1:
            return self.rent1
        else:
            #Ifno hotels, no houses:
            #check for ownership of an entire neighborhood
            for item in game.neighborhoods[self.neighborhood]:
                if item.owned_by != self.owned_by:
                    return self.rent0
            return 2 * self.rent0

    def downgrade_hotel(self, player, bank):
        self.hotels = 0
        bank.houses -= 4
        bank.hotels += 1
        bank.move_money(self.hotel_cost / 2, player)

    def downgrade_house(self, player, bank):
        self.houses -= 1
        bank.houses += 1
        bank.move_money(self.house_cost / 2, player)

    def upgrade_house(self, player, bank):
        self.houses += 1
        bank.houses -= 1
        bank.move_money(-self.house_cost, player)

    def upgrade_hotel(self, player, bank):
        self.hotels = 1
        bank.hotels -= 1
        bank.houses += 4
        bank.move_money(-self.hotel_cost, player)

    def is_upgradeable_by(self, player):
        return self.owned_by == player and \
            self.min_upgrade == self.houses and self.hotels == 0 and \
            ((self.houses == 4 and self.hotel_cost <= player.cash) or
            (self.houses < 4 and self.house_cost <= player.cash))

    def bank_allows_upgrade(self, bank):
        return (self.houses < 4 and bank.houses > 0) or \
            (self.houses == 4 and bank.hotels > 0)

    def all_upgrade_conditions(self, bank, player):
        return self.is_upgradeable_by(player) and \
            self.bank_allows_upgrade(bank)

    def bank_allows_downgrade(self, bank):
        return (self.hotels == 1 and bank.houses >= 4) or (
            self.hotels == 0 and bank.houses > 0)

    def __repr__(self):
        return self.name + ", " + self.neighborhood + " (" + \
            str(self.location) + "), $: " + str(self.price) + ", r: " + \
            str(self.rent1) + ", " + str(self.rent2) + ", " + \
            str(self.rent3) + ", " + str(self.rent4) + ", " + \
            str(self.rent_h) + ", m: " + str(self.mortgage) + ", h+: " + \
            str(self.house_cost) + ", H+: " + str(self.hotel_cost) + \
            ", h: " + str(self.houses) + ", H: " + str(self.hotels)


class Railroad(Place):
    """
    Railroad rents depend on the number of railroads owned.
    There is also a mortgage value.
    The rents and mortgage values are identical for all railroads.
    They are still defined in __init__().
    """

    def __init__(self, name, price, rent1, rent2, rent3, rent4, mortgage):
        self.name = name
        self.price = price
        self.rent1 = rent1
        self.rent2 = rent2
        self.rent3 = rent3
        self.rent4 = rent4
        self.mortgage = mortgage
        self.txt = "R"

    def rent(self, game):
        counter = 0
        for item in game.board:
            if isinstance(item, Railroad) and item.owned_by == self.owned_by:
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
            str(self.price) + ", rents: " + str(self.rent1) + " " + \
            str(self.rent2) + " " + str(self.rent3) + " " + str(self.rent4) + \
            ", mortgage: " + str(self.mortgage) + "; demortgage: " + \
            str(int(self.mortgage * 1.1))


class Utility(Place):
    """
    Utility rents depend on the dice values:
        - if one utility is owned, four times the dice value;
        - if both utilities are owned, 10 times the dice value.
    They also have a mortgage value.
    """

    def __init__(self, name, price, mortgage):
        self.name = name
        self.price = price
        self.mortgage = mortgage
        self.txt = "W"

    def rent(self, game):
        print "Let us roll the dice for rent!"
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        print "Dice: " + str(a) + " " + str(b)
        counter = 0
        for item in game.board:
            if isinstance(item, Utility) and item.owned_by == self.owned_by:
                counter += 1
        if counter == 1:
            return 4 * (a + b)
        else:
            return 10 * (a + b)

    def __repr__(self):
        return self.name + " (" + str(self.location) + "), price: " + \
            str(self.price) + ", mortgage: " + str(self.mortgage) + \
            "; demortgage: " + str(int(self.mortgage * 1.1))


class CommunityChest(Place):
    """
    No specific data.
    """
    name = "Community Chest"

    def __repr__(self):
        return "Community Chest at pos {0}".format(str(self.location))


class Chance(Place):
    """
    No specific data.
    """
    name = "Chance"

    def __init__(self):
        self.txt = "?"

    def __repr__(self):
        return "Chance at pos {0}".format(str(self.location))


class Tax(Place):
    def __init__(self, name, option1, option2, text):
        """
        Each tax location has a name or one or two taxation options, as
        some tax locations allow you to choose one of two alternatives.
        """
        self.name = name
        self.option1 = option1
        self.option2 = option2
        self.text = text
        self.txt = "$"

    def __repr__(self):
        return self.name + " at pos " + str(self.location)


class Jail(Place):
    """
    This is the jail
    """
    name = "Jail"

    def __init__(self):
        self.txt = "X"

    def __repr__(self):
        return "Jail at pos {0}".format(str(self.location))


class GoToJail(Place):
    """
     Here you go to jail.
     """
    name = "Go To Jail"

    def __init__(self):
        self.txt = "->"

    def __repr__(self):
        return "Go To Jail at pos {0}".format(str(self.location))


class FreeParking(Place):
    """
    This is the free parking corner.
    """
    name = "Free Parking"

    def __init__(self):
        self.txt = "FP"

    def __repr__(self):
        return "Free Parking at pos {0}".format(str(self.location))


class Start(Place):
    """
    This is the starting corner.
    """
    name = "Start"

    def __init__(self):
        self.txt = "GO"

    def __repr__(self):
        return "Start at pos {0}".format(str(self.location))


class CommunityCard(object):
    """
    All community chest cards have a text description.
    These cards:
    - give or take cash from you; or
    - move you to a new location; or
    - order you to make general repairs (USD 25 per house, USD 100 per hotel);
    - give you an out-of-jail ticket.
    """

    def __init__(self, text, go_start, cash, jail_card, repairs, collect,
                 go_to_jail):
        self.text = text
        self.go_start = go_start  # 0 or 1
        self.cash = cash  # Positive or negative int
        self.jail_card = jail_card  # 0 or 1
        self.repairs = repairs  # 0 or 1
        self.collect = collect  # 0 or 1
        self.go_to_jail = go_to_jail  # 0 or 1

    def __repr__(self):
        return "Community Card: " + self.text


class ChanceCard(object):
    """
    Chance cards are generally similar to community chest cards,
    with several added features:
    - you advance to the nearest railroad and pay twice the rental or buy it
    from the bank;
    - take a ride on the some_rail name; if you pass go, collect 200.
    """

    def __init__(self, text, movement, cash, jail_card, rail, repairs,
                 go_to_jail, some_rail, go_to):
        self.text = text
        self.movement = movement  # Integer
        self.cash = cash
        self.jail_card = jail_card  # 0 or 1?
        self.rail = rail  # Boolean
        self.repairs = repairs  # 0 or 1
        self.go_to_jail = go_to_jail  # 0 or 1
        self.some_rail = some_rail  # 0 or 1
        self.go_to = go_to  # 0 / 1 if Start / string; also used for some_rail

    def __repr__(self):
        return "Chance Card: " + self.text


class Player(object):
    """
    Each player is initialized with an amount of money and a starting position.
    """
    human = True
    location = 0
    doubles = 0  # How many doubles in a row
    in_jail = False
    time_in_jail = 0
    jail_comm_cards = 0
    jail_chance_cards = 0
    doubles_in_a_row = 0
    double_rent = 1  # 1 or 2; flag for the chance card sending to next R.R.
    teleport = 0  # Indicates whether the player was sent over by a Chance card
    in_auction = False  # Used for auctions
    col = None  # Player color
    #Random position variation
    x_rand = 0
    y_rand = 0

    def __init__(self, name, cash, human, col):
        self.name = name
        self.cash = cash
        self.human = human
        self.col = col

    def draw(self, display, game):
        game.draw_doughnut(display, self.col, (0, 0, 0),
                           game.board[self.location].x + game.square_side/2 +
                           self.x_rand,
                           game.board[self.location].y + game.square_side/2 +
                           self.y_rand,
                           10, 5, 1)

    def move_to_jail(self, game):
        print self.name + " goes to JAIL!"
        #find next jail (you can have several, if you ask me)
        search_jail = self.location
        while not isinstance(game.board[search_jail], Jail):
            search_jail = (search_jail + 1) % len(game.board)
        self.location = search_jail
        self.in_jail = True

    def mortgage(self, game):
        print "List of properties that you can mortgage:"
        for item in game.board:
            if item.owned_and_not_mortgaged_by(self) and item.houses == 0:
                print item
        choose = game.choose_int(0, len(game.board) - 1)
        if game.board[choose].owned_and_not_mortgaged_by(self) and \
                game.board[choose].houses == 0:
            game.bank.move_money(game.board[choose].mortgage, self)
            game.board[choose].mortgaged = True
            print "You have successfully mortgaged " + game.board[
                choose].name + "."

    def demortgage(self, game):
        print "List of properties that you can demortgage:"
        for item in game.board:
            if item.owned_and_mortgaged_by(self):
                print item
        choose = game.choose_int(0, len(game.board) - 1)
        if game.board[choose].owned_and_mortgaged_by(self) and \
                self.cash >= int(game.board[choose].mortgage * 1.1):
            game.bank.move_money(-int(game.board[choose].mortgage * 1.1), self)
            game.board[choose].mortgaged = False
            print "You have successfully demortgaged " + \
                  game.board[choose].name + "."

    def downgrade(self, game):
        print "List of properties that you can downgrade:"
        for item in game.board:
            if item.owned_and_not_mortgaged_by(self) and \
                    item.houses > 0 and item.bank_allows_downgrade(game.bank):
                print item
        choose = game.choose_int(0, len(game.board) - 1)
        if game.board[choose].owned_and_not_mortgaged_by(self) and \
                game.board[choose].houses > 0 and game.board[
                choose].bank_allows_downgrade(game.bank):
            if game.board[choose].hotels == 1:
                game.board[choose].downgrade_hotel(self, game.bank)
            else:
                game.board[choose].downgrade_house(self, game.bank)
            print "You have downgraded " + game.board[choose].name + "."

    def upgrade(self, game):
        #Flag the upgradeable locations
        game.flag_upgradeable_places(self)
        #Print the upgradeable locations
        print self.name + ", these are the locations you can upgrade now:"
        for item in game.board:
            if isinstance(item, Street) and item.all_upgrade_conditions(
                    game.bank, self):
                print item
        choose = game.choose_int(0, len(game.board) - 1)
        if isinstance(game.board[choose], Street) and game.board[
                choose].all_upgrade_conditions(game.bank, self):
            if game.board[choose].houses < 4:
                game.board[choose].upgrade_house(self, game.bank)
            else:
                game.board[choose].upgrade_hotel(self, game.bank)
            print "You have successfully upgraded " + game.board[
                choose].name + "."
            #restore to 5
        for item in game.board:
            if isinstance(item, Street):
                item.min_upgrade = 5

    def choose_action(self):
        return raw_input("Do you want to " +
                         "[u]pgrade/[d]owngrade/[m]ortgage/d[e]mortgage/do " +
                         "[n]othing? ").lower()

    def reply_to_auction(self, player, game, auction_price):
        print "Hello," + self.name + "! " + player.name + " did not buy " + \
              game.board[player.location].name + \
              ". Do you want to buy it instead? Last price is " + \
              str(auction_price) + ". Enter your price below."
        return game.choose_int(0, max(self.cash, 0))

    def start_auction(self, game):
        #set auction flag
        print "Starting auction..."
        for person in game.players:
            person.in_auction = True
        auction_running = True
        auction_price = 0
        best_candidate = None
        while auction_running:
            still_in_play = 0
            for person in game.players:
                if person.in_auction and person != best_candidate:
                    choose = person.reply_to_auction(self, game, auction_price)
                    if isinstance(choose, int) and choose > auction_price:
                        best_candidate = person
                        auction_price = choose
                        still_in_play += 1
                    else:
                        person.in_auction = False
            if still_in_play == 0:
                auction_running = False
        if best_candidate is None:
            print "Sadly, nobody wants that place."
        else:
            print "Congratulations, " + best_candidate.name + \
                  "! You have bought " + game.board[self.location].name + \
                  " for $" + str(auction_price) + "."
            game.bank.move_money(-auction_price, best_candidate)
            game.board[self.location].new_owner(best_candidate)  # New owner

    def buy(self, game):
        text = "Wanna buy {}?".format(game.board[self.location].name)
        button_size = 40
        return game.yes_no(text, button_size)

    def use_jail_card(self, game):
        return game.choose_yes_no(
            "Do you want to use a 'Get Out Of Jail' card? [yes/no] ")

    def pay_jail_fine(self, game,display, background, x, y):
        text = "Pay $" + str(game.jail_fine) + " to leave jail?"
        return game.yes_no(text, 40)

    def reset_jail(self):
        self.in_jail = False
        self.time_in_jail = 0
        self.doubles_in_a_row = 0

    def return_card_leave_jail(self, game):
        #return community/chance card back to the pile
        if self.jail_comm_cards > self.jail_chance_cards:
            to_add = CommunityCard("Get out of jail, free", 0, 0, 1, 0, 0, 0)
            self.jail_comm_cards -= 1
            game.current_comm = game.return_card_and_add(game.community_chest,
                                                         game.current_comm,
                                                         to_add)
        else:
            to_add = ChanceCard("Get out of jail free", 0, 0, 1, 0, 0, 0, 0, 0)
            self.jail_chance_cards -= 1
            game.current_chance = game.return_card_and_add(game.chances,
                                                           game.current_chance,
                                                           to_add)
        self.reset_jail()
        print self.name + " gets out of jail."

    def pay_rent(self, place, game):
        rent_due = place.rent(game)
        if self.double_rent == 2:
            rent_due *= 2  # Rent is doubled when sent by Chance card to a R.R.
            self.double_rent = 1
        if not place.mortgaged:
            print place.name + " is owned by " + place.owned_by.name + \
                ", you (" + self.name + ") must pay rent amounting to: " + \
                str(rent_due) + "."
            self.cash -= rent_due
            place.owned_by.cash += rent_due
        else:
            print place.name + " is owned by " + place.owned_by.name + \
                ", but is mortgaged and you pay nothing."

    def pay_tax(self, place, game):
        #Yyou can pay either a lump sum or a percentage of total assets.
        #Sometimes, the second option can be "None"
        tax1 = game.tax_rate(place.option1, self)
        tax2 = game.tax_rate(place.option2, self)
        if tax1 is None or tax2 is None:
            tax = max(tax1, tax2)
        else:
            tax = min(tax1, tax2)
        print "Well done, " + self.name + ", you pay taxes amounting to: $" + \
              str(tax)
        game.bank.move_money_to_table(-tax, self)

    def move_to_start(self, game):
        self.location = 0
        game.bank.move_money(game.start_wage, self)
        print "You go to Start and only receive $" + str(game.start_wage)

    def pay_card_money(self, cash, game):
        if cash > 0:
            game.bank.move_money(cash, self)
        else:
            game.bank.move_money_to_table(cash, self)

    def check_common_cards(self, game, card_set, repairs_0, repairs_1,
                           card_ind, flag):
        if card_set[card_ind].cash != 0:
            self.pay_card_money(card_set[card_ind].cash, game)
        elif card_set[card_ind].jail_card == 1:
            self.jail_comm_cards += 1
            #remove card & decrease index,to compensate for increase after IF
            card_set.pop(card_ind)
            if flag == "comm":
                game.current_comm = (card_ind + len(card_set) - 1) % \
                    len(card_set)
            else:
                game.current_chance = (card_ind + len(card_set) - 1) % \
                    len(card_set)
        elif card_set[card_ind].go_to_jail == 1:
            self.move_to_jail(game)
        elif card_set[card_ind].repairs == 1:
            game.repairs(repairs_0, repairs_1, self)
    
    def check_specific_chance(self, game):
        if game.chances[game.current_chance].some_rail == 1:
            #find rail location, if any, and move there
            destination = self.location  # Variable initialization
            for item in game.board:
                # rail name is stored in go_to
                if item.name == game.chances[game.current_chance].go_to:
                    destination = item.location
                    break
            if destination < self.location:
                print "You pass Go and collect $" + str(game.start_wage) +\
                      "."
                game.bank.move_money(game.start_wage, self)
            self.location = destination
            print "You move to " + game.chances[game.current_chance].go_to + \
                  ", at location " + str(destination) + "."
            self.teleport = 1
        elif game.chances[game.current_chance].movement != 0:
            self.location = (self.location + len(game.board) +
                             game.chances[game.current_chance].movement) % \
                len(game.board)
            self.teleport = 1
        elif game.chances[game.current_chance].rail == 1:
            counter = 0
            self.double_rent = 2
            while not isinstance(game.board[self.location], Railroad):
                self.location = game.add_one(self.location, len(game.board))
                counter += 1
                if counter == len(game.board):
                    self.double_rent = 1  # Back to normal rent
                    print "Rail not found!"
                    break  # Rail not found, back again to original location
            print "You have moved to: " + game.board[self.location].name + \
                  ", at pos " + str(self.location) + "."
            self.teleport = 1
        elif game.chances[game.current_chance].go_to != "0":
            if game.chances[game.current_chance].go_to == "1":
                self.move_to_start(game)
            else:
                for item in game.board:
                    if item.name == game.chances[
                            game.current_chance].go_to:
                        #you get $200 if you pass Go.
                        if self.location > item.location:
                            game.bank.move_money(game.start_wage,
                                                 self)
                            print "You get $" + str(game.start_wage)
                        self.location = item.location
                        break
                print "You move to " + game.board[self.location].name + \
                      " at pos " + str(self.location) + "."
                self.teleport = 1

    def check_jail(self, game, dice, display, background, x, y):
        # Resolve jail status
        if self.in_jail:  # Check for doubles while in jail
            if dice[0] == dice[1]:
                self.reset_jail()
                print self.name + " has got a double: " + str(dice[0]) + \
                    " " + str(dice[1]) + "."
            else:
                self.time_in_jail += 1
        #Else use a get ouf of jail card
        if self.in_jail and \
                max(self.jail_comm_cards, self.jail_chance_cards) > 0:
            choose = self.use_jail_card(game)
            if choose == 'yes':
                self.return_card_leave_jail(game)
        #Else pay
        if self.in_jail and self.cash >= game.jail_fine:
            choose = self.pay_jail_fine(game, display, background, x, y)
            if choose == 'yes':
                game.bank.move_money(-game.jail_fine, self)
                self.reset_jail()
                print self.name + " pays $" + str(game.jail_fine) + \
                    " to get out of jail."
        #Else if already three turns in jail:
        if self.time_in_jail == 3:
            game.bank.move_money(-game.jail_fine, self)
            self.reset_jail()
            print self.name + " pays anyway $" + str(game.jail_fine) +\
                " to get out of jail after three turns."
    
    def check_specific_comm(self, game):
        if game.community_chest[game.current_comm].collect == 1:
            for person in game.players:
                if person != self:
                    person.cash -= game.collect_fine
                    self.cash += game.collect_fine
                    print person.name + " pays $" + \
                        str(game.collect_fine) + " to " + self.name + \
                        "."
        elif game.community_chest[game.current_comm].go_start == 1:
            self.move_to_start(game)

    def __repr__(self):
        return "Player " + self.name + ", human: " + str(self.human)


def message(display, text, background, x, y):
    print text
    font_obj = pygame.font.Font(None, 20)
    text_surface_obj = font_obj.render(text, True, (0,0,0), background)
    text_rect_obj = text_surface_obj.get_rect()
    text_rect_obj.center = (x, y)
    display.blit(text_surface_obj, text_rect_obj)
    pygame.display.update()


class Cheatoid(Player):
    """
    The computer player class is a subclass of the player class with specific
    methods.
    """
    human = False
    successful_downgrade = True
    successful_mortgage = True
    successful_upgrade = True
    successful_demortgage = True

    def mortgage(self, game):
        """
        Changes mortgage status
        """
        self.successful_mortgage = False
        for item in game.board:
            if item.owned_and_not_mortgaged_by(self) and item.houses == 0:
                game.bank.move_money(item.mortgage, self)
                item.mortgaged = True
                print self.name + " has mortgaged " + item.name + "."
                self.successful_mortgage = True
                break

    def demortgage(self, game):
        """
        Changes mortgage status
        """
        self.successful_demortgage = False
        for item in reversed(game.board):
            if item.owned_and_mortgaged_by(self) and \
                    self.cash >= int(item.mortgage * 1.1):
                game.bank.move_money(-int(item.mortgage * 1.1), self)
                item.mortgaged = False
                print self.name + " has demortgaged " + item.name + "."
                self.successful_demortgage = True
                break

    def downgrade(self, game):
        """
        Changes house/hotel values
        """
        self.successful_downgrade = False
        for item in game.board:
            if item.owned_by == self and item.hotels == 1:
                item.downgrade_hotel(self, game.bank)
                print self.name + " has downgraded " + item.name + "."
                self.successful_downgrade = True
                break
            elif item.owned_by == self and item.houses > 0:  # For streets: > 0
                item.downgrade_house(self, game.bank)
                print self.name + " has downgraded " + item.name + "."
                self.successful_downgrade = True
                break

    def upgrade(self, game):
        """
        Changes house/hotel values
        """
        self.successful_upgrade = False
        #Flag the upgradeable locations
        game.flag_upgradeable_places(self)
        level = 0
        upgrade_done = False
        while not upgrade_done and level < 5:
            for item in game.board:
                if isinstance(item, Street) and item.owned_by == self and \
                        item.houses == level and item.all_upgrade_conditions(
                        game.bank, self):
                    #upgrade
                    if level < 4:
                        item.upgrade_house(self, game.bank)
                        print self.name + " has successfully upgraded " + \
                            item.name + "."
                        upgrade_done = True
                        self.successful_upgrade = True
                    elif item.hotels == 0:
                        item.upgrade_hotel(self, game.bank)
                        print self.name + " has successfully upgraded " + \
                            item.name + "."
                        upgrade_done = True
                        self.successful_upgrade = True
            level += 1
            #restore to 5
        for item in game.board:
            if isinstance(item, Street):
                item.min_upgrade = 5

    def choose_action(self):
        """
        Computer chooses between [u]pgrade / [d]owngrade / [m]ortgage /
        d[e]mortgage / do [n]othing
        Returns "u"/"d"/"m"/"e"/"n"
        """
        if self.cash < 0 and self.successful_downgrade:
            return "d"
        if self.cash < 0 and not self.successful_downgrade and \
                self.successful_mortgage:
            return "m"
        if self.cash > 125 and self.successful_demortgage:
            return "e"
        if self.cash > 125 and not self.successful_demortgage and \
                self.successful_upgrade:
            return "u"
            #at the very end
        self.successful_downgrade = True
        self.successful_mortgage = True
        self.successful_upgrade = True
        self.successful_demortgage = True
        return "n"

    def reply_to_auction(self, other, game, auction_price):
        """
        Returns a new auction price (int)

        Check whether other players own something in the neighborhood.
        If yes,then aim low.
        If not, then aim high.
        """
        my_neighborhood = True
        for neighborhood in game.neighborhoods.values():
            if game.board[other.location] in neighborhood:
                for street in neighborhood:
                    if street.owned_by is not None and street.owned_by != self:
                        my_neighborhood = False
                break
        a = random.randint(-game.board[other.location].price / 10,
                           game.board[other.location].price / 10)
        if isinstance(game.board[other.location], Street) and my_neighborhood:
            reply = min(auction_price + 1,
                        game.board[other.location].rent_h + a, self.cash)
        else:
            reply = min(auction_price + 1,
                        game.board[other.location].price + a, self.cash)
        print self.name + " bids " + str(reply) + "."
        return reply

    def buy(self, game, display, background, x, y):
        """
        Returns "yes"/"no"
        """
        return "yes"  # The Cheatoid always tries to buy

    def use_jail_card(self, game):
        """
        Returns "yes"/"no"
        The main program already checks whether the player has a jail card.
        Here the computer only tests the cost-effectiveness of its use.
        It's worthy when there are many free places and few opponent places.
        """
        mine = 0
        empty = 0
        theirs = 0
        for item in game.board:
            if isinstance(item, (Street, Railroad, Utility)):
                if item.owned_by is None:
                    empty += 1
                elif item.owned_by == self:
                    mine += 1
                else:
                    theirs += 1
        if len(game.players) < 4 and empty > 0 and self.cash > 125 and \
                game.bank.hotels > 8:  # Rudimentary
            return "yes"
        else:
            return "no"  # Better stay in jail

    def pay_jail_fine(self, game,display, background, x, y):
        """
        Returns "yes"/"no"
        """
        return self.use_jail_card(game)  # The easy way

    def __repr__(self):
        return "Player " + self.name + " is NOT human."