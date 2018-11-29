class Character(self, playerNumber, role, status):
    def __init__(self):
        self.playerNumber = playerNumber
        self.role = role
        self.status = "alive"

    def set_number(self,number):
        self.playerNumber = number
    def set_status(self,new_status):
        self.status = new_status
    def set_role(self,new_role):
        self.role = new_role
