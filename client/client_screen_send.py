import socket
import pyautogui
import numpy as np
import cv2
from threading import Thread
from config import SERVER_IP, SCREEN_PORT, FRAME_WIDTH, FRAME_HEIGHT, QUALITY, CHUNK_SIZE, HEADER_SIZE

class ScreenSender:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (SERVER_IP, SCREEN_PORT)
        self.running = True

    def start(self):
        self.thread = Thread(target=self.capture_and_send_screen)
        self.thread.start()
        print("Screen capturing and sending started")

    def capture_and_send_screen(self):
        while self.running:
            screen = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY]
            _, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
            data = encoded_frame.tobytes()

            total_chunks = (len(data) // CHUNK_SIZE) + 1
            for i in range(total_chunks):
                chunk = data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
                header = f"{i}/{total_chunks}".encode().ljust(HEADER_SIZE)
                self.client_socket.sendto(header + chunk, self.server_address)
                print(f"Sent chunk {i + 1}/{total_chunks}")

    def stop(self):
        self.running = False
        self.thread.join()
        print("Screen capturing and sending stopped")
