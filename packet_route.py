
"""
       NPD
       @01-05-2018
"""
import os
import sys
import socket
import select
import pgpy
import json
import threading
import time
import copy
import signal
import struct
from encryption import Encryption
msg_Enc=Encryption()#Instantiate the Encryption class "to be used latter"
class route:
    
    def __init__(self):
        self.INFINITY = float('inf')#Set Cost to infinity 
        self.self_id = ''        #Node Id 
        self.email=''            #User email
        self.time_out=30         #Time out
        self.dest_id=''          #Destination node ID,
        self.neighbour = {}      # Dictionary that holds neighbour table 
        self.routing_table = {}  # Dictionary for routing table it holds holds 'cost' and 'link'
        self.via_links = {}      # maps neighbpur ID to cost for every link in topography
        self.active_hist = {}    # for the timer
        #Prompt user for input for private Message
    def msg_prompt(self,_socket):
        dst_id = input("Input Destination Address: ")
        content = input("Input your message: ")
        self.send_prv_msg(_socket,dst_id,content)
        sys.stdout.flush()
    def file_prompt(self,_socket):
        dst_id = input("Input Destination Address: ")
        filename = input("Input file name: ")
        self.fileTransfer(_socket,dst_id,filename)
        sys.stdout.flush()
    def update_neighbor(self,_socket): #send this node's routing table to all neighbors
        for neighbor in copy.deepcopy(self.neighbour):
            temp = neighbor.split(':')
            addr = (temp[0], int(temp[1]))
            send_dict = {'type': 'update', 'routing_table': {}, }
            rt_copy = copy.deepcopy(self.routing_table)
            for node in rt_copy: # our own routing table
                send_dict['routing_table'][node] = rt_copy[node]
                #using deepcopy to keep this code thread-safe
                #-- POISONED REVERSE IMPLEMENTATION --#
                if node != neighbor and rt_copy[node]['link'] == neighbor:
                    send_dict['routing_table'][node]['cost'] = self.INFINITY
            try:
                _socket.sendto(json.dumps(send_dict).encode('utf-8'), addr)
            except:
                pass
    # thread for Each node to sends whole table every 30 seconds 
    # with flag RoutingFull.
    def time_update(self,recvSock,time_out):
        self.update_neighbor(recvSock)
        try:
            t = threading.Timer(self.time_out, self.time_update, [self.time_out])
            t.setDaemon(True)
            t.start()
        except:
            pass
            #Handle incomming comands from the terminal

    def show_routingT(self,routing_table):
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        print("---------- Routing Table --------------------------------")
        print(" | "+ "--Time--"+ " | "+ "--Dest--" + "     | " + "---Link--- " + "      | " + "--Cost--" + " | ")
        for node in self.routing_table:
            link = self.routing_table[node]['link']
            print (" | " + str(t_log) +  " |" + str(node) +  "| " + link + "   |"+ str(self.routing_table[node]['cost']) + "         | ")
            print ("----------------------------------------------------------")

    # thread to check to see if nodes have timed out
    def msg_handler(self,recvSock,rcv_data, tuple_addr):

        global self_id
        table_changed = False
        t_now = int(time.time())
        addr = str(tuple_addr[0]) + ":" + str(tuple_addr[1])

        # ------------------ RECEIVED TABLE UPDATE ---------------------- #
        if rcv_data['type'] == 'update':
            self.active_hist[addr] = t_now

            # update our existing neighbor table for this address
            if addr in self.neighbour:
                self.neighbour[addr] = rcv_data['routing_table']

            if addr in self.routing_table:
                if self.routing_table[addr]['cost'] == self.INFINITY:
                    self.routing_table[addr]['cost'] = self.via_links[addr]
                    self.routing_table[addr]['link'] = addr
                    self.routing_table[addr]['email'] = self.email
                    table_changed = True
                    # online node was a former neighbor
                    if addr in self.via_links:
                        self.neighbour[addr] = rcv_data['routing_table']

            # they know of us but we don't know them yet
            elif rcv_data['routing_table'].has_key(self.self_id):
                self.routing_table[addr] = {} #new entry
                self.routing_table[addr]['cost'] = rcv_data['routing_table'][self.self_id]['cost']
                self.routing_table[addr]['link'] = addr
                self.routing_table[addr]['email'] = self.email
                table_changed = True

                # new node enters the network as immediate neighbor
                if rcv_data['routing_table'][self.self_id]['link'] == self.self_id:
                    self.neighbour[addr] = rcv_data['routing_table']
                    self.via_links[addr] = rcv_data['routing_table'][self.self_id]['cost']
            else:
                    sys.exit("Unrecognized case. Possible error in topography construction.")

            for node in rcv_data['routing_table']:
                if node != self.self_id:
                    # discover a new node that entered network 
                    # regardless of if this node has contacted us directly
                    if node not in self.routing_table:
                        self.routing_table[node] = {
                        'cost': self.INFINITY,
                        'link': "n/a"
                        }
                        table_changed = True
                    # BELLMAN FORD ALGORITHM
                    for dest in self.routing_table:
                        old_cost = self.routing_table[dest]['cost']
                        if addr in self.neighbour and dest in self.neighbour[addr]:
                            new_cost = self.routing_table[addr]['cost'] + self.neighbour[addr][dest]['cost']

                            if new_cost < old_cost:
                                self.routing_table[dest]['cost'] = new_cost
                                self.routing_table[dest]['link'] = addr
                                self.table_changed = True
                if table_changed:
                    self.update_neighbor(recvSock)
                    table_changed = False

        elif rcv_data['type'] == 0x02:
            if rcv_data['sender'] != self.self_id:
                self.active_hist[addr] = t_now
                print ('\n' + rcv_data['msg'])
                # send_dict = { 'type': 'update', 'msg': rcv_data['msg'], 'sender': rcv_data['sender'] }
                # self.tell_neighbor(recvSock, send_dict)
                self.msg_prompt(recvSock)     
        elif rcv_data['type'] == 0x03:
            if rcv_data['sender'] != self.self_id:
                t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
                print ('\n You have recived a file @['+str(t_log)+'] ' + rcv_data['file_Name']+'.txt')
                with open('{}.txt'.format(rcv_data['file_Name']), 'wb').write(bytes(rcv_data['file'])) as f:
                    f.close()
                self.msg_prompt(recvSock)       
        # ------------ RECEIVED CLOSE MESSAGE --------------------- #
        elif rcv_data['type'] == 'close':

            print ("DEBUG: [received CLOSE message from %s]" % str(tuple_addr))
            self.active_hist[addr] = t_now
            close_node = rcv_data['target']
            if self.routing_table[close_node]['cost'] != self.INFINITY:
                self.routing_table[close_node]['cost'] = self.INFINITY
                self.routing_table[close_node]['link'] = "n/a"

                if close_node in self.neighbour:
                    del self.neighbour[close_node]
                # reinitialize routing table
                for node in self.routing_table:
                    if node in self.neighbour:
                        self.routing_table[node]['cost'] = self.via_links[node]
                        self.routing_table[node]['link'] = node
                    else:
                        self.routing_table[node]['cost'] = self.INFINITY
                        self.routing_table[node]['link'] = "n/a"
                        send_dict = { 'type': 'close', 'target': close_node, }
                        self.tell_neighbor(recvSock, send_dict)
            else:
                self.update_neighbor(recvSock)
    def ip2int(self,ip_addr):
        if ip_addr == 'localhost':
            ip_addr = '127.0.0.1'
        return [int(x) for x in ip_addr.split('.')]
    def chunks(self,lst, n):
        #returns successive n-sized chunks from lst
        for i in range(0, len(lst), n):
            yield lst[i:i+n]
    def send_prv_msg(self,recvSock,dst_id,send_msg):
        temp = self.self_id.split(":")
        self_id=temp[0]
        dest_ip = self.ip2int(dst_id)
        dest_port = 9999
        src_port = temp[1]
        email= self.email
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        # print(self.self_id)
        msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(send_msg)
        send_dict = { 'type': 0x02, 'msg': msg, 'sender': self_id,\
        'reciever': dest_ip,'src_port': src_port, 'dest_port':dest_port,'email':email,'time':t_log}
        self.tell_neighbor(recvSock,send_dict)
    def broadcast_msg(self,conn,_socket):
            msg=input("input Message: ")
            temp = self.self_id.split(":")
            self_id=temp[0]
            t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
            msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(msg)
            send_dict = { 'type': 0x02, 'msg': msg, 'sender': self_id,'time':t_log}
            for sock in conn:
                sock.send(send_dict)
    def fileTransfer(self,recvSock,dest,file_name):
        temp = self.self_id.split(":")
        self_id=temp[0]
        dest_ip = self.ip2int(dest)
        dest_port = 9999
        src_port = temp[1]
        email= self.email
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        # print(self.self_id)
        text_inside="This is message in the file"
        open('{}.txt'.format(file_name), 'wb').write(bytes(text_inside,'utf-8'))
        f=open(file_name+".txt", 'r')
        data=f.read(1024)
        if data:
            send_dict = { 'type': 0x03, 'file': data, 'sender': self_id,\
            'reciever': dest_ip,'file_Name': file_name,'src_port': src_port, 'dest_port':dest_port,'email':email,'time':t_log}
            self.tell_neighbor(recvSock,send_dict)

    def tell_neighbor(self,sock, payload):
            package = json.dumps(payload)
            #Let us Encrypt the whole message before chunking and sending it
            if not os.path.isfile("first.asc"):
                # generate keys first
                msg_Enc.generate_certificates()
            try:
                enc_package= msg_Enc.encrypt(package)
            except pgpy.errors.PGPError:
                print('Encryption failed!')
            for neighbor in self.neighbour:
                temp = neighbor.split(":")
                for chunk in self.chunks(enc_package, 100):
                    try:
                        sock.sendto(chunk, (temp[0], int(temp[1])))    
                    except:
                        print("can not send data")
                    