#Role Assign
import random
import character 
import chat_group 

class Players():
    
    def __init__(self):
        self.gaming_group = []

    def role_assign(self, chat_group):
        #roles for 2 players is just for test
        roles = {2:["villager","wolf"],\
                4:["villager","witch", "wolf", "prophet"],\
                 5:['villager', 'villager', 'wolf', 'prophet', 'witch'],\
                 6:['villager','villager', 'wolf', 'prophet', 'witch', 'wolf'],\
                 7:['villager','villager', 'wolf','wolf', 'prophet', 'witch', 'villager'],\
                 8:['villager','villager','villager', 'wolf','wolf', 'prophet', 'witch', 'wolf'],\
                 9:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'villager'],\
                 10:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'wolf']}
        number = len(chat_group)
        game_roles = roles[number]
        print("Roles in this round: ", game_roles)
        gaming_groups = []
        for player in chat_group:
            c = character.Character(player)
            random.shuffle(game_roles)
            c.set_role(game_roles.pop())
            gaming_groups.append(c)
            
        return gaming_groups
    
    def get_gaming_group(self, chat_group):
        self.gaming_group = self.role_assign(chat_group)
        return self.gaming_group
    
    def get_alives(self):
        alive = []
        for player in self.gaming_grp:
            if player.get_status() == 'alive':
                alive.append(player.playerName)
        alivePlayers = ', '.join(alive)
        return alivePlayers
    
    def judge_resule(self):
        alive = {}
        for player in self.get_alives():
                alive[player.playerName] = player.get_role()
        if len(alive) > 3:
            if 'wolf' not in alive.values():
                self.win_side = 'villigers'
                self.status = 'gameover'
            elif 'villager' not in alive.values():
                self.win_side = 'wolves'
                self.status = 'gameover'
            return self.status,self.win_side
        else:
            wolf_number = 0
            for role in alive.values():
                if role == 'wolf':
                    wolf_number += 1
            
            if wolf_number >= (len(alive) - wolf_number):
                self.win_side = 'wolves'
                self.status = 'gameover'
                
                return self.status, self.win_side
        
        return self.status
        
  
            
            
            






    

