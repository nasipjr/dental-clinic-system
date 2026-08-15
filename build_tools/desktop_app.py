import webview
import threading
import time
import socket
import sys
import os

# Set base dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)

def wait_for_server(host="127.0.0.1", port=PORT, timeout=15.0):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((host, port)) == 0:
                    time.sleep(0.3)  # Brief delay to guarantee Flask worker readiness
                    return True
        except Exception:
            pass
        time.sleep(0.1)
    return False

if __name__ == '__main__':
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    # Wait until Flask server is active and accepting TCP connections
    wait_for_server("127.0.0.1", PORT)
    
    webview.create_window(
        title='Dental Clinic MS - نظام إدارة عيادة الأسنان',
        url=f'http://127.0.0.1:{PORT}',
        width=1280,
        height=800,
        min_size=(1024, 768)
    )
    webview.start(gui='edge')
