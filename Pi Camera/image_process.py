import cv2
import numpy as np
import time
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)

print("Starting camera stream...")
picam2.start()

try:
    while True:
        start_time = time.time()
        
        # 1. Grab frame from camera
        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # 📸 ADD THIS LINE HERE TO SAVE THE IMAGE FILE:
        cv2.imwrite('/home/projecteng-bd/Supermarket-Inventory-Tracker/Pi Camera/live_view.jpg', frame)
        
        # 2. Your image processing logic goes here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 3. Calculate processing time and FPS
        elapsed = (time.time() - start_time) * 1000  
        fps = 1000 / elapsed if elapsed > 0 else 0
        
        # 4. Clean print statement
        print(f"Cycle Time: {elapsed:.1f}ms | Frame Rate: {fps:.1f} FPS   ", end="\r")
        
        # 5. Artificially cap the loop
        time.sleep(0.1)  


except KeyboardInterrupt:
    print("\nStopping script gracefully via user command.")
        
finally:
    print("Closing camera system.")
    picam2.stop()
