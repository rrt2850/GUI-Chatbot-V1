from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

from KivyWidgets.ClearableInput import ClearableTextInput

class EditFormTextInput(ClearableTextInput):
    def __init__(self, **kwargs):
        super(EditFormTextInput, self).__init__(**kwargs)
        self.multiline = True  # allows for multiple lines
        self.size_hint_y = None  # necessary for scrollview
        self.bind(minimum_height=self.setter('height'))  # bind minimum height to height of the TextInput
        self.defaultText = kwargs.get('defaultText', False)

class ScrollableForm(BoxLayout):
    def __init__(self, on_button_press, formNames=[], formText=[], defaultText=False, **kwargs):
        super(ScrollableForm, self).__init__(**kwargs)
        self.orientation = 'vertical'
        layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Store text inputs in a dictionary
        self.text_inputs = {}

        # create TextInput and Label instances and add to the layout
        for i in range(len(formNames)):  # change the range to add more TextInput fields
            print(f"\033[32m{formNames[i]}\033[0m", formText[i])
            label = Label(text=formNames[i], size_hint_y=None, height=50)  # create a Label instance
            formText[i] = formText[i] if formText[i] is not None else ""  
            if defaultText:
                textInput = EditFormTextInput(defaultText=formText[i])  # create a TextInput instance
            else: textInput = EditFormTextInput(text=formText[i])  # create a TextInput instance

            # Store the text input instance in the dictionary
            self.text_inputs[formNames[i]] = textInput

            layout.add_widget(label)  # add Label to the layout
            layout.add_widget(textInput)  # add TextInput to the layout

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(layout)  # add the layout to your ScrollView
        self.add_widget(scroll)

        button = Button(text='Submit', size_hint_y=None, height=50)
        button.bind(on_release=on_button_press)  # bind the on_button_press function to the button's on_release event
        self.add_widget(button)  # add the button to the form

def submit_edit(instance):
    form = instance.parent  # the form is the parent of the button
    # Now you can access the text of each MyTextInput through the text_inputs dictionary
    player_name = form.text_inputs["label1"].text
    player_lore = form.text_inputs["label2"].text
    character_description = form.text_inputs["label3"].text
    # Update the player and character with the new text...
    print(player_name, player_lore, character_description)

class MyApp(App):
    def build(self):
        return ScrollableForm(
            formNames=["label1", "label2", "label3"],
            formText=["text1", "text2", "text3"],
            on_button_press=submit_edit)

if __name__ == '__main__':
    MyApp().run()
