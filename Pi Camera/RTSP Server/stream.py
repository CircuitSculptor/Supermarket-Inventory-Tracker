import cv2
import time
from picamera2 import Picamera2
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import socket

# 1. Initialize the Pi Camera
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# Global variables for sharing frames safely between threads
latest_frame = None
frame_lock = threading.Lock()

port = 5000  # Port for the HTTP server

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't actually establish a connection, but triggers 
        # the OS to find the interface used to route to the internet.
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback to localhost if not connected to a network
    finally:
        s.close()
    return IP

# 2. Setup the Streaming Request Handler
class CamStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global latest_frame
        if self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    with frame_lock:
                        if latest_frame is None:
                            time.sleep(0.01)
                            continue
                        # Encode raw frame to JPEG format bytes
                        ret, buffer = cv2.imencode('.jpg', latest_frame)
                        if not ret:
                            continue
                        frame_bytes = buffer.tobytes()

                    # Write MJPEG boundary headers and raw image data to the network stream
                    self.wfile.write(b'--frame\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame_bytes)))
                    self.end_headers()
                    self.wfile.write(frame_bytes)
                    self.wfile.write(b'\r\n')
                    time.sleep(0.04) # Cap streaming delivery around ~25 FPS
                    # 0.04 (20mbps) | 0.02 (40mbps) | 0.01 (60mbps)
            except Exception as e:
                pass
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate background threads."""
    allow_reuse_address = True

# 3. Main Frame Processing Loop Function
def capture_loop():
    global latest_frame
    print("Starting processing loop...")
    try:
        while True:
            start_time = time.time()
            
            # Grab raw frame data array
            frame_rgb = picam2.capture_array()
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
            # --- YOUR IMAGE PROCESSING LOGIC GOES HERE ---
            # You can perform edge detection, tracking, or color filtering right here
            
            # Share the frame securely with the streaming server
            with frame_lock:
                latest_frame = frame.copy()
            
            # Keep processing loop pacing under steady control
            elapsed = (time.time() - start_time) * 1000
            time.sleep(max(0.01, 0.033 - (elapsed / 1000.0)))
    except KeyboardInterrupt:
        print("\nStopping capture thread.")

if __name__ == '__main__':
    # Start the server on your laptop hotspot interface (Port 5000)
    server_address = (get_ip_address(), port)
    httpd = ThreadedHTTPServer(server_address, CamStreamHandler)

    
    # Run the stream frame handler loop function in a separate background daemon thread
    process_thread = threading.Thread(target=capture_loop, daemon=True)
    process_thread.start()
    
    print(f"Server active! Network feed path available at http://{get_ip_address()}:{port}/video_feed")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down streaming engine safely.")
    finally:
        picam2.stop()
        httpd.server_close()
