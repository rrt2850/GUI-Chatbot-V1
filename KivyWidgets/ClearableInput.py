"""
Author: Robert Tetreault (rrt2850)
Filename: ClearableInput.py
Description: A text input that clears itself when clicked on if the text is the default text
"""

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

class ClearableTextInput(TextInput):
    def __init__(self, defaultText='Default Text', text='', **kwargs):
        super().__init__(**kwargs)
        if text:
            self.text = text
        else:
            self.defaultText = defaultText
            self.text = defaultText
            self.bind(focus=self.on_focus)

    def on_focus(self, instance, value):
        if value and self.text == self.defaultText:  # on focus and if text is default text
            self.text = ''

class MyApp(App):
    def build(self):
        layout = BoxLayout()
        text_input = ClearableTextInput()
        layout.add_widget(text_input)
        return layout

if __name__ == '__main__':
    MyApp().run()
