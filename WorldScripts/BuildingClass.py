from collections import deque

opposite = {
    'up': 'down',
    'down': 'up',
    'left': 'right',
    'right': 'left'
}

class Room:
    def __init__(self, name:str, description:str, width, height):
        self.name = name
        self.description = description
        self.characters=[]
        self.items=[]
        self.x = None
        self.y = None
        self.width = width
        self.height = height
        self.connections = []

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name


class Building:
    def __init__(self, name:str, description:str):
        self.name = name
        self.description = description
        self.rooms = []
        self.grid = None

    def addRoom(self, room, connections=[]):
        if not connections and not self.rooms:
            # If this is the first room, place it at (0, 0)
            room.x = 0
            room.y = 0
        else:
            for connection, position, offset, conn_offset in connections:
                # Calculate the position
                if position == 'left':
                    room.x = connection.x + connection.width
                    room.y = connection.y + conn_offset - offset
                elif position == 'right':
                    room.x = connection.x - room.width
                    room.y = connection.y + conn_offset - offset
                elif position == 'down':
                    room.x = connection.x + conn_offset - offset
                    room.y = connection.y - room.height
                elif position == 'up':
                    room.x = connection.x + conn_offset - offset
                    room.y = connection.y + connection.height

                connection.connections.append((room, opposite.get(position), conn_offset, offset))
                room.connections.append((connection, position, offset, conn_offset))

        self.rooms.append(room)

    def makeGrid(self):
        # Calculate grid dimensions
        minX = min(room.x for room in self.rooms)
        minY = min(room.y for room in self.rooms)
        maxX = max(room.x + room.width for room in self.rooms) - minX
        maxY = max(room.y + room.height for room in self.rooms) - minY

        # Adjust room coordinates and initialize the grid
        for room in self.rooms:
            room.x -= minX
            room.y -= minY

        grid = [[None for _ in range(maxX)] for _ in range(maxY)]

        # Add rooms to grid
        for room in self.rooms:
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    grid[y][x] = room

        self.grid = grid
    

def gymPreset():
    # Create Building
    building = Building("Gym", "A gym")
    entrance = Room("Entrance", "The main entrance to the building", 1, 1)
    lobby = Room("Lobby", "A large room with a reception desk and a few chairs", 1, 2)
    gym = Room("Gym", "A large room with lots of equipment", 2, 4)
    mensLocker = Room("Mens Locker Room", "Shit's hangin", 1, 1)
    womensLocker = Room("Womens Locker Room", "The womens locker room", 1, 1)
    pool = Room("Pool", "A large pool with a diving board", 2, 2)
    tennisCourt = Room("Tennis Court", "A large tennis court", 2, 2)
    basketballCourt = Room("Basketball Court", "A large basketball court", 2, 2)
    yogaRoom = Room("Yoga Room", "A room with mats and yoga equipment", 2, 2)

    # Add Rooms to Building
    building.addRoom(entrance)
    building.addRoom(lobby, connections=[(entrance, 'down', 0, 0)])
    building.addRoom(mensLocker, connections=[(lobby, 'right', 0, 0)])
    building.addRoom(womensLocker, connections=[(lobby, 'right', 0, 1)])
    building.addRoom(gym, connections=[(mensLocker, 'right', 2, 0), (womensLocker, 'right', 3, 0)])
    building.addRoom(tennisCourt, connections=[(gym, 'left', 1, 1), (gym, 'left', 0, 0), (lobby, 'down', 1, 0)])
    building.addRoom(basketballCourt, connections=[(tennisCourt, 'down', 0, 0), (tennisCourt, 'down', 1, 1)])
    building.addRoom(pool, connections=[(tennisCourt, 'left', 0, 0), (tennisCourt, 'left', 1, 1)])
    building.addRoom(yogaRoom, connections=[(lobby, 'left', 0, 0)])

    # Generate and print the building grid
    building.makeGrid()

    return building
