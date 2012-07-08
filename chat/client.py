# Echo client program
import socket
from tkinter import *
from time import sleep
import _thread

HOST = 'localhost'    # The remote host
PORT = 50017              # The same port as used by the server
    

class ChatClient(object):
    def __init__(self):
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sendSocket.connect((HOST, PORT))
        
        sleep(1)
        self.receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiveSocket.connect((HOST, PORT+1))
        
        self.window = Tk()
        self.msg = StringVar()
        self.chatMessages = StringVar()
        
        self.label = Label(self.window, textvariable=self.chatMessages)
        self.entry = Entry(self.window, textvariable=self.msg)
        self.button = Button(self.window, text='go', command=self.sendMsg)
        
        self.label.pack()
        self.entry.pack()
        self.button.pack()
        
        _thread.start_new_thread(self.receiveMessages, ())
    
        self.window.mainloop()
        
        self.sendSocket.close()
        self.receiveSocket.close()
    
    def sendMsg(self):
        msg = self.msg.get()
        print(msg)
        if msg != '':
            self.sendSocket.sendall(bytes(msg, encoding='utf8'))
        
        self.msg.set('')
    
    
    def receiveMessages(self):
        while True:
            data = self.receiveSocket.recv(1024)
            if data != b'':
                print('received', data)
                tmp = self.chatMessages.get()
                tmp = str(data, encoding='utf8') + '\n' + tmp
                self.chatMessages.set(tmp)
    
    #===========================================================================
    # sendSocket.sendall(b'Hello, world')
    # sleep(2)
    # sendSocket.sendall(b'Hello, world2')
    # data = receiveSocket.recv(1024)
    # 
    # print('Received', repr(data))
    #===========================================================================

ChatClient()