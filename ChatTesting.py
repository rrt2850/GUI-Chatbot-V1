import copy
import json
import os
import re
from typing import List, Union

import pinecone
from dotenv import load_dotenv
from langchain import LLMChain, LLMMathChain, OpenAI, SerpAPIWrapper
from langchain.agents import (AgentExecutor, AgentOutputParser, AgentType,
                              LLMSingleActionAgent, Tool, initialize_agent,
                              load_tools, tool)
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.text_splitter import CharacterTextSplitter
from langchain.tools import BaseTool
from langchain.vectorstores import Pinecone
from pydantic import BaseModel

from CharacterClass import Character
from CharacterMaker import Player, makeCharacter
from ItemClass import Item

player=None
character=None
items=None
characters=None
saveFile = "save.json"

def loadSave():
    global player, character, characters, items
    if os.path.exists(saveFile):
        print("\033[32mSave file found. Loading...\033[0m")
        try:
            # Load the data from a JSON file
            with open(saveFile, "r") as file:
                data = json.load(file)

            # Convert character dictionaries back to Character objects
            characters = {id: Character(**character_dict) for id, character_dict in data["characters"].items()}

            # Convert item dictionaries back to Item objects
            items = {id: Item(**item_dict) for id, item_dict in data["items"].items()}

            # Convert the player dictionary back to a Player object
            player = Player(**data["player"])
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
    character_dicts = {id: character.dict() for id, character in characters.items()}

    # Convert the Item objects to dictionaries
    item_dicts = {id: item.dict() for id, item in items.items()}

    # Convert the Player object to a dictionary
    player_dict = player.dict()

    # Combine the dictionaries into one
    data = {
        "characters": character_dicts,
        "items": item_dicts,
        "player": player_dict
    }

    # Save the data to a JSON file
    with open(saveFile, "w") as file:
        json.dump(data, file, indent=4)

def newGame():
    global player, character, characters, items
    player, character= makeCharacter()
    characters = {
        f"{character.name}": character
    }
    items = {

    }
    save()


loadSave()
@tool
def CharacterEquip(characterName: str=None,outfitSlot:str=None, item: str=None) -> str:
    """Equips an item to a character's outfit slot"""
    if characterName is None:
        return "You need to specify a character to equip the item to"
    if item is None:
        return "You need to specify an item to equip"
    if outfitSlot is None:
        return "You need to specify an outfit slot to equip the item to"

    temp = characters[characterName]
    result = temp.equip(outfitSlot, item)
    if result[0] == True:
        characters[characterName] = result[1][0]
    return result[1][1]


@tool
def CharacterUnequip(characterName: str=None,outfitSlot:str=None) -> str:
    """Unequips an item from a character's outfit slot"""
    if characterName is None:
        return "You need to specify a character to unequip the item from"
    if outfitSlot is None:
        return "You need to specify an outfit slot to unequip the item from"
    
    temp = characters[characterName]
    result = temp.unequip(outfitSlot)
    if result[0] == True:
        characters[characterName] = result[1][0]
    return result[1][1]

@tool
def CharacterIncreaseAttribute(characterName: str=None, attribute:str=None, amount: int=None) -> str:
    """Increases a character's attribute by a specified amount. The attributes are affection, arousal, and exhibitionism."""
    if characterName is None:
        return "You need to specify a character to increase the attribute of"
    if attribute is None:
        return "You need to specify an attribute to increase"
    if amount is None:
        return "You need to specify an amount to increase the attribute by"
    
    temp = characters[characterName]

    results = temp.increaseAttribute(attribute, amount)
    
    if results[0] == True:
        characters[characterName] = results[1][0]
    return results[1][1]

@tool
def CharacterGetPlayerRelation(characterName: str=None) -> str:
    """Gets the relationship of a character to the player"""
    if characterName is None:
        return "You need to specify a character to get the relation of"
    
    temp = characters[characterName]
    if temp is None:
        return "That character does not exist"

    return temp.getRelationship(player)[1]

@tool
def CharacterAddToInventory(charName: str = None, itemName: str=None, itemQuantity: str=None) -> str:
    """Adds an item to a character's inventory"""
    if charName is None:
        return "You need to specify a character to add the item to"
    if itemName is None:
        return "You need to specify an item to add to the inventory"
    if itemQuantity is None:
        return "You need to specify a quantity of the item to add to the inventory"
    try:
        itemQuantity = int(itemQuantity)
    except:
        return "You need to specify a quantity of the item to add to the inventory"
    
    temp = characters[charName]
    if temp is None:
        return "That character does not exist"

    item = copy.deepcopy(items[itemName])
    if item is None:
        return "That item does not exist, please create it first"
    
    item.quantity = itemQuantity
    result = temp.addToInventory(item)

    if result[0] == True:
        characters[charName] = result[1][0]
    return result[1][1]

@tool
def CharacterRemoveFromInventory(charName: str = None, itemName: str=None, itemQuantity: str=None) -> str:
    """Removes an item from a character's inventory"""
    if charName is None:
        return "You need to specify a character to remove the item from"
    if itemName is None:
        return "You need to specify an item to remove from the inventory"
    if itemQuantity is None:
        return "You need to specify a quantity of the item to remove from the inventory"
    try:
        itemQuantity = int(itemQuantity)
    except:
        return "You need to specify a quantity of the item to remove from the inventory"
    
    temp = characters[charName]
    if temp is None:
        return "That character does not exist"

    item = copy.deepcopy(items[itemName])
    if item is None:
        return "That item does not exist, please create it first"
    
    item.quantity = itemQuantity
    result = temp.removeFromInventory(item)

    if result[0] == True:
        characters[charName] = result[1][0]
    return result[1][1]

@tool
def CharacterAddToMemory(charName: str = None, memoryName: str=None, memoryValue: str=None) -> str:
    """Adds a memory to a character's memory, memoryName is a name for the memory and memoryValue is a summary of the memory"""
    if charName is None:
        return "You need to specify a character to add the memory to"
    if memoryName is None:
        return "You need to specify a memory to add to the character"
    if memoryValue is None:
        return "You need to specify a value for the memory"
    
    temp = characters[charName]
    if temp is None:
        return "That character does not exist"

    result = temp.addToMemory(memoryName, memoryValue)

    if result[0] == True:
        characters[charName] = result[1][0]
    return result[1][1]

@tool
def CharacterGetRelationships(charName:str=None):
    """Gets all the characters a character knows and their relationships to them"""
    if charName is None:
        return "You need to specify a character to get the relationships of"
    
    temp = characters[charName]
    if temp is None:
        return "That character does not exist"

    return temp.knows()[1]

@tool
def GetEntireCharacter(charName:str=None):
    """Gets all the information about a character (very long response, use with caution)"""
    if charName is None:
        return "You need to specify a character to get"
    
    temp = characters[charName]
    if temp is None:
        return "That character does not exist"

    return repr(temp)

"""
PROMPT="""

"""

llm = ChatOpenAI(temperature=0)
tools = load_tools(["CharacterEquip", "CharacterUnequip", "CharacterIncreaseAttribute",
                    "CharacterGetPlayerRelation", "CharacterAddToInventory", "CharacterRemoveFromInventory",
                    "CharacterAddToMemory", "CharacterGetRelationships", "GetEntireCharacter"], llm=llm)

"""