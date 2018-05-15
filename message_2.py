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
from encryption import Encoder

main = main()
router= route()
RECV_BUFFER=1024
zero = 0
protocol = 17
conn=[]
chunk=[]
d_Chunk=[]
def recieve_msg(_socket,listen,peer_port,peer_ip,cost,node_id):
    m_data=""
    
    _socket.bind(('', listen))
    host = socket.gethostbyname(socket.gethostname())
    router.self_id = str(host) + ":" + str(listen)
    #set neighbour IP and initialize routing table
    n_ip = socket.gethostbyname(peer_ip)
    neighbor_id = str(n_ip) + ":" + peer_port
    #Fill routing data
    router.routing_table[neighbor_id] = {}
    router.routing_table[neighbor_id]['cost'] = cost
    router.routing_table[neighbor_id]['link'] = neighbor_id
    router.routing_table[neighbor_id]['email'] = node_id
    router.adjacent_links[neighbor_id] = cost
    router.neighbors[neighbor_id] = {}
    router.time_out=main.time_out()
    router.email=node_id

    print ("bfclient running at address [%s] on port [%s]" % (str(host), listen))
    # router.update_timer(_socket,route.time_out)
    # router.node_timer(_socket,route.time_out)
    os.system("clear")
    option =main.menu()
    if option==1:
        router.msg_prompt()
    elif option == 2:
        router.msg_prompt()
    elif option == 3:
        pass
    else:
        router.msg_prompt()
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
                if data:
                    chunk.append(data)
                    merge_data=merge(chunk)  
                    try:
                        data = json.loads(merge_data)
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
                    router.msg_prompt()
                else:
                    sys.stdout.flush()
                    router.msg_prompt()
    _socket.close()
    

def merge(data):
    m_data=""
    for x in data:
        m_data +=x.decode('utf-8')
    return m_data 


if __name__ == '__main__':
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
    t_recv = threading.Thread(target=recieve_msg, args=(serverSocket,src_port,peer_port,peer_ip,cost,node_id))
    t_recv.start()
    
    


    



