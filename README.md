# NPD-ITC8060-

                                        --- NETWORK PROTOCOL APP README ---

Group Members:                                                    
            
            Abenezer  Weldegiorgis            
            
            Krishna Vaishnav 
            
            Tedel Baca 

Submited to: 
           
           Professor Olaf Maennel  
           May 28,2018    

* This is a guide on how to use the our chat room application developed for Network Protocol Design project which was lectured by:  Professor Olaf Maennel.

The files of this application can be downloaded from the following link: https://github.com/Abenaman/NPD-ITC8060-

In order to run this program it is required to use python version >=3.5 and tested in a Linux environment but can run in Windows aswell.

To run this program first we need to install "pgpy" library with "pip3 install pgpy" and also make sure you have installed  pycrypto module.

Defined Modules: 
   
   CLI.py: Contains mainly menu and pre defined src and dest port which is 9999.
   
   message.py: Is the main module of the program which contains the nodes message reciving and sending functions.
   
   packet_route.py: Consists of different functions which are used to handle and route message
   
   encryption.py: This module contains functions which are used to generate certificate based on plus encryption and decription methods based on pgp.

This program has a CLI and is compatible with Python3.5  so to run it we have the following procedure:

1. In Linux terminal write the following command: $python3.5 message.py

2. In our terminal we will see a new screen with an output: "Please input peer IP to connet to chat room:", and waits for our input so here we put our IP address in the network so that we can communicate in network with other nodes, initialize chat by sending message to the destination node.

3.We get an output: "Please input your email:", and here we input our email address

4. We get an output: "Please input link cost of the node:", and here we input the cost of our node

5. After the first four steps a new terminal window will appear with the message: Welcome to the chat room. Here we have 6 options which we can choose for our chat application:

Option !-1): For Private msg - Here we can send private messages between nodes. To do this we choose the destination address in "Input Destination Address:" field and then we write our message,
*initializing conversation reqquires the recivers aknowledgment, after sending a any message from source node to the destination we can creat a session and start chating in order to go back to Menu we Type MENU (UPPER CASE).
*Up on sending of message the program dynamicaly generate files "pgp certificate: <first.asc,second.asc> which we will use for encryption and", "text file: for file transfer<file name.txt>"

Option !-2): For Group message: - Here we can send broadcast message. We just input our messages and send it

Option !-3): For File Transfer:Here we can send private file messages between nodes. To do this we choose the destination address in "Input Destination Address:" field and then we write the file name, if a file with the file name exists in our path it will take that file other wise it will create a .txt file with the given name and input a message on it "for this case we have hard coded the text input"(this is a text in the file! ), here we just only want to show that we can send a file. 

Option !-4): List Users: When we choose this option, list of connected users to us will appear from the connection list.

Option !-5): Show Routing Table: Here we show the nodes distance vector or current routing table which shows: the time when we ran the command, the destination address of the node, the link address of the node, and the cost for the node

Option !-6): We close the application

Reference: 

Reference link : https://pythonexample.com/code/pgpy/ accessed on 21-05-2018

Reference link :https://github.com/nschue/NetworksProject/blob/master/RouterClient.py accessed on 10-05-2018 

Reference link  https://github.com/tummim/jaban-jargon accessed on 10-5-2018

Reference link https://github.com/houluy/UDP/blob/master/udp.py accessed on 10-5-2018


