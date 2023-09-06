"""
Author: Robert Tetreault (rrt2850)
Filename: main.py
Description: Main entry point for the chat simulator. This script provides a starting point for the 
             application, either in developer mode or player mode.
"""

import json
from CharacterScripts.DataHandler import loadSave, sharedVars

from KivyWidgets.ChatSim import ChatBotApp
#from KivyWidgets.DisplayBuilding import start
#from KivyWidgets.AdminEditForm import start


def startDev():
    """
    Initializes the application in developer mode. This function loads saved characters, lets the user select 
    characters to chat with, and runs the chatbot application in a quick, console based, version.
    """
    
    # Load save data
    loadSave()
    
    # Create a list of characters from shared variables
    characters = list(sharedVars.characters.values())
    players = sharedVars.players

    # Check if there are no players, if so, print an error message and exit the function
    if not players:
        print("Error: No players found")
        return

    # If there's more than one player, ask the user which one they'd like to play as
    if len(players) > 1:
        print("Which player would you like to play as?")
        print("\n".join(f"{i}: {player.name}" for i, player in enumerate(players)))
        playerIndex = input("Enter the number of the player you would like to play as: ")
        sharedVars.player = players[int(playerIndex)]
    else:
        sharedVars.player = players[0]

    # Check if there are no characters, if so, print an error message and exit the function
    if not characters:
        print("Error: No characters found")
        return

    # If there's more than one character, ask the user which ones they'd like to talk to
    if len(characters) > 1:
        print("Which characters would you like to talk to? (up to two)")
        
        # Print out the list of characters
        print("\n".join(f"{i}: {character.name}" for i, character in enumerate(characters)))

        # Get input from the user on which characters they'd like to talk to
        characterIndices = input("Enter the numbers of the characters you would like to talk to, separated by a space: ").split()

        # If no characters were selected, print an error message and quit
        if not characterIndices:
            print("Error: No characters selected")
            return

        # Get the characters chosen by the user
        currCharacter = characters[int(characterIndices[0])]
        currCharacter2 = characters[int(characterIndices[1])] if len(characterIndices) > 1 else None
    else:
        # If there's only one character, select that one by default
        currCharacter, currCharacter2 = characters[0], None

    # Set the current character(s) in shared variables
    sharedVars.currCharacter = currCharacter
    sharedVars.currCharacter2 = currCharacter2

    # if there is no setting, set it to the default. feel free to change the default to whatever you want
    if sharedVars.setting is None:
        setting = f"*{sharedVars.player.name} is chilling with {sharedVars.currCharacter.name.first}. The mood is relaxed*"

    # Set the system message and prompt in shared variables
    sharedVars.setting = setting

    # Generate the initial prompt and system message
    prompt = currCharacter.makePrompt()
    sharedVars.prompt = prompt

    # Initialize the chat history
    chatHistory = {"logs": {}}

    try:
        # Attempt to load the chat history from a file
        with open(f"CharacterJsons/ChatHistory{sharedVars.player.name}.json", 'r') as f:
            chatHistory = json.load(f)
        
        # If there are two characters and their history is in the logs, set the chat key to their conversation
        if currCharacter2 and f"{repr(currCharacter2.name)}, {repr(currCharacter.name)}" in chatHistory["logs"]:
            sharedVars.chatKey = f"{repr(currCharacter2.name)}, {repr(currCharacter.name)}"
        else:
            # If the history is not found, raise an exception
            raise ValueError("reversed key not found")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        # If there was a problem, set the chat key to default
        sharedVars.chatKey = f"{repr(currCharacter.name)}, {repr(currCharacter2.name)}" if currCharacter2 else repr(currCharacter.name)
    
    for character in [currCharacter, currCharacter2]:
        if character:
            # If Character info was written with Robert as the player name, replace it with the actual player name
            if 'Robert' in character.personality:
                character.personality = character.personality.replace('Robert', sharedVars.player.name)
            if 'Robert' in character.backstory:
                character.backstory = character.backstory.replace('Robert', sharedVars.player.name)

    # Run the application
    ChatBotApp().run()

if __name__ == '__main__':
    sharedVars.devMode = False # There's probably a better way to do this, but it's not super important for now
    
    if sharedVars.devMode:
        startDev()
    else:
        # Set the kivy console to so that it doesn't display debug messages
        import os
        os.environ["KIVY_NO_CONSOLELOG"] = "1"

        # Load the environment variable that was just set
        import dotenv
        from KivyWidgets.GUISetup import Startup

        dotenv.load_dotenv()
        Startup().run()
