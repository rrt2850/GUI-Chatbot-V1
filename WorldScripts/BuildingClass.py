from __future__ import annotations

class Room:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.characters = []
        self.items = []
        self.visited = False

    def insertNorth(self, room: Room):
        self.north = room

    def insertSouth(self, room: Room):
        self.south = room

    def insertEast(self, room: Room):
        self.east = room

    def insertWest(self, room: Room):
        self.west = room

    def __repr__(self):
        return f"{self.name}"

class Building:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.rooms = []
        self.currentRoom = -1

    def addRoom(self, room: Room=None, connectedRooms: list(Room) = [], directions: list(str) = []) -> bool:
        if len(self.rooms) == 0:
            if room is None:
                return False
            self.rooms.append(room)
            return True
        
        if [room, connectedRooms, directions].count(None) > 0:
            return False  # All parameters must be specified

        if len(directions) != len(connectedRooms):
            return False
        
        for connectedRoom, direction in zip(connectedRooms, directions):
            if direction.lower() == "north":
                connectedRoom.insertNorth(room)
            elif direction.lower() == "south":
                connectedRoom.insertSouth(room)
            elif direction.lower() == "east":
                connectedRoom.insertEast(room)
            elif direction.lower() == "west":
                connectedRoom.insertWest(room)
            else:
                return False  # Invalid direction

        self.rooms.append(room)
        return True