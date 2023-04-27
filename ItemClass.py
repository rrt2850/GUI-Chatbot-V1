class Item:
    def __init__(self, name, description):
        self.name = name
        self.quantity = 0
        self.description = description

    def updateName(self, name:str = ""):
        if name == "":
            return (False, (None, "You need to specify a name to update the item to"))
        self.name = name
        return (True, (self, f"Updated item name to {name}"))
    
    def updateQuantity(self, quantity:int = 0):
        self.quantity = quantity
        return (True, (self, f"Updated item quantity to {quantity}"))
    
    def updateDescription(self, description:str = ""):
        if description == "":
            return (False, (None, "You need to specify a description to update the item to"))
        self.description = description
        return (True, (self, f"Updated item description to {description}"))

    def dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "description": self.description
        }
    def __str__(self):
        return f"""[name="{self.name}" quantity="{self.quantity}"]"""
    
    def __repr__(self):
        return f"""Item:[name="{self.name}" quantity="{self.quantity}"]"""
    
    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name and self.description == other.description
        return False