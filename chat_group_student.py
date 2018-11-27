S_ALONE = 0
S_TALKING = 1

# ==============================================================================
# Group class:
# member fields:
#   - An array of items, each a Member class
#   - A dictionary that keeps who is a chat group
# member functions:
#    - join: first time in
#    - leave: leave the system, and the group
#    - list_my_peers: who is in chatting with me?
#    - list_all: who is in the system, and the chat groups
#    - connect: connect to a peer in a chat group, and become part of the group
#    - disconnect: leave the chat group but stay in the system
# ==============================================================================


class Group:

    def __init__(self):
        self.members = {}
        self.chat_grps = {}
        self.grp_ever = 0

    def join(self, name):
        self.members[name] = S_ALONE
        return

    def is_member(self, name):

        # IMPLEMENTATION
        # ---- start your code ---- #
        if name in self.members.keys():
            return True
        else:
            return False
        # ---- end of your code --- #

    # implement
    def leave(self, name):
        """
        leave the system, and the group
        """
        # IMPLEMENTATION
        # ---- start your code ---- #
        if self.is_member(name):
            self.members.pop(name)
            for i in range(self.grp_ever):
                if name in self.chat_grps[i]:
                    self.chat_grps[i].remove(name)
                    break

        # ---- end of your code --- #
        return self.members, self.chat_grps

    def find_group(self, name):
        """
        Auxiliary function internal to the class; return two
        variables: whether "name" is in a group, and if true
        the key to its group
        """
        found = False
        group_key = 0
        # IMPLEMENTATION
        # ---- start your code ---- #
        if self.grp_ever == 0:
            return found, group_key
        while group_key <= self.grp_ever:
            if name in self.chat_grps[group_key]:
                found = True
                break
            else:
                group_key += 1
        # ---- end of your code --- #
        return found, group_key

    def connect(self, me, peer):
        """
        me is alone, connecting peer.
        if peer is in a group, join it
        otherwise, create a new group with you and your peer
        """
        peer_in_group, group_key = self.find_group(peer)

        # IMPLEMENTATION
        # ---- start your code ---- #
        if peer_in_group:
            self.chat_grps[group_key].append(me)
        else:
            self.chat_grps[self.grp_ever] = [me, peer]
            self.grp_ever += 1
            self.members[peer] = S_TALKING
            
        self.members[me] = S_TALKING

        # ---- end of your code --- #
        return self.chat_grps

    # implement
    def disconnect(self, me):
        """
        find myself in the group, quit, but stay in the system
        """
        # IMPLEMENTATION
        # ---- start your code ---- #
        if self.members[me] == S_TALKING:
            gp_key = self.find_group(me)[1]
            if len(self.chat_grps[gp_key]) == 2:
                for i in self.chat_grps[gp_key]:
                    self.members[i] = S_ALONE
                    self.chat_grps.pop(gp_key, None)
                self.grp_ever -= 1
            else:
                self.members[me] = S_ALONE
                self.chat_grps[gp_key].pop(me)

        # ---- end of your code --- #
        return self.chat_grps

    def list_all(self):
        # a simple minded implementation
        full_list = "Users: ------------" + "\n"
        full_list += str(self.members) + "\n"
        full_list += "Groups: -----------" + "\n"
        full_list += str(self.chat_grps) + "\n"
        return full_list

    # implement
    def list_me(self, me):
        """
        return a list, "me" followed by other peers in my group
        """
        my_list = []
        # IMPLEMENTATION
        # ---- start your code ---- #
        if self.members[me] == S_TALKING:
            my_list.append(me)
            gp_key = self.find_group(me)[1]
            for i in self.chat_grps[gp_key]:
                if i != me:
                    my_list.append(i)

        # ---- end of your code --- #
        return my_list


if __name__ == "__main__":
    g = Group()
    g.join('a')
    g.join('b')
    g.join('c')
    g.join('d')
    print(g.list_all())

    g.connect('a', 'b')
    print(g.list_all())
    g.connect('c', 'a')
    print(g.list_all())
    g.leave('c')
    print(g.list_all())
    g.disconnect('b')
    print(g.list_all())
