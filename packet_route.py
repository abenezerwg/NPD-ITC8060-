import sys
import socket
import select
import json
import threading
import time
import copy
import signal
import struct
import os
import pgpy
# from __future__ import division
import sys
from CLI import main
from encryption import Encryption
msg_Enc=Encryption()#Instantiate the Encryption class "to be used latter"
main= main()#Instantiate the Encryption class "to be used latter"
class route:
    
    def __init__(self):
        self.RECV_BUFFER = 4096
        self.INFINITY = float('inf')
        self.self_id = '' #Node ID
        self.email=''     #User email to be converted to Hash value
        self.dest_id=''   #Destination node ID
        self.neighbors = {}      # Neighbour node dictionary
        self.routing_table = {}  # Each node routing dictionary value holds 3 keys:'Time','cost' and 'link'
        self.adjacent_links = {} # maps neighbor_id to edge cost for every link in topography
        self.active_hist = {}    # Active nodes for the timer
        self.conn={}
        
    def msg_prompt(self):#prompt user to input message
        sys.stdout.write('Type MENU to go back, Msg: > ')
        sys.stdout.flush()

    def neighbour_update(self,recvSock): #send this node's routing table to all neighbors
        for neighbor in copy.deepcopy(self.neighbors):
            temp = neighbor.split(':') 
            addr = (temp[0], int(temp[1]))#change to hex-decimal int base 16

            send_dict = {'type': 'update', 'routing_table': {}, }
            rt_copy = copy.deepcopy(self.routing_table)
            for node in rt_copy: # our own routing table
                send_dict['routing_table'][node] = rt_copy[node]
                #using deepcopy to keep this code thread-safe

                #-- POISONED REVERSE IMPLEMENTATION --#
                if node != neighbor and rt_copy[node]['link'] == neighbor:
                    send_dict['routing_table'][node]['cost'] = self.INFINITY
            msg=json.dumps(send_dict).encode('utf-8')
            recvSock.sendto(msg, addr) 

            #Handle incomming comands from the terminal
    def close(self):
        sys.exit("(%s) going offline." % self.self_id)
    def show_routingT(self,routin_table):
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        print ("[%s] Distance vector list for [%s] is:" % (str(t_log), self.self_id))
        print("---------- Routing Table --------------------------------")
        print(" | "+ "--Time--"+ " | "+ "--Dest--" + "     | " + "---Link--- " + "      | " + "--Cost--" + " | ")
        for node in self.routing_table:
            link = self.routing_table[node]['link']
            print (" | " + str(t_log) +  " |" + str(node) +  "| " + link + "   |"+ str(self.routing_table[node]['cost']) + "         | ")
            print ("----------------------------------------------------------")

    # thread to check to see if nodes have timed out
    def node_timer(self,recvSock,time_out=10):
        # deep copy for thread safety
        for neighbor in copy.deepcopy(self.neighbors):
            if neighbor in self.active_hist:
                t_threshold = (3 * time_out)
                # found a node assumed to be 'dead'
                if ((int(time.time()) - self.active_hist[neighbor]) > t_threshold):
                    if self.routing_table[neighbor]['cost'] != self.INFINITY:
                        self.routing_table[neighbor]['cost'] = self.INFINITY
                        self.routing_table[neighbor]['link'] = "n/a"
                        self.routing_table[neighbor]['email'] = "n/a"
                        del self.neighbors[neighbor]
                        # reinitialize table
                        for node in self.routing_table:
                            if node in self.neighbors:
                                self.routing_table[node]['cost'] = self.adjacent_links[node]
                                self.routing_table[node]['link'] = node
                                self.routing_table[node]['email'] = self.email
                            else:
                                self.routing_table[node]['cost'] = self.INFINITY
                                self.routing_table[node]['link'] = "n/a"
                                self.routing_table[node]['email'] = "n/a"

                        send_dict = { 'type': 'close', 'target': neighbor }
                        for neighbor in self.neighbors:
                            temp = neighbor.split(':')
                            recvSock.sendto(json.dumps(send_dict), (temp[0], int(temp[1])))

                    else:
                        self.neighbour_update(recvSock)

        # run thread every 3 seconds (timeout threshold will be multiple of 3)
        try:
            t = threading.Timer(30, self.node_timer, [time_out])
            t.setDaemon(True)
            t.start()
        except:
            pass
       
    #Handle incomming messages
    def msg_handler(self,recvSock,rcv_data, tuple_addr):

        global self_id
        table_changed = False
        t_now = int(time.time())
        addr = str(tuple_addr[0]) + ":" + str(tuple_addr[1])

        # ------------------ RECEIVED TABLE UPDATE ---------------------- #
        if rcv_data['type'] == 'update':
            self.active_hist[addr] = t_now

            # update our existing neighbor table for this address
            if addr in self.neighbors:
                self.neighbors[addr] = rcv_data['routing_table']

            if addr in self.routing_table:
                if self.routing_table[addr]['cost'] == self.INFINITY:
                    self.routing_table[addr]['cost'] = self.adjacent_links[addr]
                    self.routing_table[addr]['link'] = addr
                    self.routing_table[addr]['email'] = self.email
                    table_changed = True
                    # online node was a former neighbor
                    if addr in self.adjacent_links:
                        self.neighbors[addr] = rcv_data['routing_table']

            # they know of us but we don't know them yet
            elif rcv_data['routing_table'].has_key(self.self_id):
                self.routing_table[addr] = {} #new entry
                self.routing_table[addr]['cost'] = rcv_data['routing_table'][self.self_id]['cost']
                self.routing_table[addr]['link'] = addr
                self.routing_table[addr]['email'] = self.email
                table_changed = True

                # new node enters the network as immediate neighbor
                if rcv_data['routing_table'][self.self_id]['link'] == self.self_id:
                    self.neighbors[addr] = rcv_data['routing_table']
                    self.adjacent_links[addr] = rcv_data['routing_table'][self.self_id]['cost']
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
                        if addr in self.neighbors and dest in self.neighbors[addr]:
                            new_cost = self.routing_table[addr]['cost'] + self.neighbors[addr][dest]['cost']

                            if new_cost < old_cost:
                                self.routing_table[dest]['cost'] = new_cost
                                self.routing_table[dest]['link'] = addr
                                self.table_changed = True

                if table_changed:
                    self.neighbour_update(recvSock)
                    table_changed = False

        elif rcv_data['type'] == 0x02:#message recived with type 0X02
            if rcv_data['sender'] != self.self_id: 
                self.active_hist[addr] = t_now
                print ('\n' + rcv_data['msg'])
                send_dict = { 'type': 'update', 'msg': rcv_data['msg'], 'sender': rcv_data['sender'] }
                self.tell_neighbor(recvSock, send_dict)
                self.msg_prompt()
        
        elif rcv_data['type'] == 0x03:#file recieved with type 0X03
            if rcv_data['sender'] != self.self_id:
                t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
                print ('\n You have recieved a file @['+str(t_log)+'] ' + rcv_data['file_Name']+'.txt')
                open('{}.txt'.format(rcv_data['file_Name']), 'wb').write(bytes(rcv_data['file']))
                self.msg_prompt()

        # ------------ RECEIVED CLOSE MESSAGE --------------------- #
        elif rcv_data['type'] == 'close':

            print ("DEBUG: [received CLOSE message from %s]" % str(tuple_addr))
            self.active_hist[addr] = t_now
            close_node = rcv_data['target']
            if self.routing_table[close_node]['cost'] != self.INFINITY:
                self.routing_table[close_node]['cost'] = self.INFINITY
                self.routing_table[close_node]['link'] = "n/a"

                if close_node in self.neighbors:
                    del self.neighbors[close_node]

                # reinitialize routing table
                for node in self.routing_table:
                    if node in self.neighbors:
                        self.routing_table[node]['cost'] = self.adjacent_links[node]
                        self.routing_table[node]['link'] = node
                    else:
                        self.routing_table[node]['cost'] = self.INFINITY
                        self.routing_table[node]['link'] = "n/a"

                        send_dict = { 'type': 'close', 'target': close_node, }
                        self.tell_neighbor(recvSock, send_dict)

            else:
                self.neighbour_update(recvSock)
    
    
    def ip2int(self,ip_addr):#change localhost to 127.0.0.1 and chnge string IP to int
        if ip_addr == 'localhost':
            ip_addr = '127.0.0.1'
        return [int(x) for x in ip_addr.split('.')]
    def chunks(self,lst, n):#chunk incoming messages to n sized packets 
        "Yield successive n-sized chunks from lst"
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    def send_prv_msg(self,recvSock,dst_id,send_msg):#send private message
        temp = self.self_id.split(":")
        self_id=temp[0]
        dest_ip = self.ip2int(dst_id)
        dest_port = main.dest_port()
        src_port = temp[1]
        email= self.email
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(send_msg)
        send_dict = { 'type': 0x02, 'msg': msg, 'sender': self_id,\
        'reciever': dest_ip,'src_port': src_port, 'dest_port':dest_port,'email':email }
        self.tell_neighbor(recvSock,send_dict)
    def broadcast_msg(self,conn,_socket):#brodcast message
            msg=input("input Message: ")
            temp = self.self_id.split(":")
            self_id=temp[0]
            t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
            msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(msg)
            send_dict = { 'type': 0x02, 'msg': msg, 'sender': self_id,'time':t_log}
            for sock in conn:
                sock.send(send_dict)
    def fileTransfer(self,recvSock,dest,file_name):#transfer file
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
    def tell_neighbor(self,sock, payload):#send data to direct neighbour 
            package = json.dumps(payload)
            #Let us Encrypt the whole message before chunking and sending it
            if not os.path.isfile("first.asc"):
                # generate keys first
                msg_Enc.generate_certificates()
            try:
                 enc_package= msg_Enc.encrypt(package)
            except pgpy.errors.PGPError:
                print('Encryption failed!')
            for neighbor in self.neighbors:
                temp = neighbor.split(":")
                for chunk in self.chunks(enc_package, 100):
                    try:
                       sock.sendto(chunk, (temp[0], int(temp[1])))    
                    except:
                        print("can not send data")
                    
                        # i=i+1
                
                    