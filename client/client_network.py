import socket
import threading
from config import SERVER_IP, SERVER_PORT

class ClientNetwork:
    def __init__(self, gui):
        self.gui = gui
        self.client_socket = None
        self.running = False

    def connect(self, client_name):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.client_socket.sendall(client_name.encode())
            self.running = True
            self.listener_thread = threading.Thread(target=self.listen_for_commands)
            self.listener_thread.start()
            print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
            return True
        except socket.error:
            self.client_socket = None
            return False

    def send_command(self, command):
        if self.client_socket:
            self.client_socket.sendall(command)
            print(f"Command sent to server: {command}")

    def listen_for_commands(self):
        while self.running:
            try:
                if self.client_socket:
                    command = self.client_socket.recv(1024)
                    print(f"Command received from server: {command}")
                    if command == b"START_SCREEN_SHARE":
                        self.gui.start_screen_share()
                    elif command == b"STOP_SCREEN_SHARE":
                        self.gui.stop_screen_share()
            except socket.error:
                break

    def disconnect(self):
        if self.client_socket:
            self.running = False
            self.client_socket.sendall(b"DISCONNECT")
            self.client_socket.close()
            self.client_socket = None
            self.listener_thread.join()
            print("Disconnected from server")
