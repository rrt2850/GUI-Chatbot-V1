from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CharacterScripts.CharacterClass import Character
    from CharacterScripts.CharacterMaker import Player

class SharedVariables:
    def __init__(self):
        self._devMode = True
        self._characters = {}
        self._items={}
        self._player = None
        self._players = []
        self._currCharacter = None
        self._currCharacter2 = None
        self._saveFile = "CharacterJsons/save.json"
        self._chatKey = None        
        self._prompt = None
        self._systemMessage = None
        self._gptStuff = {
            "temperature": 1,
            "topP": 1,
            "maxTokens": 210,
            "frequencyPenalty": 1.7,
            "presencePenalty": 1.7,
            "tokenLimit": 3500
        }
        self._messages = []

    #
    #   Getters
    #

    @property
    def devMode(self) -> bool:
        return self._devMode
    
    @property
    def characters(self) -> dict:
        return self._characters
    
    @property
    def items(self) -> dict:
        return self._items
    
    @property
    def player(self) -> 'Player':
        return self._player
    
    @property
    def players(self) -> list:
        return self._players
    
    @property
    def currCharacter(self) -> 'Character':
        return self._currCharacter
    
    @property
    def currCharacter2(self) -> 'Character':
        return self._currCharacter2
    
    @property
    def saveFile(self) -> str:
        return self._saveFile
    
    @property
    def chatKey(self) -> str:
        return self._chatKey
    
    @property
    def prompt(self) -> str:
        return self._prompt
    
    @property
    def systemMessage(self) -> str:
        return self._systemMessage
    
    @property
    def gptStuff(self) -> dict:
        return self._gptStuff
    
    @property
    def messages(self) -> list:
        return self._messages
    
    
    #
    #   Setters
    #

    @devMode.setter
    def devMode(self, value: bool):
        self._devMode = value

    @characters.setter
    def characters(self, value: dict):
        self._characters = value

    @items.setter
    def items(self, value: dict):
        self._items = value

    @player.setter
    def player(self, value: 'Player'): 
        self._player = value

    @players.setter
    def players(self, value: list):
        self._players = value
    
    @currCharacter.setter
    def currCharacter(self, value: 'Character'):
        self._currCharacter = value

    @currCharacter2.setter
    def currCharacter2(self, value: 'Character'):
        self._currCharacter2 = value

    @saveFile.setter
    def saveFile(self, value: str):
        self._saveFile = value

    @chatKey.setter
    def chatKey(self, value: str):
        self._chatKey = value

    @prompt.setter
    def prompt(self, value: str):
        self._prompt = value

    @systemMessage.setter
    def systemMessage(self, value: str):
        self._systemMessage = value

    @gptStuff.setter
    def gptStuff(self, value: dict):
        self._gptStuff = value

    @messages.setter
    def messages(self, value: list):
        self._messages = value

    #
    #   Methods
    #

    def updateCharacter(self, character: 'Character'):
        self._characters[character.name] = character
     
    def appendMessage(self, message:dict):
        self._messages.append(message)

    def appendPlayer(self, player: 'Player'):
        self._players.append(player)

    def getPlayer(self, name: str) -> 'Player':
        for player in self._players:
            if player.name == name:
                return player
        return None

    def getCharacter(self, name: str) -> 'Character':
        return self._characters.get(str(name), None)
    
    def getItemTemplate(self, name: str) -> dict:
        return self._items[name]