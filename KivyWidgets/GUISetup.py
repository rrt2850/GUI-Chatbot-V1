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
            self.icon = 'dreamybull.jpg'
        else:
            self.title = 'super neat robo-girlfriend, name tbd'

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

        self.newPlayer = Button(text='New Player', on_press=self.newPlayer)
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

        return self.layout

    def newPlayer(self, instance):
        modalView = ModalView()
        modalView.add_widget(NewPlayerForm())
        modalView.open()

    def selectPlayer(self, index):
        def callback(instance):
            sharedVars.player = sharedVars.players[index]
            instance.background_color = (0, 1, 0, 1)  # change button color to green

            # reset color for all other player buttons
            for button in self.playerButtons:
                if button != instance:
                    button.background_color = (1, 1, 1, 1)  # change button color to default (white)

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
        
        # if there is no system message, set it to the default. feel free to change the default to whatever you want
        if sharedVars.systemMessage is None:
            sharedVars.systemMessage = f"*{sharedVars.player.name} is smoking on the couch with {sharedVars.currCharacter.name.first}. The mood is relaxed*"

        # System message text input
        self.systemMessageInput = TextInput(text=sharedVars.systemMessage)
        self.inputs.add_widget(Label(text="Edit system message:"))
        self.inputs.add_widget(self.systemMessageInput)

        # Lore text input
        self.loreInput = TextInput(text=sharedVars.player.lore)
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
        sharedVars.systemMessage = self.systemMessageInput.text
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

        # Start the chat
        self.layout.clear_widgets()
        self.layout.add_widget(RootWidget())

if __name__ == '__main__':
    Startup().run()
