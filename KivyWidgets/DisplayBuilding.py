from kivy.app import App
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from WorldScripts.BuildingClass import gymPreset


class SquareLayout(BoxLayout):
    def __init__(self, grid, buildingGrid, **kwargs):
        super(SquareLayout, self).__init__(**kwargs)
        self.size_hint_y = None
        self.bind(width=self.update_height)

        self.add_widget(SpanLayout(grid, buildingGrid))

    def update_height(self, instance, value):
        self.height = value


class RoomButton(ToggleButton):
    def __init__(self, room, buildingGrid, **kwargs):
        super(RoomButton, self).__init__(**kwargs)
        self.room = room
        self.buildingGrid = buildingGrid
        self.padding = (5, 5)
        
        self.bind(size=lambda *x: self.setter('text_size')(self, (self.width - 20, None))) # Update the text size when the button size changes
        self.bind(on_release=lambda instance, room=room: self.buildingGrid.onRoomClick(room, instance))

    def on_release(self, *args):
        self.buildingGrid.onRoomClick(self.room, self)


class SpanLayout(RelativeLayout):
    def __init__(self, grid, buildingGrid, **kwargs):
        super(SpanLayout, self).__init__(**kwargs)
        self.grid = grid
        self.buildingGrid = buildingGrid
        self.bind(size=self.update_layout, pos=self.update_layout, parent=self.update_layout)

    def update_layout(self, *args):
        if self.parent is None or self.width == 0 or self.height == 0:
            return
        self.clear_widgets()
        for widget in self.create_widgets():
            self.add_widget(widget)

    def create_widgets(self):
        rows, cols = len(self.grid), len(self.grid[0])
        visited = [[False]*cols for _ in range(rows)]
        for y, row in enumerate(self.grid):
            for x, room in enumerate(row):
                if room is not None and not visited[y][x]:
                    width = 1
                    while x + width < cols and room == row[x + width] and not visited[y][x+width]:
                        width += 1
                    height = 1
                    while y + height < rows and all(self.grid[y + height][x:x + width] == [room]*width for _ in range(width)):
                        height += 1
                    for dy in range(height):
                        for dx in range(width):
                            visited[y+dy][x+dx] = True
                    yield RoomButton(room, self.buildingGrid, text=str(room),
                                     size_hint=(None, None),
                                     size=(width*self.width/cols, height*self.height/rows),
                                     font_size=12,
                                     group='room_buttons',
                                     pos_hint={'x': x / cols, 'y': (rows - y - height) / rows})
                    
                else:
                    yield Widget(size_hint=(None, None), size=(self.width/cols, self.height/rows),
                                 pos_hint={'x': x / cols, 'y': (rows - y - 1) / rows})


class BuildingGrid(BoxLayout):
    grid = ListProperty([])
    gridSize = NumericProperty(0)

    def __init__(self, building, **kwargs):
        super(BuildingGrid, self).__init__(**kwargs)
        self.building = building
        self.roomName = Label(font_size=20, size_hint_y=None, height=30)
        self.roomDescription = Label(font_size=16, size_hint_y=None, height=30)
        self.roomCharacters = Label(font_size=16, size_hint_y=None, height=30)
        self.roomItems = Label(font_size=16, size_hint_y=None, height=30)
        self.buildingName = Label(text=building.name, font_size=20)
        self.buildingDescription = Label(text=building.description, font_size=16)
        self.orientation = 'vertical'
        self.padding = [20, 20, 20, 20]
        self.spacing = 30
        self.grid = self.building.grid

        buildingInfo = BoxLayout(orientation='vertical', size_hint_y=0.1, spacing=5)
        room_info = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=20)
        roomBio = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        roomChars = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        roomItemHolder = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=10)
        self.gridWidget = SquareLayout(self.grid, self)
        
        buildingInfo.add_widget(self.buildingName)
        buildingInfo.add_widget(self.buildingDescription)
        roomBio.add_widget(self.roomName)
        roomBio.add_widget(self.roomDescription)
        roomBio.add_widget(Widget())  # Add empty Widget
        roomChars.add_widget(self.roomCharacters)
        roomChars.add_widget(Widget())  # Add empty Widget
        roomItemHolder.add_widget(self.roomItems)
        roomItemHolder.add_widget(Widget())  # Add empty Widget
        room_info.add_widget(roomBio)
        room_info.add_widget(roomChars)
        room_info.add_widget(roomItemHolder)

        room_info.bind(minimum_height=room_info.setter('height'))

        self.add_widget(buildingInfo)
        self.add_widget(self.gridWidget)
        self.add_widget(room_info)


    def onRoomClick(self, room, instance):
        if instance.state == 'down':
            self.roomName.text = room.name
            self.roomDescription.text = room.description
            temp = "Characters:\n"
            for character in room.characters:
                temp += character.name + ", "

            self.roomCharacters.text = temp
            temp = "Items:\n"
            for item in room.items:
                temp += item.name + ", "

            self.roomItems.text = temp

            for label in [self.roomName, self.roomDescription, self.roomCharacters, self.roomItems]:
                label.text_size = label.width, None # Wrap the text
                label.halign = 'center' # Align the text horizontally
                label.valign = 'top' # Align the text vertically
                label.bind(size=lambda *x: label.setter('text_size')(label, (label.width, None))) # Update the text size when the label size changes
        else:
            self.roomName.text = ''
            self.roomDescription.text = ''
            self.roomCharacters.text = ''
            self.roomItems.text = ''

    def updateBuilding(self, newBuilding):
        self.building = newBuilding
        self.buildingName.text = newBuilding.name
        self.buildingDescription.text = newBuilding.description
        self.grid = newBuilding.grid
        self.gridWidget.clear_widgets()  # Clear current widgets from the grid
        self.gridWidget.add_widget(SquareLayout(self.grid, self))  # Add new building layout

class MyApp(App):
    def build(self):
        return BuildingGrid(gymPreset())

 
def start():
    MyApp().run()
    
