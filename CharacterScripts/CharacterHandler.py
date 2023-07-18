"""
Author: Robert Tetreault (rrt2850)
Filename: CharacterHandler.py
Description: This script is the draft for an AI backend manager for a character.
             the idea is that it will recieve a string from the front end
             chatbot AI and modify the backend character based on the sentiment
             and content of the string. It's kind of functional right now, but
             not enough to use, so it's not being called anywhere yet and doesn't
             have proper documentation.
"""

import copy
import difflib
import json
import os
import openai

from SharedVariables import SharedVariables
from CharacterScripts.CharacterClass import Character, Name
from CharacterScripts.CharacterMaker import Player, makeCharacter
from WorldScripts.ItemClass import Item

sharedVars = SharedVariables()

prompt = """
You are an AI character backend manager. Your job is to receive JSON input from the user and respond ONLY in the same JSON format with no extra commentary. Analyze the input, apply the RULES, use the appropriate TOOLS, and update the JSON response accordingly. Remember not to decide things for characters, and only take steps to update the character based on the GOAL and input.

IMPORTANT: Do NOT assume the success of any actions. Only list the actions in the "ACTIONS" section of the JSON response, and make sure the "STATUS" does not assume success or failure of any actions.
RULES:
1. ONLY respond in the format specified below
2. Identify the GOAL from the initial user input (UI). The GOAL is initially set to "To be determined". Replace the initial goal based on the user input, focusing on clear and relevant objectives directly related to the input. Consider the context and implications of the input when setting the goal. If the input describes an action without an explicit goal, use the action as the goal.
3. Update the GOAL as needed: replace initial goal, append new goals, remove completed goals, or mark as "Goal complete" if achieved.
4. DO NOT decide things for characters. Only take steps to update the character based on the GOAL and input. If the input implies a removal or addition of an item to or from the inventory, adjust the ACTIONS accordingly. However, consider the implied consequences of actions in the input (e.g., if the input states a character places an item on a table, you should infer that the item should be removed from their inventory).
5. Do NOT create scenarios or characters. Only use given characters and scenarios.
6. Include a "STATUS" in your JSON response summarizing the ACTIONS and THOUGHTS using HISTORY. Do not assume the success of any actions in the STATUS.
7. Add initial UI to HISTORY.
8. Explain THOUGHT process and update HISTORY as needed.
9. List ACTIONS using available TOOLS. Don't execute actions or assume success. However, consider the implied consequences of actions in the input (e.g., if the input states a character places an item on a table, the AI should infer that the item is removed from their inventory).
10. If ACTION needs follow-up or confirmation, add it to ACTIONS and wait for the next prompt.
11. Use the most suitable TOOL for the situation. Leave INPUT EMPTY until further instructions or confirmations.
12. TOOLS that modify character aspects always update the character.
13. When modifying the inventory, if an item is not present, ignore the action and consider the task complete.
14. Respond in JSON format specified below, including the "STATUS" element when all goals are complete.
15. Avoid changing character attributes without direct input or context indicating a change is warranted. Be cautious in making assumptions about character attributes or emotions, and ensure there is sufficient evidence before taking action.
16. if GOAL is not "To be determined" take input at face value. For example, if it says something is added to a characters inventory, assume the message is just to update you and no actions are requried unless relevant to the GOAL.

TOOLS:
1. manageOutfit(characterName:str, action:str, outfitSlot:str, itemName:str) manages the character's outfit. actions: add, remove
2. manageInventory(characterName:str, action:str, itemName:str, itemQuantity:int)  # manages the character's inventory. actions: add, remove
5. getCharacterInfo(characterName:str, info:str)  # gets a character's info. info: inventory, outfit
7. createItem(itemName:str, itemDescription:str) # creates an item with the given name and description
8. updateItem(itemName:str, itemDescription:str) # updates an item's description
9. getAllItems() # gets all items

RESPONSE FORMAT:
{
    "GOAL": [List of incomplete goals or "Goal complete" if all goals are achieved],
    "HISTORY": [Summary of actions taken so far, including the initial user input],
    "ACTIONS": [WHAT TOOL TO USE IN THE FORMAT: {"function":"functionName", "arguments":["arg1", "arg2", ...]}],
    "THOUGHT": [A short explanation of the reasoning behind the action],
    "INPUT": [Leave EMPTY until further instructions or confirmations],
    "STATUS": [A summary of the current task's status based on the HISTORY of actions taken and the GOAL to be achieved. example: "Tried to add 4 oreos to Nina's inventory but oreos don't exist. Failed creating item oreos."]
}

Analyze the input, apply the RULES, use the appropriate TOOLS, and update the JSON response accordingly. Remember not to decide things for characters, and only take steps to update the character based on the GOAL and input.
"""


openai.api_key = os.environ["OPENAI_API_KEY"]

#
#   System Functions
#

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loadSave():

    # TODO rewrite this so that it accesses the dictionaries in a safer way
    if os.path.exists(sharedVars.saveFile):
        print("\033[32mSave file found. Loading...\033[0m")
        try:
            # Load the data from a JSON file
            with open(sharedVars.saveFile, "r") as file:
                data = json.load(file)

            # Convert character dictionaries back to Character objects
            characters = {id: Character(**character_dict) for id, character_dict in data["characters"].items()}

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
            sharedVars.systemMessage = data.get("systemMessage", None)
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
        "systemMessage": sharedVars.systemMessage
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

#
#   Helper Functions and Makers
#

def makeInput(goal=None, history=None, action=None, thought=None, input=None, status=None):
    tempInput = {
        "GOAL": goal or ['Goal complete'],
        "HISTORY": history or [],
        "ACTIONS": action or [],
        "THOUGHT": thought or [],
        "INPUT": input or []
    }
    if status is not None:
        tempInput["STATUS"] = status

    return json.dumps(tempInput)

def handleGPTResponse(response):
    if type(response) != dict:
        return "ERROR parsing response, give up."
    goal = response.get('GOAL', ['Goal complete'])
    history = response.get('HISTORY', [])
    actions = response.get('ACTIONS', [])
    thought = response.get('THOUGHT', [])
    input = response.get('INPUT', [])
    status = response.get('STATUS', None)

    while len(actions) > 0:
        action = actions[0]
        
        print(f"\033[34mCalling {action.get('function') or 'error no function'} with {action.get('arguments') or 'error no arguments'}\033[0m\n")
        name, args = action.get('function', None), action.get('arguments', [])
        
        result = functions.get(name, lambda x: "ERROR: Function not found")(*args)
        input.append(result[1])
        if result[0]:
            actions.pop(0)
        else:
            break

    return makeInput(goal, history, actions, thought, input, status)

def strInputToJSON(inputStr):
    inputData = json.loads(inputStr)
    # Convert actions from dictionaries to usable format
    actions = inputData.get("ACTIONS", [])
    if actions:
        for i, action in enumerate(actions):
            function = action.get("function", "")
            arguments = action.get("arguments", [])
            actions[i] = {"function": function, "arguments": arguments}

        inputData["ACTIONS"] = actions

    return inputData

def getAllCharacters():
    """getAllCharacters() gets a list of all the characters in the game"""

    return sharedVars.characters.keys()

def getAllItems():
    """getAllItems() gets a list of all the items in the game"""

    return sharedVars.items.keys()

def getCharacter(name:str=None):
    """getCharacter(name:str) gets a character by name. If the character isn't found it returns a list of similar names"""
    if name is None:
        return "No name given"
    
    similar = []
    for characterName in sharedVars.characters.keys():
        firstName = characterName.lower().split(" ")[0]
        if firstName == name.lower():
            return sharedVars.characters[characterName]
        if characterName.lower() in name.lower():
            similar.append(characterName)

    if len(similar) == 0:
        return f"Character {name} doesn't exist."
    if len(similar) == 1:
        return sharedVars.characters[similar[0]], "Success"
    if len(similar) > 1:
        return f"Couldn't find character {name}. Did you mean any of these similar names? [{', '.join(similar)}]?"

def itemLookup(itemName: str = None):
    """itemLookup(itemName:str) gets an item by name. If the item isn't found it returns a list of similar names"""
    if itemName is None:
        return "No name given"
    
    itemNameLower = itemName.lower()
    exactMatch = None
    similarItems = []

    for name in sharedVars.items.keys():
        nameLower = name.lower()
        if nameLower == itemNameLower:
            return sharedVars.items[name]
            
        similarity = difflib.SequenceMatcher(None, itemNameLower, nameLower).ratio()
        if similarity > 0.6:
            similarItems.append((similarity, name))

    if not similarItems:
        return f"Item {itemName} doesn't exist. Either create it or give up on your task."

    similarItems.sort(reverse=True)
    similarNames = [name for _, name in similarItems]

    if len(similarNames) == 1:
        return sharedVars.items[similarNames[0]]
    
    return similarNames

#  
#   Item managing functions
#

def createItem(itemName:str = None, itemDescription:str=None):
    """CreateItem(itemName:str, itemDescription:str) creates an item with the given name and description"""

    if not itemName:
        return False, "I need to specify an item name"
    if type(itemLookup(itemName)) == Item:
        return f"Item {itemName} already exists"
    if not itemDescription:
        return False, "I need to specify an item description"
        
    itemName = itemName.lower()
    temp = Item(itemName, itemDescription)
    sharedVars.items[temp.name] = temp
    return True, f"Created item: {temp.name}"

def updateItem(itemName:str = None, itemDescription:str=None):
    """UpdateItem(itemName:str, itemDescription:str) updates an item's description"""
    if not itemName or not itemDescription:
        return False, "I need to specify an item name" if not itemName else False, "I need to specify an item description"

    item = itemLookup(itemName)

    if type(item) == str:
        return False, item

    item.description = itemDescription
    for key in sharedVars.characters.keys():
        for index, i in enumerate(sharedVars.characters[key].inventory):
            if i.name == itemName:
                i.description = itemDescription
                sharedVars.characters[key].inventory[index] = i

    sharedVars.items[itemName] = item
    return True, f"Updated item {item.name}'s description to {item.description}"

#
#   Character managing functions
#

def getCharacterInfo(character:str=None, info:str=None):
    """getCharacterInfo(character:str, info:str) gets a character's info. info: knownCharacters, playerRelation, inventory, outfit, memories, appearance, personality"""
    if character is None: return False, "ERROR: No character specified"
    if info is None: return False, "ERROR: No info specified"

    character: Character = getCharacter(character)
    if type(character) == str: return character

    if info == "knownCharacters": return True, character.knows()
    if info == "playerRelation": return True, character.relationshipStatus()
    if info == "inventory": return True, character.getInventory()
    if info == "outfit": return True, character.getOutfit()
    if info == "memories": return True, character.getMemories()
    if info == "appearance": return True, character.getPhysicalAppearance()
    if info == "personality": return True, character.getPersonality()
    return False, "ERROR: Info not found"

def ManageOutfit(characterName:str=None, action:str=None, outfitSlot:str=None, itemName:str=None):
    """manageOutfit(character:str, action:str, outfitSlot:str, itemName:str) manages the character's outfit. actions: add, remove"""
    
    if characterName is None: return False, "ERROR: No character specified"

    characterName: Character = getCharacter(characterName)
    if type(characterName) == str: return characterName

    temp = characterName.manageOutfit(action, outfitSlot, itemName)
    
    success = False
    if temp[0]:
        sharedVars.characters[temp[0].name] = temp[0]
        success = True
    return success, temp[1]

def ManageInventory(characterName:str=None, action:str=None, itemName:str=None, itemQuantity:int=None):
    """manageInventory(characterName:str, action:str, itemName:str, itemQuantity:int) manages the character's inventory. actions: add, remove"""
    
    if not all([characterName, action, itemQuantity, itemName]):
        return False, "ERROR: must specify characterName, action, itemQuantity, and itemName"

    characterName: Character = getCharacter(characterName)
    if type(characterName) == str: return characterName

    if action=="remove":
        item = copy.deepcopy(characterName.getInventoryItem(itemName))
        if not item[0]: return item
        item = item[1]
    elif action=="add":
        item = itemLookup(itemName)
        item = copy.deepcopy(item)
        temp = characterName.getInventoryItem(itemName)
        if type(item) == str and not temp[0]: return False, item
        if type(item) ==str:
            item = copy.deepcopy(temp[1])
            item.quantity = 0
            sharedVars.items[item.name] = item
    
    item.quantity = itemQuantity
    temp = characterName.manageInventory(item, action)
    
    success = False
    if temp[0]:
        sharedVars.characters[temp[0].name] = temp[0]
        success = True
    return success, temp[1]

def ManageMemory(characterName:str=None, action:str=None, key:str=None, memory:str=None, tags:list=None):
    """manageMemory(character:str, action:str, key:str, memory:str(optional), tags:list(optional)) manages the character's memories. actions: add, remember"""

    if not characterName:
        return False, "ERROR: must specify character"

    characterName: Character = getCharacter(characterName)
    if type(characterName) == str: return characterName

    temp = characterName.manageMemory(action, key, memory, tags)
    
    success = False
    if temp[0]:
        sharedVars.characters[temp[0].name] = temp[0]
        success = True
    return success, temp[1]

def ChangeAttribute(characterName:str=None, attribute:str=None, amount:int=None):
    """changeAttribute(character:str, attribute:str, amount:int) changes the character's attribute by the specified amount. attributes: affection, arousal, exhibitionism, confidence, intelligence, charisma, willpower, obedience"""

    if not characterName:
        return "ERROR: must specify character"

    characterName: Character = getCharacter(characterName)
    if type(characterName) == str: return characterName

    temp = characterName.changeAttribute(attribute, amount)
    
    success = False
    if temp[0]:
        sharedVars.characters[temp[0].name] = temp[0]
        success = True
    return success, temp[1]

functions = {
    'createItem': createItem,
    'updateItem': updateItem,
    'getCharacterInfo': getCharacterInfo,
    'manageOutfit': ManageOutfit,
    'manageInventory': ManageInventory,
    'manageMemory': ManageMemory,
    'changeAttribute': ChangeAttribute
}

#
#   Testing functions
#

def testLoop():
    # Load the existing JSON data from the file
    file_name = 'data.json'
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    sharedVars.currCharacter(getCharacter("Kasumi"))
    chat = makeInput(goal=["To be determined"], input=[f"{sharedVars.currCharacter.name.first} puts four apples in her inventory"])
    print("\033[32m" + chat + "\033[0m\n")

    conversationEntry = {
            "prompt": chat
    }

    messages = [
        {"role": "user", "content": prompt},
        {"role": "user", "content": chat}
    ]

    # completion model ft-cOJAWaU8N1vE1eYiirs7FWd2
    while True:
        # Get GPT response
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        #clearScreen()
        messages.append(response.choices[0].message)
        print("\033[33m" + response.choices[0].message.content + "\033[0m\n")

        # Add the response to the conversation entry
        conversationEntry["completion"] = response.choices[0].message.content
        
        # Add the new conversation entry to the existing data
        data.append(conversationEntry)

        # Save the updated data back to the file
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)


        if "Goal complete" in response.choices[0].message.content or "To be determined" in response.choices[0].message.content or "Goal Failed" in response.choices[0].message.content or "the goal cannot be completed" in response.choices[0].message.content:
            messages = [{"role": "system", "content": prompt}]
            break

        response = handleGPTResponse(strInputToJSON(response.choices[0].message.content))
        conversationEntry={}
        # Add the response to the conversation entry
        conversationEntry["prompt"] = response
        print("\033[32m" + str(response) + "\033[0m\n")
        
        messages.append({"role": "user", "content":response})
        temp = input("continue? ")
        if "n" in temp.lower(): break

    save()

if __name__ == "__main__":
    loadSave()
    testLoop()