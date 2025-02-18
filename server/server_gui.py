import tkinter as tk
from tkinter import ttk
import threading
import cv2
from PIL import Image, ImageTk

from config import SERVER_IP, FRAME_WIDTH, FRAME_HEIGHT
from server.server_screen_viewer import ScreenViewer
from .server_network import ServerNetwork

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Server")
        self.master.geometry("1280x800")
        self.master.resizable(False, False)

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        # Create frames for tabs
        self.config_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.monitor_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.config_tab, text="Server Configuration")
        self.notebook.add(self.history_tab, text="History & Connected Clients")
        self.notebook.add(self.monitor_tab, text="Client Monitoring")

        # Server Configuration tab content
        self.server_status_label = tk.Label(self.config_tab, text="Server Status: Active", font=("Helvetica", 12))
        self.server_status_label.pack(anchor="nw", pady=10)

        # History & Connected Clients tab content
        self.connection_label = tk.Label(self.history_tab, text="No clients connected", font=("Helvetica", 12))
        self.connection_label.pack(anchor="nw", pady=10)

        self.connected_clients_history_frame = ttk.LabelFrame(self.history_tab, text="Currently Connected Clients", padding="10")
        self.connected_clients_history_frame.pack(anchor="nw", fill="x", padx=10, pady=(10, 0))

        self.connected_clients_history_table = ttk.Treeview(self.connected_clients_history_frame, columns=("Name"), show='headings')
        self.connected_clients_history_table.heading("Name", text="Client Name")
        self.connected_clients_history_table.column("Name", width=200)
        self.connected_clients_history_table.pack(fill="x", expand=False)

        self.history_frame = ttk.LabelFrame(self.history_tab, text="Connection History", padding="10")
        self.history_frame.pack(anchor="nw", fill="x", padx=10, pady=(10, 10))

        self.history_table = ttk.Treeview(self.history_frame, columns=("Name", "IP Address", "Connected Time", "Disconnected Time"), show='headings')
        self.history_table.heading("Name", text="Client Name")
        self.history_table.heading("IP Address", text="IP Address")
        self.history_table.heading("Connected Time", text="Connected Time")
        self.history_table.heading("Disconnected Time", text="Disconnected Time")
        self.history_table.pack(fill="both", expand=True)

        # Disable selection for history tables
        self.connected_clients_history_table.bind("<Button-1>", self.disable_selection)
        self.history_table.bind("<Button-1>", self.disable_selection)

        # Client Monitoring tab content
        self.left_frame = tk.Frame(self.monitor_tab, width=384, height=800)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.left_frame.pack_propagate(False)

        # Subsections in left_frame
        self.left_frame_label = tk.Label(self.left_frame, text="Viewer Configurations", font=("Helvetica", 12))
        self.left_frame_label.pack(anchor="nw", pady=10)

        self.client_list_frame = tk.Frame(self.left_frame)
        self.client_list_frame.pack(fill="x", pady=(0, 10))

        self.selected_client_frame = tk.Frame(self.left_frame)
        self.selected_client_frame.pack(fill="x", pady=(0, 10))

        self.control_panel_frame = tk.Frame(self.left_frame)
        self.control_panel_frame.pack(fill="x", pady=(0, 10))

        self.connected_clients_table = ttk.Treeview(self.client_list_frame, columns=("Name"), show='headings')
        self.connected_clients_table.heading("Name", text="Client Name")
        self.connected_clients_table.column("Name", width=200)
        self.connected_clients_table.pack(fill="x", expand=False)

        self.selected_client_label = tk.Label(self.selected_client_frame, text="No client selected", font=("Helvetica", 12))
        self.selected_client_label.pack(anchor="nw", pady=10)

        self.see_screen_button = tk.Button(self.selected_client_frame, text="See Screen", command=self.see_screen)
        self.see_screen_button.pack(anchor="nw", pady=5)

        self.stop_view_screen_button = tk.Button(self.selected_client_frame, text="Stop View Screen", command=self.stop_view_screen)
        self.stop_view_screen_button.pack(anchor="nw", pady=5)

        self.control_panel_label = tk.Label(self.control_panel_frame, text="Control Panel", font=("Helvetica", 12))
        self.control_panel_label.pack(anchor="nw", pady=10)

        # Screen Viewer section
        
        self.screen_viewer_frame = tk.Frame(self.monitor_tab, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.screen_viewer_frame.pack(side="left", padx=10, pady=10)
        self.screen_viewer_frame.pack_propagate(False)

        self.screen_viewer_frame_label = tk.Label(self.screen_viewer_frame, text="Screen Viewer", font=("Helvetica", 12))
        self.screen_viewer_frame_label.pack(anchor="nw", pady=10)

        # Create canvas for screen viewer
        self.canvas = tk.Canvas(self.screen_viewer_frame, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.canvas.pack(fill="both", expand=True)

        self.server_network = ServerNetwork(self)
        self.server_network.start()

        self.screen_viewer = None

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def disable_selection(self, event):
        return "break"

    def update_connected_clients_table(self, clients):
        for row in self.connected_clients_table.get_children():
            self.connected_clients_table.delete(row)

        for client_address, (client_name, connected_time) in clients.items():
            self.connected_clients_table.insert("", "end", values=(client_name,))

        # Update the connected clients history table as well
        for row in self.connected_clients_history_table.get_children():
            self.connected_clients_history_table.delete(row)

        for client_address, (client_name, connected_time) in clients.items():
            self.connected_clients_history_table.insert("", "end", values=(client_name,))

    def update_history_table(self, history):
        for row in self.history_table.get_children():
            self.history_table.delete(row)

        for client_name, client_address, connected_time, disconnected_time in history:
            self.history_table.insert("", "end", values=(client_name, client_address, connected_time, disconnected_time))

    def update_connection_label(self, text):
        def update():
            self.connection_label.config(text=text)
        self.master.after(0, update)

    def see_screen(self):
        selected_item = self.connected_clients_table.selection()
        if selected_item:
            client_info = self.connected_clients_table.item(selected_item)["values"]
            client_name = client_info[0]
            self.server_network.send_command_to_client(client_name, b"START_SCREEN_SHARE")
            self.start_screen_viewer(SERVER_IP)  # Pass server's IP to start the screen viewer
            print(f"See screen request sent to {client_name}")
            self.update_connection_label(f"Currently viewing: {client_name}")
            self.selected_client_label.config(text=f"Currently selected: {client_name}")

    def stop_view_screen(self):
        selected_item = self.connected_clients_table.selection()
        if selected_item:
            client_info = self.connected_clients_table.item(selected_item)["values"]
            client_name = client_info[0]
            self.server_network.send_command_to_client(client_name, b"STOP_SCREEN_SHARE")
            if self.screen_viewer:
                self.screen_viewer.stop()
                self.screen_viewer = None
            print(f"Stop view screen request sent to {client_name}")
            self.see_screen_button.config(state="normal")  # Re-enable the See Screen button
            self.stop_view_screen_button.config(state="disabled")
            self.update_connection_label("No clients connected")
            self.selected_client_label.config(text="No client selected")

    def start_screen_viewer(self, server_ip):
        if not self.screen_viewer:
            self.screen_viewer = ScreenViewer(self.canvas, server_ip)  # Initialize ScreenViewer with the canvas and server's IP
            self.screen_viewer.start()
            self.see_screen_button.config(state="disabled")
            self.stop_view_screen_button.config(state="normal")
            print("Screen viewer started")

    def on_closing(self):
        self.server_network.stop()
        if self.screen_viewer:
            self.screen_viewer.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()
