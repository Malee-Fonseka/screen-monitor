import socket
import numpy as np
import cv2
from threading import Thread
from config import SCREEN_PORT, CHUNK_SIZE, HEADER_SIZE
from PIL import Image, ImageTk

class ScreenViewer:
    def __init__(self, canvas, server_ip):
        self.canvas = canvas
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((server_ip, SCREEN_PORT))
        self.running = True
        self.buffer = {}

    def start(self):
        self.thread = Thread(target=self.receive_and_display_screen)
        self.thread.start()
        print("Screen viewer started")

    def receive_and_display_screen(self):
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(CHUNK_SIZE + HEADER_SIZE)
                header = data[:HEADER_SIZE].strip().decode()
                chunk_data = data[HEADER_SIZE:]

                index, total_chunks = map(int, header.split("/"))
                if addr not in self.buffer:
                    self.buffer[addr] = {}

                self.buffer[addr][index] = chunk_data
                if len(self.buffer[addr]) == total_chunks:
                    full_data = b"".join(self.buffer[addr][i] for i in range(total_chunks))
                    frame = np.frombuffer(full_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.display_frame(frame)
                        self.buffer.pop(addr)
                        print(f"Frame received and displayed from {addr}")
            except Exception as e:
                print(f"Error receiving or displaying frame: {e}")

    def display_frame(self, frame):
        # Resize the frame to fit the canvas
        frame_height, frame_width = frame.shape[:2]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        scale_width = canvas_width / frame_width
        scale_height = canvas_height / frame_height
        scale = min(scale_width, scale_height)

        new_width = int(frame_width * scale)
        new_height = int(frame_height * scale)
        resized_frame = cv2.resize(frame, (new_width, new_height))

        # Convert the frame to a format suitable for display on the canvas
        frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        image_tk = ImageTk.PhotoImage(image)

        # Update the canvas with the new frame
        self.canvas.create_image(0, 0, anchor="nw", image=image_tk)
        self.canvas.image = image_tk  # Keep a reference to avoid garbage collection

    def stop(self):
        self.running = False
        self.thread.join()
        self.server_socket.close()
        print("Screen viewer stopped")
