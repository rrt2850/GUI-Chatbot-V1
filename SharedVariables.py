from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CharacterScripts.CharacterClass import Character
    from CharacterScripts.CharacterMaker import Player

class SharedVariables:
    def __init__(self):
        self.characters = {}
        self.items={}
        self.player=None
        self.currCharacter=None
        self.saveFile = "save.json"        
        self.prompt=None
        self.systemMessage = None
        self.gptStuff = {
            "temperature": 1,
            "topP": 1,
            "maxTokens": 210,
            "frequencyPenalty": 2,
            "presencePenalty": 2,
            "tokenLimit": 3500
        }
        self.messages = []

    #
    #   Getters
    #
    def getCharacter(self, name):
        return self.characters.get(name)

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
    
    def getPrompt(self):
        return self.prompt
    
    def getSystemMessage(self):
        return self.systemMessage
    
    def getGptStuff(self):
        return self.gptStuff
    
    def getMessages(self):
        return self.messages
    
    
    #
    #   Setters
    #

    def updateCharacter(self, character):
        self.characters[character.name] = character

    def setCharacters(self, characters:dict):
        self.characters = characters

    def setItems(self, items:dict):
        self.items = items

    def setPlayer(self, player: 'Player'):
        self.player = player

    def setCurrCharacter(self, currCharacter: 'Character'):
        self.currCharacter = currCharacter
    
    def setSaveFile(self, saveFile:str):
        self.saveFile = saveFile

    def setPrompt(self, prompt:str):
        self.prompt = prompt
    
    def setSystemMessage(self, systemMessage:str):
        self.systemMessage = systemMessage
    
    def setGptStuff(self, gptStuff:dict):
        self.gptStuff = gptStuff

    def setMessages(self, messages:list):
        self.messages = messages
        
    def appendMessage(self, message:dict):
        self.messages.append(message)

