"""
       NPD
       @09-05-2018
"""

import hashlib
import socket
from packet_route import route
route = route()
"""

This part of the code mainly contains the view, and some controls

"""
class main:
    def login(self):
        print("!-------------------------!")
        print("!-Network Protocol Design-!")        
        print("!-------------------------!")
        pear_ip=input("Please input peer IP to connet to chat room:  ")
        return pear_ip

    def welcome(self):
        print("!--------------------------!")
        print("!-Welcome to the chat room-!")        
        print("!--------------------------!")  
  
    def node_id(self):
        email =input("Please input your email: ")
        mail =hashlib.md5(email.encode('utf-8'))
        hash_mail = mail.hexdigest()
        return hash_mail
    def src_port(self):
        return 9999
    def dest_port(self):
        return 8888
    def peer_port(self):
        return '9999'
    def cost_matrix(self):
        cost= int(input("Please input link cost of the node: "))
        return cost
    def packet_type(self,typ):
        if typ == "data":
            return 0x02
        elif typ == "conf":
            return 0x04
        else:
            print("Packet Type Error!!")