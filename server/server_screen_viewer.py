import socket
import numpy as np
import cv2
from threading import Thread
from config import SERVER_IP, SCREEN_PORT, CHUNK_SIZE, HEADER_SIZE

class ScreenViewer:
    def __init__(self, server_ip):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((server_ip, SCREEN_PORT))  # Bind to server's IP and SCREEN_PORT
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
                        cv2.imshow("Screen Viewer", frame)
                        cv2.waitKey(1)
                    self.buffer.pop(addr)
                    print(f"Frame received and displayed from {addr}")
            except Exception as e:
                print(f"Error receiving or displaying frame: {e}")

    def stop(self):
        self.running = False
        self.thread.join()
        self.server_socket.close()
        cv2.destroyAllWindows()
        print("Screen viewer stopped")
