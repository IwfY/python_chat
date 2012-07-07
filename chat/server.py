import socket
from time import *
import _thread

toSend = []
outSockets = set()
inSockets = set()

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50017              # Arbitrary non-privileged port

def handleInConnection(inSocket, toSend):
    while True:
        data = inSocket.recv(1024)
        if data != b'':
            print('received', data)
            toSend.append(data)


def handleOutConnection(outSocket, toSend):
    while True:
        sleep(1)
        print('toSend', toSend)
        if len(toSend) > 0:
            msg = toSend[0]
            outSocket.send(msg)
            toSend.remove(msg)

# socket for incoming data
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(1)
s.bind((HOST, PORT))
s.listen(3)

# socket for outgoing data
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.bind((HOST, PORT+1))
s2.listen(3)

while True:    
    conn, addr = s.accept()
    inSockets.add(conn)

    conn2, addr2 = s2.accept()
    outSockets.add(conn2)
    
    _thread.start_new_thread(handleInConnection, (conn, toSend))
    _thread.start_new_thread(handleOutConnection, (conn2, toSend))
    print('Connected by', addr, addr2)
    sleep(0.5)

conn.close()
conn2.close()
