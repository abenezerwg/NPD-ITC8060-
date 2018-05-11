import sys
import socket
import select
import json
import threading
import time
import copy
import signal
import struct
from main import main
from encryption import encrypt
encrypt =encrypt()
main= main()
class route:
    
    def __init__(self):
        self.RECV_BUFFER = 4096
        self.INFINITY = float('inf')
        self.self_id = ''
        self.email=''
        self.time_out=0
        self.dest_id=''
        self.neighbors = {}      # maps neighbor nodes to the neighbor node's routing table
        self.routing_table = {}  # maps node_id to each node's dictionary.               # each dictionary value holds 2 keys: 'cost' and 'link'
        self.adjacent_links = {} # maps neighbor_id to edge cost for every link in topography
        self.old_links = {}      # maps previously active neighbor nodes to their link costs
        self.active_hist = {}    # for the timer
        self.dead_links = [] # node pairs for link taken offline by either node
    
    # def parse(self,data):
    #     packet = {}
    #     packet['version']       =  4
    #     packet['TTL']           = 30
    #     packet['type']           = 0x02        
    #     packet['src_ip']        = '.'.join(list(map(str, [data[x] for x in range(12, 16)])))
    #     packet['dest_ip']       = '.'.join(list(map(str, [data[x] for x in range(16, 20)])))
    #     packet['src_port']      = (data[20] << 8) + data[21]
    #     packet['dest_port']     = (data[22] << 8) + data[23]
    #     packet['udp_length']    = (data[24] << 8) + data[25]
    #     packet['UDP_checksum']  = (data[26] << 8) + data[27]
    #     packet['data']          = ''.join(list(map(chr, [data[28 + x] for x in range(0, packet['udp_length'] - 8)])))
        
    #     return packet

    def msg_prompt(self):
        sys.stdout.write('Msg: > ')
        sys.stdout.flush()
    def prompt(self):
        sys.stdout.write('Input your command: > ')
        sys.stdout.flush()
        
    def verify_checksum(self,data, checksum):
        data_len = len(data)
        if (data_len%2) == 1:
            data_len += 1
            data += struct.pack('!B', 0)
        
        for i in range(0, len(data), 2):
            w = (data[i] << 8) + (data[i + 1])
            checksum += w
            checksum = (checksum >> 16) + (checksum & 0xFFFF)
    
    def update_neighbor(self,recvSock): #send this node's routing table to all neighbors
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

    # thread to periodically send updates
    def update_timer(self,recvSock,time_out):
        self.update_neighbor(recvSock)
        try:
            t = threading.Timer(self.time_out, self.update_timer, [self.time_out])
            t.setDaemon(True)
            t.start()
        except:
            pass
            #Handle incomming comands from the terminal
    def cmd_handler(self,recvSock,args):
        if args[0] == "HELLO":
            content = ' '.join(args[1:(len(args))])
            self.auth_hello(recvSock,self.self_id, content)
        elif args[0] == "SHOWRT":
            self.show_rt(self.routing_table)
        elif args[0] == "PMSG":
            dst_id = ' '.join(args[1:2])
            content = ' '.join(args[2:(len(args))])
            self.send_prv_msg(recvSock,self.self_id,dst_id,content)
        elif args[0] == "CLOSE":
            self.close()
        elif args[0] == "MENU":
            main.menu()
    def auth_hello(self,recvSock,self_id, message):
        t_log = t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(message)
        send_dict = {'type': 'update', 'routing_table': {},'msg':msg }
        self.tell_neighbor(recvSock, send_dict)
   
    def close(self):
        sys.exit("(%s) going offline." % self.self_id)
    def show_rt(self,routin_table):
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        print ("[%s] Distance vector list for [%s] is:" % (str(t_log), self.self_id))
        for node in self.routing_table:
            link = self.routing_table[node]['link']
            print ("Destination = (" + str(node) + "), Cost = " + str(self.routing_table[node]['cost']) + ", Link = " + '(' + link + ')')

    # thread to check to see if nodes have timed out
    def node_timer(self,recvSock,time_out):
        # deep copy for thread safety
        for neighbor in copy.deepcopy(self.neighbors):
            if neighbor in self.active_hist:
                t_threshold = (3 * self.time_out)
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
                        self.update_neighbor(recvSock)

        # run thread every 3 seconds (timeout threshold will be multiple of 3)
        try:
            t = threading.Timer(30, self.node_timer, [self.time_out])
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
                    # discover a new node that entered network regardless of if this node has contacted us directly
                    if node not in self.routing_table:
                        self.routing_table[node] = {
                        'cost': self.INFINITY,
                        'link': "n/a"
                        }
                        table_changed = True

                    # --- BELLMAN FORD ALGORITHM --- #
                    for dest in self.routing_table:
                        old_cost = self.routing_table[dest]['cost']
                        if addr in self.neighbors and dest in self.neighbors[addr]:
                            new_cost = self.routing_table[addr]['cost'] + self.neighbors[addr][dest]['cost']

                            if new_cost < old_cost:
                                self.routing_table[dest]['cost'] = new_cost
                                self.routing_table[dest]['link'] = addr
                                self.table_changed = True

                if table_changed:
                    self.update_neighbor(recvSock)
                    table_changed = False
        #Authorize first time
        # ---- RECEIVED TWEET --- #
        # extra feature here. retweets all tweets. is not a chat room but sometimes you have a custom message.

        elif rcv_data['type'] == 0x02:
            if rcv_data['sender'] != self.self_id:
                self.active_hist[addr] = t_now
                print ('\n' + rcv_data['msg'])
                send_dict = { 'type': 'update', 'msg': rcv_data['msg'], 'sender': rcv_data['sender'] }
                self.tell_neighbor(recvSock, send_dict)
                self.prompt()


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
                self.update_neighbor(recvSock)
    
    
    def ip2int(self,ip_addr):
        if ip_addr == 'localhost':
            ip_addr = '127.0.0.1'
        return [int(x) for x in ip_addr.split('.')]
    def checksum_func(self,data):
        checksum = 0
        data_len = len(data)
        if (data_len%2) == 1:
            data_len += 1
            data += struct.pack('!B', 0)
        
        for i in range(0, len(data), 2):
            w = (data[i] << 8) + (data[i + 1])
            checksum += w

        checksum = (checksum >> 16) + (checksum & 0xFFFF)
        checksum = ~checksum&0xFFFF
        return checksum	
    def send_prv_msg(self,recvSock,self_id,dst_id,send_msg):
        temp = self_id.split(":")
        dest_ip = self.ip2int(dst_id)
        dest_port = main.dest_port()
        src_port = main.src_port()
        email= self.email
        t_log = time.strftime('%H:%M:%S', time.localtime(time.time()))
        msg = '['+str(t_log)+'] ' + "@" + self_id + ": " + str(send_msg)
        send_dict = { 'type': 0x02, 'msg': msg, 'sender': self_id,\
        'reciever': dest_ip,'src_port': src_port, 'dest_port':dest_port,'email':email }
        self.tell_neighbor(recvSock,send_dict)

    def tell_neighbor(self,sock, payload):
            package = json.dumps(payload)
            msg = encrypt.encrypt(self.email,package)
            for neighbor in self.neighbors:
                temp = neighbor.split(":")
                sock.sendto(msg, (temp[0], int(temp[1])))
               
        