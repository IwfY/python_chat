import socket
from time import *
import _thread

toSend = []
outSockets = set()
inSockets = set()

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port

class Message(object):
    def __init__(self, message, receivers):
        self.message = bytes(message, 'utf8')
        self.receivers = set()
        self.receivers = self.receivers.union(set(receivers))
        print('Message_init: ', self.message, self.receivers)
    
    def getReceivers(self):
        return self.receivers
    
    def getMessage(self):
        '''return message as utf8 encoded byte data'''
        return self.message
    
    def removeReceiver(self, receiver):
        if receiver in self.receivers:
            self.receivers.remove(receiver)
    
    def hasPendingReceivers(self):
        if len(self.receivers) == 0:
            return True
        return False


class SendBuffer(object):
    def __init__(self, connectionManager):
        self.messages = []
        self.connectionManager = connectionManager
        
        _thread.start_new_thread(self.collectMessageGarbage, ())
    
    def addMessage(self, message):
        self.messages.append(
                Message(message, self.connectionManager.getConnections()))
    
    def getMessages(self):
        return self.messages
    
    def collectMessageGarbage(self):
        while True:
            for message in self.messages:
                if not message.hasPendingReceivers():
                    print('SendBuffer_gc: removed', message.getMessage())
                    self.messages.remove(message)
            sleep(1)
    
    def removeReceiverFromMessages(self, receiver):
        for message in self.messages:
            message.removeReceiver(receiver)


class ConnectionManager(object):
    '''manage a set of client connections'''
    
    def __init__(self):
        self.connections = set()
        
        _thread.start_new_thread(self.collectConnectionGarbage, ())
    
    def addConnection(self, connection):
        self.connections.add(connection)
    
    def getConnections(self):
        return self.connections
    
    def getConnectionByID(self, iD):
        for connection in self.connections:
            if connection.connectionID == iD:
                return connection
        return None
    
    def collectConnectionGarbage(self):
        while True:
            toRemove = []
            for connection in self.connections:
                if not connection.isAlive():
                    print('ConnectionManager_gc: removed', connection)
                    toRemove.append(connection)
                    #self.connections.remove(connection)
            for connection in toRemove:
                self.connections.remove(connection)
            sleep(0.5)


class ClientConnection(object):
    lastID = 0
    def __init__(self, receiveSocket, sendSocket, buffer):
        self.connectionID = ClientConnection.lastID + 1
        ClientConnection.lastID += 1
        self.alive = True
        
        self.sendSocket = sendSocket
        self.receiveSocket = receiveSocket
        self.buffer = buffer
        
        _thread.start_new_thread(self.handleInConnection, ())
        _thread.start_new_thread(self.handleOutConnection, ())        
    

    def handleInConnection(self):
        while self.alive:
            data = self.receiveSocket.recv(1024)
            print('received', data)
            data = str(data, 'utf8')
            if data == 'CMD:CLOSE':
                self.stop()
            elif data != '':
                self.buffer.addMessage(data)
    
    
    def handleOutConnection(self):
        while self.alive:
            sleep(0.5)
            for message in self.buffer.getMessages():
                if self in message.getReceivers():
                    self.sendSocket.sendall(message.getMessage())
                    message.removeReceiver(self)
    
    def isAlive(self):
        return self.alive
    
    def stop(self):
        self.alive = False
        self.buffer.removeReceiverFromMessages(self)
        sleep(1)
        self.sendSocket.close()
        self.receiveSocket.close()


class ChatServer(object):
    def __init__(self):
        self.connectionManager = ConnectionManager()
        self.buffer = SendBuffer(self.connectionManager)
        
        self.run()
    
    def run(self):
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
            conn2, addr2 = s2.accept()
            
            self.connectionManager.addConnection(
                    ClientConnection(conn, conn2, self.buffer))
            print('Connected by', addr, addr2)
            sleep(0.5)
        
        s.close()
        s2.close()

ChatServer()
