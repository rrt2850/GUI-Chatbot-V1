import json
import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.app import App
from kivy.core.window import Window

from CharacterScripts.CharacterHandler import loadSaveDev, sharedVars, save
from KivyWidgets.ChatSim import RootWidget
from KivyWidgets.SetupForms import NewPlayerForm

kivy.require('2.0.0')

class Startup(App):
    def build(self):
        self.layout = GridLayout(cols=1)

        # initialize title and icon
        if sharedVars.devMode:
            self.title = 'b-b-b-buss'
            self.icon = 'dreamybull.jpg'
        else:
            self.title = 'super neat robo-girlfriend, name tbd'

        def on_request_close(*args):
            save()

        # Set the function to be called when the window is about to close
        Window.bind(on_request_close=on_request_close)

        # Load save data
        loadSaveDev()
        
        # Create a list of characters from shared variables
        characters = list(sharedVars.characters.values())
        players = sharedVars.players

        # Check if there are no players, if so, print an error message and exit the function
        if not players:
            self.layout.add_widget(Label(text='Error: No players found'))

        self.player_buttons = []
        self.character_buttons = []
        self.selected_characters = []

        if len(players) > 0:
            self.layout.add_widget(Label(text='Which player would you like to play as?'))
            for i, player in enumerate(players):
                btn = Button(text=f'{i}: {player.name}', on_press=self.select_player(i))
                self.player_buttons.append(btn)
                self.layout.add_widget(btn)

        self.newPlayer = Button(text='New Player', on_press=self.new_player)
        self.layout.add_widget(self.newPlayer)

        # Check if there are no characters, if so, print an error message and exit the function
        if not characters:
            self.layout.add_widget(Label(text='Error: No characters found'))

        self.layout.add_widget(Label(text='Which characters would you like to talk to? (up to two)'))
        for i, character in enumerate(characters):
            btn = Button(text=f'{i}: {character.name}', on_press=self.select_character(character.name))
            self.character_buttons.append(btn)
            self.layout.add_widget(btn)

        # Create an error label and add it to the layout
        self.error_label = Label(text='')
        self.layout.add_widget(self.error_label)

        # Add the start button to the layout
        start_btn = Button(text='Start', on_press=self.start_chat)
        self.layout.add_widget(start_btn)

        return self.layout

    def new_player(self, instance):
        modalView = ModalView()
        modalView.add_widget(NewPlayerForm())
        modalView.open()

    def select_player(self, index):
        def callback(instance):
            sharedVars.player = sharedVars.players[index]
            instance.background_color = (0, 1, 0, 1)  # change button color to green

            # reset color for all other player buttons
            for btn in self.player_buttons:
                if btn != instance:
                    btn.background_color = (1, 1, 1, 1)  # change button color to default (white)

        return callback

    def select_character(self, name):
        def callback(instance):
            if instance in self.selected_characters:  # if character already selected, deselect it
                self.selected_characters.remove(instance)
                instance.background_color = (1, 1, 1, 1)  # change button color to default (white)
                
                if sharedVars.currCharacter == sharedVars.getCharacter(name):
                    if sharedVars.currCharacter2:
                        sharedVars.currCharacter = sharedVars.currCharacter2
                        sharedVars.currCharacter2 = None
                    else:
                        sharedVars.currCharacter = None
                else:
                    sharedVars.currCharacter2 = None
            elif len(self.selected_characters) < 2:  # if less than two characters are selected, select it
                self.selected_characters.append(instance)
                instance.background_color = (0, 1, 0, 1)  # change button color to green
                if sharedVars.currCharacter is None:
                    sharedVars.currCharacter = sharedVars.getCharacter(name)
                else:
                    sharedVars.currCharacter2 = sharedVars.getCharacter(name)

        return callback

    def start_chat(self, instance):
        # Check if both a player and at least one character have been selected
        if sharedVars.player is None or sharedVars.currCharacter is None:
            # If not, display an error message in the error label and return from the function
            self.error_label.text = 'Error: Please select a player and at least one character before starting the chat.'
            return

        # If no error, clear the error label
        self.error_label.text = ''

        # Clear the screen
        self.layout.clear_widgets()
        
        # System message text input
        self.system_message_input = TextInput(text=f"*{sharedVars.player.name} is smoking on the couch with {sharedVars.currCharacter.name.first}. The mood is relaxed*")
        self.layout.add_widget(Label(text="Edit system message:"))
        self.layout.add_widget(self.system_message_input)
        
        # Button to save the system message and display the prompt
        self.layout.add_widget(Button(text="Start Conversation", on_press=self.start_conversation))
        
        # Label to display the prompt
        self.prompt_label = Label()
        self.layout.add_widget(self.prompt_label)
    
    def start_conversation(self, instance):
        # Set system message
        sharedVars.systemMessage = self.system_message_input.text
        
        # Generate initial prompt
        sharedVars.prompt = sharedVars.currCharacter.makePrompt()
        
        # Display the prompt
        self.prompt_label.text = "Prompt: " + sharedVars.prompt
        
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

