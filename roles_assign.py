#Role Assign
import random
def role_assign(chat_group):
    roles = {4:["villager","villager", "wolf", "prophet"],5:['villager', 'villager', 'wolf', 'prophet', 'witch'],6:['villager','villager', 'wolf', 'prophet', 'witch', 'hunter'],7:['villager','villager', 'wolf','wolf', 'prophet', 'witch', 'hunter'],8:['villager','villager','villager', 'wolf','wolf', 'prophet', 'witch', 'hunter'],9:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'hunter'],10:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'hunter']}
    print(roles)
    number = len(chat_group)
    game_roles = roles[number]
    for player in chat_group:
        game_roles.random.shuffle()
        player.set_role(game_roles.pop())

