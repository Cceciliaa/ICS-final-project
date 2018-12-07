"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import players as p

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        self.players = p.Players()
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        # self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        # self.sonnet = pkl.load(self.sonnet_f)
        # self.sonnet_f.close()
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.gaming_players = [] #record the gaming players 
        self.wolves = grp.Group() #add the wolves to a seperate chat group
        self.dead = []
        self.newkilled = ''
        self.newpoisoned = ''
        self.poll = {}
        self.pollNumber = 0
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        #move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        #add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        #load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name]=pkl.load(open(name+'.idx','rb'))
                            except IOError: #chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps({"action":"login", "status":"ok"}))
                    else: #a client under this name has already logged in
                        mysend(sock, json.dumps({"action":"login", "status":"duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print ('wrong code received')
            else: #client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()
    


#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
#==============================================================================
# handle connect request
#==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"connect", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action":"connect", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"connect", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"connect", "status":"no-user"})
                mysend(from_sock, msg)
                
            elif msg["action"] == "game":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"game", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action":"game", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"game", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"game", "status":"no-user"})
                mysend(from_sock, msg)
#==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                #said = msg["from"]+msg["message"]
                said2 = text_proc(msg["message"], from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"], "message":msg["message"]}))
                    
#==============================================================================
#                 listing available peers
#==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))
#==============================================================================
#             retrieve a sonnet
#==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = '\n'.join(poem).strip()
                print('here:\n', poem)
                mysend(from_sock, json.dumps({"action":"poem", "results":poem}))
#==============================================================================
#                 time
#==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps({"action":"time", "results":ctime}))
#==============================================================================
#                 search
#==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                # search_rslt = (self.indices[from_name].search(term))
                search_rslt = '\n'.join([x[-1] for x in self.indices[from_name].search(term)])
                print('server side search: ' + search_rslt)
                mysend(from_sock, json.dumps({"action":"search", "results":search_rslt}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"disconnect"}))
                
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================
            elif msg["action"] == "listAlive":
                from_name = self.logged_sock2name[from_sock]
                msg = ''
                for player in self.gaming_players:
                    if player.get_status() == "alive":
                        msg += str(player.playerName) + ", "
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))

            # GET the player just dead
            elif msg["action"] == "getDead":
                msg = ''
                if len(self.newkilled) > 0:
                    msg = 'Player that was killed tonight: ' + self.newkilled
                else:
                    msg = 'No player was killed tonight.'
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))

            elif msg["action"] == "listAll":
                from_name = self.logged_sock2name[from_sock]
                msg = ''
                for player in self.gaming_players:
                    msg += str(player.playerName) + ", "
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))
                
                
            elif msg["action"] == "start":
                '''set gaming group'''
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.gaming_players = self.players.get_gaming_group(the_guys)
                for i in self.gaming_players[1:]:
                    to_name = i.playerName
                    to_sock = self.logged_name2sock[to_name]            
                    mysend(to_sock, json.dumps({"action":"start","role":i.get_role(),"status":i.get_status()}))
                me = self.gaming_players[0]
                mysend(from_sock, json.dumps({"action":"start","role":me.get_role(),"status":me.get_status()}))
                for player in self.gaming_players:
                    if player.get_role() == "wolf":
                        self.wolves.join(player.playerName)
                    elif player.get_role() == "witch":
                        player.set_poison()
                        player.set_cure()
                    
            elif msg["action"] == "gaming":
                from_name = self.logged_sock2name[from_sock]
                # action
                if msg["round"] == "action":
                    if msg["role"] == "wolf":
                        the_guys = self.wolves.list_me(from_name)
                        said2 = text_proc(msg["message"], from_name)
                        for g in the_guys[1:]:
                            to_sock = self.logged_name2sock[g]
                            mysend(to_sock, json.dumps({"action":"gaming","round":"action", "role":"wolf", \
                                                        "from":msg["from"], "message":msg["message"]}))
                elif msg["round"] == "kill":

                    kill = msg["message"]
                    kill_state = False
                    for player in self.gaming_players:
                        if player.playerName == kill and player.get_status() == "alive":
                            if player.get_role() == "wolf":
                                self.wolves.leave(kill)
                            self.dead.append(player)
                            player.set_status("dead")
                            self.newkilled = player.playerName
                            kill_state = True
                            break
    
                    if kill_state == False:
                        mysend(from_sock, json.dumps({"action":"gaming","round":"kill", "role":"wolf", \
                                                        "from":msg["from"], "message":"Killing failed."}))
    
                    if msg["role"] == "wolf" and kill_state == True:
                            the_guys = self.wolves.list_me(from_name)
                            for g in the_guys:
                                to_sock = self.logged_name2sock[g]
                                mysend(to_sock, json.dumps({"action":"gaming","round":"kill", "role":"wolf", \
                                                            "from":msg["from"], "message":"asleep"}))
                    
                    wake = False
                    for player in self.gaming_players:
                        if player.get_role() == "prophet":
                            if player.get_status() == 'alive' or player.playerName == self.newkilled:
                                toProphet = self.logged_name2sock[player.playerName]
                                mysend(toProphet, json.dumps({"action":"gaming","round":"action", "role":"prophet", \
                                                        "from":msg["from"], "message":"You are now awaken. \n"}))
                                wake = True
                                break
                    if wake == False:  
                        for player in self.gaming_players:
                            if player.get_role() == "witch":
                                if player.get_status() == 'alive' or player.playerName == self.newkilled:
                                    toWitch = self.logged_name2sock[player.playerName]
                                    mysend(toWitch, json.dumps({"action":"gaming","round":"action", "role":"witch", \
                                                            "from":msg["from"], "message":"You are now awaken. \n"}))
                                    wake = True
                                    break
                    if wake == False:  
                        message = "The sun has arisen. Now enter discussion.\n"
                        if self.newkilled == "" and self.newpoisoned == "":
                            message += "No one was killed last night.\n"
                        elif self.newkilled == "":
                            message += "Last night " + self.newpoisoned + " was killed.\n"
                        elif self.newpoisoned == "":
                            message += "Last night " + self.newkilled + " was killed.\n"
                        elif self.newkilled == self.newpoisoned:
                            message += "Last night " + self.newkilled + " was killed.\n"
                        else:
                            message += "Last night " + self.newkilled + " and" + self.newpoisoned + " were killed.\n"
                            
                        for player in self.gaming_players:    
                            to_sock = self.logged_name2sock[player.playerName]
                            mysend(to_sock, json.dumps({"action":"gaming","round":"discuss",\
                                                                "from":"server", "message": message}))
                            

                elif msg["round"] == "check":
                    check = msg["message"]
                    check_role = ''
                    for player in self.gaming_players:
                        if player.playerName == check:
                            check_role = player.get_role()
                    mysend(from_sock, json.dumps({"action":"gaming","round":"check", "role":"prophet", \
                                                                "from":msg["from"], "message":check_role}))

                            
                    for player in self.gaming_players:
                        if player.get_role() == "witch":
                            toWitch = self.logged_name2sock[player.playerName]
                            mysend(toWitch, json.dumps({"action":"gaming","round":"action", "role":"witch", \
                                                            "from":msg["from"], "message":"You are now awaken. \n"}))

                elif msg["round"] == "poison":
                    from_name = self.logged_sock2name[from_sock]
                    poison = msg["message"]
                    if poison != "skip" and player.get_poison() != 0:
                        for player in self.gaming_players:
                            if player.playerName == poison:
                                player.set_status("dead")
                                self.dead.append(player)
                                self.newpoisoned = player.playerName
                        player.use_poison()
                        if player.get_cure() != 0:
                            mysend(from_sock, json.dumps({"action":"gaming","round":"poison", "role":"witch", \
                                                        "from":msg["from"], "message":"Finish poisoning! Tehehee \n"}))
                        else:
                            mysend(from_sock, json.dumps({"action":"gaming","round":"skip", "role":"witch", \
                                                        "from":msg["from"], "message":"You have used up your cure! \n"}))

                    elif poison == "skip":
                        self.newpoisoned = ''
                        mysend(from_sock, json.dumps({"action":"gaming","round":"poison", "role":"witch", \
                                                        "from":msg["from"], "message":"Skipped poisoning. Duh\n"}))
                    
                    elif player.get_poison() == 0:
                        self.newpoisoned = ''
                        if player.get_cure() != 0:
                            mysend(from_sock, json.dumps({"action":"gaming","round":"cure", "role":"witch", \
                                                        "from":msg["from"], "message":"\n"}))
                        else:
                            mysend(from_sock, json.dumps({"action":"gaming","round":"skip", "role":"witch", \
                                                        "from":msg["from"], "message":"You have used up your poison and cure! \n"}))
    
                elif msg["round"] == "cure":
                    cure = msg["message"]
                    from_name = self.logged_sock2name[from_sock]
                    if cure == self.newkilled:
                        for player in self.gaming_players:
                            if player.playerName == cure:
                                player.set_status("alive")
                                self.newkilled = ''
                                self.dead.remove(player)
                                if self.newpoisoned == player.playerName:
                                    self.newpoisoned == ''
                        player.use_cure()
                        mysend(from_sock, json.dumps({"action":"gaming","round":"cure", "role":"witch", \
                                                                "from":msg["from"], "message":"Finish curing!"}))
                    elif cure == "skip":
                        mysend(from_sock, json.dumps({"action":"gaming","round":"cure", "role":"witch", \
                                                            "from":msg["from"], "message":"Skipped curing. Cruel:(\n"}))
                    else:
                        mysend(from_sock, json.dumps({"action":"gaming","round":"cure", "role":"witch", \
                                                                "from":msg["from"], "message":"FAIL"}))
                    
                    message = "The sun has arisen. Now enter discussion.\n"
                    if self.newkilled == "" and self.newpoisoned == "":
                        message += "No one was killed last night.\n"
                    elif self.newkilled == "":
                        message += "Last night " + self.newpoisoned + " was killed.\n"
                    elif self.newpoisoned == "":
                        message += "Last night " + self.newkilled + " was killed.\n"
                    elif self.newkilled == self.newpoisoned:
                        message += "Last night " + self.newkilled + " was killed.\n"
                    else:
                        message += "Last night " + self.newkilled + " and" + self.newpoisoned + " were killed.\n"
                        
                    for player in self.gaming_players:    
                        to_sock = self.logged_name2sock[player.playerName]
                        mysend(to_sock, json.dumps({"action":"gaming","round":"discuss",\
                                                            "from":"server", "message": message}))
                                
            
    
                elif msg["round"] == "discussion":
                    for player in self.gaming_players:
                        if player.status == "alive":
                            self.poll[player.playerName] = 0
                    from_name = self.logged_sock2name[from_sock]
                    the_guys = self.group.list_me(from_name)
                    #said = msg["from"]+msg["message"]
                    said2 = text_proc(msg["message"], from_name)
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        self.indices[g].add_msg_and_index(said2)
                        mysend(to_sock, json.dumps({"action":"gaming","round":"discussion", "from":msg["from"], "message":msg["message"]}))
                
                elif msg["round"] == "poll":
                    from_name = self.logged_sock2name[from_sock]
                    the_guys = self.group.list_me(from_name)
                    for player in self.gaming_players:
                        message = msg["message"]
                        if message == player.playerName:
                            try:
                                self.poll[player.playerName] += 1
                                self.pollNumber += 1
                            except:
                                self.pollNumber += 0
                                mysend(from_sock, json.dumps({"action":"gaming","round":"poll", "from":msg["from"],"message":"Wrong name! Please try again:"}))
                            if self.pollNumber == len(self.poll):
                                values = []
                                for v in self.poll.values():
                                    values.append(v)
                                values.sort()
                                print(values)
                                if values[len(values)-1] == values[len(values)-2]:
                                    for player in self.gaming_players:
                                        if player.status == "alive":
                                            self.poll[player.playerName] = 0
                                    values = []
                                    mysend(from_sock, json.dumps({"action":"gaming","round":"poll", "from":msg["from"],"message":"Tied! please vote again (Can't eliminate more than one player):"}))
                                
                                for g in the_guys:
                                    to_sock = self.logged_name2sock[g]
                                    mysend(to_sock, json.dumps({"action":"gaming","round":"vote_result", "from":msg["from"], "message":"test"}))
            
                    
                    
                    
                    
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"gaming","round":"poll", "from":msg["from"], "message":msg["message"]}))
                    
                    

                                
                                
                                
                    #mysend(to_sock, json.dumps({"action":"gaming","round":"poll", "from":msg["from"], "message":msg["message"]}))
                    #message = msg["message"]
                        
                        

                
            else:
                #client died unexpectedly
                self.logout(from_sock)

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
            read,write,error=select.select(self.all_sockets,[],[])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read :
                #new client request
                sock, address=self.server.accept()
                self.new_client(sock)

def main():
    server=Server()
    server.run()

main()
