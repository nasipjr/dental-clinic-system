import webview
import threading
import time
import socket
import sys
from app import app

def find_free_port(start_port=5000):
    port = start_port
    while port < 6000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
            port += 1
    return start_port

PORT = find_free_port(5000)

def start_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    time.sleep(1.5)
    
    webview.create_window(
        title='Clinic MS',
        url=f'http://127.0.0.1:{PORT}',
        width=1280,
        height=800,
        min_size=(1024, 768)
    )
    webview.start()
