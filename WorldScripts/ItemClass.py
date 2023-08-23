class Item:
    """
    A class to represent an item in the game.
    """

    def __init__(self, name, description):
        self.name = name
        self.quantity = 0
        self.description = description

    def dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "description": self.description
        }
    def __str__(self):
        temp = f"""[name:'{self.name}', description:'{self.description}', quantity:'{self.quantity}']"""
        return temp
    
    def __repr__(self):
        temp = f"""[name:'{self.name}', quantity:'{self.quantity}']"""
        return temp
    
    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name.lower() == other.name.lower() and self.description.lower() == other.description.lower()
        return False