import random
import os
import pygame
import pygame.locals as loc


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

    #Trade
    sell = []
    buy = []
    trade_cash = 0

    #Player colors
    player_cols = [(255, 51, 51), (153, 255, 51), (51, 153, 255),
                   (255, 153, 51), (51, 255, 153, ), (255, 51, 153)]

    def __init__(self, height, width, background, display, line_height,
                 font_size):
        self.neighborhoods = {}
        self.community_chest = []
        self.chances = []
        self.players = []
        self.board = []
        self.height = height
        self.width = width
        self.background = background
        self.display = display
        self.line_height = line_height
        self.font_size = font_size

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

    def choose_six(self):
        #message
        central = min(self.width, self.height)/2
        message(self.display,
                "Choose a number of players", self.background,
                central, self.height/4)
        blue = (0, 0, 255)
        width = 60
        step = 40
        #buttons
        two = self.button("2", blue, central - width/2,
                          self.height/4 + step, width, step - 10)
        three = self.button("3", blue, central - width/2,
                            self.height/4 + 2*step, width, step - 10)
        four = self.button("4", blue, central - width/2,
                           self.height/4 + 3*step, width, step - 10)
        five = self.button("5", blue, central - width/2,
                           self.height/4 + 4*step, width, step - 10)
        six = self.button("6", blue, central - width/2,
                          self.height/4 + 5*step, width, step - 10)
        pygame.display.update()
        #detect click and return
        while True:
            for event in pygame.event.get():
                if event.type == loc.MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    if two.collidepoint(mouse_x, mouse_y):
                        return 2
                    if three.collidepoint(mouse_x, mouse_y):
                        return 3
                    if four.collidepoint(mouse_x, mouse_y):
                        return 4
                    if five.collidepoint(mouse_x, mouse_y):
                        return 5
                    if six.collidepoint(mouse_x, mouse_y):
                        return 6

    def initialize_players(self):
        self.cover()
        num_players = self.choose_six()
        self.cover()
        list_of_names = ['']
        green = (0, 255, 0)
        red = (255, 0, 0)
        middle = min(self.width, self.height)/2
        for i in range(num_players):
            self.button("", green, middle - 50, (i+1)*self.height/8 + 10, 100,
                        20)
        pygame.display.update()
        for i in range(num_players):
            # draw name box and enter name
            name = self.capture_word((i+1)*self.height/8 + 10)
            # draw human/not human dialog
            human = self.draw_yes_no("Human?", 20, green, red, middle + 90,
                                     (i+1)*self.height/8 - 30)
            if human == "yes":
                self.players.append(Player(name, self.player_cash, True,
                                           self.player_cols[i]))
            else:
                self.players.append(Cheatoid(name, self.player_cash, False,
                                             self.player_cols[i]))
            list_of_names.append(name)

    def mock_players(self):
        self.cover()
        num_players = self.choose_six()
        for i in range(num_players):
            name = "Borg{0}".format(str(i + 1))
            self.players.append(Cheatoid(name, self.player_cash, False,
                                         self.player_cols[i]))
        print self.players

    def buy_or_auction(self, choose, player, place):
        if choose == "yes":
            if player.cash > place.price:
                place.new_owner(player)  # Assign new owner
                self.bank.move_money(-place.price, player)
                place.draw(self)
                for person in self.players:
                    person.draw(self)
                pygame.display.update()
                self.cover_n_central(
                    player.name + ", you have bought " + place.name + ".")
                self.visual_refresh()

            else:
                self.cover_n_central(
                    "Sorry, you do not have the required funds!")
                a = random.randint(1, 4)
                if a == 1:
                    self.cover_n_central("Beggar...!")
                player.start_auction(self)  # Launch auction
                self.visual_refresh()
        else:
            player.start_auction(self)  # Launch auction
            self.visual_refresh()

    def draw_players(self):
        for player in self.players:
            player.draw(self)
            pygame.display.update()

    def flag_upgradeable_places(self, player):
        """ Flag upgradeable locations

        """
        for neighborhood in self.neighborhoods.values():
            min_upgrade = 5
            for street in neighborhood:
                if street.owned_by != player or street.mortgaged:
                    #restore to 5
                    for strt in neighborhood:
                        strt.min_upgrade = 5
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
        self.cover_n_central(
            "Your repair costs have amounted to $" + str(repair_cost) + ".")

    def check_eliminate(self, player):
        if player.cash < 0:
            self.cover_n_central(player.name + " HAS BEEN ELIMINATED!")
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
    
    def game_end(self):
        self.visual_refresh()
        if len(self.players) == 1:
            self.cover_n_central(self.players[0].name + " HAS WON THE GAME")
        else:
            best_score = 0
            best_player = None
            for person in self.players:
                if person.cash > best_score:
                    best_player = person
                    best_score = person.cash
            if best_player is not None:
                self.cover_n_central(best_player.name + " HAS WON THE GAME")
            else:
                self.cover_n_central("INCREDIBLE BUNCH OF LOSERS.")
        self.click_n_cover()
    
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
                item.orientation = orientation
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
            item.draw(self)
        for player in self.players:
            player.draw(self)

    def roll_dice(self, player):
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        text = "Dice roll for " + player.name + ": " + str(a) + " " + str(b)
        self.central_message(text)
        pygame.time.wait(1000)
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
                    self.draw_doughnut(self.display, (0, 0, 0), (0, 0, 0),
                                       self.height + 10, 10 + i*30, 10, 5, 1)
                self.write_left(self.display, 25,
                                player.name + ": $" + str(player.cash),
                                player.col, self.background,
                                (self.height + 80, 10 + i*30),
                                self.height + 25)
                i += 1
            # Draw bank
            i += 1
            self.write_left(self.display, 20, "Bank: $" + str(self.bank.money),
                            (0, 0, 0), self.background, (self.height + 80,
                                                         10 + i*30),
                            self.height + 25)
            i += 1
            self.write_left(self.display, 20, "Houses: " +
                                              str(self.bank.houses), (0, 0, 0),
                            self.background, (self.height + 80, 10 + i*30),
                            self.height + 25)
            i += 1
            self.write_left(self.display, 20, "Hotels: " +
                                              str(self.bank.hotels), (0, 0, 0),
                            self.background, (self.height + 80, 10 + i*30),
                            self.height + 25)
            # Money on table
            i += 1
            self.write_left(self.display, 20, "On table: " +
                                              str(self.bank.card_payments),
                            (0, 0, 0), self.background, (self.height + 80,
                                                         10 + i*30),
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

    def visual_refresh(self):
        self.display.fill(self.background)
        self.draw_board()
        self.draw_stats()
        pygame.display.update()

    def start_turn(self, player):
        message(self.display, "Hello, " + player.name +
                              ", click to begin turn",
                (255, 0, 255), self.height/2, self.height/2)
        pygame.display.update()
        self.click_n_cover()

    def click_n_cover(self):
        mouse_click = False
        while True:
                for event in pygame.event.get():
                    if event.type == loc.MOUSEBUTTONUP:
                        mouse_click = True
                if mouse_click:
                    self.cover()
                    break

    def wait_n_cover(self, milliseconds):
        pygame.time.wait(milliseconds)
        self.cover()

    def cover(self):
        remainder = len(self.board) % 4
        side = (len(self.board) + remainder)/4 - 1
        pygame.draw.rect(self.display, self.background,
                         (self.square_side + 1,
                          self.square_side + 1,
                          side*self.square_side - 1,
                          side*self.square_side - 1))
        pygame.display.update()

    def central_message(self, text):
        message(self.display, text, self.background,
                min(self.height, self.width)/2, min(self.height, self.width)/2)

    def cover_n_central(self, text):
        self.cover()
        self.central_message(text)
        pygame.time.wait(1000)

    def choose_place(self):
        choose = None
        while True:
            for event in pygame.event.get():
                if event.type == loc.MOUSEBUTTONUP:
                    m_x, m_y = event.pos
                    for item in self.board:
                        if item.x <= m_x <= item.x + self.square_side and \
                                item.y <= m_y <= item.y + self.square_side:
                            choose = item.location
                            break
            if choose is not None:  # Need valid location
                self.cover()
                break
        return choose

    def add_one(self, location, length):
        return (location + 1) % length

    def draw_yes_no(self, text, button_size, col_yes, col_no, x, y):
        message(self.display, text, self.background, x, y + 20)
        yes_box = pygame.draw.rect(self.display, col_yes,
                                   (x - int(button_size*1.5), y + 40,
                                    button_size, button_size))
        no_box = pygame.draw.rect(self.display, col_no,
                                  (x + int(button_size*0.5), y + 40,
                                   button_size, button_size))
        pygame.display.update()
        while True:
                for event in pygame.event.get():
                    if event.type == loc.MOUSEBUTTONUP:
                        mouse_x, mouse_y = event.pos
                        #check click
                        if yes_box.collidepoint(mouse_x, mouse_y):
                            return "yes"
                        if no_box.collidepoint(mouse_x, mouse_y):
                            return "no"

    def yes_no(self, text, button_size):
        red = (255, 0, 0)
        green = (0, 255, 0)
        x = min(self.width, self.height)/2
        y = x
        #draw yes/no boxes
        return self.draw_yes_no(text, button_size, green, red, x, y)

    def button(self, text, box_color, left, up, width, thickness):
        text_box = pygame.draw.rect(self.display, box_color,
                                    (left, up, width, thickness))
        message(self.display, text, box_color, left + width/2,
                up + thickness/2)
        pygame.display.update()
        return text_box

    def trade_board(self, sell, x, player_left, player_right):
        message(self.display, "Time to trade!", self.background, x,
                self.height/5 - 20)
        message(self.display, player_left.name, self.background, x/2,
                self.height/5)
        message(self.display, player_right.name, self.background,
                x + x/2, self.height/5)
        message(self.display, "You give:", self.background,
                x/2, self.height/5 + 20)
        for i in range(len(sell)):
            item = sell[i]
            if isinstance(item, (Street, Railroad, Utility)):
                message(self.display, item.name, self.background, x/2,
                        self.height/5 + 20*(2 + i))
            else:
                print "$" + str(item)

    def sell_list(self, sell, x):
        for i in range(len(sell)):
            item = sell[i]
            message(self.display, item.name, self.background, x,
                    self.height/5 + 20*(2 + i))

    def player_arrows(self, player):
        for item in self.board:
            if item.owned_by == player and item.houses == 0:
                item.draw_arrow(self)

    def choose_places(self, central, seller, buyer, player, place_list, text):
        red = (255, 0, 0)
        button_w = 120
        self.cover()
        self.trade_board(self.sell, central, seller, buyer)
        self.sell_list(self.sell, central/2)
        self.sell_list(self.buy, central + central/2)
        self.player_arrows(player)
        enough = self.button(text, red, central - button_w/2,
                             self.height - 3*self.square_side, button_w, 30)
        pygame.display.update()

        while True:
            exit_loop = False
            for event in pygame.event.get():
                if event.type == loc.MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    if enough.collidepoint(mouse_x, mouse_y):
                        exit_loop = True
                        break
                    for item in self.board:
                        if item.x <= mouse_x <= item.x + self.square_side and \
                                item.y <= mouse_y <= item.y + self.square_side:
                            if not item.in_trade and item.owned_by == player \
                                    and item.houses == 0:
                                item.in_trade = True
                                place_list.append(item)
                            elif item.in_trade and item.owned_by == player:
                                item.in_trade = False
                                place_list.remove(item)
                            self.cover()
                            self.trade_board(self.sell, central, seller, buyer)
                            self.sell_list(self.sell, central/2)
                            self.sell_list(self.buy, central + central/2)
                            self.player_arrows(player)
                            enough = self.button(
                                text, red, central - button_w/2,
                                self.height - 3*self.square_side, button_w, 30)
                            pygame.display.update()
                            break
            if exit_loop:
                break

    def move_table(self, player):
        #player gets money on the table
        self.cover_n_central("Congratulations, " + player.name +
                             "! You have landed on Free Parking!")
        self.cover_n_central(
            "You get ${0} from the community & chance card payments.".format(
                str(self.bank.card_payments)))
        player.cash += self.bank.card_payments
        self.bank.card_payments = 0

    def capture_word(self, y_pos):
        name = ""
        green = (0, 255, 0)
        central = min(self.width, self.height)/2
        while True:
            for event in pygame.event.get():
                if event.type == loc.KEYDOWN:
                    if event.unicode.isalpha():
                        name += event.unicode
                        self.button(name, green,
                                    central - max(10*len(name), 100)/2, y_pos,
                                    max(10*len(name), 100), 20)
                    elif event.key == loc.K_BACKSPACE:
                        #cover the button
                        self.button("", self.background,
                                    central - max(10*len(name), 100)/2, y_pos,
                                    max(10*len(name), 100), 20)
                        name = name[:-1]
                        self.button(name, green,
                                    central - max(10*len(name), 100)/2, y_pos,
                                    max(10*len(name), 100), 20)
                    elif event.key == loc.K_RETURN and len(name) > 0:
                        return name

    def add_values(self, value, item_list):
        for item in item_list:
            if isinstance(item, Street):
                value += item.rent_h
            if isinstance(item, Railroad):
                value += item.rent4
            if isinstance(item, Utility):
                value += 70
        return value

    def neighb_value(self, neighborhood):
        value = 0
        for street in neighborhood:
            value += street.rent_h
        return value

    def display_trade_cash(self, player_1, player_2, central, button_w):
        left = self.button(
            "Gives: " + str(max(-self.trade_cash, 0)), player_1.col,
            central/2 - button_w/4, self.height - 3*self.square_side,
            button_w/2, 30)
        right = self.button(
            "Gives: " + str(max(self.trade_cash, 0)), player_2.col,
            central + central/2 - button_w/4, self.height - 3*self.square_side,
            button_w/2, 30)

    def transfer_properties(self, initiator, chosen_one):
        # Transfer properties
        for item in self.sell:
            item.owned_by = chosen_one
        for item in self.buy:
            item.owned_by = initiator
        # Transfer cash
        initiator.cash += self.trade_cash
        chosen_one.cash -= self.trade_cash
        self.cover_n_central("Processing trade...")
        self.visual_refresh()

    def robot_negotiate(self, receiver, sender):
        receiver_value = 0
        sender_value = 0
        # Check for complete neighborhoods
        for item in self.buy:
            #find neighborhood
            my_neighborhood = None
            for neighborhood in self.neighborhoods.values():
                for street in neighborhood:
                    if street == item:
                        my_neighborhood = neighborhood
            if my_neighborhood is not None:
                # 1. Do not dismantle own neighborhood
                all_mine = True
                for street in my_neighborhood:
                    if street.owned_by != receiver:
                        all_mine = False
                if all_mine:
                    return False
                # 2. Don't give streets used by opponent to finish neighborhood
                # in 25% of the cases (sometimes the cheatoid is stubborn)
                all_their = True
                for street in my_neighborhood:
                    if street.owned_by != sender and street not in self.buy:
                        all_their = False
                if all_their and random.randint(1, 4) == 1:
                    return False

        # Calculate how many neighborhoods each player gains from exchange
        old_mine_c, new_mine_c, old_theirs_c, new_theirs_c, receiver_value, \
            sender_value = \
            self.compute_neighborhoods(
                receiver, sender, receiver_value, sender_value)
        # Reject outright if other player gets more neighborhoods (1 vs 0 etc)
        if new_mine_c - old_mine_c < new_theirs_c - old_theirs_c:
            return False
        # Parse sell/buy lists
        receiver_value += self.add_values(receiver_value, self.sell)
        sender_value += self.add_values(sender_value, self.buy)
        # Add trade_cash
        sender_value += self.trade_cash
        # Compare values
        result = receiver_value - sender_value
        # Add some random element
        result -= random.randint(0, int(receiver_value/4))
        return result > 0

    def show_trade(self, initiator, receiver):
        central = min(self.width, self.height)/2
        self.cover_n_central(
            initiator.name + " wants to trade with " + receiver.name)
        message(self.display, receiver.name + "would get:", self.background,
                central - central/2, self.height/5 + 20)
        self.sell_list(self.sell, central - central/2)
        message(self.display, initiator.name + " would get:", self.background,
                central + central/2, self.height/5 + 20)
        self.sell_list(self.buy, central + central/2)
        if self.trade_cash < 0:
            message(self.display, receiver.name + " would also get $" +
                    str(-self.trade_cash), self.background, central,
                    self.height/3)
        elif self.trade_cash > 0:
            message(self.display, initiator.name + " would also get $" +
                    str(self.trade_cash), self.background, central,
                    self.height/3)

    def compute_neighborhoods(self, receiver, sender, receiver_value,
                              sender_value):
        old_mine_c = 0
        new_mine_c = 0
        old_theirs_c = 0
        new_theirs_c = 0
        for neighborhood in self.neighborhoods.values():
            old_mine = True
            new_mine = True
            old_theirs = True
            new_theirs = True
            for strt in neighborhood:
                if strt.owned_by != receiver:
                    old_mine = False
                if strt.owned_by != sender:
                    old_theirs = False
                if (strt.owned_by != receiver and strt not in self.sell) or \
                        (strt.owned_by == receiver and strt in self.buy):
                    new_mine = False
                if (strt.owned_by != sender and strt not in self.buy) \
                        or (strt.owned_by == sender and strt in self.sell):
                    new_theirs = False
            # Count how many new neighborhoods each player gets
            old_mine_c += old_mine
            old_theirs_c += old_theirs
            new_mine_c += new_mine
            new_theirs_c += new_theirs
            # Add value of entire neighborhood to player estimations
            receiver_value += \
                self.neighb_value(neighborhood)*(new_mine - old_mine)/2
            sender_value += \
                self.neighb_value(neighborhood)*(new_theirs - old_theirs)/2
        return old_mine_c, new_mine_c, old_theirs_c, new_theirs_c, \
            receiver_value, sender_value

    def compute_trade(self, receiver, sender):
        old_mine_c, new_mine_c, old_theirs_c, new_theirs_c, receiver_value, \
            sender_value = \
            self.compute_neighborhoods(receiver, sender, 0, 0)
        receiver_value += self.add_values(receiver_value, self.sell)
        sender_value += self.add_values(sender_value, self.buy)
        return sender_value, receiver_value

    def send_trade(self, receiver, sender):
        self.show_trade(sender, receiver)
        pygame.time.wait(1000)
        response = receiver.reply_negotiate(self, sender)
        if response:
            self.transfer_properties(sender, receiver)
        else:
            sender.other_players[receiver] = 2

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
    orientation = None
    col = None
    txt = ""
    in_trade = False

    def write(self, text, font_size, col, background, lines, line_height,
              display, game):
        font_obj = pygame.font.Font(None, font_size)
        text_surface_obj = font_obj.render(text, True, col, background)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = (self.x + game.square_side/2,
                                self.y + lines*line_height)
        display.blit(text_surface_obj, text_rect_obj)

    def draw(self, game):
        # Draw place rectangle
        pygame.draw.rect(game.display, self.col,
                         (self.x, self.y, game.square_side, game.square_side))
        # Draw street owner color, if any
        if self.owned_by is not None and isinstance(self, Street):
            pygame.draw.rect(game.display, self.owned_by.col,
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
        self.write(self.txt, 40, col, self.col, 1, y_pos, game.display, game)
        # Draw railroad/utility owner color, if any
        if self.owned_by is not None and isinstance(self, (Railroad, Utility)):
            pygame.draw.rect(game.display, self.owned_by.col,
                             (self.x,
                              self.y + game.square_side - game.square_side/4,
                              game.square_side, game.square_side/4))

        # Draw community chest symbol
        if isinstance(self, CommunityChest):
            pygame.draw.circle(game.display, (255, 247, 0),
                               (self.x + game.square_side/2,
                                self.y + game.square_side/2),
                               game.square_side/2, game.square_side/2)
        # Draw place names and split it as necessary
        background = self.col
        owner_name = ""
        if self.owned_by is not None:
            #col = (180, 180, 180)
            owner_name = self.owned_by.name
        if isinstance(self, Street) or isinstance(self, Utility) or \
                isinstance(self, Railroad):
            name_split = self.name.split(" ")
            name_end = name_split[-1]
            name_begin = " ".join(name_split[:-1])
            lines = 1
            if len(name_begin) != 0:
                self.write(name_begin, game.font_size, col, background, lines,
                           game.line_height, game.display, game)
                lines += 1
            self.write(name_end, game.font_size, col, background, lines,
                       game.line_height, game.display, game)
            lines += 1
            if isinstance(self, (Utility, Railroad)) and  \
                    self.owned_by is not None:
                lines += 4
                background = self.owned_by.col
            self.write(owner_name, game.font_size, col, background, lines,
                       game.line_height, game.display, game)
        # Draw street houses and hotels
        if isinstance(self, Street):
            empty_col = self.col
            full_col = (11, 255, 255)
            for i in range(4):
                if self.houses >= i + 1:
                    col = full_col
                else:
                    col = empty_col
                pygame.draw.rect(game.display, col,
                                 (self.x + i*game.square_side/4,
                                  self.y + game.square_side -
                                  game.square_side/4,
                                  game.square_side/4 - 1,
                                  game.square_side/4 - 1))
            if self.hotels == 1:
                col = full_col
            else:
                col = empty_col
            pygame.draw.rect(game.display, col, (self.x,
                                                 self.y + game.square_side -
                                                 game.square_side/2,
                                                 game.square_side,
                                                 game.square_side/4 - 1))
        # Draw outline
        pygame.draw.line(game.display, (0, 0, 0), (self.x, self.y),
                         (self.x + game.square_side, self.y), 1)
        pygame.draw.line(game.display, (0, 0, 0), (self.x, self.y),
                         (self.x, self.y + game.square_side), 1)
        pygame.draw.line(game.display, (0, 0, 0), (self.x + game.square_side,
                                                   self.y),
                         (self.x + game.square_side,
                          self.y + game.square_side),
                         1)
        pygame.draw.line(game.display, (0, 0, 0), (self.x,
                                                   self.y + game.square_side),
                         (self.x + game.square_side,
                          self.y + game.square_side),
                         1)
        # Draw mortgage triangle
        if self.mortgaged:
            pygame.draw.polygon(game.display, (0, 0, 0),
                                [(self.x + game.square_side,
                                  self.y + game.square_side/2),
                                 (self.x + game.square_side,
                                  self.y + game.square_side),
                                 (self.x, self.y + game.square_side)])

    def draw_arrow(self, game):
        r_len = 20
        r_width = 10
        rect_off = 40
        triangle_h = 10
        triangle_w = 14
        small_side = (triangle_w - r_width)/2
        # Find coordinates and draw rectangle and triangle
        if self.orientation == "right":
            x = self.x + game.square_side/2 - r_width/2
            y = self.y + game.square_side + rect_off - r_len
            pygame.draw.rect(game.display, self.col, (x, y, r_width, r_len))
            pygame.draw.polygon(game.display, self.col,
                                ((x - small_side, y),
                                 (x + r_width + small_side, y),
                                 (x + r_width/2, y - triangle_h)))
        elif self.orientation == "down":
            x = self.x - rect_off
            y = self.y + game.square_side/2 - r_width/2
            pygame.draw.rect(game.display, self.col, (x, y, r_len, r_width))
            pygame.draw.polygon(game.display, self.col,
                                ((x + r_len, y + r_width + small_side),
                                 (x + r_len, y - small_side - 1),
                                 (x + r_len + triangle_h, y + r_width/2)))
        elif self.orientation == "left":
            x = self.x + game.square_side/2 - r_width/2
            y = self.y - rect_off
            pygame.draw.rect(game.display, self.col, (x, y, r_width, r_len))
            pygame.draw.polygon(game.display, self.col,
                                ((x - small_side, y + r_len),
                                 (x + r_width + small_side, y + r_len),
                                 (x + r_width/2, y + r_len + triangle_h)))
        elif self.orientation == "up":
            x = self.x + game.square_side + rect_off - r_len
            y = self.y + game.square_side/2 - r_width/2
            pygame.draw.rect(game.display, self.col, (x, y, r_len, r_width))
            pygame.draw.polygon(game.display, self.col,
                                ((x, y + r_width + small_side),
                                 (x, y - small_side - 1),
                                 (x - triangle_h, y + r_width/2)))

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
        self.hotels -= 1
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
        self.hotels += 1
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
        game.cover_n_central("Let us roll the dice for rent!")
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        game.cover_n_central("Dice: " + str(a) + " " + str(b))
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
    jail_doubles = False  # Flag whether left jail with doubles
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

    def draw(self, game):
        game.draw_doughnut(game.display, self.col, (0, 0, 0),
                           game.board[self.location].x + game.square_side/2 +
                           self.x_rand,
                           game.board[self.location].y + game.square_side/2 +
                           self.y_rand,
                           10, 5, 1)

    def choose_action(self, game):
        game.cover()
        # Draw menu
        smallest = min(game.width, game.height)
        step = smallest/10
        thickness = step - 10
        width = smallest/2
        message(game.display, self.name + ", choose an action:",
                game.background, smallest/2, game.height/5)
        white = (255, 255, 255)
        upgrade_box = game.button("UPGRADE", white, smallest/4,
                                  smallest/4, width, thickness)
        downgrade_box = game.button("DOWNGRADE", white, smallest/4,
                                    step + smallest/4, width, thickness)
        mortgage_box = game.button("MORTGAGE", white, smallest/4,
                                   2*step + smallest/4, width, thickness)
        demortgage_box = game.button("DEMORTGAGE", white, smallest/4,
                                     3*step + smallest/4, width, thickness)
        negotiate_box = game.button("TRADE", white, smallest/4,
                                    4*step + smallest/4, width, thickness)
        nothing_box = game.button("DO NOTHING", white, smallest/4,
                                  5*step + smallest/4, width, thickness)
        # Detect click
        while True:
                for event in pygame.event.get():
                    if event.type == loc.MOUSEBUTTONUP:
                        mouse_x, mouse_y = event.pos
                        #check click
                        if upgrade_box.collidepoint(mouse_x, mouse_y):
                            game.cover()
                            return "u"
                        if downgrade_box.collidepoint(mouse_x, mouse_y):
                            game.cover()
                            return "d"
                        if mortgage_box.collidepoint(mouse_x, mouse_y):
                            game.cover()
                            return "m"
                        if demortgage_box.collidepoint(mouse_x, mouse_y):
                            game.cover()
                            return "e"
                        if negotiate_box.collidepoint(mouse_x, mouse_y):
                            return "g"
                        if nothing_box.collidepoint(mouse_x, mouse_y):
                            game.cover()
                            return "n"

    def move_to_jail(self, game):
        #find next jail (you can have several, if you ask me)
        search_jail = self.location
        while not isinstance(game.board[search_jail], Jail):
            search_jail = (search_jail + 1) % len(game.board)
        self.location = search_jail
        self.in_jail = True
        game.visual_refresh()
        game.cover_n_central(self.name + " goes to JAIL!")

    def mortgage(self, game):
        text = self.name + ", arrows indicate the locations you can mortgage."
        game.central_message(text)
        for item in game.board:
            if item.owned_and_not_mortgaged_by(self) and item.houses == 0:
                item.draw_arrow(game)
        pygame.display.update()
        choose = game.choose_place()
        if game.board[choose].owned_and_not_mortgaged_by(self) and \
                game.board[choose].houses == 0:
            game.bank.move_money(game.board[choose].mortgage, self)
            game.board[choose].mortgaged = True
            game.visual_refresh()
            game.cover_n_central(
                "You have mortgaged " + game.board[choose].name + ".")

    def demortgage(self, game):
        text = self.name + \
            ", arrows indicate the locations you can demortgage."
        game.central_message(text)
        for item in game.board:
            if item.owned_and_mortgaged_by(self):
                item.draw_arrow(game)
        pygame.display.update()
        choose = game.choose_place()
        if game.board[choose].owned_and_mortgaged_by(self) and \
                self.cash >= int(game.board[choose].mortgage * 1.1):
            game.bank.move_money(-int(game.board[choose].mortgage * 1.1), self)
            game.board[choose].mortgaged = False
            game.visual_refresh()
            game.cover_n_central(
                "You have demortgaged " + game.board[choose].name + ".")

    def downgrade(self, game):
        text = self.name + ", arrows indicate the locations you can downgrade."
        game.central_message(text)
        for item in game.board:
            if item.owned_and_not_mortgaged_by(self) and \
                    item.houses > 0 and item.bank_allows_downgrade(game.bank):
                item.draw_arrow(game)
        pygame.display.update()
        choose = game.choose_place()
        if game.board[choose].owned_and_not_mortgaged_by(self) and \
                game.board[choose].houses > 0 and game.board[
                choose].bank_allows_downgrade(game.bank):
            if game.board[choose].hotels == 1:
                game.board[choose].downgrade_hotel(self, game.bank)
            else:
                game.board[choose].downgrade_house(self, game.bank)
            game.visual_refresh()
            game.cover_n_central(
                "You have downgraded " + game.board[choose].name + ".")

    def negotiate(self, game):
        game.cover()

        # Choose player to negotiate with (interactive menu)
        central = min(game.width, game.height)/2
        message(game.display, "Choose a player to trade with:",
                game.background, central,
                game.height/5)
        player_buttons = {}
        col = (0, 0, 255)
        width = 60
        thickness = 40
        step = 0
        for i in range(len(game.players)):
            if game.players[i] != self:
                player_buttons[i] = game.button(
                    game.players[i].name, col, central - width/2,
                    game.height/5 + (2*step+1)*thickness, width, thickness)
                step += 1
        chosen_one = None
        while True:
            for event in pygame.event.get():
                if event.type == loc.MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    for item in player_buttons:
                        if player_buttons[item].collidepoint(mouse_x, mouse_y):
                            chosen_one = game.players[item]
                            break
                    break
            if chosen_one is not None:
                break

        # Choose what to sell
        game.choose_places(central, self, chosen_one, self, game.sell,
                           "Enough selling")

        # Choose what to buy
        game.choose_places(central, self, chosen_one, chosen_one, game.buy,
                           "Enough buying")

        # Add/request money
        message(game.display, "Ask/give cash?", game.background, central,
                game.height/4)
        col = (0, 0, 255)
        box_l = 60
        box_step = 30
        box_w = 20
        buttons = {}
        sums = [1, -1, 10, -10, 50, -50, 100, -100]
        for i in range(len(sums)):
            buttons[sums[i]] = game.button(
                str(sums[i]), col, central - box_l/2,
                game.height/4 + (i+1)*box_step, box_l, box_w)
        red = (255, 0, 0)
        button_w = 200
        enough = game.button("SEND OFFER", red,
                             central - button_w/2,
                             game.height - 3*game.square_side, button_w, 30)
        game.display_trade_cash(self, chosen_one, central, button_w)

        while True:
            exit_loop = False
            for event in pygame.event.get():
                if event.type == loc.MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    for item in buttons:
                        if buttons[item].collidepoint(mouse_x, mouse_y):
                            if -self.cash <= game.trade_cash + item <= \
                                    chosen_one.cash:
                                game.trade_cash += item
                            enough = game.button(
                                "SEND OFFER", red, central - button_w/2,
                                game.height - 3*game.square_side, button_w, 30)
                            game.display_trade_cash(self, chosen_one, central,
                                                    button_w)
                            break
                    if enough.collidepoint(mouse_x, mouse_y):
                        exit_loop = True
                        break
            if exit_loop:
                break

        #Send offer to the other player
        choose = chosen_one.reply_negotiate(game, self)
        if choose:
            game.transfer_properties(self, chosen_one)
        else:
            game.cover_n_central(chosen_one.name + " has rejected your offer!")
        #Reset trade variables
        for item in game.sell:
            item.in_trade = False
        for item in game.buy:
            item.in_trade = False
        game.sell = []
        game.buy = []
        game.trade_cash = 0

    def reply_negotiate(self, game, initiator):
        central = min(game.width, game.height)/2
        game.cover_n_central("Hello, " + self.name + ", " + initiator.name +
                             " wants to trade with you!")
        message(game.display, "You get:", game.background, central - central/2,
                game.height/5 + 20)
        game.sell_list(game.sell, central - central/2)
        message(game.display, "You give:", game.background,
                central + central/2, game.height/5 + 20)
        game.sell_list(game.buy, central + central/2)
        if game.trade_cash < 0:
            message(game.display, "You also get $" + str(-game.trade_cash),
                    game.background, central, game.height/3)
        elif game.trade_cash > 0:
            message(game.display, "You also give $" + str(game.trade_cash),
                    game.background, central, game.height/3)
        choose = game.yes_no("Do you accept?", 40)
        if choose == "yes":
            return True
        else:
            return False

    def upgrade(self, game):
        # Flag the upgradeable locations
        game.flag_upgradeable_places(self)
        # Draw the upgradeable locations
        text = self.name + ", arrows indicate the locations you can upgrade."
        game.central_message(text)
        for item in game.board:
            if isinstance(item, Street) and item.all_upgrade_conditions(
                    game.bank, self):
                item.draw_arrow(game)
        pygame.display.update()
        # Choose a place to upgrade
        choose = game.choose_place()
        if isinstance(game.board[choose], Street) and game.board[
                choose].all_upgrade_conditions(game.bank, self):
            if game.board[choose].houses < 4:
                game.board[choose].upgrade_house(self, game.bank)
            else:
                game.board[choose].upgrade_hotel(self, game.bank)
            game.visual_refresh()
            game.cover_n_central(
                "You have upgraded " + game.board[choose].name + ".")
        #restore to 5
        for item in game.board:
            if isinstance(item, Street):
                item.min_upgrade = 5

    def reply_to_auction(self, player, game, auction_price):
        game.cover()
        line_w = 20
        box_step = 40
        box_w = 30
        box_l = 40
        central = min(game.width, game.height)/2
        message(game.display,
                "Hey, " + self.name + "! " + game.board[player.location].name +
                " is available.", game.background, central, game.height/4)
        message(game.display, "Last price: " + str(auction_price),
                game.background, central, game.height/4 + line_w)
        message(game.display, "Do you bid more?", game.background,
                central, game.height/4 + 2*line_w)
        green = (0, 255, 0)
        red = (255, 0, 0)
        col = game.background
        if self.cash - auction_price >= 1:
            col = green
        plus_one = game.button("+1", col, central - box_l,
                               game.height/4 + 3*box_step, 2*box_l, box_w)
        col = game.background
        if self.cash - auction_price >= 5:
            col = green
        plus_five = game.button("+5", col, central - box_l,
                                game.height/4 + 4*box_step, 2*box_l, box_w)
        col = game.background
        if self.cash - auction_price >= 10:
            col = green
        plus_ten = game.button("+10", col, central - box_l,
                               game.height/4 + 5*box_step, 2*box_l, box_w)
        if self.cash - auction_price >= 50:
            col = green
        plus_fifty = game.button("+50", col, central - box_l,
                                 game.height/4 + 6*box_step, 2*box_l, box_w)
        col = game.background
        if self.cash - auction_price >= 100:
            col = green
        plus_hundr = game.button("+100", col, central - box_l,
                                 game.height/4 + 7*box_step, 2*box_l, box_w)
        do_nothing = game.button("No,thanks", red, central - box_l,
                                 game.height/4 + 8*box_step, 2*box_l, box_w)
        # Detect click
        while True:
                for event in pygame.event.get():
                    if event.type == loc.MOUSEBUTTONUP:
                        mouse_x, mouse_y = event.pos
                        remaining = self.cash - auction_price
                        #check click
                        if plus_one.collidepoint(mouse_x, mouse_y) \
                                and remaining >= 1:
                            game.cover()
                            return auction_price + 1
                        if plus_five.collidepoint(mouse_x, mouse_y) \
                                and remaining >= 5:
                            game.cover()
                            return auction_price + 5
                        if plus_ten.collidepoint(mouse_x, mouse_y) \
                                and remaining >= 10:
                            game.cover()
                            return auction_price + 10
                        if plus_fifty.collidepoint(mouse_x, mouse_y) \
                                and remaining >= 50:
                            game.cover()
                            return auction_price + 50
                        if plus_hundr.collidepoint(mouse_x, mouse_y) \
                                and remaining >= 100:
                            return auction_price + 100
                        if do_nothing.collidepoint(mouse_x, mouse_y):
                            game.cover()
                            return 0

    def start_auction(self, game):
        #set auction flag
        game.cover_n_central("Starting auction...")
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
                    if choose > auction_price:
                        best_candidate = person
                        auction_price = choose
                        still_in_play += 1
                    else:
                        person.in_auction = False
            if still_in_play == 0:
                auction_running = False
        if best_candidate is None:
            game.cover_n_central("Sadly, nobody wants that place.")
        else:

            game.bank.move_money(-auction_price, best_candidate)
            game.board[self.location].new_owner(best_candidate)  # New owner
            game.visual_refresh()
            text = "Congratulations, " + best_candidate.name + \
                "! You have bought " + game.board[self.location].name + \
                " for $" + str(auction_price) + "."
            game.cover_n_central(text)

    def buy(self, game):
        text = self.name + \
            ", wanna buy {}?".format(game.board[self.location].name)
        button_size = 40
        ans = game.yes_no(text, button_size)
        game.cover()
        return ans

    def use_jail_card(self, game):
        return game.yes_no("Use a 'Get Out Of Jail' card?", 40)

    def pay_jail_fine(self, game):
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
        game.cover_n_central(self.name + " gets out of jail.")

    def pay_rent(self, place, game):
        rent_due = place.rent(game)
        if self.double_rent == 2:
            rent_due *= 2  # Rent is doubled when sent by Chance card to a R.R.
            self.double_rent = 1
        if not place.mortgaged:
            game.cover_n_central(place.owned_by.name + " owns " + place.name +
                                 ", " + self.name + " pays rent: " +
                                 str(rent_due) + ".")
            self.cash -= rent_due
            place.owned_by.cash += rent_due
        else:
            game.cover_n_central(place.owned_by.name + " owns " + place.name +
                                 ", but is mortgaged.")

    def pay_tax(self, place, game):
        #Yyou can pay either a lump sum or a percentage of total assets.
        #Sometimes, the second option can be "None"
        tax1 = game.tax_rate(place.option1, self)
        tax2 = game.tax_rate(place.option2, self)
        if tax1 is None or tax2 is None:
            tax = max(tax1, tax2)
        else:
            tax = min(tax1, tax2)
        game.cover_n_central(self.name + " pays taxes amounting to: $" +
                             str(tax))
        game.bank.move_money_to_table(-tax, self)

    def move_to_start(self, game):
        self.location = 0
        game.bank.move_money(game.start_wage, self)
        game.cover_n_central("You go to Start and only receive $" +
                             str(game.start_wage))

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
                game.cover_n_central(
                    "You pass Go and collect $" + str(game.start_wage) + ".")
                game.bank.move_money(game.start_wage, self)
            self.location = destination
            game.cover_n_central("You move to " +
                                 game.chances[game.current_chance].go_to +
                                 ", at location " + str(destination) + ".")
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
                    game.cover_n_central("Rail not found!")
                    break  # Rail not found, back again to original location
            game.cover_n_central("You have moved to: " +
                                 game.board[self.location].name +
                                 ", at pos " + str(self.location) + ".")
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
                            game.cover_n_central(
                                "You get $" + str(game.start_wage))
                        self.location = item.location
                        break
                game.cover_n_central("You move to " +
                                     game.board[self.location].name + ".")
                self.teleport = 1

    def check_jail(self, game, dice):
        # Resolve jail status
        if self.in_jail:  # Check for doubles while in jail
            if dice[0] == dice[1]:
                self.reset_jail()
                self.jail_doubles = True

                text = self.name + " has got a double: " + str(dice[0]) + \
                    " " + str(dice[1]) + "."
                game.cover_n_central(text)
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
            choose = self.pay_jail_fine(game)
            if choose == 'yes':
                game.bank.move_money(-game.jail_fine, self)
                self.reset_jail()
                text = self.name + " pays $" + str(game.jail_fine) + \
                    " to get out of jail."
                game.cover_n_central(text)
        #Else if already three turns in jail:
        if self.time_in_jail == 3:
            game.bank.move_money(-game.jail_fine, self)
            self.reset_jail()
            text = self.name + " pays anyway $" + str(game.jail_fine) +\
                " to get out of jail after three turns."
            game.cover_n_central(text)
    
    def check_specific_comm(self, game):
        if game.community_chest[game.current_comm].collect == 1:
            for person in game.players:
                if person != self:
                    person.cash -= game.collect_fine
                    self.cash += game.collect_fine
                    game.cover_n_central(person.name + " pays $" +
                                         str(game.collect_fine) + " to " +
                                         self.name + ".")
        elif game.community_chest[game.current_comm].go_start == 1:
            self.move_to_start(game)

    def __repr__(self):
        return "Player " + self.name + ", human: " + str(self.human)


def message(display, text, background, x, y):
    font_obj = pygame.font.Font(None, 20)
    text_surface_obj = font_obj.render(text, True, (0, 0, 0), background)
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
    # Trade
    trades = 0
    other_players = {}
    poor_guy = None
    poor_trade = True
    street_trade = None

    def mortgage(self, game):
        """
        Changes mortgage status
        """
        self.successful_mortgage = False
        for item in game.board:
            if item.owned_and_not_mortgaged_by(self) and item.houses == 0:
                game.bank.move_money(item.mortgage, self)
                item.mortgaged = True
                game.visual_refresh()
                game.cover_n_central(
                    self.name + " has mortgaged " + item.name + ".")
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
                game.visual_refresh()
                game.cover_n_central(
                    self.name + " has demortgaged " + item.name + ".")
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
                game.visual_refresh()
                game.cover_n_central(
                    self.name + " has downgraded " + item.name + ".")
                self.successful_downgrade = True
                break
            elif item.owned_by == self and item.houses > 0:  # For streets: > 0
                item.downgrade_house(self, game.bank)
                game.visual_refresh()
                game.cover_n_central(
                    self.name + " has downgraded " + item.name + ".")
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
                        game.visual_refresh()
                        game.cover_n_central(
                            self.name + " has upgraded " + item.name + ".")
                        upgrade_done = True
                        self.successful_upgrade = True
                    elif item.hotels == 0:
                        item.upgrade_hotel(self, game.bank)
                        game.visual_refresh()
                        game.cover_n_central(
                            self.name + " has upgraded " + item.name + ".")
                        upgrade_done = True
                        self.successful_upgrade = True
            level += 1
            #restore to 5
        for item in game.board:
            if isinstance(item, Street):
                item.min_upgrade = 5

    def choose_action(self, game):
        """
        Computer chooses between [u]pgrade / [d]owngrade / [m]ortgage /
        d[e]mortgage / do [n]othing / ne[g]otiate
        Returns "u"/"d"/"m"/"e"/"n"
        """
        if self.cash < 0 and self.successful_downgrade:
            return "d"
        if self.cash < 0 and not self.successful_downgrade and \
                self.successful_mortgage:
            return "m"
        # Computer negotiates if cash negative after downgrade and mortgage
        # Number of consecutive trade attempts cannot exceed number of players.
        # That is an arbitrary value.
        if self.cash < 0 and not self.successful_downgrade and \
                not self.successful_mortgage and \
                self.trades <= len(game.players):
            self.trades += 1
            return "g"
        if self.cash > 125 and self.successful_demortgage:
            return "e"
        if self.cash > 125 and not self.successful_demortgage and \
                self.successful_upgrade:
            return "u"

        # Computer should also trade strategically under certain conditions:
        # - another player has a street in same neighborhood;
        if self.trades <= len(game.players):
            shuffle_neighb = random.sample(game.neighborhoods.values(),
                                           len(game.neighborhoods.values()))
            for neighborhood in shuffle_neighb:
                # trade only if there are 2 owners only and no empty streets
                mine, other, empty, c = self.neighborhood_players(neighborhood)
                if mine and other and not empty and c == 2:
                    self.trades += 1
                    print "trying to get street!"
                    return "g"
                else:
                    self.street_trade = None
        # - there is a very poor player compared to the other players.
        min_cash = float("inf")
        avg_cash = 0
        for player in game.players:
            if player.cash < min_cash:
                min_cash = player.cash
                self.poor_guy = player
            avg_cash += player.cash
        if min_cash < (avg_cash/len(game.players))/3 and \
                min_cash < 2*self.cash and self.poor_guy != self and \
                self.poor_trade and self.trades <= len(game.players):
            print "trying to trade with poor guy!"
            self.poor_trade = False  # Only one poor-trade attempt per turn
            self.trades += 1
            return "g"

        #at the very end
        self.successful_downgrade = True
        self.successful_mortgage = True
        self.successful_upgrade = True
        self.successful_demortgage = True
        self.trades = 0
        self.poor_trade = True
        return "n"

    def negotiate(self, game):
        # There are three cases where the cheatoid wants to trade:
        # 1. has negative cash
        if self.cash < 0:
            # Choose a random (not banned) person to trade with
            shuffle_players = random.sample(game.players, len(game.players))
            chosen_one = None
            for person in shuffle_players:
                if person != self and self.other_players[person] == 0 and \
                        person.cash > -self.cash:
                    chosen_one = person
                    break
            if chosen_one is not None:
                # Loop through assets and add them one by one
                shuffle_board = random.sample(game.board, len(game.board))
                for item in shuffle_board:
                    if item.owned_by == self:
                        game.sell.append(item)
                        # Calculate sell list value and add to trade cash
                        old_mine_c, new_mine_c, old_theirs_c, new_theirs_c, \
                            receiver_value, sender_value = \
                            game.compute_neighborhoods(chosen_one, self, 0, 0)
                        game.trade_cash = \
                            game.add_values(receiver_value, game.sell) + \
                            random.randint(0, 50)
                        # Send offer only if cash becomes positive
                        if game.trade_cash > -self.cash:
                            game.send_trade(chosen_one, self)
                            break  # break loop and basically exit method

        # 2. wants a street to complete neighborhood

        elif self.street_trade is not None:
            #get neighborhood with desired street
            first_neighborhood = None
            new_neighborhood = []
            for neighborhood in game.neighborhood.values():
                if self.street_trade in neighborhood:
                    first_neighborhood = neighborhood
            chosen_one = self.street_trade.owned_by

            # Add street to offer
            game.buy.append(self.street_trade)

            # Assess trade value
            sender_value, receiver_value = game.compute_trade(chosen_one, self)

            #If chosen_one is human, give less
            if isinstance(chosen_one, Cheatoid):
                game.trade_cash = -sender_value - random.randint(0, 100)
            else:
                game.trade_cash = -int(sender_value*0.66)

            #If self has not enough cash, sell properties
            if self.cash >= -game.trade_cash:
                game.send_trade(chosen_one, self)
            else:
                # Find neighborhood shared between self and chosen_one
                for neighborhood in game.neighborhood.values():
                    mine, other, empty, c = \
                        self.neighborhood_players(neighborhood)
                    if mine and not empty and c == 2 and \
                            neighborhood != first_neighborhood:
                        new_neighborhood = neighborhood
                        break
                #  Sell all properties in that neighborhood to chosen_one
                for street in new_neighborhood:
                    if street.owned_by == chosen_one:
                        game.sell.append(street)
                if len(game.sell) > 0:
                    sender_value, receiver_value = \
                        game.compute_trade(chosen_one, self)
                    if isinstance(chosen_one, Cheatoid):
                        sender_value += random.randint(0, 100)
                    else:
                        sender_value = int(sender_value*0.66)
                    game.trade_cash = receiver_value - sender_value
                    if self.cash > game.trade_cash:
                        game.send_trade(chosen_one, self)

            # at the end:
            self.street_trade = None

        # 3. wants to profit from the poorest player
        elif self.poor_guy is not None:
            # search through poor player assets for streets in the same nb
            # if player street(s) enough to complete self's nb, offer more
            # if not enough to complete nb, but no other owners, offer less

            # TODO

            for neighborhood in game.neighborhoods:
                #if mine and other and not empty and other == poor_guy:
                #    offer more (send_trade); break
                #if mine and other and empty and other == poor_guy:
                #    offer less (send_trade); break
                # if no break as above, then reset trades?
                pass
            # at the and
            self.poor_guy = None

        # at the very end:
        game.sell = []
        game.buy = []
        game.trade_cash = 0

    def neighborhood_players(self, neighborhood):
        unique_players = set()  # Create list of unique players
        mine = False  # True if the cheatoid owns at least one street
        other = False  # True if there is at least one player available
        empty = False  # True if there are unowned streets
        for street in neighborhood:
            unique_players.add(street.owned_by)
            if street.owned_by == self:
                mine = True
            elif street.owned_by is not None and \
                    self.other_players[street.owned_by] == 0:
                other = True
                self.street_trade = street
            else:
                if street.owned_by is None:
                    empty = True
        return mine, other, empty, len(unique_players)

    def reply_negotiate(self, game, other):
        return game.robot_negotiate(self, other)

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
            reply = min(auction_price + 5,
                        game.board[other.location].rent_h + a, self.cash)
        else:
            reply = min(auction_price + 5,
                        game.board[other.location].price + a, self.cash)
        game.cover_n_central(self.name + " bids " + str(reply) + ".")
        return reply

    def buy(self, game):
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

    def pay_jail_fine(self, game):
        """
        Returns "yes"/"no"
        """
        return self.use_jail_card(game)  # The easy way

    def __repr__(self):
        return "Player " + self.name + " is NOT human."