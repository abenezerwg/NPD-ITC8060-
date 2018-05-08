# # # from scapy import *
# # import socket
# # host = '127.0.0.1' #replace with your IP
# # my_port = 3002
# # message = "some string I want to send in chunks"

# # def chunks(lst, n):
# #     "Yield successive n-sized chunks from lst"
# #     for i in xrange(0, len(lst), n):
# #         yield lst[i:i+n]

# # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # client_socket.connect((host, my_port))
# # ss=StreamSocket(client_socket,Raw)
# # for chunk in chunks(message, 10):
# #     print "sending: " + chunk
# #     ss.send(Raw(chunk) )

# # client_socket.close()

# print 'Please select an option.'
# option = interactive_choice(['Option 1', 'Option 2', 'Option 3'])
# print 'You have chosen: ' + option

# import os
# import sys
# import re
# sys.path.append(os.path.realpath('.'))
# from pprint import pprint
# import inquirer

# questions = [
#     inquirer.List('size',
#                   message="What size do you need?",
#                   choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
#               ),
# ]

# answers = inquirer.prompt(questions)

# pprint(answers)

# 
# message_type = [
#     inquirer.List('Msg_T', message = "What type of message you want to send ?", choices= ['1. Peer to Peer', '2. Broadcst :'],),
# ]
# choice = inquirer.prompt(message_type)
# print("Your choice is : " , choice)

# # broadcast
# for id, neighbour in r_neighbours.items():  #senidng to every neigbor
#         sendSocket.sendto(create_pkt(id, sendLinkCost), ('localhost', neighbour.port))
#     lock.release()
#     sendSocket.close()

import threading
import time
import socket
import struct
from tkinter import filedialog
import json
from tkinter import *
import tkinter
from tkinter.filedialog import askopenfilename

neighbour_list = []

def sender(_socket, dest_addr):
    option1 = 0
    option2 = 0
    print("what you want to send ...")
    option1 = int(input('1: Message. \n2: Picture \n'))
    print("How you want to send ..")
    option2 = int(input('1: Personal Message. \n2: Group Message '))

    while 1:
    
        if option1 == 1:

            if option2 == 1:
                # if (_socket != neighbour_list)
                send_msg = input("Enter your message")
                _socket.sendto(send_msg.encode(), dest_addr)
            else:
                for neighbour in neighbour_list:
                    if neighbour != 
                    _socket.sendto(send_msg.encode(), neighbour)
        else:
            root = tkinter.Tk()
        
            filename = askopenfilename(filetypes = (("PDF File" , "*.pdf"),("All Files","*.*")))
            print (filename)
            if filename.endswith('.png','.jpeg','.jpg'):
                f = open(filename, 'rb')
                send_msg = f.read(100)
                while(f):
                    if (option2 == 1):
                        _socket.sendto(send_msg.encode('utf8'), dest_addr)
                        # send_msg = f.read(1024)
                        print(send_msg)
                        _socket.close()
                    else: 
                        for neighbour in neighbour_list:
                            _socket.sendto(send_msg.encode(), neighbour)
            else:
                print(".... Invalid file type ...")
            root.mainloop()

        # if(option2 == 1):
        #     while True:
        #         send_msg = input("Enter Message ")
        #         _socket.sendto(send_msg.encode(), dest_addr)

        # else:
        #     global neighbour_list
        #     for neighbour in neighbour_list:
        #         _socket.sendto(send_msg, neighbour[1])



   

def recver(_socket, listen):
    _socket.bind(("", listen))
    data, n_addr = _socket.recvfrom(1024)
    # message = json.loads(data)
    neighbour =  n_addr
    if neighbour not in neighbour_list:
        neighbour_list.append(_socket)

    print("\nNeighbour list :", neighbour_list)
    while True: 
        print("Message from  " + str(neighbour[1]) + " is : " + data.decode())
        new_msg = input("enter broadcst:")
        for i in neighbour_list:
            _socket.sendto(new_msg.encode(),i)

   

if __name__ == '__main__':
	listen_port = int(input("Enter listening Port: "))
	send_to_addr = input("The other's IP: ")
	send_to_port = int(input("Enter others Port: "))
    
	# Create socket
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    neighbour_list.append(serverSocket)
	#  Create receive thread
	t_recv = threading.Thread(target=recver, args=(serverSocket, listen_port))
	t_recv.start()

	# Create Thread
	t_send = threading.Thread(target=sender, args=(serverSocket, (send_to_addr,send_to_port)))
	t_send.start()
