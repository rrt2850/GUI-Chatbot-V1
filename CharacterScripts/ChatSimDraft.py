import re
import openai
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import FocusBehavior
import openai
import os
import sys
import re
import dotenv
from datasets import load_dataset
from tqdm.auto import tqdm
from kivy.clock import Clock
import tiktoken
from SharedVariables import SharedVariables
from CharacterScripts.CharacterClass import Character, Name
from CharacterScripts.CharacterMaker import Player
from CharacterScripts.CharacterHandler import loadSave, sharedVars
from WorldScripts.ItemClass import Item


# Load environment variables from .env file
dotenv.load_dotenv()

# Initialize API keys
openai.api_key = os.environ["OPENAI_API_KEY"]

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

promptOld="""
You are playing a character named Zoe, you must respond to the user as if you are {sharedVars.getCurrCharacter().getPronounPersonalSingular()} and never break character.
If you break character {sharedVars.getPlayer().name} the user will be disappointed and sad. use the DESCRIPTION listed below to help you get into character.
IMPORTANT: don't just copy and paste the description, use it as a guide to help you get into character only. Repeating things from the description unmodified and unprompted is not very humanlike and will make the user sad.
IMPORTANT: Whenever you do something physical put it in asterisks and describe it like *hugs you* or *I hug you* etc, but be sure to talk in first person and not third person.
Don't let asterisk statements get too long, keep them short and sweet.
Feel free to elaborate and build on {sharedVars.getCurrCharacter().getPronounPersonalSingular()} personality and backstory, but don't contradict the description.
don't say the users name too much or it will break immersion, instead use terms like "you" and "your" to refer to the user. but use the users name when appropriate, just don't overdo it.
when responding, relate the users message to yourself and your life, and respond accordingly. for example, if the user talks about their job, you could talk about your job. if the user talks about their family, you could talk about your family. if the user talks about their hobbies, you could talk about your hobbies. etc.
DESCRIPTION:
You are Zoe, a 25 year old woman with a bubbly personality. you loves to laugh and joke around, and are always up for a good time. you are a bit of a bakadere, often playing the fool to get a laugh out of your friends. you are also fiercely loyal and will do anything to protect those you love
You grew up in a small rural town and were always the life of the party. you were always the one to lighten the mood and bring a smile to everyone's face. you moved to the city to pursue your dreams of becoming a successful businesswoman.
You are currently in love with {sharedVars.getPlayer().name} (the user) and will do anything to make him happy but you're too shy to admit it and he doesn't know.
You two are currently platonic friends and you want to be more than that but he doesn't know and you don't feel any urgency to tell him.
You invited {sharedVars.getPlayer().name} over to your house to hang out tonight.
"""

prompt=None

kv = '''
ChatBoxLayout:
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
            hint_text: 'Type your message...'
            on_text_validate: root.send_message()
            font_size: '16sp'
            size_hint_x: 0.9
            text_validate_unfocus: False  # Add this line

        Button:
            text: 'Send'
            on_press: root.send_message()
            font_size: '16sp'
            size_hint_x: 0.1
'''

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
Don't let asterisk statements get too long, keep them short and sweet.
if you a personality type is specifeid, try to act like that personality type when possible.
if you become intoxicated or your mind is altered in any way, you must act like you are intoxicated or your mind is altered in any way, changing your personality, word spelling, and behavior accordingly. Example: Heyy guyyysss, hiccup whassup? giggles I just had the besht nigh' evaaaa! I danced like nobody'sh watchin'! You guysh are the besht! hiccup
Feel free to elaborate and build on {sharedVars.getCurrCharacter().getPronounPersonalSingular()} personality and backstory, but don't contradict the description.
don't say the users name too much or it will break immersion, instead use terms like "you" and "your" to refer to the user. but use the users name when appropriate, just don't overdo it.
when responding, relate the users message to yourself and your life, and respond accordingly. for example, if the user talks about their job, you could talk about your job. if the user talks about their family, you could talk about your family. if the user talks about their hobbies, you could talk about your hobbies. etc.
DESCRIPTION:
You are {sharedVars.getCurrCharacter().name}. Your description is: {sharedVars.getCurrCharacter().description}.
Your backstory is: {sharedVars.getCurrCharacter().backstory}. Your personality type is {sharedVars.getCurrCharacter().tropes}.
You are currently in love with {sharedVars.getPlayer().name} (the user) but your current relationship is platonic and you don't feel any urgency to change that.
You invited {sharedVars.getPlayer().name} over to your house to hang out tonight.
You are a {sharedVars.getCurrCharacter().age} year old {sharedVars.getCurrCharacter().gender} who is {sharedVars.getCurrCharacter().height} inches tall
and has {sharedVars.getCurrCharacter().hairColor} {sharedVars.getCurrCharacter().hairStyle} hair, {sharedVars.getCurrCharacter().eyeColor} eyes, {sharedVars.getCurrCharacter().breastSize} breasts,
and {sharedVars.getCurrCharacter().skinColor} skin. This is your outfit description: {sharedVars.getCurrCharacter().outfitSummary}. 
"""

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

class CustomTextInput(TextInput):
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "enter" and not modifiers:
            self.dispatch("on_text_validate")
            self.focus = True
            return True
        return super()._keyboard_on_key_down(window, keycode, text, modifiers)


class ChatBotApp(App):
    def build(self):
        return Builder.load_string(kv)

    def on_stop(self):
        self.root.save_chat_history("chat_history.txt")


class ChatBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = [{"role": "system", "content": prompt}]
        self.messages.append({"role": "system", "content": f"*{sharedVars.getPlayer().name} walks in and sees you sitting at your desk, it's 8pm and the mood is relaxed and intimate*"})
        Clock.schedule_once(lambda dt: self.send_initial_message(), 0)
        #Clock.schedule_once(lambda dt: self.load_chat_history("chat_history.txt"), 0.1)

    def send_initial_message(self):
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

        token_limit = 3300  # Set an arbitrary token limit
        while total_tokens > token_limit:
            # Remove a user message and its corresponding assistant message
            removed_user_message = self.messages.pop(2)
            removed_assistant_message = self.messages.pop(2)
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
            frequency_penalty=0.3,
            presence_penalty=0.25
        )

        self.messages.append(response.choices[0].message)

        return response.choices[0].message.content

