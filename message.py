
import threading
import time
import socket
import struct

VERSION_OFF     = 0
IHL_OFF         = VERSION_OFF
DSCP_OFF        = IHL_OFF + 1
ECN_OFF         = DSCP_OFF
LENGTH_OFF      = DSCP_OFF + 1
ID_OFF          = LENGTH_OFF + 2
FLAGS_OFF       = ID_OFF + 2
OFF_OFF         = FLAGS_OFF
TTL_OFF         = OFF_OFF + 2
PROTOCOL_OFF    = TTL_OFF + 1
IP_CHECKSUM_OFF = PROTOCOL_OFF + 1
SRC_IP_OFF      = IP_CHECKSUM_OFF + 2
DEST_IP_OFF     = SRC_IP_OFF + 4
SRC_PORT_OFF    = DEST_IP_OFF + 4
DEST_PORT_OFF   = SRC_PORT_OFF + 2
UDP_LEN_OFF     = DEST_PORT_OFF + 2
UDP_CHECKSUM_OFF= UDP_LEN_OFF + 2
DATA_OFF        = UDP_CHECKSUM_OFF + 2

IP_PACKET_OFF   = VERSION_OFF
UDP_PACKET_OFF  = SRC_PORT_OFF

def parse(data):
	packet = {}
	packet['version']       = data[VERSION_OFF] >> 4
	packet['IHL']           = data[IHL_OFF] & 0x0F
	packet['DSCP']          = data[DSCP_OFF] >> 2
	packet['ECN']           = data[ECN_OFF] & 0x03
	packet['length']        = (data[LENGTH_OFF] << 8) + data[LENGTH_OFF + 1]
	packet['Identification']= (data[ID_OFF] << 8) + data[ID_OFF + 1]
	packet['Flags']         = data[FLAGS_OFF] >> 5
	packet['Offset']        = ((data[OFF_OFF] & 0b11111) << 8) + data[OFF_OFF + 1]
	packet['TTL']           = data[TTL_OFF]
	packet['Protocol']      = data[PROTOCOL_OFF]
	packet['Checksum']      = (data[IP_CHECKSUM_OFF] << 8) + data[IP_CHECKSUM_OFF + 1]
	packet['src_ip']        = '.'.join(list(map(str, [data[x] for x in range(SRC_IP_OFF, SRC_IP_OFF + 4)])))
	packet['dest_ip']       = '.'.join(list(map(str, [data[x] for x in range(DEST_IP_OFF, DEST_IP_OFF + 4)])))
	packet['src_port']      = (data[SRC_PORT_OFF] << 8) + data[SRC_PORT_OFF + 1]
	packet['dest_port']     = (data[DEST_PORT_OFF] << 8) + data[DEST_PORT_OFF + 1]
	packet['udp_length']    = (data[UDP_LEN_OFF] << 8) + data[UDP_LEN_OFF + 1]
	packet['UDP_checksum']  = (data[UDP_CHECKSUM_OFF] << 8) + data[UDP_CHECKSUM_OFF + 1]
	packet['data']          = ''.join(list(map(chr, [data[DATA_OFF + x] for x in range(0, packet['udp_length'] - 8)])))

	return packet

def recver(_socket, listen):
	
	zero = 0
	protocol = 17
	_socket.bind(("", listen))
	while True:
		get_msg, sender_ip = _socket.recvfrom(1024)
		#print(get_msg)
		packet = parse(get_msg)
		ip_addr = struct.pack('!8B', *[get_msg[x] for x in range(SRC_IP_OFF, SRC_IP_OFF + 8)])
		udp_psuedo = struct.pack('!BB5H', zero, protocol, packet['udp_length'], packet['src_port'], packet['dest_port'], packet['udp_length'], 0)
		verify = verify_checksum(ip_addr + udp_psuedo + bytes(packet['data'].encode('utf-8')), packet['UDP_checksum'])
		if verify == 0xFFFF:
			print("\n\nsender:%s\nMessage content:%s\n" % (sender_ip[0], packet['data']))
			time.sleep(0.1)
		else:
			print('Checksum Error!Packet is discarded')
		


def sender(_socket, dest_addr):
	src_ip, dest_ip = ip2int(dest_addr[0]), ip2int(dest_addr[0])
	src_ip = struct.pack('!4B', *src_ip)
	dest_ip = struct.pack('!4B', *dest_ip)
	dest_port = dest_addr[1]
	src_port = dest_addr[1]
	protocol = socket.IPPROTO_UDP 
	zero=0
	while True:
		send_msg = input("Enter Message ")
		if type(send_msg) != bytes:
			send_msg = bytes(send_msg.encode('utf-8'))
		data_len = len(send_msg)
		udp_length = 8 + len(send_msg)
		
		checksum = 0
    #Check the type of data
		pseudo_header = struct.pack('!BBH', zero, protocol, udp_length)
		pseudo_header = src_ip + dest_ip + pseudo_header
		udp_header = struct.pack('!4H',src_port,dest_port, udp_length, checksum)
		checksum = checksum_func(pseudo_header + udp_header + send_msg)
		udp_header = struct.pack('!4H',src_port,dest_port, udp_length, checksum)
		_socket.sendto(udp_header + send_msg, dest_addr)
def ip2int(ip_addr):
	if ip_addr == 'localhost':
		ip_addr = '127.0.0.1'
	return [int(x) for x in ip_addr.split('.')]
def verify_checksum(data, checksum):
    data_len = len(data)
    if (data_len%2) == 1:
        data_len += 1
        data += struct.pack('!B', 0)
    
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i + 1])
        checksum += w
        checksum = (checksum >> 16) + (checksum & 0xFFFF)

    return checksum

def checksum_func(data):
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

def udp_segment(data):																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																		
     src_port, dest_port, size = struct.unpack('! H H 2x H', data[:8])
     return src_port, dest_port, size, data[8:]  

if __name__ == '__main__':
	listen_port = int(input("Enter listening Port: "))
	send_to_addr = input("The other's IP: ")
	send_to_port = int(input("Enter others Port: "))

	# Create socket
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.SOCK_DGRAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

	#  Create receive thread
	t_recv = threading.Thread(target=recver, args=(serverSocket, listen_port))
	t_recv.start()

	# Create Thread
	t_send = threading.Thread(target=sender, args=(serverSocket, (send_to_addr,send_to_port)))
	t_send.start()