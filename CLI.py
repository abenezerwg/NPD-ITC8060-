import hashlib
import socket
class main:
    def login(self):
        print("!-------------------------!")
        print("!-Network Protocol Design-!")        
        print("!-------------------------!")
        pear_ip=input("Please input peer IP to connet to chat room:  ")
        return pear_ip# return neighbour Ip

    def welcome(self):
        print("!--------------------------!")
        print("!-Welcome to the chat room-!")        
        print("!--------------------------!")
    def menu(self):#main menu return option input
         try:
            self.welcome()
            option=int(input("!-Please use\
            ---!\n!-1)For Private msg--------!\
            \n!-2)For Group message------!\
            \n!-3)ForFile Transfer-------!\
            \n!-4)List Users-------------!\
            \n!-5)Show Routing Table-----!\
            \n!-6)To Close-----!\
            \n Choose:  "))
            print("!-------------------------!")
            return option
         except:
             print("Please imput correctly")
             self.menu()
        
        
    def private_msg(self):
         self.welcome()
         dest_addr=input("Input destination address: ")
         return dest_addr#return destination address
    def node_id(self):
        email =input("Please input your email: ")
        mail =hashlib.md5(email.encode('utf-8'))
        hash_mail = mail.hexdigest()
        return hash_mail#return MD5 hash of node email
    def src_port(self):
        return 9999 #used us source port "Lestning port"
    def dest_port(self):
        return 9999
    def peer_port(self):
        return "9999"#used as neighbour port
    def cost_matrix(self):
        cost= int(input("Please input link cost of the node: "))
        return cost#return cost of the node
    def time_out(self):
        return 30#return time out(update time)
    def packet_type(self,typ):
        if typ == "data":
            return 0x02#return 2 if message is data
        elif typ == "conf":
            return 0x04#return 4 if message is configuration(authorization)
        else:
            print("Packet Type Error!!")