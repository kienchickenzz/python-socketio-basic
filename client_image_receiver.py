import base64
from queue import Queue, Empty, Full

import socketio
import cv2
import numpy as np


sio = socketio.Client()

frame_queue: Queue = Queue(maxsize=1)

# Sự kiện khi nhận được ảnh
@sio.event
def image_data(data):

    image_data = data.get('image', '')
    sender = data.get('sender', 'unknown')

    # Chuyển base64 thành numpy array
    try:
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            # Non-blocking put: nếu queue đầy, bỏ qua frame cũ
            try:
                frame_queue.put_nowait((frame, sender))
            except Full:
                pass  # Frame cũ bị discard, giữ frame mới

    except Exception:
        import traceback
        traceback.print_exc()

# Sự kiện khi kết nối
@sio.event
def connect():
    print("Connected to server")

# Sự kiện khi ngắt kết nối
@sio.event
def disconnect():
    print("Disconnected from server")

sio.connect('http://localhost:8002')

# Vòng lặp chính để hiển thị frames
try:
    while True:
        # Lấy frame từ queue
        try:
            frame, sender = frame_queue.get_nowait()
            cv2.imshow(f'Stream from {sender}', frame)
            frame_queue.task_done()  # Đánh dấu đã xử lý
        except Empty:
            # Không có frame mới, hiển thị màn hình đen hoặc chờ
            pass

        # Chờ 1ms và kiểm tra phím
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break

except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    # Dọn dẹp
    sio.disconnect()
    cv2.destroyAllWindows()
    print("Disconnected and closed")
