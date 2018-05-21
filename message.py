import threading
import time
import socket
import struct
import sys
import json
import os
import select
from main import main
from packet_route import route
from encryption import Encryption
pgp = Encryption()#Instantiate the Encryption class "to be used latter"
main = main()#Instantiate the main class "to be used latter"
router= route()#Instantiate the router class "to be used latter"
RECV_BUFFER=1024
conn={}
chunk=[]
d_Chunk=[]
def recieve_msg(_socket,listen,peer_port,peer_ip,cost,node_id):
    _socket.bind(('', listen))
    host = socket.gethostbyname(socket.gethostname())
    router.self_id = str(host) + ":" + str(listen)
    #set neighbour IP and initialize routing table
    n_ip = socket.gethostbyname(peer_ip)
    neighbor_id = str(n_ip) + ":" + peer_port
    #Fill node routing data
    router.routing_table[neighbor_id] = {}
    router.routing_table[neighbor_id]['cost'] = cost
    router.routing_table[neighbor_id]['link'] = neighbor_id
    router.routing_table[neighbor_id]['email'] = node_id
    router.via_links[neighbor_id] = cost
    router.neighbour[neighbor_id] = {}
    router.email=node_id
    os.system("clear")
    menu(_socket,conn,router.routing_table)
    route_update(serverSocket)
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
                conn[addr] = node_id
                if data:
                    if not os.path.isfile("first.asc"):
                        # generate keys first
                        pgp.generate_certificates()
                    chunk.append(data)
                    merge_data=merge(chunk) 
                    try:
                        """
                        Decrypt the merged file a if there is data let's decrypt 
                         it and load it to the json to be sent to msg_handler method
                        """
                        try:
                            decrypted = pgp.decrypt(merge_data)
                        except:
                            pass
                        data = json.loads(decrypted)
                        chunk[:]=[]
                        router.msg_handler(_socket,data, addr)
                        time.sleep(0.1)
                    except:
                        pass
                else:
                    print("no data recived!") 
                
            else:
                data = sys.stdin.readline().rstrip()
                if len(data) > 0:
                    data_list = data.split()
                    router.cmd(_socket,data_list)
                    menu(_socket,conn,router.routing_table)
                else:
                    sys.stdout.flush()
                    menu(_socket,conn,router.routing_table)
    _socket.close()
    
def menu(_socket,conn,routin_table):
    try:
        main.welcome()
        option=int(input("!-Please use\
            ---!\n!-1)For Private msg--------!\
            \n!-2)For Group message------!\
            \n!-3)ForFile Transfer-------!\
            \n!-4)List Users-------------!\
            \n!-5)Show Routing Table-----!\
            \n Choose:  "))
        print("!-------------------------!")
        if option == 1:
            router.msg_prompt(_socket)
        elif option == 2:
            router.broadcast_msg(conn,_socket)
        elif option == 3:
            pass
        elif option == 4:
            pass
        elif option == 5:
            router.show_routingT(routin_table)
        else:
            print("Please input Correctly!")
            menu(_socket,conn,routin_table)
    except:
        print("Error on Input!")
        menu(_socket,conn,routin_table)
def route_update(_socket,timeout_interval=10):
        router.update_neighbor(_socket)
        time = threading.Timer(timeout_interval, route_update, [timeout_interval])
        time.setDaemon(True)
        time.start()
        
def merge(data):
    m_data=b''
    for x in data:
        m_data +=x
    return m_data 

if __name__ == '__main__':
    os.system("clear")
    peer_ip = main.login()
    peer_port=main.peer_port()
    src_port = main.src_port()
    dest_port = main.dest_port()
    node_id= main.node_id()
    cost = main.cost_matrix()
    time_out= 10
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    t_recv = threading.Thread(target=recieve_msg, args=(serverSocket,src_port,peer_port,peer_ip,cost,node_id))
    t_recv.start()
    
    
    


    



