"""
Author: Robert Tetreault (rrt2850)
Filename: ChatSim.py
Description: Initializes the app and it's components and then runs it
"""
import importlib

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from KivyWidgets.DisplayBuilding import BuildingGrid
from KivyWidgets.AdminEditForm import EditForm
from KivyWidgets.CollapsibleSidebar import CollapsibleSidebar
from KivyWidgets.ChatWindow import ChatBoxLayout
from kivy.core.window import Window

from CharacterScripts.CharacterHandler import sharedVars, save

def makeBuilding(functionName=None):
    """
    Constructs the building grid for the map.

    Args:
        functionName (str, optional): A string name of the function to create the building. Defaults to None.
    
    Returns:
        BuildingGrid: The created building grid, or None if an error occurs during creation.
    """
    
    try:
        # Only try to import if a function name was provided
        if functionName is not None:
            module = importlib.import_module('WorldScripts.BuildingClass')
            func = getattr(module, functionName)
        else:
            raise ImportError
    except (ImportError, AttributeError):
        # If no function name was provided or the import fails, default to gymPreset
        from WorldScripts.BuildingClass import gymPreset
        func = gymPreset

    # attempt to make the building
    building = func()
    if building.grid is None:
        print("Error: Unable to make building grid")
        return
    
    # display text version of building if in dev mode
    if sharedVars.devMode:
        print(f"{len(building.grid)} x {len(building.grid[0])}")
        for row in building.grid:
            print(row)

    # create the building widget and initialize the grid
    buildingGrid = BuildingGrid(building=building)
    buildingGrid.grid = building.grid
    
    # if something went wrong, don't add the grid
    if not buildingGrid.grid:
        return
    
    # set the grid size to the largest dimension so that it's square
    buildingGrid.gridSize = max(len(building.grid[0]), len(building.grid))
    return buildingGrid


class RootWidget(BoxLayout):
    """
    Root widget of the application. It hosts building widget, admin form, and chat box.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        # make the building widget and add it's sidebar to the app if it succeeded
        temp = makeBuilding("starterHousePreset")

        if temp:
            self.building = CollapsibleSidebar(buttonTextClosed="Map", buttonTextOpen="Close Map")
            self.building.content.add_widget(temp)
            self.add_widget(self.building)

        # make the admin form and add it, keeping this in both versions for now since the users will
        # want to customize characters probably
        self.adminForm = CollapsibleSidebar(buttonTextClosed="Edit", buttonTextOpen="Close")
        self.adminForm.content.add_widget(EditForm())

        # initialize the chat window
        self.chatBox = ChatBoxLayout()

        # add the widgets to the app
        self.add_widget(self.chatBox)
        self.add_widget(self.adminForm)

class ChatBotApp(App):
    """
    Main application class. Initializes and runs the chatbot application.
    """
    def build(self):
        """
        Build the application. Sets up the title, icon, and root widget.

        Returns:
            RootWidget: The root widget of the application.
        """

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

        return RootWidget()
    
    
