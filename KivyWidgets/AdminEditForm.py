# A version of a ScrollableEditForm formatted for editing various variables during runtime.
# This is a very specific class, and is not intended to be used for anything other than editing
# the settings of the game.

import json
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from CharacterScripts.CharacterHandler import loadSave, save, sharedVars
from KivyWidgets.ScrollableEditForm import ScrollableForm

class EditForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.gptVariables = sharedVars.getGptStuff()
        self.createEditForm()

    def createEditForm(self):
        formNames = [
            "System Message", "Player Name", "Player Lore", 
            f"{sharedVars.getCurrCharacter().name} Personality", f"{sharedVars.getCurrCharacter().name} Backstory", 
            f"{sharedVars.getCurrCharacter().name} Outfit Summary", f"{sharedVars.getCurrCharacter().name} Tropes",
            "Temperature", "Top P", "Max Tokens", 
            "Frequency Penalty", "Presence Penalty", "Token Limit"
        ]
        formText = [
            sharedVars.getSystemMessage(), sharedVars.getPlayer().name, sharedVars.getPlayer().lore,
            sharedVars.getCurrCharacter().personality, sharedVars.getCurrCharacter().backstory,
            sharedVars.getCurrCharacter().outfitSummary, sharedVars.getCurrCharacter().tropes,
            str(self.gptVariables["temperature"]), str(self.gptVariables["topP"]), str(self.gptVariables["maxTokens"]),
            str(self.gptVariables["frequencyPenalty"]), str(self.gptVariables["presencePenalty"]), str(self.gptVariables["tokenLimit"])
        ]

        self.form = ScrollableForm(on_button_press=self.submit, formNames=formNames, formText=formText)
        self.form.size_hint_y = 0.95
        self.add_widget(self.form)

    def submit(self, instance):
        tempPlayer = sharedVars.getPlayer()
        tempChar = sharedVars.getCurrCharacter()

        if not tempPlayer or not tempChar:
            print("Error: Unable to find either player or character")
            return

        # Update gptVariables, Player and Character from form inputs
        self.updateFromFormInputs(tempPlayer, tempChar)

        sharedVars.setPlayer(tempPlayer)
        sharedVars.setCurrCharacter(tempChar)
        sharedVars.setGptStuff(self.gptVariables)

        save()

        prompt = tempChar.makePrompt()
        messages = sharedVars.getMessages()

        # Update chatHistory and messages with new prompt
        self.updateChatHistoryAndMessages(prompt, "system", messages)

        systemMessage = self.form.text_inputs["System Message"].text
        if systemMessage != sharedVars.getSystemMessage():
            messages.append({"role": "system", "content": systemMessage})

            # Update chatHistory and messages with new system message
            self.updateChatHistoryAndMessages(systemMessage, "system", messages, append=True)

            self.parent.parent.parent.chatBox.sendInitialMessage(0.2)
            sharedVars.setSystemMessage(systemMessage)

        sharedVars.setPrompt(prompt)
        sharedVars.setMessages(messages)
        
        self.parent.parent.toggleSidebar(None)  # Close the form

    def updateFromFormInputs(self, player, character):
        formFields = ["Temperature", "Top P", "Max Tokens", "Frequency Penalty", "Presence Penalty", "Token Limit"]
        for field in formFields:
            self.gptVariables[field.lower()] = float(self.form.text_inputs[field].text) if "Tokens" not in field else int(self.form.text_inputs[field].text)
        
        player.name = self.form.text_inputs["Player Name"].text
        player.lore = self.form.text_inputs["Player Lore"].text
        characterFields = ["Description", "Backstory", "Tropes", "Outfit Summary"]
        for field in characterFields:
            character.__setattr__(field.lower(), self.form.text_inputs[f"{character.name} {field}"].text)

    def updateChatHistoryAndMessages(self, content, role, messages, append=False):
        try:
            with open(f"ChatHistory{sharedVars.getPlayer().name}.json", 'r') as f:
                chatHistory = json.load(f)

            if chatHistory.get("logs") is not None:
                characterName = repr(sharedVars.getCurrCharacter().name)
                if chatHistory["logs"].get(characterName) is not None:
                    if append:
                        chatHistory["logs"][characterName].append({"role": role, "content": content})
                        messages.append({"role": role, "content": content})
                    else:
                        chatHistory["logs"][characterName][0] = {"role": role, "content": content}
                        messages[0] = {"role": role, "content": content}

                    with open(f"ChatHistory{sharedVars.getPlayer().name}.json", 'w') as f:
                        json.dump(chatHistory, f, indent=4)

        except (FileNotFoundError, json.JSONDecodeError):
            pass


   
class MyApp(App):
    def build(self):
        loadSave()
        systemMessage = "yo?"
        temperature=1
        topP = 1
        maxTokens=210
        frequencyPenalty=2
        presencePenalty=2
        tokenLimit=3500
        sharedVars.setSystemMessage(systemMessage)
        sharedVars.setGptStuff({
            "temperature": temperature,
            "topP": topP,
            "maxTokens": maxTokens,
            "frequencyPenalty": frequencyPenalty,
            "presencePenalty": presencePenalty,
            "tokenLimit": tokenLimit
        })
        currCharacter = (list(sharedVars.getCharacters().items())[0])[1]
        sharedVars.setCurrCharacter(currCharacter)
        return EditForm()

 
def start():
    MyApp().run()