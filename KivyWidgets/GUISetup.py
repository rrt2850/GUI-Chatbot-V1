import json
import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.core.window import Window

from CharacterScripts.DataHandler import loadSave, sharedVars, save
from KivyWidgets.ChatSim import RootWidget
from KivyWidgets.SetupForms import NewPlayerForm
from KivyWidgets.ClearableInput import ClearableTextInput

kivy.require('2.0.0')

class Startup(App):
    def build(self):
        self.inputs = GridLayout(cols=1)
        self.layout = BoxLayout(orientation='horizontal')        
        self.layout.add_widget(Label(text=""))  # Add padding to the left of the inputs
        self.layout.add_widget(self.inputs)     # Add the inputs to the layout
        self.layout.add_widget(Label(text=""))  # Add padding to the right of the inputs

        def on_request_close(*args):
            save()

        # Set the function to be called when the window is about to close
        Window.bind(on_request_close=on_request_close)
        
        # Load save data
        loadSave()

        # initialize title and icon
        if sharedVars.devMode:
            self.title = 'b-b-b-buss'
        else:
            self.title = 'super neat robo-girlfriend, name tbd'

        # Create a list of characters from shared variables
        characters = list(sharedVars.characters.values())
        players = sharedVars.players

        # Check if there are no players, if so, print an error message and exit the function
        if not players:
            self.inputs.add_widget(Label(text='Error: No players found'))
        
        self.populateButtons()

        return self.layout

    def populateButtons(self):
        # Create a list of characters from shared variables
        characters = list(sharedVars.characters.values())
        players = sharedVars.players

        # Check if there are no players, if so, print an error message and exit the function
        if not players:
            self.inputs.add_widget(Label(text='Error: No players found'))

        self.playerButtons = []
        self.characterButtons = []
        self.selectedCharacters = []

        if len(players) > 0:
            self.inputs.add_widget(Label(text='Which player would you like to play as?'))
            for i, player in enumerate(players):
                btn = Button(text=f'{i+1}. {player.name}', on_press=self.selectPlayer(i))
                self.playerButtons.append(btn)
                self.inputs.add_widget(btn)

        self.newPlayer = Button(text='New Player', on_press=self.handleNewPlayer)
        self.inputs.add_widget(self.newPlayer)

        # Check if there are no characters, if so, print an error message and exit the function
        if not characters:
            self.inputs.add_widget(Label(text='Error: No characters found'))

        self.inputs.add_widget(Label(text='Which characters would you like to talk to? (up to two)'))
        for i, character in enumerate(characters):
            btn = Button(text=f'{i+1}. {character.name}', on_press=self.selectCharacter(character.name))
            self.characterButtons.append(btn)
            self.inputs.add_widget(btn)

        # Create an error label and add it to the layout
        self.errorLabel = Label(text='')
        self.inputs.add_widget(self.errorLabel)

        # Add the start button to the layout
        startButton = Button(text='Start', on_press=self.startChat)
        self.inputs.add_widget(startButton)

    def refreshButtons(self, instance):
        self.inputs.clear_widgets()
        self.populateButtons()

    def handleNewPlayer(self, instance):
        modalView = ModalView(on_dismiss=self.refreshButtons)
        modalView.add_widget(NewPlayerForm())
        modalView.open()

    def selectPlayer(self, index):
        def callback(instance):
            # If the player is already selected, deselect them
            if hasattr(self, 'selectedPlayerButton') and self.selectedPlayerButton == instance:
                sharedVars.player = None
                instance.background_color = (1, 1, 1, 1)  # change button color to default (white)
                del self.selectedPlayerButton  # delete the reference to the selected player button
            else:
                sharedVars.player = sharedVars.players[index]
                instance.background_color = (0, 1, 0, 1)  # change button color to green
                if hasattr(self, 'selectedPlayerButton'):
                    self.selectedPlayerButton.background_color = (1, 1, 1, 1)  # reset color for previously selected player button
                self.selectedPlayerButton = instance  # store the reference to the newly selected player button

        return callback


    def selectCharacter(self, name):
        def callback(instance):
            if instance in self.selectedCharacters:  # if character already selected, deselect it
                self.selectedCharacters.remove(instance)
                instance.background_color = (1, 1, 1, 1)  # change button color to default (white)
                
                if sharedVars.currCharacter == sharedVars.getCharacter(name):
                    if sharedVars.currCharacter2:
                        sharedVars.currCharacter = sharedVars.currCharacter2
                        sharedVars.currCharacter2 = None
                    else:
                        sharedVars.currCharacter = None
                else:
                    sharedVars.currCharacter2 = None
            elif len(self.selectedCharacters) < 2:  # if less than two characters are selected, select it
                self.selectedCharacters.append(instance)
                instance.background_color = (0, 1, 0, 1)  # change button color to green
                if sharedVars.currCharacter is None:
                    sharedVars.currCharacter = sharedVars.getCharacter(name)
                else:
                    sharedVars.currCharacter2 = sharedVars.getCharacter(name)

        return callback

    def startChat(self, instance):
        # Check if both a player and at least one character have been selected
        if sharedVars.player is None or sharedVars.currCharacter is None:
            # If not, display an error message in the error label and return from the function
            self.errorLabel.text = 'Error: Please select a player and at least one character before starting the chat.'
            return

        # If no error, clear the error label
        self.errorLabel.text = ''

        # Clear the screen
        self.inputs.clear_widgets()
        if sharedVars.player.charLores:
            loreInfo = sharedVars.player.charLores.get(repr(sharedVars.currCharacter.name), None)
            sharedVars.player.setting = loreInfo.get("setting", None) if loreInfo else ""
            sharedVars.player.lore = loreInfo.get("lore", None) if loreInfo else ""

        # System message text input
        self.currSettingInput = ClearableTextInput(defaultText="Enter a setting/situation here")
        if sharedVars.player.setting and sharedVars.player.setting != "Enter a setting/situation here":
            self.currSettingInput.text = sharedVars.player.setting
        

        self.inputs.add_widget(Label(text="Edit the current setting:"))
        self.inputs.add_widget(self.currSettingInput)

        # Lore text input
        self.loreInput = ClearableTextInput(defaultText="Enter player lore here")
        if sharedVars.player.lore and sharedVars.player.lore != "Enter player lore here":
            self.loreInput.text = sharedVars.player.lore

        self.inputs.add_widget(Label(text="Edit player lore:"))
        self.inputs.add_widget(self.loreInput)

        # Add a blank label to add some space between the text input and the button
        self.inputs.add_widget(Label(text=""))
        
        # Button to save the system message and display the prompt
        self.inputs.add_widget(Button(text="Start Conversation", on_press=self.startConversation))
        
        # Label to display the prompt
        self.promptLabel = Label()
        self.inputs.add_widget(self.promptLabel)

    def startConversation(self, instance):
        # Set system message
        sharedVars.setting = self.currSettingInput.text
        sharedVars.player.setting = self.currSettingInput.text
        sharedVars.player.lore = self.loreInput.text
        
        # Generate initial prompt
        sharedVars.prompt = sharedVars.currCharacter.makePrompt()
        
        # Display the prompt
        self.promptLabel.text = "Prompt: " + sharedVars.prompt
        
        # Initialize chat history
        chatHistory = {"logs": {}}
        
        try:
            # Attempt to load chat history
            with open(f"CharacterJsons/ChatHistory{sharedVars.player.name}.json", 'r') as f:
                chatHistory = json.load(f)
            
            if sharedVars.currCharacter2 and f"{repr(sharedVars.currCharacter2.name)}, {repr(sharedVars.currCharacter.name)}" in chatHistory["logs"]:
                sharedVars.chatKey = f"{repr(sharedVars.currCharacter2.name)}, {repr(sharedVars.currCharacter.name)}"
            else:
                raise ValueError("reversed key not found")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            sharedVars.chatKey = f"{repr(sharedVars.currCharacter.name)}, {repr(sharedVars.currCharacter2.name)}" if sharedVars.currCharacter2 else repr(sharedVars.currCharacter.name)
        
        for character in [sharedVars.currCharacter, sharedVars.currCharacter2]:
            if character:
                if 'Robert' in character.personality:
                    character.personality = character.personality.replace('Robert', sharedVars.player.name)
                if 'Robert' in character.backstory:
                    character.backstory = character.backstory.replace('Robert', sharedVars.player.name)

        sharedVars.player.charLores[sharedVars.chatKey] = {"setting": self.currSettingInput.text, "lore": self.loreInput.text}

        # Start the chat
        self.layout.clear_widgets()
        self.layout.add_widget(RootWidget())

if __name__ == '__main__':
    Startup().run()

