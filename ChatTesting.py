import copy
import json
import os
import re
from typing import List, Union
import openai

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

# We will add a custom parser to map the arguments to a dictionary
class CustomOutputParser(AgentOutputParser):
    def parse_tool_input(self, action_input: str) -> dict:
        try:
            parsed_input = json.loads(action_input)
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse action input: `{action_input}`")
        return parsed_input

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print(llm_output)
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        regex = r"Action\s*:\n```\n(\{.*\})\n```\n"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action_input = match.group(1)
        tool_input = self.parse_tool_input(action_input)
        action = tool_input.get("action")
        if not action:
            raise ValueError(f"Could not find action in action_input: `{action_input}`")
        del tool_input["action"]
        return AgentAction(tool=action, tool_input=tool_input, log=llm_output)

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

            # Convert character inventories back to items
            for key, value in characters.items():
                new_inventory = []
                for temp in characters[key].inventory:
                    item = Item(temp.get("name"), temp.get("description"))
                    item.quantity = temp.get("quantity")
                    new_inventory.append(item)
                characters[key].inventory = new_inventory
        
            # Convert item dictionaries back to Item objects
            items = {}
            for itemName, itemDict in data["items"].items():
                item = Item(itemDict["name"], itemDict["description"])
                items[itemName] = item

            # Convert the player dictionary back to a Player object
            player = Player(**data["player"])
        except Exception as e:
            print(f"\033[31mError loading save file: {e}\033[0m")
            makeNewGame = input("Would I like to start a new game? (y/n) ")
            if makeNewGame.lower() == "y":
                newGame()
            else:
                exit()
    
    else:
        print("\033[31mNo save file found. Would I like to start a new game?\033[0m")
        makeNewGame = input("Would I like to start a new game? (y/n) ")
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
    if os.path.exists(saveFile):
        os.remove(saveFile)
    save()

loadSave()

tools=[]

def CharacterEquip(args) -> str:
    """CharacterEquip(characterName, outfitSlot, itemName) Equips an item to a character's outfit slot"""
    
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')
        outfitSlot=args.get("outfitSlot")
        item=args.get("item")
        characterName=args.get("characterName")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        outfitSlot=args[1]
        item=args[2]

    if characterName is None:
        return "I need to specify a character to equip the item to"
    
    temp = characters.get(characterName)

    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    if item is None:
        return "I need to specify an item to equip"
    if outfitSlot is None:
        return "I need to specify an outfit slot to equip the item to"
    
    result = temp.equip(outfitSlot, item)
    if result[0] == True:
        characters[characterName] = result[1][0]
    return result[1][1]

def CharacterUnequip(args) -> str:
    """CharacterUnequip(characterName, outfitSlot) Unequips an item from a character's outfit slot"""
    "top, bottom, socks, shoes, head, face, bra, underwear, neck, ring, wristware, waistware, ankleware"
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        outfitSlot=args.get("outfitSlot")
        characterName=args.get("characterName")

    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName = args[0]
        outfitSlot = args[1]

    if characterName is None:
        return "I need to specify a character to unequip the item from"
    
    temp = characters.get(characterName)

    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    if outfitSlot is None:
        return "I need to specify an outfit slot to unequip the item from"
    
    result = temp.unequip(outfitSlot)

    if result[0] == True:
        characters[characterName] = result[1][0]
    return result[1][1]

def CharacterIncreaseAttribute(args) -> str:
    """CharacterIncreaseAttribute(characterName, attribute, amount) Increases a character's attribute by a specified amount. The attributes are affection, arousal, and exhibitionism."""
    
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
        attribute=args.get("attribute")
        amount=args.get("amount")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        attribute=args[1]
        amount=int(args[2])

    if characterName is None:
        return "I need to specify a character to increase the attribute of"
    temp = characters.get(characterName)

    if temp is None:
        print(f"Character {characterName} is not a character")
        return f"force"
    if attribute is None:
        return "I need to specify an attribute to increase"
    if amount is None:
        return "I need to specify an amount to increase the attribute by"
    

    results = temp.increaseAttribute(attribute, amount)
    
    if results[0] == True:
        characters[characterName] = results[1][0]
    return results[1][1]

def CharacterDecreaseAttribute(args:dict=None) -> str:
    """CharacterDecreaseAttribute(charactername, attribute, amount) Decreases a character's attribute by a specified amount. The attributes are affection, arousal, and exhibitionism."""

    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
        attribute=args.get("attribute")
        amount=args.get("amount")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        attribute=args[1]
        amount=int(args[2])
    
    temp = characters.get(characterName)

    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    if characterName is None:
        return "I need to specify a character to decrease the attribute of"
    if attribute is None:
        return "I need to specify an attribute to decrease"
    if amount is None:
        return "I need to specify an amount to decrease the attribute by"

    results = temp.decreaseAttribute(attribute, amount)
    
    if results[0] == True:
        characters[characterName] = results[1][0]
    return results[1][1]

def CharacterGetPlayerRelation(args) -> str:
    """CharacterGetPlayerRelation(characterName) Gets the relationship status of a character to the player"""
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
    elif type(args) is str:
        characterName=args
    elif type(args) is list:
        characterName=args[0]

    temp = characters.get(characterName)

    if characterName is None:
        return "I need to specify a character to get the relation of"
    if temp is None:
        print(f"\n{characterName} is not a character")
        return f"force"
    
    
    return (temp.getRelationship())[1][1]

def CharacterAddToInventory(args) -> str:
    """CharacterAddToInventory(characterName, itemName, itemQuantity) Adds an item to a character's inventory"""
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
        itemName=args.get("itemName")
        itemQuantity=args.get("itemQuantity")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        itemName=args[1]
        itemQuantity=args[2]

    if characterName is None:
        return "I need to specify a character to add the item to"
    temp = characters.get(characterName)

    if temp is None:
        return (False, f"Character {characterName} is not a character")
    if itemName is None:
        return (False, "I need to specify an item to add to the inventory")
    if itemQuantity is None:
        return (False, "I need to specify a quantity of the item to add to the inventory")
    try:
        itemQuantity = int(itemQuantity)
    except:
        return (False, "I need to specify a quantity of the item to add to the inventory")

    item = items.get(itemName)
    if item is None:
        return (False, "That item does not exist, please create it first")
    item = copy.deepcopy(items.get(itemName))
    item.quantity = itemQuantity
    result = temp.addToInventory(item)

    if result[0] == True:
        characters[characterName] = result[1][0]
    return result

def CharacterRemoveFromInventory(args) -> str:
    """CharacterRemoveFromInventory(characterName, itemName, itemQuantity) Removes an item from a character's inventory"""
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
        itemName=args.get("itemName")
        itemQuantity=args.get("itemQuantity")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        itemName=args[1]
        itemQuantity=args[2]
    
    if characterName is None:
        return "I need to specify a character to remove the item from"
    
    temp = characters.get(characterName)
    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    if itemName is None:
        return "I need to specify an item to remove from the inventory"
    if itemQuantity is None:
        return "I need to specify a quantity of the item to remove from the inventory"
    try:
        if type(itemQuantity) is str and itemQuantity.lower() != "all":
            itemQuantity = int(itemQuantity)
    except:
        return "I need to specify a quantity of the item to remove from the inventory"

    item = copy.deepcopy(items[itemName])

    if item is None:
        return "That item does not exist, please create it first"
    
    item.quantity = itemQuantity
    result = temp.removeFromInventory(item)

    if result[0] == True:
        characters[characterName] = result[1][0]
    return result[1][1]

def CharacterNewMemory(args) -> str:
    r"""CharacterNewMemory(dict{{"characterName":str, "memoryName":str, "memoryContent":list[str], "tags":[str]}}) Adds a memory to a character's memory bank"""
    
    if type(args) is str:
        if args[0] == "{":
            args = json.loads(args)

    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
        memoryName=args.get("memoryName")
        memoryContent=args.get("memoryContent")
        tags = args.get("tags")

    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        memoryName=args[1]
        memoryContent=args[2]
        tags = args[3]

    if characterName is None:
        return "I need to specify a character to add the memory to"

    temp = characters.get(characterName)
    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    if memoryName is None:
        return "I need to specify a memory to add to the character"
    if memoryContent is None:
        return "I need to specify a value for the memory"
    if tags is None:
        tags = []

    result = temp.addToMemory(memoryName, memoryContent, tags)

    if result[0] == True:
        characters[characterName] = result[1][0]
    return result[1][1]

def CharacterGetRelevantMemories(args) -> str:
    """CharacterGetRelevantMemories(characterName, query) gets all memory names related to a query so you can pick which one to view"""
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        query=args[1]
    
    if characterName is None:
        return "I need to specify a character to get the memories of"
    if query is None:
        return "I need to specify a query to search for"
    
    temp = characters.get(characterName)
    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    
    temp = temp.getRelevantMemories(query)
    if temp is None:
        return "No memories found"
    print(temp[1][1])
    return str(temp[1][1])

def CharacterRemember(args) -> str:
    """CharacterRemember(characterName, memoryName) Gets a memory from a character USED WHEN REMEMBERING"""
    if type(args) is str:
        if args[0] == "{":
            args = json.loads(args)
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
        memoryName=args.get("memoryName")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        characterName=args[0]
        memoryName=args[1]
    
    if characterName is None:
        return "I need to specify a character to get the memory of"
    if memoryName is None:
        return "I need to specify a memory to get"
    
    temp = characters.get(characterName)
    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"
    
    temp = temp.memory.get(memoryName)
    if temp is None:
        relevantMemories=CharacterGetRelevantMemories(f"{characterName}, {memoryName}")
        return f"No memory with that key, related memories: {relevantMemories}"
    
    temp = temp.remember(memoryName)
    return temp[1][1]

def CharacterGetRelationships(args) -> str:
    """CharacterGetRelationships(characterName) Gets all the characters a character knows and their relationships to them"""
    
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')

        characterName=args.get("characterName")
    elif type(args) is str:
        characterName=args
    elif type(args) is list:
        characterName=args[0]
    if characterName is None:
        return "I need to specify a character to get the relationships of"

    temp = characters.get(characterName)

    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"

    return temp.knows()[1]

def GetCharacterTemplate() -> str:
    """GetCharacterTemplate() Gets the template for characters"""
    temp = Character()
    return temp.template

def GetEntireCharacter(args) -> str:
    """GetEntireCharacter(characterName) Gets all the information about a character (very long response, use with caution)"""

    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')
        
        characterName=args.get("characterName")
    elif type(args) is str:
        characterName=args
    elif type(args) is list:
        characterName=args[0]
    if characterName is None:
        return "I need to specify a character to get"
    
    temp = characters.get(characterName)
    if temp is None:
        print(f"Character {characterName} is not a character")
        return "force"

    return repr(temp)

def CreateItem(args) -> str:
    """CreateItem(itemName, itemDescription) Creates a template item (not character) with a name and description"""
    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')
        
        itemName=args.get("itemName")
        itemDescription=args.get("itemDescription")
    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        itemName=args[0]
        itemDescription=args[1]

    if itemName is None:
        return (False, "I need to specify an item name")
    if items.get(itemName) is not None:
        return (False, "That item already exists")
    if itemDescription is None:
        return (False, "I need to specify an item description")
    
    temp = Item(itemName, itemDescription)
    items[f"{temp.name}"] = temp
    return (True, f"Created item: {temp.name}")

def UpdateItem(args) -> str:
    """UpdateItem(itemName, itemDescription) Updates an item's description"""

    if type(args) is dict:
        if args.get('action_input') is not None:
            args = args.get('action_input')
        
        itemName=args.get("itemName")
        itemDescription=args.get("itemDescription")

    elif type(args) is str or type(args) is list:
        if type(args) is str: args = args.split(", ")
        itemName=args[0]
        itemDescription=args[1]

    if itemName is None:
        return "I need to specify an item name"
    
    temp = items.get(itemName)

    if temp is None:
        print(f"Item {itemName} is not an item")
        return "force"
    if itemDescription is None:
        return "I need to specify an item description"

    temp.description = itemDescription

    for key in characters.keys():
        for index, item in enumerate(characters[key].inventory):
            if item.name == itemName:
                item.description = itemDescription
                # Update the inventory with the modified item
                characters[key].inventory[index] = item

    items[itemName] = temp
    return f"Updated item {temp.name}'s description to {temp.description}"

tools.append(CharacterEquip)
tools.append(CharacterUnequip)
tools.append(CharacterIncreaseAttribute)
tools.append(CharacterDecreaseAttribute)
tools.append(CharacterGetPlayerRelation)
tools.append(CharacterAddToInventory)
tools.append(CharacterRemoveFromInventory)
tools.append(CharacterGetRelevantMemories)
tools.append(CharacterRemember)
tools.append(CharacterNewMemory)
tools.append(CharacterGetRelationships)
tools.append(GetEntireCharacter)
tools.append(CreateItem)
tools.append(UpdateItem)




def makeUserInput(goal=["To be determined"], history=[], action=[], thought=[], input=[]):
    return f"""
GOAL: {goal}
HISTORY: {history}
ACTIONS: {action}
THOUGHT: {thought}
INPUT: {input}
"""

def makeUserInputFromResponse(goal=["goal complete"], history=[], action=[], thought=[], input=[]):
    if goal == [] or goal is None or "goal complete" in goal[0].lower():
        input = "AAAH WE'RE DONE. STOP CHARGING ME"

    return makeUserInput(goal, history, action, thought, input)

def parseGPTResponseOld(response):
    response = response.choices[0].message.content.strip()
    text = None
    variables = {}

    def extract_value(match):
        if match.group(1):
            return match.group(1).strip("[]")
        else:
            return ""

    # Extract GOAL
    goal_match = re.search(r"GOAL:\s*(\[[^]]*\]|[^[\n]+)", response)
    if goal_match:
        variables['GOAL'] = [extract_value(goal_match)]

    # Extract HISTORY
    history_match = re.search(r"HISTORY:\s*(\[[^]]*\]|[^[\n]+)", response)
    if history_match:
        variables['HISTORY'] = [extract_value(history_match)]

    # Extract ACTIONS
    action_match = re.search(r"ACTIONS:\s*(.*)", response)
    if action_match:
        action_code = action_match.group(1).strip()
        action_matches = re.findall(r"(\w+)\((.*?)\)", action_code)
        variables['ACTIONS'] = []
        for m in action_matches:
            function_name = m[0]
            args = [arg.strip(" '\"") for arg in m[1].split(',')] if m[1] else []
            action_dict = {
                'function': function_name,
                'arguments': args
            }
            variables['ACTIONS'].append(action_dict)

    # Extract THOUGHT
    thought_match = re.search(r"THOUGHT:\s*(\[[^]]*\]|[^[\n]+)", response)
    if thought_match:
        variables['THOUGHT'] = [extract_value(thought_match)]

    # Extract INPUT
    input_match = re.search(r"INPUT:\s*(\[[^]]*\]|[^[\n]+)", response)
    if input_match:
        variables['INPUT'] = [extract_value(input_match)]

    return variables

def parseGPTResponse(response):
    response = response.choices[0].message.content.strip()
    text = None
    variables = {}

    def extract_value(match):
        if match.group(1):
            return match.group(1).strip("[]")
        else:
            return ""

    # Use non-greedy matching and a negative lookahead for escaped single quotes
    pattern = r"\s*(\[[^]]*\]|(?:[^[\n\']|(?:\\'))+)"
    
    # Extract GOAL
    goal_match = re.search(r"GOAL:" + pattern, response)
    if goal_match:
        variables['GOAL'] = [extract_value(goal_match)]

    # Extract HISTORY
    history_match = re.search(r"HISTORY:" + pattern, response)
    if history_match:
        variables['HISTORY'] = [extract_value(history_match)]

    # Extract ACTIONS
    action_match = re.search(r"ACTIONS:\s*(.*)", response)
    if action_match:
        action_code = action_match.group(1).strip()
        action_matches = re.findall(r"(\w+)\((.*?)\)", action_code)
        variables['ACTIONS'] = []
        for m in action_matches:
            function_name = m[0]
            args = [arg.strip(" '\"") for arg in m[1].split(',')] if m[1] else []
            action_dict = {
                'function': function_name,
                'arguments': args
            }
            variables['ACTIONS'].append(action_dict)

    # Extract THOUGHT
    thought_match = re.search(r"THOUGHT:" + pattern, response)
    if thought_match:
        variables['THOUGHT'] = [extract_value(thought_match)]

    # Extract INPUT
    input_match = re.search(r"INPUT:" + pattern, response)
    if input_match:
        variables['INPUT'] = [extract_value(input_match)]

    return variables



functions = {
    'CharacterEquip': CharacterEquip,
    'CharacterUnequip': CharacterUnequip,
    'CharacterIncreaseAttribute': CharacterIncreaseAttribute,
    'CharacterDecreaseAttribute': CharacterDecreaseAttribute,
    'CharacterGetPlayerRelation': CharacterGetPlayerRelation,
    'CharacterAddToInventory': CharacterAddToInventory,
    'CharacterRemoveFromInventory': CharacterRemoveFromInventory,
    'CharacterGetRelevantMemories': CharacterGetRelevantMemories,
    'CharacterRemember': CharacterRemember,
    'CharacterNewMemory': CharacterNewMemory,
    'CharacterGetRelationships': CharacterGetRelationships,
    'GetEntireCharacter': GetEntireCharacter,
    'CreateItem': CreateItem,
    'UpdateItem': UpdateItem
}

def handleGPTResponse(response):
    print(response)
    if type(response) != dict:
        return "ERROR parsing response, give up."
    goal = response.get('GOAL', ["Goal complete"])
    history= response.get('HISTORY', [])
    actions = response.get('ACTIONS', [])
    thought = response.get('THOUGHT', [])
    input = response.get('INPUT', [])

    if len(goal) == 1 and goal[0] == '': goal = []
    if len(history) == 1 and history[0] == '': history = []
    if len(actions) == 1 and actions[0] == '': actions = []
    if len(thought) == 1 and type(thought[0])==str and thought[0] == '': thought = []
    if len(input) == 1 and input[0] == '': input = []

    if len(actions) != 0:
        action = actions.pop(0)
        actionOld = f"{action['function']}({', '.join(action['arguments'])})"
        actions = [actionOld]

        # use *args here to unpack args if you decide to use different format args
        name = action.get('function', None)
        args = action.get('arguments', [])

        if name is not None:
            function = functions.get(name, None)
            if function is None:
                result = "ERROR: Function not found"
            else:
                result = function(args)

                if isinstance(result, tuple) and len(result) == 2:
                    if isinstance(result[1], tuple) and len(result[1]) == 2:
                        result = result[1][1]
                    elif isinstance(result[1], str):
                        result = result[1]
                else:
                    result = "Error executing function"
                input.append(result)
    elif len(input) != 0:
        result = input[0]

    return makeUserInputFromResponse(goal, history, actions, thought, input)



promptShort = """
You are a Character Manager AI. Your task is to respond to the USER INPUT by carefully selecting the appropriate TOOLS in ACTION based on the given situation, considering the context.

If the GOAL hasn't been determined, analyze the initial USER INPUT to identify the objectives and list them in the GOAL section.
It's sometimes appropriate to assume the GOAL. For example if a character picks something up and that's all you know, assume the goal is to put it in their inventory and only try to accomplish that.
Update the GOAL section as needed: append new goals, remove completed goals, or mark the goal as "Goal complete" if all goals have been achieved.
Add the initial USER INPUT to the HISTORY. Explain your THOUGHT process behind your decisions and update the HISTORY as needed.
List the appropriate ACTIONS using the available TOOLS, considering the context and any moral implications. Do not execute any actions or make assumptions about their success.
If an ACTION requires a follow-up ACTION or confirmation, add it to the ACTIONS list and wait for the next prompt to confirm the completion of the first action or provide further instructions.
Do NOT make assumptions about a character's traits, memories, or emotional reactions. Instead, use the appropriate TOOL to find out, or wait for explicit input to guide your decision.
Respond to EXPLICIT INPUT about a character's emotions or traits, using the appropriate TOOL and considering the context.
Always use the most suitable TOOL for the given situation.
Leave the INPUT section EMPTY until you receive further instructions or confirmations or need to execute a pending ACTION.
FORMAT:
GOAL: [The overall objective of the current situation. IF ALL GOALS ARE COMPLETE, PUT "Goal complete" HERE]
HISTORY: [A summary of actions taken so far, including the initial USER INPUT]
ACTIONS: [A list of TOOLS to use in order, with variables substituted accordingly]
THOUGHT: [A brief explanation of the reasoning behind the action, considering the context and any moral implications]
INPUT: [LEAVE EMPTY until you receive further instructions or confirmations]

TOOLS:
[CharacterEquip(characterName:str, outfitSlot:str, itemName:str) Equips an item to a character's outfit slot,
CharacterUnequip(characterName:str, outfitSlot:str) Unequips an item from a character's outfit slot,
CharacterIncreaseAttribute(characterName:str, attribute:str, amount:int) Increases a character's attribute by a specified amount. The attributes are affection, arousal, and exhibitionism.,
CharacterDecreaseAttribute(charactername:str, attribute:str, amount:int) Decreases a character's attribute by a specified amount. The attributes are affection, arousal, and exhibitionism.,
CharacterRemember(characterName:str, memoryName:str) Gets a memory from a character USED WHEN REMEMBERING SOMETHING,
CharacterGetRelevantMemories(characterName:str, query:str) gets all memory names related to a query so you can pick which one to view,
CharacterNewMemory(dict{{"characterName":str, "memoryName":str, "memoryContent":list[str], "tags":[str]}}) Adds a memory to a character's memory bank,
CharacterRemoveFromInventory(characterName:str, itemName:str, itemQuantity:int) Removes an item from a character's inventory,
CharacterAddToInventory(characterName:str, itemName:str, itemQuantity:int) Adds an item to a character's inventory,
CharacterGetPlayerRelation(characterName:str) Gets the relationship status of a character to the player,
CharacterGetRelationships(characterName:str) Gets all the characters a character knows and their relationships to them,
GetCharacterTemplate() Gets the template for characters,
GetEntireCharacter(characterName:str) Gets all the information about a character (very long response, use with caution),
CreateItem(itemName:str, itemDescription:str) Creates a template item (not character) with a name and description,
UpdateItem(itemName:str, itemDescription:str) Updates an item's description]
"""
openai.api_key = os.getenv("OPENAI_API_KEY")

chat = makeUserInput(input=["Aiko drops a hotdog on the floor"])
print(chat + "\n")
messages = [
    {"role": "system", "content": promptShort},
    {"role": "user", "content": chat}
]

while True:
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    print(response.choices[0].message.content.strip() + "\n")
    messages.append(response.choices[0].message)
    response = handleGPTResponse(parseGPTResponse(response))
    print(response + "\n")
    if "AAAH WE'RE DONE. STOP CHARGING ME" in response:
        messages = [{"role": "system", "content": promptShort}]
        break
    messages.append({"role": "user", "content":response})
    temp = input("continue?")
    if temp.lower() == "n": break



"""
OLD STUFF
llm=OpenAI(temperature=0)

agent = initialize_agent(
                        tools=tools,
                        allowed_tools=tools,
                        llm=llm,
                        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                        verbose=True,
                        agent_kwargs={"output_parser": CustomOutputParser()},
                        stop=["force", "\nforce"],
                        early_stopping_method="force"
                        )

agent.run("Aiko wants to remember her dogs name")
"""

save()


