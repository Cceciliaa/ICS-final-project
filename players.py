#Role Assign
import random
import character as Character

class Players(Character):
    
    def __init__(self):
        self.gaming_group = []

    def role_assign(self, chat_group):
        roles = {4:["villager","villager", "wolf", "prophet"],\
                 5:['villager', 'villager', 'wolf', 'prophet', 'witch'],\
                 6:['villager','villager', 'wolf', 'prophet', 'witch', 'hunter'],\
                 7:['villager','villager', 'wolf','wolf', 'prophet', 'witch', 'hunter'],\
                 8:['villager','villager','villager', 'wolf','wolf', 'prophet', 'witch', 'hunter'],\
                 9:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'hunter'],\
                 10:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'hunter']}
        print(roles)
        number = len(chat_group)
        game_roles = roles[number]
        gaming_group = []
        for player in chat_group:
            c = Character(player)
            random.shuffle(game_roles)
            c.set_role(game_roles.pop())
            gaming_group.append(c)
            
        self.gaming_group = gaming_group
    
    def get_gaming_group(self):
        return self.gaming_group
    
    def judge_status(self):
        gaming_grp = self.get_gaming_group()
        alive = {}
        for player in gaming_grp:
            if player.get_status() == 'alive':
                alive[player.playerName] = player.get_role()






    

