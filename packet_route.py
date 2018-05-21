import sys
import socket
import select
import json
import threading
import time
import copy
import signal
import struct
from encryption import Encoder
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
    
    def msg_prompt(self,_socket):
        dst_id = input("Input Destination Address: ")
        content = input("Input your message: ")
        self.send_prv_msg(_socket,dst_id,content)
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
    def neigh_update(self,recvSock): #send this node's routing table to all neighbors
        for neighbor in copy.deepcopy(self.neighbour):
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

    # thread for Each node to sends whole table every 30 seconds 
    # with flag RoutingFull.
    def time_update(self,recvSock,time_out):
        self.neigh_update(recvSock)
        try:
            t = threading.Timer(self.time_out, self.time_update, [self.time_out])
            t.setDaemon(True)
            t.start()
        except:
            pass
            #Handle incomming comands from the terminal
    def cmd(self,recvSock,args):
        if args[0] == "HELLO":
            content = ' '.join(args[1:(len(args))])
            self.auth_hello(recvSock,self.self_id, content)
        elif args[0] == "SHOWRT":
            self.show_routingT(self.routing_table)
        elif args[0] == "PMSG":
            dst_id = ' '.join(args[1:2])
            content = ' '.join(args[2:(len(args))])
            self.send_prv_msg(recvSock,dst_id,content)
        elif args[0] == "CLOSE":
            self.close()
        elif args[0] == "MENU":
            pass
    def auth_hello(self,recvSock,self_id, message):
        t_log = t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(message)
        send_dict = {'type': 'update', 'routing_table': {},'msg':msg }
        self.tell_neighbor(recvSock, send_dict)
   
    def close(self):
        sys.exit("(%s) going offline." % self.self_id)
    def show_routingT(self,routin_table):
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
                    self.neigh_update(recvSock)
                    table_changed = False

        elif rcv_data['type'] == 0x02:
            if rcv_data['sender'] != self.self_id:
                self.active_hist[addr] = t_now
                print ('\n' + rcv_data['msg'])
                send_dict = { 'type': 'update', 'msg': rcv_data['msg'], 'sender': rcv_data['sender'] }
                self.tell_neighbor(recvSock, send_dict)
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
                self.neigh_update(recvSock)
    
    def ip2int(self,ip_addr):
        if ip_addr == 'localhost':
            ip_addr = '127.0.0.1'
        return [int(x) for x in ip_addr.split('.')]
    def chunks(self,lst, n):
        "Yield successive n-sized chunks from lst"
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
    def tell_neighbor(self,sock, payload):
            package = json.dumps(payload)
            for neighbor in self.neighbour:
                temp = neighbor.split(":")
                for chunk in self.chunks(package, 100):
                    try:
                        sock.sendto(chunk.encode('utf-8'), (temp[0], int(temp[1])))           
                    except:
                        print("can not send data")
                    