# Echo client program
import socket
from time import sleep

HOST = 'localhost'    # The remote host
PORT = 50017              # The same port as used by the server
sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sendSocket.connect((HOST, PORT))

sleep(0.5)
receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiveSocket.connect((HOST, PORT+1))

sendSocket.sendall(b'Hello, world')
sleep(2)
sendSocket.sendall(b'Hello, world2')
data = receiveSocket.recv(1024)
data2 = receiveSocket.recv(1024)
sendSocket.close()
receiveSocket.close()
print('Received', repr(data), repr(data2))
