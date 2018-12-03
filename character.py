class Character:
    
    def __init__(self, playerName):
        self.playerName = playerName
        self.status = 'alive'
        self.role = ''
        
    def set_status(self,new_status):
        self.status = new_status
        
    def set_role(self,new_role):
        self.role = new_role
        return self.role
    
    def kill(self):
        self.status = 'dead'
        return self.status
    
    def save(self):
        self.status = 'alive'
        return self.status
    
    def get_status(self):
        return self.status
    
    def get_role(self):
        return self.role



# Functions for the Witch
    def set_poison(self):
        self.poison = 1
    def use_poison(self):
        self.poison = 0
    def get_poison(self):
        return self.poison

    def set_cure(self):
        self.cure = 1
    def use_cure(self):
        self.cure = 0
    def get_cure(self):
        return self.cure
    
    
