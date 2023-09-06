"""
Author: Robert Tetreault (rrt2850)
Filename: DataHandler.py
Description: Handles loading and saving data directly from and to JSON files
Note:   This file is not used for loading messages because they're handled by the
        kivy message widgets    
"""


import json
import os

from SharedVariables import SharedVariables

from WorldScripts.ItemClass import Item

from CharacterScripts.CharacterClass import Character, Name
from CharacterScripts.CharacterMaker import Player, makeCharacter
from CharacterScripts.CharacterClass import Character, Player

sharedVars = SharedVariables()

def loadSave():
    """
    Loads the save file if it exists, otherwise it asks the user if they'd like to start a new game
    """
    if os.path.exists(sharedVars.saveFile):
        print("\033[32mSave file found. Loading...\033[0m")
        try:
            # Load the data from a JSON file
            with open(sharedVars.saveFile, "r") as file:
                data = json.load(file)

            if data.get("characters") is None:
                # If there are no characters, create an empty dictionary for now
                # Later on, the user will be able to generate characters
                data["characters"] = {}

            else:
                # Convert character dictionaries back to Character objects
                characters = {id: Character(**characterDict) for id, characterDict in data["characters"].items()}

            # Convert character inventories back to items
            for key, _ in characters.items():
                newInventory = []
                for temp in characters[key].inventory:
                    item = Item(temp.get("name"), temp.get("description"))
                    item.quantity = temp.get("quantity")
                    newInventory.append(item)
                characters[key].inventory = newInventory
                characters[key].name = Name(data["characters"][key]["name"].get("first"), characters[key].name.get("last"))
        
            # Convert item dictionaries back to Item objects
            items = {}
            for itemName, itemDict in data["items"].items():
                item = Item(itemDict["name"], itemDict["description"])
                items[itemName] = item

            # Convert all the player dictionaries back to Player objects
            players = []
            for _, playerDict in data["players"].items():
                player = Player(**playerDict)
                players.append(player)

            
            # Get the last system message if there is one
            # TODO make this work with multiple players
            sharedVars.setting = data.get("systemMessage", None)
            sharedVars.characters = characters
            sharedVars.items = items
            sharedVars.players = players

        except Exception as e:
            print(f"\033[31mError loading save file: {e}\033[0m")
            makeNewGame = input("Would you like to start a new game? (y/n) ")
            if makeNewGame.lower() == "y":
                newGame()
            else:
                exit()
    
    else:
        print("\033[31mNo save file found. Would you like to start a new game?\033[0m")
        makeNewGame = input("Would you like to start a new game? (y/n) ")
        if makeNewGame.lower() == "y":
            newGame()
        else:
            exit()

def save():
    print("\033[32mSaving...\033[0m")
    # Convert the Character objects to dictionaries
    characterDicts = {str(id): character.dict() for id, character in sharedVars.characters.items()}

    # Convert the Item objects to dictionaries
    itemDicts = {id: item.dict() for id, item in sharedVars.items.items()}

    playerDict = {}
    # Convert the Player object to a dictionary
    for player in sharedVars.players:
        player = player.dict()
        playerDict[player["name"]] = player

    # Combine the dictionaries into one
    data = {
        "characters": characterDicts,
        "items": itemDicts,
        "players": playerDict,
        "systemMessage": sharedVars.setting
    }

    # Save the data to a JSON file
    with open(sharedVars.saveFile, "w") as file:
        json.dump(data, file, indent=4)

def newGame():
    player, character= makeCharacter()
    characters = {
        f"{character.name}": character
    }
    items = {

    }
    if os.path.exists(sharedVars.saveFile):
        os.remove(sharedVars.saveFile)

    sharedVars.characters = characters
    sharedVars.items = items
    sharedVars.player = player
    save()