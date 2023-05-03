from collections import deque
import os
import re
import sys

import dotenv
import openai
import tiktoken
from datasets import load_dataset
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from tqdm.auto import tqdm
from kivy.uix.relativelayout import RelativeLayout
from CharacterScripts.CharacterClass import Character, Name
from CharacterScripts.CharacterHandler import loadSave, sharedVars
from CharacterScripts.CharacterMaker import Player
from SharedVariables import SharedVariables
from WorldScripts.BuildingClass import Building, Room
from WorldScripts.ItemClass import Item
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, Color
from kivy.uix.floatlayout import FloatLayout

dotenv.load_dotenv()

# Initialize API keys
openai.api_key = os.environ["OPENAI_API_KEY"]

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

prompt=None


def load_chat_history(self, filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            self.ids.messages.text = f.read()

def save_chat_history(self, filename):
    with open(filename, "w") as f:
        f.write(self.ids.messages.text)

def formatPropt():
    global prompt
    prompt=f"""
You are playing a character named {sharedVars.getCurrCharacter().name.first}, you must respond to the user as if you are {sharedVars.getCurrCharacter().getPronounPersonalSingular()} and never break character.
If you break character {sharedVars.getPlayer().name} the user will be disappointed and sad. use the DESCRIPTION listed below to help you get into character.
IMPORTANT: don't just copy and paste the description, use it as a guide to help you get into character only. Repeating things from the description unmodified and unprompted is not very humanlike and will make the user sad.
IMPORTANT: Whenever you do something physical put it in asterisks and describe it like *hugs you* or *I hug you* etc, but be sure to talk in first person and not third person.
Don't let asterisk statements get too long.
if you a personality type is specified, try to act like that personality type when possible.
if you become intoxicated or your mind is altered in any way, you must act like you are intoxicated or your mind is altered in any way, changing your personality, word spelling, and behavior accordingly. Example: Heyy guyyysss, hiccup whassup? giggles I just had the besht nigh' evaaaa! I danced like nobody'sh watchin'! You guysh are the besht! hiccup
Feel free to elaborate and build on {sharedVars.getCurrCharacter().getPronounPersonalSingular()} personality and backstory, but don't contradict the description.
don't say the users name too much or it will break immersion, instead use terms like "you" and "your" to refer to the user. but use the users name when appropriate, just don't overdo it.
when responding, think about your DESCRIPTION and relate the users message to yourself and your life, and respond accordingly. for example, if the user talks about their job, you could talk about your job. if the user talks about their family, you could talk about your family. if the user talks about their hobbies, you could talk about your hobbies. etc.
DESCRIPTION:
You are {sharedVars.getCurrCharacter().name}. Your description is: {sharedVars.getCurrCharacter().description}.
Your backstory is: {sharedVars.getCurrCharacter().backstory}. Your personality type is {sharedVars.getCurrCharacter().tropes}.
You are currently roommates with {sharedVars.getPlayer().name} (the user) you planned this but he doesn't know.
You are a {sharedVars.getCurrCharacter().age} year old {sharedVars.getCurrCharacter().gender} who is {sharedVars.getCurrCharacter().height} inches tall
and has {sharedVars.getCurrCharacter().hairColor} {sharedVars.getCurrCharacter().hairStyle} hair, {sharedVars.getCurrCharacter().eyeColor} eyes, {sharedVars.getCurrCharacter().breastSize} breasts,
and {sharedVars.getCurrCharacter().skinColor} skin. This is your outfit description: {sharedVars.getCurrCharacter().outfitSummary}. 
"""
#You invited {sharedVars.getPlayer().name} over to your house to hang out tonight.

kv = '''
<RootWidget>:
    orientation: 'horizontal'

<CollapsibleSidebar>:
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size

<ChatBoxLayout>:
    orientation: 'vertical'
    padding: 10
    spacing: 4

    ScrollView:
        id: scroll_view
        bar_width: 10
        effect_cls: 'ScrollEffect'
        scroll_type: ['bars', 'content']
        scroll_wheel_distance: 10

        Label:
            id: messages
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            font_size: '16sp'
            markup: True
            valign: 'top'
            halign: 'left'
            padding: 10, 10
            spacing: 4

    BoxLayout:
        size_hint_y: 0.1
        orientation: 'horizontal'
        CustomTextInput:
            id: user_input
            multiline: False
            do_wrap: True
            hint_text: 'Type your message...'
            on_text_validate: root.send_message()
            font_size: '16sp'
            size_hint_x: 0.9
            text_validate_unfocus: False

        Button:
            text: 'Send'
            on_press: root.send_message()
            font_size: '16sp'
            size_hint_x: 0.1
'''

def count_tokens(text):
    tokens = []
    try:
        tokens = encoding.encode(text)
    except:
        print("Error: Unable to encode text")
    return len(tokens)

def start():
    loadSave()
    currCharacter = list(sharedVars.getCharacters().items())[0]
    sharedVars.setCurrCharacter(currCharacter[1])
    formatPropt()
    ChatBotApp().run()

from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

class BuildingMap(ScrollView):
    building = ObjectProperty(None)

    def __init__(self, building, **kwargs):
        super(BuildingMap, self).__init__(**kwargs)
        self.building = building
        self.draw_map()

    def draw_map(self):
        map_layout = {}  # Dictionary to store room positions
        start_room = self.building.rooms[0]
        map_layout[start_room] = (0, 0)

        # Recursive function to traverse rooms and set their positions
        def set_room_positions(room, x, y):
            if room.north and room.north not in map_layout:
                map_layout[room.north] = (x, y + 1)
                set_room_positions(room.north, x, y + 1)
            if room.south and room.south not in map_layout:
                map_layout[room.south] = (x, y - 1)
                set_room_positions(room.south, x, y - 1)
            if room.east and room.east not in map_layout:
                map_layout[room.east] = (x - 1, y)
                set_room_positions(room.east, x - 1, y)
            if room.west and room.west not in map_layout:
                map_layout[room.west] = (x + 1, y)
                set_room_positions(room.west, x + 1, y)

        set_room_positions(start_room, 0, 0)

        max_x = max(pos[0] for pos in map_layout.values())
        min_x = min(pos[0] for pos in map_layout.values())
        max_y = max(pos[1] for pos in map_layout.values())
        min_y = min(pos[1] for pos in map_layout.values())

        width = (max_x - min_x + 1) * 100
        height = (max_y - min_y + 1) * 100

        map_layout_widget = FloatLayout(size_hint=(None, None), size=(width, height))

        for room, pos in map_layout.items():
            x, y = pos
            button = Button(text=room.name, size_hint=(None, None), size=(100, 100))
            button.pos = ((x - min_x) * 100, (max_y - (y - min_y)) * 100)
            map_layout_widget.add_widget(button)

        self.add_widget(map_layout_widget)






class CollapsibleSidebar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = 0.25
        self.collapsed = False

        self.button = Button(text="Toggle Sidebar", size_hint_y=None, height=30, font_size='12sp')
        self.button.bind(on_press=self.toggle_sidebar)
        self.add_widget(self.button)

        self.building_widget = self.create_building_representation()
        self.add_widget(self.building_widget)

    def create_building_representation(self):
        building = Building("My Building", "This is my building")

        kitchen = Room()
        kitchen.name = "Kitchen"
        characterRoom = Room()
        characterRoom.name = f"{sharedVars.getCurrCharacter().name}'s Room"
        playerRoom = Room()
        playerRoom.name = f"{sharedVars.getPlayer().name}'s Room"
        livingRoom = Room()
        livingRoom.name = "Living Room"
        entrance = Room()
        entrance.name = "Entrance"
        hallwayA = Room()
        hallwayA.name = "Hallway A"
        hallwayB = Room()
        hallwayB.name = "Hallway B"
        hallwayC = Room()
        hallwayC.name = "Hallway C"
        hallwayD = Room()
        hallwayD.name = "Hallway D"

        building.addRoom(entrance, [kitchen], ["north"])
        building.addRoom(kitchen, [entrance, livingRoom, hallwayA], ["south", "west", "east"])
        building.addRoom(livingRoom, [kitchen], ["east"])
        building.addRoom(hallwayA, [hallwayB, kitchen], ["north", "west"])
        building.addRoom(hallwayB, [hallwayC, hallwayA], ["north", "south"])
        building.addRoom(hallwayC, [hallwayD, characterRoom, hallwayB], ["north", "west", "south"])
        building.addRoom(characterRoom, [hallwayC], ["east"])
        building.addRoom(hallwayD, [playerRoom, hallwayC], ["east", "south"])
        building.addRoom(playerRoom, [hallwayD], ["west"])

        print(building.rooms)
        building_representation = BuildingMap(building)
        return building_representation

    def toggle_sidebar(self, instance):
        if self.collapsed:
            self.size_hint_x = 0.40
            self.collapsed = False
            self.button.text = "Toggle Sidebar"
            self.building_widget.opacity = 1  # Make the building visible
        else:
            self.size_hint_x = 0.10
            self.collapsed = True
            self.button.text = "..."
            self.building_widget.opacity = 0  # Hide the buildin

class CustomTextInput(TextInput):
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "enter" and not modifiers:
            self.dispatch("on_text_validate")
            self.focus = True
            return True
        return super()._keyboard_on_key_down(window, keycode, text, modifiers)

class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.sidebar = CollapsibleSidebar()
        self.chat_box = ChatBoxLayout()
        self.add_widget(self.sidebar)
        self.add_widget(self.chat_box)


class ChatBotApp(App):
    def build(self):
        Builder.load_string(kv)
        return RootWidget()


class ChatBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.messages = [{"role": "system", "content": prompt}]
        #self.messages.append({"role": "system", "content": f"*{sharedVars.getPlayer().name} walks in and sees you sitting at your desk, it's 8pm and the mood is relaxed and intimate*"})
        #Clock.schedule_once(self.send_initial_message, 0.5)
        #Clock.schedule_once(lambda dt: self.load_chat_history("chat_history.txt"), 0.1)

    def send_initial_message(self, dt):
        response_message = self.chatLoop("")  # Pass an empty string as the initial user message
        formatted_response_message = f"[color=#FFA500][b]{sharedVars.getCurrCharacter().name.first}:[/b][/color] {response_message}"
        self.append_message(formatted_response_message)

    def send_message(self):
        user_message = self.ids.user_input.text
        if not user_message.strip():
            return

        formatted_user_message = f"[color=#32CD32][b]You:[/b][/color] {user_message}"
        self.append_message(formatted_user_message)
        self.ids.user_input.text = ""

        response_message = self.chatLoop(user_message)
        formatted_response_message = f"[color=#FFA500][b]{sharedVars.getCurrCharacter().name.first}:[/b][/color] {response_message}"
        self.append_message(formatted_response_message)

    def append_message(self, message):
        if self.ids.messages.text:
            self.ids.messages.text += "\n\n"
        self.ids.messages.text += message

    def chatLoop(self, user_message):
        if user_message:
            self.messages.append({"role": "user", "content": user_message})

        total_tokens = 0
        for message in self.messages:
            total_tokens += count_tokens(message["content"])

        print(f"Total tokens: {total_tokens}")
        token_limit = 3300  # Set an arbitrary token limit
        while total_tokens > token_limit:
            # Remove a user message and its corresponding assistant message
            removed_user_message = self.messages.pop(1)
            removed_assistant_message = self.messages.pop(1)
            print(f"Removed user message: {removed_user_message}")
            print(f"Removed assistant message: {removed_assistant_message}")
            total_tokens -= count_tokens(removed_user_message["content"])
            total_tokens -= count_tokens(removed_assistant_message["content"])

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            temperature=.5,
            max_tokens=210,
            top_p=1,
            frequency_penalty=0.7,
            presence_penalty=0.5
        )

        self.messages.append(response.choices[0].message)

        return response.choices[0].message.content
