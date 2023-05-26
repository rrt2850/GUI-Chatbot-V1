import os
import dotenv
from numpy import size
import openai
import tiktoken
import json
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from CharacterScripts.CharacterHandler import sharedVars

dotenv.load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def countTokens(text):
    tokens = []
    try:
        tokens = encoding.encode(text)
    except:
        print("Error: Unable to encode text")
    return len(tokens)

class CustomTextInput(TextInput):
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == "enter" and not modifiers:
            self.dispatch("on_text_validate")
            self.focus = True
            return True
        return super()._keyboard_on_key_down(window, keycode, text, modifiers)
    

class ChatBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatBoxLayout, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 4
        self.totalTotal = 0
        self.updateVars()

        self.scrollView = ScrollView(
            bar_width=10,
            effect_cls='ScrollEffect',
            scroll_type=['bars', 'content'],
            scroll_wheel_distance=10
        )

        self.messageLabel = Label(
            size_hint_y=None,
            size_hint_x=0.9,
            text_size=(self.width, None),
            font_size='16sp',
            markup=True,
            valign='top',
            halign='left',
            padding=(10, 10)
        )
        self.messageLabel.bind(
            width=lambda *x: self.messageLabel.setter('text_size')(self.messageLabel, (self.messageLabel.width, None)),
            texture_size=lambda *x: self.messageLabel.setter('height')(self.messageLabel, self.messageLabel.texture_size[1])
        )

        self.scrollView.add_widget(self.messageLabel)

        self.inputLayout = BoxLayout(
            size_hint_y=0.1,
            orientation='horizontal'
        )

        self.userInput = CustomTextInput(
            multiline=False,
            do_wrap=True,
            hint_text='Type your message...',
            font_size='16sp',
            size_hint_x=0.9,
            text_validate_unfocus=False
        )
        self.userInput.bind(on_text_validate=lambda instance: self.sendMessage())


        self.sendButton = Button(
            text='Send',
            font_size='16sp',
            size_hint_x=0.1
        )
        self.sendButton.bind(on_press=self.sendMessage)

        self.inputLayout.add_widget(self.userInput)
        self.inputLayout.add_widget(self.sendButton)

        self.add_widget(self.scrollView)
        self.add_widget(self.inputLayout)

        self.loadMessages()
        
        if sharedVars.getMessages() == []:
            Clock.schedule_once(self.sendInitialMessage, 0.5)

        elif sharedVars.getMessages()[-1]["role"] != "assistant":
            self.chatLoop()

    def updateVars(self):
        temp = sharedVars.getGptStuff()
        self.temperature, self.topP, self.maxTokens, self.frequencyPenalty, \
        self.presencePenalty, self.tokenLimit = temp.values()
        self.prompt = sharedVars.getPrompt()
        self.systemMessage = sharedVars.getSystemMessage()
        self.char2 = None

    def makeInitialMessage(self):
        for content in [self.prompt, self.systemMessage]:
            message = {"role": "system", "content": content}
            sharedVars.appendMessage(message)
            self.saveChatHistory(message)

    def sendInitialMessage(self, dt):
        if not sharedVars.getMessages():
            self.makeInitialMessage()
        self.chatLoop()

    def appendMessage(self, message):
        roleColors = {"system": "#ADD8E6", "user": "#32CD32", "assistant": "#FFA500"}
        role = message["role"]
        name = "System" if role == "system" else "You" if role == "user" else sharedVars.getCurrCharacter().name.first
        formattedMessage = f"[color={roleColors[role]}][b]{name}:[/b][/color] {message['content']}"
        if formattedMessage:
            self.messageLabel.text += ("\n\n" + formattedMessage) if self.messageLabel.text else formattedMessage

    def saveChatHistory(self, message):
        chatHistory = {"logs": {}}
        try:
            with open(f"ChatHistory{sharedVars.getPlayer().name}.json", 'r') as f:
                chatHistory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        characterName = repr(sharedVars.getCurrCharacter().name)
        chatHistory["logs"].setdefault(characterName, []).append(message)
        
        with open(f"ChatHistory{sharedVars.getPlayer().name}.json", 'w') as f:
            json.dump(chatHistory, f, indent=4)

    def sendMessage(self, *args):
        userMessage = self.userInput.text.strip()
        if userMessage:
            message = {"role": "user", "content": userMessage}
            sharedVars.appendMessage(message)
            self.appendMessage(message)
            self.saveChatHistory(message)
            self.chatLoop()
            self.userInput.text = ""

    def loadMessages(self):
        try:
            with open(f"ChatHistory{sharedVars.getPlayer().name}.json", 'r') as f:
                chatHistory = json.load(f)
                characterName = repr(sharedVars.getCurrCharacter().name)
                messages = chatHistory["logs"].get(characterName, [])[1:]
                for message in messages:
                    self.appendMessage(message)
                    
                sharedVars.setMessages(messages)
                self.scrollView.scroll_y = 0
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def chatLoop(self):
        self.updateVars()
        messages = sharedVars.getMessages()
        last_message = messages[-1]
        if last_message["role"] == "system" and last_message["content"] not in self.messageLabel.text:
            self.appendMessage(last_message)

        totalTokens = sum(countTokens(message["content"]) for message in messages)
        print(f"Total tokens: {totalTokens}")
        
        while totalTokens > self.tokenLimit:
            print(f"Total tokens: {totalTokens}, Token limit: {self.tokenLimit}")
            for _ in range(2):
                removedMessage = messages.pop(2)
                if removedMessage["role"] == "system":
                    messages[1] = removedMessage
                totalTokens -= countTokens(removedMessage["content"])
                print(f"Removed message: {removedMessage}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.maxTokens,
            top_p=self.topP,
            frequency_penalty=self.frequencyPenalty,
            presence_penalty=self.presencePenalty,
        )

        responseMessage = response.choices[0].message
        self.saveChatHistory(responseMessage)
        sharedVars.appendMessage(responseMessage)
        self.appendMessage(responseMessage)

