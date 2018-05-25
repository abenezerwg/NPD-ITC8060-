# NPD-ITC8060-

                                        --- NETWORK PROTOCOL APP README ---

* This is a readme text file guide how to use the Network Protocol chat room application that me Tedel Baca, Krishna Vaishnav and Abenezer Berhanu Weldegiorgis developed for Network Protocol class which was lectured by professor Olaf Maennel.

The files of this application can be downloaded from the following link: https://github.com/Abenaman/NPD-ITC8060-

This application was tested in Linux environment and this guide will be for Linux environment but this application can run in Windows aswell.

To run our program we need to install with "pip install" command in Linux the "pgpy" library


This program has a CLI and is compatible with Python3.5 so to run it we have the following procedure:

1. In Linux terminal write the following command: $python3.5 message.py

2. In our terminal we will see a new screen with an output: "Please input peer IP to connet to chat room:", and waits for our input so here we put our IP address in the network so that we can communicate in network with other nodes

3.We get an output: "Please input your email:", and here we input our email address

4. We get an output: "Please input link cost of the node:", and here we input the cost of our node

5. After the first four steps a new terminal window will appear with the message: Welcome to the chat room. Here we have 6 options which we can choose for our chat application:

Option !-1): For Private msg - Here we can send private messages between nodes. To do this we choose the destination address in "Input Destination Address:" field and then we write our message

Option !-2): For Group message: - Here we can send broadcast message. We just input our messages and send it

Option !-3): For File Transfer: 

Option !-4): List Users: When we choose this option, list of connected users to us will appear

Option !-5): Show Routing Table: Here we show our current routing table which shows: the time when we ran the command, the destination address of the node, the link address of the node, and the cost for the node

Option !-6): We close the application
