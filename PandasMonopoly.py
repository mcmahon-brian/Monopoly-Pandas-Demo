import random as rand
from math import isnan
from turtle import position
import pandas as pd
from argparse import ArgumentParser
import sys

class GameState:
    """Written by Brian McMahon.
    A class that represents the Monopoly board, property cards, and chance/community chest cards. 
    It uses an updatable pandas dataframe to store all of this information.
    
    Attributes:
        board(Pandas DataFrame): An updatable Pandas DataFrame imported from an excel document. 
            This is used to hold all information relating to the Monopoly board and property cards.
        current_players(list of strings): Used to store the names of all the players currently playing.
        bankrupt_players(list of strings): Used to store the names of all player who have lost.
        chance(list of strings): A list of every chance card
        used_chance(list of strings): A list of chance cards that have been used this game.
        community_chest(list of strings): A list of every community chest card.
        used_community_chest(list of strings): A list of community chest cards that have been used this game.
    """ 
    def __init__(self):
        self.board = pd.read_csv(r"board.csv")
        
        #List of players currently in the game and a list of current players who lost
        self.current_players = []
        self.bankrupt_players = []
        
        #List of Chance cards, used cards are popped into the "used" list and returned when all cards have been used.
        self.chance = ["Advance to Boardwalk", "Advance to Go (Collect $200)", 
                       "Advance to Illinois Avenue. If you pass Go, collect $200", 
                       "Advance to St. Charles Place. If you pass Go, collect $200", 
                       "Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, "\
                           "pay owner twice the rental to which they are otherwise entitled", 
                       "Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, "\
                           "pay owner twice the rental to which they are otherwise entitled", 
                       "Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, "\
                           "throw dice and pay owner a total ten times amount thrown", 
                       "Bank pays you dividend of $50", "Get Out of Jail Free", "Go Back 3 Spaces", 
                       "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200", 
                       "Speeding fine $15", "Take a trip to Reading Railroad. If you pass Go, collect $200", 
                       "You have been elected Chairman of the Board. Pay other player $50", 
                       "Your building loan matures. Collect $150"]
        self.used_chance = []
        
        #List of community chest cards, used cards are popped into the "used" list and returned when all cards have been used.
        self.community_chest = ["Bank error in your favor. Collect $200"]
        self.used_community_chest = ["Advance to Go (Collect $200)", "Bank error in your favor. Collect $200", 
                                     "Doctor’s fee. Pay $50", "From sale of stock you get $50", 
                                "Get Out of Jail Free", "Go to Jail. Go directly to jail, do not pass Go, do not collect $200", 
                                "Holiday fund matures. Collect $100", 
                                "Income tax refund. Collect $20", "It is your birthday. Collect $10 from the other player", 
                                "Life insurance matures. Collect $100", 
                                "Pay hospital fees of $100", "Pay school fees of $50", "Collect $25 consultancy fee", 
                                "You have won second prize in a beauty contest. Collect $10",
                                "You inherit $100"]
        
        
    def get_property_overview(self, space_number):
        """Written by Brian McMahon.
        Accesses the DataFrame and returns an fstring representation of a property card.
        
        Args: 
            space_number(int): The space number of the property whos card will be returned.
        
        Returns:
            (string): An fstring representation of a property card.
        """
        if space_number in [12, 28]:#Utilities
            return f"{self.get_cell(space_number, 'SpaceName')}\nIf one \"Utilitiy\" is owned rent is 4 times amount shown on "\
                f"dice.\nIf both \"Utilities\" are owned rent is 10 times amount shown on dice.\nMortgage Value: $75\nCurrent "\
                    f"Owner: {self.get_owner(space_number)}"
        elif space_number in [5,15,25,35]:#Railroad
            return f"{self.get_cell(space_number, 'SpaceName')}\nRent: $25\nIf 2 Railroads are owned: $50\nIf 3 Railroads are owned: "\
                        f"$100\nIf 4 Railroads are owned: $200\nMortgage Value: $100\nCurrent Owner: {self.get_owner(space_number)}"
        elif space_number in [4, 38]:#Fees
            return f"{self.get_cell(space_number, 'SpaceName')}\nPay ${self.get_cell(space_number, 'Fee')}"
        elif self.checker(self.get_cell(space_number, "Price")) == "NaN":#Every other space
            return f"{self.get_cell(space_number, 'SpaceName')}"
        else:#Properties
            return f"{self.get_cell(space_number, 'SpaceName')} ({self.get_cell(space_number, 'Color')})\nRent: "\
                        f"${self.get_cell(space_number, 'Rent')}\nWith 1 House: ${self.get_cell(space_number, '1HouseRent')}\nWith 2 Houses: "\
                        f"${self.get_cell(space_number, '2HouseRent')}\nWith 3 Houses: ${self.get_cell(space_number, '3HouseRent')}\nWith 4 "\
                        f"Houses: ${self.get_cell(space_number, '4HouseRent')}\nWith Hotel: ${self.get_cell(space_number, 'HotelRent')}\nHouses "\
                        f"cost ${self.get_cell(space_number, 'HouseCost')} each\nMortgage Vaue: ${self.get_cell(space_number, 'MortgageValue')}\nCu"\
                        f"rrent Owner: {self.get_cell(space_number, 'Owner')}"
   
    def get_current_rent(self, space_number, dice_roll=0):
        """Written by Brian McMahon.
        Calculates and returns the amount of rent that's due when landing on a specified space.
        Hotels, houses, railroad ownership, utility ownership, and fees are all taken into account.
        
        Args:
            space_number(int): The space number of the property whos rent will be returned.
            dice_roll(int): This optional arg represents the dice roll needed when calculating utility rent.
                If it equals 0, it's not used.
                
        Returns:
            (int): The amount of rent owed
            (string): If there is not rent to return, it returns a string.
        """
        if space_number in [12, 28]:#Calculates utility rent
            if dice_roll == 0:
                return "A dice roll(int) needs to be included as a second parameter to calculate utility rent."
            elif self.get_owner(12) == self.get_owner(28):
                return (dice_roll * 10)
            else:
                return (dice_roll * 4)
            
        elif space_number in [5,15,25,35]:#Calculates Railroad rent
            rr = [self.get_owner(5), self.get_owner(15), self.get_owner(25), self.get_owner(35)]
            myrr = self.get_owner(space_number)
            counter = 0
            if myrr == rr[0]:
                counter += 1
            if myrr == rr[1]:
                counter += 1
            if myrr == rr[2]:
                counter += 1
            if myrr == rr[3]:
                counter += 1
            if counter == 0:
                return "No Railroads owned."
            elif counter == 1:
                return 25
            elif counter == 2:
                return 50
            elif counter == 3:
                return 100
            elif counter == 4:
                return 200
        
        elif space_number == 4: #Income tax
            return 200
        
        elif space_number == 38: #Luxury Tax
            return 100
        
        else: #Calculates normal property rent
            house_num = self.board.loc[space_number, "NumOfHouses"]
           
            if house_num == 0:
                return self.checker(self.board.loc[space_number, "Rent"])
            elif house_num == 1:
                return self.checker(self.board.loc[space_number, "1HouseRent"])
            elif house_num == 2:
                return self.checker(self.board.loc[space_number, "2HouseRent"])
            elif house_num == 3:
                return self.checker(self.board.loc[space_number, "3HouseRent"])
            elif house_num == 4:
                return self.checker(self.board.loc[space_number, "4HouseRent"])
            
            if house_num == 1:
                return self.checker(self.board.loc[space_number, "HotelRent"])
                
    def get_cell(self, space_number, column_name): 
        """Written by Brian McMahon.
        Fetches the contents of a cell in the DataFrame based on a given space number and a column name.
        
        Args:
            space_number(int): The space number of the cell to be returned.
            column_name(string): The name of the column with the needed cell.
            
        Returns:
            (int): Returns an int if the desired cell is an int or a float.
            (string): Returns a string if desired cell is a string or if its empty.
            
        Side effects:
            Prints a message if the given column name is spelled wrong, for testing.
        """
        if column_name not in self.board.columns:
            print("Invalid column name.")
        else:
            return self.checker(self.board.loc[space_number, column_name])

    def get_space_number(self, space_name): 
        """Written by Brian McMahon.
        Takes the name of a space and returns it's space_number.
        
        Args:
            space_name(string): The name of the property whos number while be returned.
            
        Returns:
            (int): The properties space_number
            (list of int): For multiple spaces with same name, returns all space numbers.
        """
        dex = self.board[self.board["SpaceName"]==space_name].index.values
        if len(dex) > 2:
            return list(dex)
        else:
            return int(dex)
        
    def get_owner(self, space_number):
        """Written by Brian McMahon.
        Fetches name of the owner of the property at space_number.
        
        Args:
            space_number(int): The space number of the property whos owner name will be returned.
            
        Returns:
            (string): The name of the owner of the property.
        """
        return self.checker(self.board.loc[space_number, "Owner"])
    
    def change_owner(self, space_number, player_name): 
        """Written by Brian McMahon.
        Changes the owner of the property in the DataFrame to the given name, owner is "bank" by default.
        
        Args:
            space_number(int): The space number of the property whos owner name will be changed.
            player_name(string): The name to change the owner value to.
            
        Side effects:
            Changes a value inside the board attribute.
            Prints a message if the cell is empty.
        """
        if self.checker(self.board.loc[space_number, "Owner"]) == "NaN":
            print("NaN: This space cannot have an owner, no changes were made.")
        else:
            self.board.loc[space_number, "Owner"] = player_name
        
    def change_houses(self, space_number, number_of_houses):
        """Written by Brian McMahon.
        Alters the value in the DataFrame of the number of houses.
            If removing houses, call with negative number.
            5 houses equals 1 hotel
        Args:
            space_number(int): The space number of the property.
            number_of_houses(int): The number of houses to be added or removed
            
        Side effects:
            Changes a value inside the board attribute.
            Prints a message if the cell is empty.
        """ 
        house_num =self.board.loc[space_number, "NumOfHouses"]
        if self.checker(house_num) == "NaN":
            print("NaN: This space cannot be given houses, no changes were made.")
        elif (house_num + number_of_houses) > 5 or (house_num + number_of_houses) < 0:
            print("Invalid number of houses: Properties can only have 0-5 houses, no changes were made.\n")
        else:
            self.board.loc[space_number, "NumOfHouses"] += number_of_houses
 
    def get_chance(self): 
        """Written by Brian McMahon.
        Fetches a random Chance card and moves card to the used_chance list
        
        Returns:
            (string): The card's text
            
        Side effects:
            Removes a card from the chance attribute
            Adds a card to the used_chance attribute
        """
        if len(self.chance) == 0:
            self.chance = self.used_chance
            self.used_chance = []
        card = self.chance.pop(self.chance.index(rand.choice(self.chance)))
        self.used_chance.append(card)
        return card
    
    def get_community_chest(self): 
        """Written by Brian McMahon.
        Fetches a random Community Chest card and moves card to the used list.
        
        Returns:
            (string): The card's text
            
        Side effects:
            Removes a card from the community_chest attribute
            Adds a card to the used_community_chest attribute
        """
        if len(self.community_chest) == 0:
            self.community_chest = self.used_community_chest
            self.used_community_chest = []
        card = self.community_chest.pop(self.community_chest.index(rand.choice(self.community_chest)))
        self.used_community_chest.append(card)
        return card

    def add_player(self, player_name): 
        """Written by Brian McMahon.
        Adds a player to the list of current players
        
        Args:
            player_name(string): The player name to be added
        
        Side effects:
            Adds a string to the current_player attribute
            Prints a message if the added name is "bank"
        """
        if player_name == "bank":
            print("Player name cannot be \"bank\"")
        self.current_players.append(player_name)
        
    def bankrupt_player(self, player_name): 
        """Written by Brian McMahon.
        Moves a player from the current player list to the bankrupt player list.
        
        Args:
            player_name(string): The player name to be added
        
        Side effects:
            Removes a string from the current_player attribute
            Adds a string to the bankrupt_player attribute
        """
        self.current_players.pop(self.current_players.index(player_name))
        self.bankrupt_players.append(player_name)
    
    def checker(self, cell):
        """Written by Brian McMahon.
        A method exclusively called by other methods to prevent NaN errors when trying to access empty cells
        
        Args:
            cell(string, int, float, or NaN): The value of a given cell
            
        Returns:
            (int): The cell value passed in
            (string): Either the cell value passed in or "NaN" if it's empty
        """
        if isinstance(cell, str) == False and isnan(cell):
            return "NaN"
        elif isinstance(cell, float):
            return int(cell)
        else:
            return cell
       
       
class Game(): #Class for the mechanics of the game
    def __init__(self, player):
        self.player = player
        self.gs = GameState()
        
        
        
        
        self.turn()
    
    
    def roll_dice():
        return rand.randint(1,6)
    
    def turn(self):
        roll = rand.randint(1,6)
        print(f"{self.player['name']} rolled a {roll}.") #print the roll
        self.player['position'] += roll #adds roll to player's info
        print(f"{self.player['name']} landed on {gs.get_cell(self.player['position'], 'SpaceName')}.") #Prints space landed
        print(f"\n{gs.get_property_overview(self.player['position'])}\n")#prints the card
        
    
        if int(self.player['position']) in [5,15,25,35]:#Railroad
            pass
        elif int(self.player['position']) in [12, 28]:#Utilities
            pass
        elif int(self.player['position']) == 4: #Income Tax
            pass
        elif int(self.player['position']) == 38: #Luxury Tax
            pass
        else: #Properties
            pass
            
        
        

        
if __name__ == '__main__':
    gs = GameState()
    
    #Add player names to current_players
    print('How many players?')
    player_count = int(input())
    for i in range(0, player_count):
        print(f"What is Player {i+1}'s name?")
        gs.current_players.append({'name':input(), 'position':0})
    
    #Decide turn order, goes in order for now    
    # add "save game for later" function. games saves data to the csv
    
    for player in gs.current_players:
        Game(player)

    # Game() Call the game class here
    



    # test = GameState()
    # print(test.board.head(), '\n')

    # print(test.get_property_overview(1), '\n')
