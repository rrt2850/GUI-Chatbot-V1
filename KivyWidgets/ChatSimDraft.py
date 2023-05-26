import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"

import dotenv
dotenv.load_dotenv()
import openai
import tiktoken
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from CharacterScripts.CharacterHandler import loadSave, sharedVars
from KivyWidgets.DisplayBuilding import BuildingGrid
from KivyWidgets.AdminEditForm import EditForm
from KivyWidgets.CollapsibleSidebar import CollapsibleSidebar
from KivyWidgets.ChatWindow import ChatBoxLayout
from WorldScripts.BuildingClass import gymPreset


# Initialize API keys
openai.api_key = os.environ["OPENAI_API_KEY"]

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


def start():
    loadSave()
    currCharacter = (list(sharedVars.getCharacters().items())[0])[1]
    prompt = currCharacter.makePrompt()

    sharedVars.setCurrCharacter(currCharacter)
    sharedVars.setPrompt(prompt)

    ChatBotApp().run()

def makeBuilding(func=gymPreset):
    building = func()
    if building.grid is None:
        print("Error: Unable to make building grid")
        return
    
    print(f"{len(building.grid)} x {len(building.grid[0])}")
    for row in building.grid:
        print(row)

    buildingGrid = BuildingGrid(building=building)
    buildingGrid.grid = building.grid
    buildingGrid.grid_size = max(len(building.grid), max(len(row) for row in building.grid))
    return buildingGrid


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        systemMessage = f"*{sharedVars.getCurrCharacter().name.first} is sitting in the study in her apartment when {sharedVars.getPlayer().name} walks in, {sharedVars.getPlayer().name} has been away on business for a month*"
        sharedVars.setSystemMessage(systemMessage)

        self.building = CollapsibleSidebar(buttonTextClosed="Map", buttonTextOpen="Close Map")
        self.building.content.add_widget(makeBuilding())

        self.adminForm = CollapsibleSidebar(buttonTextClosed="Edit", buttonTextOpen="Close")
        self.adminForm.content.add_widget(EditForm())

        self.chatBox = ChatBoxLayout()

        self.add_widget(self.building)
        self.add_widget(self.chatBox)
        self.add_widget(self.adminForm)

class ChatBotApp(App):
    def build(self):
        self.title = 'Chris\'s Leanbeef Fantasy'
        self.icon = 'dreamybull.jpg'
        #self.title = 'super neat robo-girlfriend, name tbd'
        return RootWidget() 
