import tkinter as tk
from tkinter import messagebox
from .client_network import ClientNetwork
from .client_screen_send import ScreenSender

class ClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Client")
        self.master.geometry("600x200")
        self.master.resizable(False, False)

        tk.Label(master, text="Client Name:", font=("Helvetica", 12)).pack(anchor="nw", padx=10, pady=(10, 0))
        self.client_name_entry = tk.Entry(master, font=("Helvetica", 12))
        self.client_name_entry.pack(anchor="nw", padx=10, pady=(0, 10))

        self.client_status_label = tk.Label(master, text="Client Status: Disconnected", font=("Helvetica", 14))
        self.client_status_label.pack(anchor="nw", padx=10, pady=(10, 0))

        button_frame = tk.Frame(master)
        button_frame.pack(anchor="w", padx=10, pady=10)

        self.connect_button = tk.Button(button_frame, text="Connect to Server", command=self.connect_to_server, width=20)
        self.connect_button.pack(side="left", padx=5)

        self.disconnect_button = tk.Button(button_frame, text="Disconnect from Server", command=self.disconnect_from_server, width=20)
        self.disconnect_button.pack(side="left", padx=5)

        self.client_network = ClientNetwork(self)
        self.screen_sender = None
        self.is_connected = False
        self.update_button_states()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect_to_server(self):
        client_name = self.client_name_entry.get().strip()
        if not client_name:
            messagebox.showerror("Connection Error", "Client Name cannot be empty")
            return

        if not self.is_connected:
            if self.client_network.connect(client_name):
                print(f"Connected to server with client name: {client_name}")
                self.client_status_label.config(text="Client Status: Connected")
                self.is_connected = True
                self.update_button_states()
            else:
                messagebox.showerror("Connection Error", "Server is not active")

    def disconnect_from_server(self):
        if self.is_connected:
            self.client_network.disconnect()
            print("Disconnected from server")
            self.client_status_label.config(text="Client Status: Disconnected")
            self.is_connected = False
            self.update_button_states()

    def start_screen_share(self):
        if self.is_connected and not self.screen_sender:
            self.screen_sender = ScreenSender()
            self.screen_sender.start()
            self.client_network.send_command(b"START_SCREEN_SHARE")
            print("Start screen share command sent")

    def stop_screen_share(self):
        if self.is_connected and self.screen_sender:
            self.client_network.send_command(b"STOP_SCREEN_SHARE")
            self.screen_sender.stop()
            self.screen_sender = None
            print("Stop screen share command sent")

    def update_button_states(self):
        if self.is_connected:
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
        else:
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")

    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_server()
        if self.screen_sender:
            self.stop_screen_share()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()
