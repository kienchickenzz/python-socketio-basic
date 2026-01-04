import base64
import time

import cv2
import socketio


sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

sio.connect('http://localhost:8002')

# Mở camera
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read() # Đọc frame từ camera
        
        if not ret:
            print("Failed to grab frame")
            break
        
        frame = cv2.resize(frame, (640, 480))
        
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70]) # Chuyển frame sang JPEG
        frame_base64 = base64.b64encode(buffer).decode('utf-8') # Chuyển sang base64
        
        # Gửi frame tới server
        sio.emit('image_data', {
            'image': frame_base64,
            'timestamp': time.time(),
        })
        
        cv2.imshow('Camera Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break
        
except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    cap.release()
    cv2.destroyAllWindows()
    sio.disconnect()
    print("Camera released and disconnected")