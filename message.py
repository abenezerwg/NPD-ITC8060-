import threading
import time
import socket
import struct
import sys
import json
import os
import select
from CLI import main
from packet_route import route
from encryption import Encryption
pgp = Encryption()#Instantiate the Encryption class "to be used latter"
main = main()#Instantiate the main class "to be used latter"
router= route()#Instantiate the route class "to be used latter"
RECV_BUFFER=1024#set initial buffer size 1024
conn={}#Creat Connection list to hold connections
chunk=[]#creat Chunk list to hold chunk packets
def recieve_msg(_socket,listen,peer_port,peer_ip,cost,node_id):
    """
    This Method will be used to recive any data from sender 
    """
    _socket.bind(('', listen))
    host = socket.gethostbyname(socket.gethostname())
    router.self_id = str(host) + ":" + str(listen)
    #set neighbour IP and initialize routing table
    n_ip = socket.gethostbyname(peer_ip)
    neighbor_id = str(n_ip) + ":" + peer_port
    #Fill nodes routing data
    router.routing_table[neighbor_id] = {}
    router.routing_table[neighbor_id]['cost'] = cost
    router.routing_table[neighbor_id]['link'] = neighbor_id
    router.routing_table[neighbor_id]['email'] = node_id
    router.adjacent_links[neighbor_id] = cost
    router.neighbors[neighbor_id] = {}
    router.time_out=main.time_out()
    router.email=node_id
    os.system("clear")
    login_menu(_socket,conn)
    while True:
        socket_list = [sys.stdin,_socket]
        try:
            read_sockets, write_sockets, error_sockets = select.select(socket_list,[],[])
        except select.error:
            break
        except socket.error:
            break
        for sock in read_sockets:
            if sock == _socket:
                data, addr = _socket.recvfrom(RECV_BUFFER) 
                conn[addr] = node_id#add node Id to connection list
                if not os.path.isfile("first.asc"):
                    # generate keys first
                    pgp.generate_certificates()#if there is no key generate a key
                chunk.append(data)#append incomming consiquitive packets
                merge_data=merge(chunk)#merge packets in chunk list
                try:
                    """
                    This block Decrypt the merged file a if there is data let's decrypt 
                        it and load it to the json to be sent to msg_handler method
                    """
                    decrypted = pgp.decrypt(merge_data)
                    data = json.loads(decrypted)
                    chunk[:]=[]
                    router.msg_handler(serverSocket,data, addr)
                    time.sleep(0.1)
                except:
                    pass 
                
            else:
                data = sys.stdin.readline().rstrip()#read command line and clear empty space
                if data=="MENU":#return to menu if user type MENU in uppercase
                    os.system("clear")
                    login_menu(_socket,conn)
                else:
                    router.send_prv_msg(_socket,router.dest_id,data)#Other wise send message to destination node 
                    router.msg_prompt()
    _socket.close()

def merge(data):# merge incoming chunked packets in to one stream of byte data
    m_data=b''
    for x in data:
        m_data +=x
    return m_data 
 # Function to creat a thread for Each node to sends whole table every 30 seconds 
def time_update(serverSocket,timeout_interval):
    router.neighbour_update(serverSocket)
def route_update(serverSocket,timeout_interval):
        router.node_timer(serverSocket)
def login_menu(_socket,conn):#login menu to be called on sending message
    option =main.menu()
    if option == 1:
        dst_id = input("Input Destination Address: ")
        content = input("Input your message: ")
        router.dest_id=dst_id
        router.send_prv_msg(_socket,dst_id,content)
    elif option == 2:
        router.broadcast_msg(conn,_socket)
    elif option == 3:
        dst_id = input("Input Destination Address: ")
        filename = input("Input file name: ")
        router.fileTransfer(_socket,dst_id,filename)
    elif option == 4:
        print("Online Nodes: ", conn)
    elif option == 5:
        router.show_routingT(router.routing_table)
    elif option == 6:
        router.close()
        
if __name__ == '__main__':
    """
    Here we  initialise variables which are used to initialise the route module
    """
    os.system("clear")
    peer_ip = main.login()
    peer_port=main.peer_port()
    src_port = main.src_port()
    dest_port = main.dest_port()
    node_id= main.node_id()
    cost = main.cost_matrix()
    time_out= main.time_out()
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    recieve_msg(serverSocket,src_port,peer_port,peer_ip,cost,node_id)
    t = threading.Timer(time_out, time_update, [time_out])
    t.setDaemon(True)
    t.start()
    time = threading.Timer(time_out, route_update, [time_out])
    time.setDaemon(True)
    time.start()



