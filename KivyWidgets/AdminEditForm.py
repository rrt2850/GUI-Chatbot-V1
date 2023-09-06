"""
Author: Robert Tetreault (rrt2850)
Filename: AdminEditForm.py
Description: A version of a ScrollableEditForm formatted for editing various variables during runtime.
             This is a very specific class, and is not intended to be used for anything other than
             editing the settings of the game.
"""

import json
from attr import field
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from CharacterScripts.DataHandler import loadSave, save, sharedVars
from KivyWidgets.ScrollableEditForm import ScrollableForm

def getCharacterFields(char):
    return [
        f"{char.name} Personality", f"{char.name} Backstory",
        f"{char.name} Outfit Summary", f"{char.name} Tropes"
    ]

def getCharacterData(char):
    return [
        char.personality, char.backstory,
        char.outfitSummary, char.tropes
    ]

gptFieldsMap = {
    "Temperature": "temperature",
    "Top P": "topP",
    "Max Tokens": "maxTokens",
    "Frequency Penalty": "frequencyPenalty",
    "Presence Penalty": "presencePenalty",
    "Token Limit": "tokenLimit"
}


class EditForm(BoxLayout):
    """
    a form for editing various variables during runtime
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.gptVariables = sharedVars.gptStuff
        self.createEditForm()

    def submit(self, instance):
        """
        Submits the form and updates the variables
        note: Assumes that player and character are already loaded
        """

        # Update gptVariables, Player and Characters from form inputs
        self.updateFromFormInputs()
        save()

        # Make a new prompt with the updated variables
        messages = sharedVars.messages
        newPrompt = sharedVars.currCharacter.makePrompt()

        # Update chatHistory and messages with new prompt
        self.updateHistory(newPrompt, messages, "prompt")
        sharedVars.prompt = newPrompt

        newSystemMessage = self.form.text_inputs["System Message"].text
        currSystemMessage = sharedVars.setting

        # If the system message has changed, update it
        if newSystemMessage != currSystemMessage:
            self.updateHistory(newSystemMessage, messages, "system")    # Update chatHistory with new system message
            sharedVars.setting = newSystemMessage                 # Update sharedVars
            self.parent.parent.parent.chatBox.chatLoop()                # get a new response from the chatbot

        self.parent.parent.toggleSidebar(None)  # Close the form

    def updateHistory(self, content, history, role):
        """
        Updates the chat history, adding the new content
        """
        # define chat history filename
        filename = f"CharacterJsons/ChatHistory{sharedVars.player.name}.json"

        # load chat history if it exists, else empty dictionary
        try:
            with open(filename, 'r') as f:
                chatHistory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            chatHistory = {}

        # Ensure 'logs' key always exists and is a dictionary
        chatHistory.setdefault("logs", {})

        # Get current conversation
        chatKey = sharedVars.chatKey
        currConversation = chatHistory["logs"].get(chatKey, [])
        
        # Update conversation and messages
        newMessage = {"role": "user" if role == "prompt" else "system", "content": content}
        if role == "prompt":

            # Note: I don't remember why I have currConversation and history,
            #       but I feel hesitant to change it
            # Note: I'm looking at it now and I REALLY don't remember why I did this
            if len(currConversation) < 5:
                currConversation.insert(-2, newMessage)
                history.insert(-2, newMessage)
            else:
                currConversation.insert(-5, newMessage)
                history.insert(-5, newMessage)
        else:
            currConversation.append(newMessage)
            history.append(newMessage)

        sharedVars.messages = history
        # update the json file
        with open(filename, 'w') as f:
            json.dump(chatHistory, f, indent=4)

    def updateFromFormInputs(self):
        """
        Updates the variables from the form inputs
        """

        # initialize variables and dictionary keys
        player = sharedVars.player
        char1 = sharedVars.currCharacter
        char2 = sharedVars.currCharacter2
        gptFields = list(gptFieldsMap.keys())
        characterFields = ["Personality", "Backstory", "Tropes", "Outfit Summary"]

        # update gptVariables
        self.gptVariables = {
            gptFieldsMap[field]: int(self.form.text_inputs[field].text) if "token" in field.lower() else float(self.form.text_inputs[field].text)
            for field in gptFields
        }

        # Update player variables
        player.name = self.form.text_inputs["Player Name"].text
        player.lore = self.form.text_inputs["Player Lore"].text

        # Update character variables
        #   I did it this way to save space, it's kind of gross doing a for loop
        #   when there's only two characters, but it's not that bad and looks better
        chars = [char1, char2] if char2 else [char1]
        for char in chars:
            for field in characterFields:
                char.__setattr__(field.lower(), self.form.text_inputs[f"{char.name} {field}"].text)

        # Update sharedVars
        if char2:
            sharedVars.currCharacter2 = char2
        sharedVars.player = player
        sharedVars.currCharacter = char1
        sharedVars.gptStuff = self.gptVariables

    def createEditForm(self):
        """
        Initializes the form with the current values of the variables
        """

        # Get the current player and characters
        char1 = sharedVars.currCharacter
        char2 = sharedVars.currCharacter2
        player = sharedVars.player

        # set up the player fields of the form
        formNames = ["Player Name", "Player Lore", "System Message"]
        formText = [player.name, player.lore, sharedVars.setting]

        # set up the character fields of the form
        formNames.extend(getCharacterFields(char1))
        formText.extend(getCharacterData(char1))

        # if there's a second character, add their fields to the form
        if char2:
            formNames.extend(getCharacterFields(char2))
            formText.extend(getCharacterData(char2))

        gptFormNames = list(gptFieldsMap.keys())
        gptFormValues = [str(self.gptVariables[gptFieldsMap[key]]) for key in gptFormNames]

        # add the gpt fields to the form
        formNames.extend(gptFormNames)
        formText.extend(gptFormValues)

        # Create the form and add it to the widget
        self.form = ScrollableForm(on_button_press=self.submit, formNames=formNames, formText=formText)
        self.form.size_hint_y = 0.95
        self.add_widget(self.form)

   
class MyApp(App):
    """
    A class for building the app on its own
    """
    def build(self):
        loadSave()
        systemMessage = "yo?"
        temperature=1
        topP = 1
        maxTokens=210
        frequencyPenalty=2
        presencePenalty=2
        tokenLimit=3500
        sharedVars.setting = systemMessage
        sharedVars.gptStuff = {
            "temperature": temperature,
            "topP": topP,
            "maxTokens": maxTokens,
            "frequencyPenalty": frequencyPenalty,
            "presencePenalty": presencePenalty,
            "tokenLimit": tokenLimit
        }
        currCharacter = (list(sharedVars.characters.items())[0])[1]
        sharedVars.currCharacter = currCharacter
        return EditForm()

 
def start():
    MyApp().run()
