from CharacterScripts.CharacterClass import Character
from CharacterScripts.CharacterMaker import Player

class SharedVariables:
    def __init__(self):
        self.characters = {}
        self.items={}
        self.player=None
        self.currCharacter=None
        self.saveFile = "save.json"

    #
    #   Getters
    #

    def getCharacters(self):
        return self.characters
    
    def getItems(self):
        return self.items
    
    def getPlayer(self):
        return self.player
    
    def getCurrCharacter(self):
        return self.currCharacter

    def getSaveFile(self):
        return self.saveFile
    
    #
    #   Setters
    #

    def setCharacters(self, characters:dict):
        self.characters = characters

    def setItems(self, items:dict):
        self.items = items

    def setPlayer(self, player:Player):
        self.player = player

    def setCurrCharacter(self, currCharacter:Character):
        self.currCharacter = currCharacter
    
    def setSaveFile(self, saveFile:str):
        self.saveFile = saveFile
