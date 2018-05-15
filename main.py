import hashlib
import socket
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
    def menu(self):
         try:
            self.welcome()
            option=int(input("!-Please use\
             --!\n!-1)<PMSG> For Private msg-!\
             \n!-2)<GMSG> For Group message\
             \n!-3)<FT> ForFile Transfer--!\
             \n Choose:  "))
            print("!-------------------------!")
         except:
             print("Please Use the format <PMSG> <IP Address> <Conntent>")
             self.menu()
        
        
    def private_msg(self):
         self.welcome()
         dest_addr=input("Input destination address: ")
         return dest_addr
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
    def time_out(self):
        return 300
    def packet_type(self,typ):
        if typ == "data":
            return 0x02
        elif typ == "conf":
            return 0x04
        else:
            print("Packet Type Error!!")