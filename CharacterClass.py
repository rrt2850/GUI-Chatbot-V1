from ItemClass import Item
import re

class Character:
    def __init__(self, name: str = None, gender: str = None, sexuality: str = None, tropes: str = None, description: str = None, backstory: str = None,
             age: str = None, height: int = None, breastSize: str = None, hairStyle: str = None, hairColor: str = None, eyeColor: str = None,
             skinColor: str = None, characterType: str = None, parents: list = [], friends:list=[], enemies:list=[], inventory:list[Item]=[],
             outfitSummary: str = None, memory: dict = {}, outfit: dict = {}, outfitTop: str = None, outfitBottom: str = None, outfitSocks: str = None,
             outfitShoes: str = None, outfitHead: str = None, outfitFace: str = None, outfitBra: str = None, outfitUnderwear: str = None, outfitNeck: str = None,
             outfitRing: str = None, outfitWrist: str = None, outfitWaist: str = None, outfitAnkle: str = None, affection: int = 0, arousal: int = 0,
             exhibitionism: int = 0, relationToPlayer: str = "stranger"):
        self.name = name
        self.gender = gender
        self.sexuality = sexuality
        self.description = description
        self.backstory = backstory
        self.age = age
        self.height = height
        if self.gender == "female": self.breastSize = breastSize
        else: self.breastSize = None
        self.hairStyle = hairStyle
        self.hairColor = hairColor
        self.eyeColor = eyeColor
        self.skinColor = skinColor
        self.outfitSummary = outfitSummary
        self.characterType = characterType
        self.parents = parents if parents is not None else []
        self.friends = friends if friends is not None else []
        self.enemies = enemies if enemies is not None else []
        self.inventory = inventory if inventory is not None else []
        self.memory = memory
        self.tropes = tropes
        self.affection = affection
        self.arousal = arousal
        self.exhibitionism = exhibitionism
        self.relationToPlayer = relationToPlayer
        if outfit != {}:
            self.outfit = outfit
        else:
            self.outfit = {
                "top": outfitTop if outfitTop else "None",
                "bottom": outfitBottom if outfitBottom else "None",
                "socks": outfitSocks if outfitSocks else "None",
                "shoes": outfitShoes if outfitShoes else "None",
                "head": outfitHead if outfitHead else "None",
                "face": outfitFace if outfitFace else "None",
                "bra": outfitBra if outfitBra else "None",
                "underwear": outfitUnderwear if outfitUnderwear else "None",
                "neck": outfitNeck if outfitNeck else "None",
                "ring": outfitRing if outfitRing else "None",
                "wristware": outfitWrist if outfitWrist else "None",
                "waistware": outfitWaist if outfitWaist else "None",
                "ankleware": outfitAnkle if outfitAnkle else "None"
            }


    def toImg(self):
        return f"""
        name="{self.name}":
            description="{self.description}"
            backstory="{self.backstory}"
            height="{self.height}"
            gender="{self.gender}"
            breastSize="{self.breastSize}"
            hairStyle="{self.hairStyle}"
            hairColor="{self.hairColor}"
            eyeColor="{self.eyeColor}"
            skinColor="{self.skinColor}"
            tropes="{self.tropes}"
            outfitSummary="{self.outfitSummary}"
                top="{self.outfit['top'] if self.outfit['top'] else 'None'}"
                bottom="{self.outfit['bottom'] if self.outfit['bottom'] else 'None'}"
                socks="{self.outfit['socks'] if self.outfit['socks'] else 'None'}"
                shoes="{self.outfit['shoes'] if self.outfit['shoes'] else 'None'}"
                head="{self.outfit['headwear'] if self.outfit['headwear'] else 'None'}"
                face="{self.outfit['face'] if self.outfit['face'] else 'None'}"
                bra="{self.outfit['bra'] if self.outfit['bra'] else 'None'}"
                underwear="{self.outfit['underwear'] if self.outfit['underwear'] else 'None'}"
                neck="{self.outfit['neckware'] if self.outfit['neckware'] else 'None'}"
                ring="{self.outfit['ring'] if self.outfit['ring'] else 'None'}"
                wristware="{self.outfit['wristware'] if self.outfit['wristware'] else 'None'}"
                waistware="{self.outfit['waistware'] if self.outfit['waistware'] else 'None'}"
                ankleware="{self.outfit['ankleware'] if self.outfit['ankleware'] else 'None'}"
        """
    
    def equip(self, outfitSlot:str = None, item: str = None):
        if outfitSlot in self.outfit:
            temp = self.outfit[outfitSlot]
            if temp == None or temp.lower() != "none":
                return (False, (None,"error: slot already occupied"))
            if item == None or item.lower() == "none":
                return (False, (None,"error: item not specified"))
            if item not in self.inventory:
                return (False, (None,"error: item not in inventory"))
            
            self.inventory.remove(item)
            self.outfit[outfitSlot] = item
            return (True, (self, f"{self.name} has equipped {item} to {outfitSlot}. {self.name}'s_inventory= {self.inventory}, {self.name}'s_outfit= {self.outfit}"))
        
    def unequip(self, outfitSlot:str = None):
        if outfitSlot in self.outfit:
            temp = self.outfit[outfitSlot]
            if temp == None or temp.lower() == "none":
                return (False, (None,"error: slot already empty"))
            self.inventory.append(temp)
            self.outfit[outfitSlot] = None
            return (True, (self, f"{self.name} has unequipped {temp} from {outfitSlot}. {self.name}'s_inventory= {self.inventory}, {self.name}'s_outfit= {self.outfit}"))

    def increaseAffection(self, amount: int = 1):
        try:
            self.affection += amount
            if self.affection > 0 and self.affection <= 25: self.relationToPlayer = "Acquaintance"
            elif self.affection > 25 and self.affection <= 50: self.relationToPlayer = "Friend"
            elif self.affection > 100 and self.affection <= 200: self.relationToPlayer = "Close Friend"
            elif self.affection > 200 and self.affection <= 250: self.relationToPlayer = "Best Friend"
            elif self.affection > 250: self.relationToPlayer = "Lover"
            else: self.relationToPlayer = "Stranger"

            return (True, (self, f"{self.name}'s affection has increased by {amount}."))
        except:
            return (False, (None, "something went wrong increasing affection: check if amount is an integer"))
        
    def increaseArousal(self, amount: int = 1):
        try:
            self.arousal += amount
            return (True, (self, f"{self.name}'s arousal has increased by {amount}."))
        except:
            return (False, (None, "something went wrong increasing arousal: check if amount is an integer"))
        
    def increaseExhibitionism(self, amount: int = 1):
        try:
            self.exhibitionism += amount
            return (True, (self, f"{self.name}'s exhibitionism has increased by {amount}."))
        except:
            return (False, (None, "something went wrong increasing exhibitionism: check if amount is an integer"))
        
    def increaseAttribute(self, attribute: str = "", amount:int =0):
        if not attribute or attribute == "":
            return (False, (None, "error: attribute not specified"))
        
        if type(amount) != str or type(amount) != int:
            return (False, (None, "error: amount is not an integer"))
    
        try:
            amount = int(amount)
        except:
            return (False, (None, "error: amount is not an integer"))
        
        if attribute.lower() == "affection":
            return self.increaseAffection(amount)
        elif attribute.lower() == "arousal":
            return self.increaseArousal(amount)
        elif attribute.lower() == "exhibitionism":
            return self.increaseExhibitionism(amount)
        else:
            return (False, (None, "error: attribute not recognized"))
        
    def addToInventory(self, item: Item = None):
        if item == None:
            return (False, (None, "error: item not specified"))
        try:
            if item.quantity <= 0:
                return (False, (None, "error: item quantity is less than or equal to 0"))
            if item in self.inventory:
                temp = self.inventory[self.inventory.index(item)]
                temp.quantity += item.quantity
            else:
                self.inventory.append(item)
            return (True, (self, f"{self.name} has added {item.name}x{item.quantity} to their inventory. {self.name}'s_inventory= {self.inventory}"))
        except:
            return (False, (None, "error: item not added to inventory"))
        
    def removeFromInventory(self, item: Item = None):
        if item == None:
            return (False, (None, "error: item not specified"))
        try:
            if item.quantity <= 0:
                return (False, (None, "error: item quantity is less than or equal to 0"))
            if item in self.inventory:
                temp = self.inventory[self.inventory.index(item)]
                temp.quantity -= item.quantity
                if temp.quantity <= 0:
                    self.inventory.remove(temp)
            else:
                return (False, (None, "error: item not in inventory"))
            return (True, (self, f"{self.name} has removed {item.name}x{item.quantity} from their inventory. {self.name}'s_inventory= {self.inventory}"))
        except:
            return (False, (None, "error: item not removed from inventory"))

    def addToMemory(self, key: str=None, memory:str=None):
        if key == None or memory == None:
            return (False, (None, "error: key or memory not specified"))
        try:
            if key in self.memory.keys():
                temp = self.memory[key]
                temp.append(memory)
                self.memory[key] = memory
            else:
                self.memory[key] = [memory]
            return (True, (self, f"{self.name} has added a memory to their memory bank. {self.name}'s_memories=[{self.memory.keys()}]"))
        except:
            return (False, (None, "error: memory not added to memory bank"))

    def getRelationship(self):
        return (self, f"{self.name}'s relationship with player =\"{self.relationToPlayer}\"")

    def knows(self):
        temp = ""
        if self.relationToPlayer != "stranger":
            temp += f"Player: {self.relationToPlayer}, "
        for character in self.parents:
            temp += f"Parent: {character.name}, "

        for character in self.friends:
            temp += f"Friend: {character.name}, "

        for character in self.enemies:
            temp += f"Enemy: {character.name}, "

        if temp == "":
            return (self, f"{self.name} knows no one.")
        else:
            return (self, f"{self.name}'s relationships:[{temp}]") 

    def __str__(self):
        return f"""
    name="{self.name}"
        gender="{self.gender}"
        sexuality="{self.sexuality}"
        age="{self.age}"
        characterType="{self.characterType}"
        description="{self.description}"
        backstory="{self.backstory}"
        height="{self.height}"
        breastSize="{self.breastSize}"
        hairStyle="{self.hairStyle}"
        hairColor="{self.hairColor}"
        eyeColor="{self.eyeColor}"
        skinColor="{self.skinColor}"
        tropes="{self.tropes}"
        outfit="{self.outfitSummary}"
            top="{self.outfit['top'] if 'top' in self.outfit else 'None'}"
            bottom="{self.outfit['bottom'] if 'bottom' in self.outfit else 'None'}"
            socks="{self.outfit['socks'] if 'socks' in self.outfit else 'None'}"
            shoes="{self.outfit['shoes'] if 'shoes' in self.outfit else 'None'}"
            head="{self.outfit['headwear'] if 'headwear' in self.outfit else 'None'}"
            face="{self.outfit['face'] if 'face' in self.outfit else 'None'}"
            bra="{self.outfit['bra'] if 'bra' in self.outfit else 'None'}"
            underwear="{self.outfit['underwear'] if 'underwear' in self.outfit else 'None'}"
            neck="{self.outfit['neckware'] if 'neckware' in self.outfit else 'None'}"
            ring="{self.outfit['ring'] if 'ring' in self.outfit else 'None'}"
            wristware="{self.outfit['wristware'] if 'wristware' in self.outfit else 'None'}"
            waistware="{self.outfit['waistware'] if 'waistware' in self.outfit else 'None'}"
            ankleware="{self.outfit['ankleware'] if 'ankleware' in self.outfit else 'None'}"
        family="{self.parents}"
        friends="{self.friends}"
        enemies="{self.enemies}"
        inventory="{self.inventory}"
        affection="{self.affection}"
        exhibitionism="{self.exhibitionism}"
        arousal="{self.arousal}"
    """
    
    def __repr__(self):
        return (f'name="{self.name}", gender="{self.gender}", sexuality="{self.sexuality}", '
            f'age="{self.age}", characterType="{self.characterType}", description="{self.description}", '
            f'backstory="{self.backstory}", height="{self.height}", breastSize="{self.breastSize}", '
            f'hairStyle="{self.hairStyle}", hairColor="{self.hairColor}", eyeColor="{self.eyeColor}", '
            f'skinColor="{self.skinColor}", tropes="{self.tropes}", outfitSummary="{self.outfitSummary}", '
            f'Outfit="{self.outfit}", '
            f'family="{self.parents}", friends="{self.friends}", enemies="{self.enemies}", '
            f'inventory="{self.inventory}", affection="{self.affection}", '
            f'exhibitionism="{self.exhibitionism}", arousal="{self.arousal}"')

    def parseText(self, text: str = None):
        if text is None:
            return None

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
    
    def dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "sexuality": self.sexuality,
            "description": self.description,
            "backstory": self.backstory,
            "age": self.age,
            "height": self.height,
            "breastSize": self.breastSize,
            "hairStyle": self.hairStyle,
            "hairColor": self.hairColor,
            "eyeColor": self.eyeColor,
            "skinColor": self.skinColor,
            "outfitSummary": self.outfitSummary,
            "characterType": self.characterType,
            "parents": [parent.dict() for parent in self.parents],
            "friends": [friend.dict() for friend in self.friends],
            "enemies": [enemy.dict() for enemy in self.enemies],
            "inventory": [item.dict() for item in self.inventory],
            "memory": self.memory,
            "tropes": self.tropes,
            "affection": self.affection,
            "arousal": self.arousal,
            "exhibitionism": self.exhibitionism,
            "relationToPlayer": self.relationToPlayer,
            "outfit": self.outfit
        }

