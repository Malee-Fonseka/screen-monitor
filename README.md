# LAN-Screen-Monitoring-Application

### Overview  
A basic client-server apllication for private Local Area Networks to monitor the screens of the connected devices.  

### Features  
1. Multi Client Connection
2. Real-Time Screen Sharing

### Limitations
ToDo

## Notes for team
### Configuration
1. Create a python virtual environment.
2. Install the following dependencies
```python
pip install opencv-python
pip install pyautogui
pip install tk
pip install pillow

```
3. Create the `config.py` file
```python
# config.py
# Network settings
SERVER_IP = "your_ip_address"
SERVER_PORT = 9999
SCREEN_PORT = 9998

# Screen settings
FRAME_WIDTH = 1366
FRAME_HEIGHT = 768
QUALITY = 90

# UDP packet settings
CHUNK_SIZE = 60000  
HEADER_SIZE = 20

```
4. Run the application in dedicated terminals. (If running on a single device)
```
python -m client.client_gui
python -m server.server_gui
```
### To Develop
1. Combine the viewer screen with GUI (Server)
2. Use multi-threading to enhance the efficiency of the application
3. Screen freezing feature is not yet implemented
