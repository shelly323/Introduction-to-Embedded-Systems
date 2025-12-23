import socket
import time

class SocketClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = None
        self.is_connected = False

    def connect(self):
        try:
            print(f"connecting to {self.ip}:{self.port} ...")
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            self.client.settimeout(2.0) 
            self.client.connect((self.ip, self.port))
            self.is_connected = True
            print("connected")
        except Exception as e:
            print(f"connect fail: {e}")
            self.is_connected = False

    def send_detection(self, label_name):
        if not self.is_connected:
            self.connect()
            return

        msg = label_name.encode('utf-8')
        self.client.sendall(msg)

    def close(self):
        if self.client:
            self.client.close()
        self.is_connected = False
        print("socket close")