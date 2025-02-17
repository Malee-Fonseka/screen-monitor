import socket
import threading
from datetime import datetime
from config import SERVER_IP, SERVER_PORT

class ServerNetwork:
    def __init__(self, gui):
        self.gui = gui
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_IP, SERVER_PORT))
        self.server_socket.listen(5)
        self.running = True
        self.connected_clients = {}
        self.history = []

    def start(self):
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

    def run_server(self):
        print("Server is running and waiting for connections...")
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_handler_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_handler_thread.start()
            except socket.error:
                break

    def handle_client(self, client_socket, client_address):
        try:
            client_name = client_socket.recv(1024).decode()
            connected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.connected_clients[client_name] = (client_socket, client_address, connected_time)
            self.gui.master.after(0, self.update_connected_clients_table)
            self.gui.master.after(0, self.update_history_table, client_name, client_address, connected_time, None)
            print(f"Connection from {client_name} ({client_address})")
            # No need to update connection_label here as it's updated in see_screen function now
            while True:
                message = client_socket.recv(1024)
                if message == b"DISCONNECT":
                    self.client_disconnected(client_name)
                    break
        except socket.error:
            self.client_disconnected(client_name)
        finally:
            client_socket.close()

    def send_command_to_client(self, client_name, command):
        if client_name in self.connected_clients:
            client_socket, client_address, _ = self.connected_clients[client_name]
            client_socket.sendall(command)
            print(f"Command '{command.decode()}' sent to {client_name} ({client_address})")

    def update_connected_clients_table(self):
        self.gui.update_connected_clients_table({
            addr: (name, time) for name, (_, addr, time) in self.connected_clients.items()
        })

    def update_history_table(self, client_name, client_address, connected_time, disconnected_time):
        if disconnected_time is None:
            disconnected_time = "N/A"
        self.history.append((client_name, client_address, connected_time, disconnected_time))
        self.gui.update_history_table(self.history)

    def client_disconnected(self, client_name):
        if client_name in self.connected_clients:
            _, client_address, connected_time = self.connected_clients.pop(client_name)
            disconnected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.gui.master.after(0, self.update_history_table, client_name, client_address, connected_time, disconnected_time)
            self.gui.master.after(0, self.update_connected_clients_table)
            print(f"Client {client_name} ({client_address}) disconnected")

    def update_connection_label(self, text):
        self.gui.master.after(0, self.gui.update_connection_label, text)

    def stop(self):
        self.running = False
        self.server_socket.close()
