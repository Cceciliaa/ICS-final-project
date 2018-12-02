"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.gaming_state = ''
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.role = ''
        self.gstatus = ''

    def set_state(self, state):
        self.state = state
    
    def set_gaming_state(self, gaming_state):
        self.gaming_state = gaming_state

    def get_state(self):
        return self.state
    
    def get_gaming_state(self):
        return self.gaming_state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
    
    def set_role(self,role):
        self.role = role
    
    def get_role(self):
        return self.role
    
    def set_gstatus(self,gstatus):
        self.gstatus = gstatus
    
    def get_gstatus(self):
        return self.gstatus

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def gaming_with(self,peer):
        msg = json.dumps({"action":"game", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You\'ve invited '+ self.peer + ' to your game\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot play with yourself\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def game_start(self):
        me = self.get_myname()
        mysend(self.s, json.dumps({"action":"start"}))

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'


                elif my_msg[0] == 'g':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.gaming_with(peer) == True:
                        self.state = S_START
                        self.out_msg += 'Add ' + peer + ' to the game!\n\n'
                        self.out_msg += 'Type "start" to start the game\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Invatation unsuccessful\n'


                else:
                    self.out_msg += menu

                    

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                elif peer_msg["action"] == "game":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'You\'ve been invited to ' + self.peer + '\'s game\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_START

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg["action"] == "exchange":
                    self.out_msg += peer_msg["from"] + peer_msg["message"]
                    
        elif self.state == S_START:
            if len(my_msg) > 0: 
                if my_msg == 'start':
                    self.game_start()
                    self.out_msg += "Game started!\n"
                    self.out_msg += "----------------------------------------\n" 
                    send_back = json.loads(myrecv(self.s))
                    self.out_msg += "Your role is: " + send_back["role"] + ", and you are now " \
                    + send_back["status"] + '\n'
                    self.set_role(send_back["role"])
                    self.set_gstatus(send_back["status"])
                    self.state = S_GAMING
                    self.out_msg += "Night is coming, please close your eyes... "
                    if self.get_role() == "wolf":
                        self.set_gaming_state("action")
                        self.out_msg += "Now please chat with your partners (if any) and decide a player to kill. \n"
                        mysend(self.s, json.dumps({"action":"listAlive"}))
                        logged_in = json.loads(myrecv(self.s))["results"]
                        self.out_msg += "Now gaming: " + logged_in + '\n'
                        self.out_msg += '''To kill a player, type "KILL" + player's name. \n'''
                    else:
                        self.set_gaming_state("asleep")
                else:
                    self.out_msg += 'Type "start" to start the game\n'
                    self.out_msg += '-----------------------------------\n'
            
            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "start":
                    self.out_msg += "Game started! \n"
                    self.out_msg += "Your role is: " + peer_msg["role"] + ", and you are now " + peer_msg["status"] + '\n'
                    self.set_role(peer_msg["role"])
                    self.set_gstatus(peer_msg["status"])
                    self.state = S_GAMING
                    self.out_msg += "Night is coming, please close your eyes...\n "
                    if self.get_role() == "wolf":
                        self.set_gaming_state("action")
                        self.out_msg += "Now please chat with your partners (if any) and decide a player to kill. \n"
                        mysend(self.s, json.dumps({"action":"listAlive"}))
                        logged_in = json.loads(myrecv(self.s))["results"]
                        self.out_msg += "Now gaming: " + logged_in + '\n'
                        self.out_msg += '''To kill a player, type "KILL" + player's name.\n'''
                    else:
                        self.set_gaming_state("asleep")
                elif peer_msg["action"] == "game":
                    self.out_msg += peer_msg["from"] + " join the game lodge.\n"  
            
           
        elif self.state == S_GAMING:
            if self.gaming_state == "action":
                if len(my_msg) > 0:     # my stuff going out
                     mysend(self.s, json.dumps({"action":"gaming", "round":"action", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":my_msg}))
                     if my_msg[:4] == "KILL":
                         kill = my_msg[4:]
                         kill.strip()
                         mysend(self.s, json.dumps({"action":"gaming", "round":"kill", "role":self.role, \
                                                    "from":"[" + self.me + "]", "message":kill}))
                         self.out_msg += "You have killed " + kill + ", now please go back to sleep. \n"
                         self.out_msg = ''
                         self.set_gaming_state("asleep")
                        
                if len(peer_msg) > 0:    # peer's stuff, coming in
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["round"] == "action":
                        self.out_msg += peer_msg["from"] + peer_msg["message"]
                    elif peer_msg["round"] == "kill":
                        self.set_gstatus("dead")
                    if peer_msg["message"] == "asleep":
                        if self.role == "wolf":
                            self.out_msg += "You have killed " + kill + ", now please go back to sleep. \n"
                            self.out_msg = ''
                            self.set_gaming_state("asleep")
                        else:
                            #should specify the output message for each character
                            self.set_gaming_state("asleep")
                        
            elif self.gaming_state == "asleep":
                if len(my_msg) > 0:
                    self.out_msg += "You are not allowed to talk right now!"
                if len(peer_msg) > 0:
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["round"] == "action":
                        if self.get_role() == peer_msg["role"]:
                            self.set_gaming_state("action")
                            self.out_msg += peer_msg["message"]
                            if self.getrole() == "prophet":
                                self.out_msg += "Choose a player to see his/her role (type the name of the player): \n"
                                mysend(self.s, json.dumps({"action":"listAlive"}))
                                logged_in = json.loads(myrecv(self.s))["results"]
                                self.out_msg += "Now gaming: " + logged_in + '\n'

                            
            else:        
                if len(peer_msg) > 0:    # peer's stuff, coming in
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["action"] == "connect":
                        self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                    elif peer_msg["action"] == "disconnect":
                        self.state = S_LOGGEDIN
                    elif peer_msg["action"]== "gaming":
                        self.out_msg += peer_msg["from"] + peer_msg["message"]
                
                


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
