import difflib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ItemClass import Item
import re
outfitSlots = ["top", "bottom", "socks", "shoes", "headwear", "face", "bra", "underwear", "neckware", "ring", "wristware", "waistware", "ankleware"]

class Name:
    def __init__(self, first: str, last: str = None):
        self.first = first
        self.last = last

    def __repr__(self):
        temp = self.first
        if self.last:
            temp += " " + self.last
        return temp

    def dict(self):
        return {
            "first": self.first,
            "last": self.last
        }

class Character:
    def __init__(self, name: Name = None, gender: str = None, sexuality: str = None, tropes: str = None, description: str = None, backstory: str = None,
             age: str = None, height: int = None, breastSize: str = None, hairStyle: str = None, hairColor: str = None, eyeColor: str = None,
             skinColor: str = None, characterType: str = None, parents: list = None, friends: list = None, enemies: list = None, inventory: list = None,
             outfitSummary: str = None, memory: dict = None, outfit: dict = None, affection: int = 0, arousal: int = 0, exhibitionism: int = 0,
             confidence: int = 0, intelligence: int = 0, charisma: int = 0, willpower: int = 0, obedience: int = 0,
             relationToPlayer: str = "stranger"):

        # basic info
        self.name = name
        self.gender = gender
        self.sexuality = sexuality
        self.description = description
        self.backstory = backstory
        self.age = age
        self.characterType = characterType

        # appearance
        self.height = height
        self.breastSize = breastSize if gender == "female" else None
        self.hairStyle = hairStyle
        self.hairColor = hairColor
        self.eyeColor = eyeColor
        self.skinColor = skinColor
        self.outfitSummary = outfitSummary
        self.outfit = outfit or {slot: Item(f"{self.name.first}'s initial {slot}", outfit.get(slot)) if outfit and slot in outfit else "None" for slot in outfitSlots}
        
        # personality
        self.tropes = tropes
        self.affection = affection
        self.arousal = arousal
        self.exhibitionism = exhibitionism
        self.confidence = confidence  
        self.intelligence = intelligence
        self.charisma = charisma
        self.willpower = willpower
        self.obedience = obedience

        # relationships
        self.relationToPlayer = relationToPlayer
        self.parents = parents or []
        self.friends = friends or []
        self.enemies = enemies or []

        # misc
        self.inventory = inventory or []
        self.memory = memory or {}
        
    def __str__(self):
        outfitStr = "\n".join([f"            {slot}='{self.outfit[slot]}'" for slot in self.outfit])
        return (f'\nname="{self.name.first}"\n'
                f'    gender="{self.gender}"\n'
                f'    sexuality="{self.sexuality}"\n'
                f'    age="{self.age}"\n'
                f'    characterType="{self.characterType}"\n'
                f'    description="{self.description}"\n'
                f'    backstory="{self.backstory}"\n'
                f'    height="{self.height}"\n'
                f'    breastSize="{self.breastSize}"\n'
                f'    hairStyle="{self.hairStyle}"\n'
                f'    hairColor="{self.hairColor}"\n'
                f'    eyeColor="{self.eyeColor}"\n'
                f'    skinColor="{self.skinColor}"\n'
                f'    tropes="{self.tropes}"\n'
                f'    outfitSummary="{self.outfitSummary}"\n'
                f'{outfitStr}\n'
                f'    parents="{self.parents}"\n'
                f'    friends="{self.friends}"\n'
                f'    enemies="{self.enemies}"\n'
                f'    inventory="{self.inventory}"\n'
                f'    affection="{self.affection}"\n'
                f'    arousal="{self.arousal}"\n'
                f'    exhibitionism="{self.exhibitionism}"\n'
                f'    confidence="{self.confidence}"\n'
                f'    intelligence="{self.intelligence}"\n'
                f'    charisma="{self.charisma}"\n'
                f'    willpower="{self.willpower}"\n'
                f'    obedience="{self.obedience}"\n'
                f'    relationToPlayer="{self.relationToPlayer}"')

    def __repr__(self):
        outfitRepr = ", ".join([f"{slot}='{self.outfit[slot]}'" for slot in self.outfit])
        return (f'name="{self.name.first}", gender="{self.gender}", sexuality="{self.sexuality}", '
                f'age="{self.age}", characterType="{self.characterType}", description="{self.description}", '
                f'backstory="{self.backstory}", height="{self.height}", breastSize="{self.breastSize}", '
                f'hairStyle="{self.hairStyle}", hairColor="{self.hairColor}", eyeColor="{self.eyeColor}", '
                f'skinColor="{self.skinColor}", tropes="{self.tropes}", outfitSummary="{self.outfitSummary}", '
                f'Outfit=({outfitRepr}), '
                f'parents="{self.parents}", friends="{self.friends}", enemies="{self.enemies}", '
                f'inventory="{self.inventory}", affection="{self.affection}", '
                f'arousal="{self.arousal}", exhibitionism="{self.exhibitionism}", '
                f'confidence="{self.confidence}", intelligence="{self.intelligence}", charisma="{self.charisma}", '
                f'willpower="{self.willpower}", obedience="{self.obedience}", '
                f'relationToPlayer="{self.relationToPlayer}"')

    #
    #   Helper Functions
    #

    def dict(self):
        """dict() returns a dictionary of the character's attributes"""

        return {
            "name": self.name.dict(),
            "gender": self.gender,
            "sexuality": self.sexuality,
            "age": self.age,
            "characterType": self.characterType,
            "description": self.description,
            "backstory": self.backstory,
            "height": self.height,
            "breastSize": self.breastSize,
            "hairStyle": self.hairStyle,
            "hairColor": self.hairColor,
            "eyeColor": self.eyeColor,
            "skinColor": self.skinColor,
            "tropes": self.tropes,
            "outfitSummary": self.outfitSummary,
            "outfit": self.outfit,
            "parents": [parent.dict() for parent in self.parents],
            "friends": [friend.dict() for friend in self.friends],
            "enemies": [enemy.dict() for enemy in self.enemies],
            "inventory": [item.dict() for item in self.inventory],
            "memory": self.memory,
            "affection": self.affection,
            "arousal": self.arousal,
            "exhibitionism": self.exhibitionism,
            "confidence": self.confidence,
            "intelligence": self.intelligence,
            "charisma": self.charisma,
            "willpower": self.willpower,
            "obedience": self.obedience,
            "relationToPlayer": self.relationToPlayer
        }
    
    def toImg(self):
        """toImg() returns a string of the character's name and description, formatted for the image generator"""

        outfit_items = [
            'top', 'bottom', 'socks', 'shoes', 'headwear', 'face', 'bra',
            'underwear', 'neckware', 'ring', 'wristware', 'waistware', 'ankleware'
        ]

        outfit_str = "\n".join([f"{item}=\"{self.outfit[item] or 'None'}\"," for item in outfit_items])

        return f"""
        name="{self.name.first}":
            description="{self.description}",
            backstory="{self.backstory}",
            height="{self.height}",
            gender="{self.gender}",
            breastSize="{self.breastSize}",
            hairStyle="{self.hairStyle}",
            hairColor="{self.hairColor}",
            eyeColor="{self.eyeColor}",
            skinColor="{self.skinColor}",
            tropes="{self.tropes}",
            outfitSummary="{self.outfitSummary}",
            {outfit_str}
        """
    
    def template():
        """template() returns a list of character class attributes and their explanations"""
        
        return r"""
        # Basic Information
        name="character name"
        characterType="datable"
        description="description"
        backstory="backstory"
        age="age"
        gender="gender"
        sexuality="sexuality"

        # Appearance
        height="height"
        breastSize="breast size (if applicable)"
        hairStyle="hair style"
        hairColor="hair color"
        eyeColor="eye color"
        skinColor="skin color"

        # Traits
        tropes="character tropes separated by commas"

        # Outfit
        outfitSummary="outfit summary"
        outfit={
            top:"outfit top",
            bottom:"outfit bottom",
            socks:"outfit socks if applicable",
            shoes:"outfit shoes if applicable",
            headwear:"outfit headwear if applicable",
            face:"outfit facewear if applicable",
            bra:"outfit bra if applicable",
            underwear:"outfit underwear",
            neckwear:"outfit neckwear if applicable",
            ring:"outfit ring if applicable",
            wristware:"outfit wristware if applicable",
            waistware:"outfit waistware if applicable",
            ankleware:"outfit ankleware if applicable"
        }

        # Relationships
        parents=[a list of the characters parents]
        friends=[a list of the characters friends]
        enemies=[a list of the characters enemies]
        relationToPlayer="how the character views the player"

        # Inventory
        inventory=[a list of items in the characters inventory]

        # Memory
        memory={a dictionary of memories}

        # Character Stats
        affection= the characters affection for the player
        exhibitionism= the characters exhibitionism
        arousal= the characters arousal
        """
    
    def parseText(self, text: str = None):
        """parseText() parses a string of text for character attributes and sets them accordingly"""
        
        if text is None: return "No text provided"

        pattern = r'(\w+)\s*=\s*"([^"]*)"'
        matches = re.findall(pattern, text)

        outfit_keys = [
            "top", "bottom", "socks", "shoes", "head", "face", "bra", "underwear",
            "neck", "ring", "wristware", "waistware", "ankleware"
        ]
        

        for match in matches:
            var_name = match[0]
            var_value = match[1]

            if var_name in outfit_keys:
                self.outfit[var_name] = var_value
            else:
                setattr(self, var_name, var_value)

        temp = self.name.split(" ")
        if len(temp) >= 2:
            self.name = Name(temp[0], temp[1])
        else:
            self.name = Name(temp[0], None)

    def stringSimilarity(self, a, b):
        """stringSimilarity() returns a float representing the similarity between two strings"""
        return difflib.SequenceMatcher(None, a, b).ratio()

    def searchInventory(self, query: str):
        """searchInventory(query:str) returns a list of items that contain or are similar to the query string"""

        queryWords = set(query.lower().split())
        itemScores = []

        for item in self.inventory:
            itemWords = set(item.name.lower().split()) | set(item.description.lower().split())
            score = 0
            count = 0

            for queryWord in queryWords:
                max_similarity = max([self.stringSimilarity(queryWord, word) for word in itemWords])
                if max_similarity > 0.5:
                    count += 1
                score += max_similarity

            count /= len(queryWords)

            itemScores.append((item, count))

        sortedItems = sorted(itemScores, key=lambda x: x[1], reverse=True)
        return [item[0] for item in sortedItems if item[1] > 0.5]
    
    def searchMemories(self, query: str):
        """searchMemories(query:str) returns a list of memories that contain or are similar to the query string"""  

        queryWords = set(query.lower().split())
        memoryScores = []

        for key, memory in self.memory.items():
            keyWords = set(key.lower().split())
            contentWords = ' '.join(memory['content']).lower().split()
            tagWords = [tag.lower() for tag in memory['tags']]
            
            allWords = keyWords | set(contentWords) | set(tagWords)
            
            score = 0
            for queryWord in queryWords:
                if queryWord in allWords:
                    word_frequency = contentWords.count(queryWord) + tagWords.count(queryWord)
                    score += word_frequency

            if score > 0:
                memoryScores.append((key, score))

        sortedMemories = sorted(memoryScores, key=lambda x: x[1], reverse=True)
        return [memory[0] for memory in sortedMemories if memory[1] > 0]

    def help():
        """help() returns a string of the character class's documentation"""

        return """
        helper functions:
            dict() returns a dictionary of the character's attributes
            toImg() returns a string of the character's name and description, formatted for the image generator
            template() returns a list of character class attributes and their explanations
            parseText(text:str) parses a string of text for character attributes and sets them accordingly
            stringSimilarity(a:str, b:str) returns a float representing the similarity between two strings
            searchMemories(query:str) returns a list of memories that contain or are similar to the query string
            help() returns a string of the character class's documentation
        getters:
            knows() returns a string of everyone the character knows
            relationshipStatus() returns a string describing how the character views the player
            getInventoryItem(item:str) returns an item from the character's inventory
            getInventory() returns a representation of the character's inventory
            getOutfit() returns a representation of the character's outfit
            getMemories() returns a representation of the character's memory keys
            getPhysicalAppearance() returns a representation of the character's appearance
            getPersonality() returns a representation of the character's personality
        managers:
            manageOutfit(action:str, outfitSlot:str, itemName:str) manages the character's outfit. actions: add,remove
            manageInventory(item:Item, action:str) manages the character's inventory. actions: add,remove
            manageMemory(action:str, key:str, memory:str, tags:list) manages the character's memories. actions: add, remember
            changeAttribute(attribute:str, amount:int) changes the character's attribute by the specified amount. attributes: affection, exhibitionism, arousal
        """
    
    #
    #   Getters
    #

    def knows(self):
        """knows() returns a string of everyone the character knows"""
        
        relationships = []

        relationships.extend([f"Parent: {character.name}" for character in self.parents])
        relationships.extend([f"Friend: {character.name}" for character in self.friends])
        relationships.extend([f"Enemy: {character.name}" for character in self.enemies])

        if not relationships:
            return self, f"{self.name.first} knows no one."
        else:
            return self, f"{self.name.first}'s relationships: [{', '.join(relationships)}]"
    
    def relationshipStatus(self):
        """relationshipStatus() returns a string describing how the character feels about the player"""
        return self, f"{self.name.first} views the player as: {self.relationToPlayer}"
    
    def getInventoryItem(self, itemName: str = None):
        """getInventoryItem(itemName:str) returns an item from the character's inventory"""
        if not itemName:
            return None, "error: item not specified"

        itemName = itemName.lower()
        for inventoryItem in self.inventory:
            if inventoryItem.name == itemName:
                return True, inventoryItem

        similarItems = self.searchInventory(itemName)
        return None, f"{self.name.first} does not have {itemName} in their inventory. Similar items in her inventory: {similarItems}"

    def getInventory(self):
        """getInventory() returns a representation of the character's inventory"""
        
        inventory = []

        for item in self.inventory:
            temp = f"[{item.name}: description=\"{item.description}\" quantity={item.quantity}]"
            inventory.append(temp)

        return inventory
    
    def getOutfit(self):
        """getOutfit() returns a representation of the character's outfit"""
        
        outfit = []

        for slot, item in self.outfit.items():
            temp = f"[{slot}: {item.name}, description=\"{item.description}\"]"
            outfit.append(temp)

        return outfit
    
    def getMemories(self):
        """getMemories() returns a representation of the character's memory keys"""
        
        return self.memory.keys()
    
    def getPhysicalAppearance(self):
        """getPhysicalAppearance() returns a representation of the character's appearance"""
        
        return (f'height="{self.height}", breastSize="{self.breastSize}", hairStyle="{self.hairStyle}", '
            f'hairColor="{self.hairColor}", eyeColor="{self.eyeColor}", skinColor="{self.skinColor}", '
            f'outfitSummary="{self.outfitSummary}"')
    
    def getPersonality(self):
        """getPersonality() returns a representation of variables that affect the character's personality"""
            
        return f"Gender:{self.gender}, Description:{self.description}, Tropes: [{self.tropes}], Personality stats: [affection={self.affection}, exhibitionism={self.exhibitionism}, arousal={self.arousal}, confidence={self.confidence}, intelligence={self.intelligence}, charisma={self.charisma}, willpower={self.willpower}, obedience={self.obedience}]"


    #
    #   Managers
    #
    
    def manageOutfit(self, action: str = None, outfitSlot: str = None, itemName: str = None):
        """manageOutfit(action:str, outfitSlot:str, itemName:str) manages the character's outfit, actions are add andremove"""

        if action not in ["add", "remove"]:
            return None, "Error: invalid action specified"

        if not outfitSlot:
            return None, "Error: slot not specified"

        outfitSlot = outfitSlot.lower()

        if outfitSlot not in self.outfit:
            return None, "Error: slot not found, outfit slots are: top, bottom, socks, shoes, head, face, bra, underwear, neck, ring, wristware, waistware, ankleware"

        if action == "add":
            if not itemName: return None, "Error: item not specified"
            if self.outfit[outfitSlot]: return None, "Error: slot already occupied"

            itemObj = None
            for i in self.inventory:
                if i.name == itemName:
                    itemObj = i
                    break
            if not itemObj:
                return self, f"{itemName} is not in {self.name.first}'s inventory, try checking the inventory contents"

            self.inventory.remove(itemObj)
            self.outfit[outfitSlot] = itemObj.description
            return self, f"{self.name.first} has equipped {itemName} to {outfitSlot}."
        
        elif action == "remove":
            temp = self.outfit.get(outfitSlot)
            if not temp:
                return None, "Error: slot already empty"

            temp = Item(f"{self.name}'s {temp} {outfitSlot}", temp)
            temp.quantity = 1
            self.inventory.append(temp)
            self.outfit[outfitSlot] = None
            return self, f"successfully removed {temp} from {self.name.first}'s {outfitSlot} and placed it in their inventory."

    def manageInventory(self, item: Item = None, action: str = "add"):
        """manageInventory(item:Item, action:str) manages the character's inventory, actions are add andremove"""
        if item is None:
            return None, "Error: item not specified"

        if action not in ["add", "remove"]:
            return None, "Error: invalid action specified"

        if item.quantity != "all" and item.quantity <= 0:
            return None, "Error: item quantity is less than or equal to 0"

        try:
            itemFound = None
            for invItem in self.inventory:
                if invItem.name == item.name:
                    itemFound = invItem
                    break
            
            if itemFound:
                if action == "add":
                    itemFound.quantity += item.quantity
                    message = f"{self.name.first} has added {item.name}*{item.quantity} to their inventory."
                else:
                    if item.quantity == "all" or itemFound.quantity == item.quantity:
                        self.inventory.remove(itemFound)
                        message = f"Removed {item.name}*{itemFound.quantity} from inventory. {self.name.first} has no more {item.name} now."
                    else:
                        if itemFound.quantity < item.quantity:
                            return None, f"Can'tremove {item.quantity} {item.name} from {self.name.first}'s inventory they only have {itemFound.quantity} {item.name} in their inventory"
                        itemFound.quantity -= item.quantity
                        message = f"{self.name.first} hasremoved {item.name}*{item.quantity} from their inventory."

                return self, message
            else:
                if action == "add":
                    self.inventory.append(item)
                    return self, f"{self.name.first} has added {item.name}*{item.quantity} to their inventory."
                else:
                    return None, f"{self.name.first} does not have any {item.name}"

        except Exception as e:
            return None, f"Error: item not {'added' if action == 'add' else 'removed'} from inventory: {str(e)}"

    def manageMemory(self, action: str = None, key: str = None, memory: str = None, tags: list = None):
        """manageMemory(action:str, key:str, memory:str, tags:list) manages the character's memories, actions are add and remember"""
        
        if action not in ["add", "remember"]: return None, "Error: invalid action specified"
        if key is None: return None, "Error: key not specified"

        if action == "add":
            if memory is None:
                return None, "Error: memory not specified"

            try:
                if key in self.memory:
                    temp = self.memory[key]['content']

                    # Check if the memory content already exists
                    if memory not in temp:
                        temp.append(memory)
                        self.memory[key]['content'] = temp

                    # Update the tags
                    self.memory[key]['tags'] = list(set(self.memory[key]['tags']).union(set(tags or [])))
                else:
                    self.memory[key] = {
                        "content": [memory],
                        "tags": tags or []
                    }
                return self, f"{self.name.first} has added a memory to their memory bank. {self.name.first}'s_memories=[{list(self.memory.keys())}]"
            except:
                return None, "Error: memory not added to memory bank"

        elif action == "remember":
            try:
                if key in self.memory:
                    temp = self.memory[key]
                    return self, f"{self.name.first} remembers {key}: {temp}"
                else:
                    relevant_memories = self.searchMemories(key)
                    if len(relevant_memories) > 0:
                        return self, f"{self.name.first}'s relevant memory keys for '{key}': {str(relevant_memories)}"
                    else:
                        return None, "Error: key not found"

            except Exception as e:
                return None, f"Error: memory not retrieved from memory bank: {str(e)}"
            
    def changeAttribute(self, attribute: str = "", amount: int = 0):
        """changeAttribute(attribute:str, amount:int) changes the character's attribute by the specified amount. attributes are affection, arousal, exhibitionism, confidence, intelligence, charisma, willpower, obedience"""

        if not attribute:
            return None, "Error: attribute not specified"

        if not isinstance(amount, int):
            return None, "Error: amount is not an integer"

        attribute = attribute.lower()

        if attribute not in ["affection", "arousal", "exhibitionism", "confidence", "intelligence", "charisma", "willpower", "obedience"]:
            return None, "Error: attribute not recognized. available attributes: affection, arousal, exhibitionism, confidence, intelligence, charisma, willpower, obedience"

        try:
            currAttribute = getattr(self, attribute)
            setattr(self, attribute, currAttribute + amount)

            if attribute == "affection":
                if self.affection <= -100:
                    self.relationToPlayer = "Enemy"
                elif -100 < self.affection < 0:
                    self.relationToPlayer = "Dislikes You"
                elif self.affection == 0:
                    self.relationToPlayer = "Stranger"
                elif 0 < self.affection <= 25:
                    self.relationToPlayer = "Acquaintance"
                elif 25 < self.affection <= 50:
                    self.relationToPlayer = "Friend"
                elif 100 < self.affection <= 200:
                    self.relationToPlayer = "Close Friend"
                elif 200 < self.affection <= 250:
                    self.relationToPlayer = "Best Friend"
                elif self.affection > 250:
                    self.relationToPlayer = "Lover"

            return self, f"{self.name.first}'s {attribute} has {'increased' if amount > 0 else 'decreased'} by {abs(amount)}."

        except Exception as e:
            return None, f"Something went wrong changing {attribute}: {str(e)}"