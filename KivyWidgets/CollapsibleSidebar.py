from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

class CollapsibleSidebar(BoxLayout):
    def __init__(self, minWidthOpen=600, buttonHeightClosed=60, buttonTextClosed="open", buttonTextOpen="close", startState="closed", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.minWidthOpen = minWidthOpen
        self.buttonTextOpen = buttonTextOpen
        self.buttonTextClosed = buttonTextClosed
        self.buttonHeightClosed = buttonHeightClosed
        self.startState = startState

        # Added these lines to set color and draw the rectangle
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.toggleButton = Button(size_hint_y=None)
        self.toggleButton.bind(on_press=self.toggleSidebar)
        self.add_widget(self.toggleButton)

        self.content = BoxLayout(orientation='vertical')
        self.add_widget(self.content)

        self.resetSidebar()

        Window.bind(width=self.updateWidth)

    # Method for updating rectangle size and position
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def updateWidth(self, instance, value):
        self.size_hint_x = max(self.minWidthOpen / value, 0.25) if self.content.opacity == 1 else max(self.minWidthOpen * 0.10 / value, 0.05)

    def toggleSidebar(self, instance):
        if instance is None:
            self.resetSidebar()
            return
        if self.content.opacity == 0:
            self.content.opacity = 1
            self.toggleButton.text = self.buttonTextOpen
            self.toggleButton.height = int(self.buttonHeightClosed / 2.5)
            self.size_hint_x = max(self.minWidthOpen / Window.width, 0.25)
            return
        self.content.opacity = 0
        self.toggleButton.text = self.buttonTextClosed
        self.toggleButton.height = self.buttonHeightClosed
        self.size_hint_x = max(self.minWidthOpen * 0.10 / Window.width, 0.05)

    def resetSidebar(self):
        self.content.opacity = 0 if self.startState == "closed" else 1
        self.size_hint_x = max(self.minWidthOpen * 0.10 / Window.width, 0.05) if self.startState == "closed" else max(self.minWidthOpen / Window.width, 0.25)
        self.toggleButton.height = self.buttonHeightClosed if self.startState == "closed" else int(self.buttonHeightClosed / 2.5)
        self.toggleButton.text = self.buttonTextClosed if self.startState == "closed" else self.buttonTextOpen
