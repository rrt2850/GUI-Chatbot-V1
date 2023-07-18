"""
Author: Robert Tetreault (rrt2850)
Filename: SetupForms.py
Description: A version of a ScrollableEditForm formatted for creating players/characters during setup.
"""

import json
from attr import field
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from CharacterScripts.CharacterHandler import loadSave, save, sharedVars
from CharacterScripts.CharacterClass import Player
from KivyWidgets.ScrollableEditForm import ScrollableForm

class NewPlayerForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.formNames = ["Name", "Age", "Gender", "Sexuality", "Lore"]
        self.formText = ["What's your name?", "How old are you?", "What is your gender?", "What is your sexuality?", "Any extra info?"]
        self.form = ScrollableForm(self.submit, self.formNames, self.formText)

        self.add_widget(self.form)

    def submit(self, instance):
        player = Player()

        for field in self.formNames:
            player.__setattr__(field.lower(), self.form.text_inputs[field].text)
        
        sharedVars.players.append(player)
        self.parent.dismiss()