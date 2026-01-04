from fastapi import FastAPI
import socketio
from fastapi.middleware.cors import CORSMiddleware


# Khởi tạo
app = FastAPI(title="WebSocket Chain Communication")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

connections = set()

# Event khi client kết nối
@sio.event
async def connect(sid, environ):
    connections.add(sid)
    print(f"Client connected: {sid}")

# # Event khi client ngắt kết nối
@sio.event
async def disconnect(sid):
    connections.remove(sid)
    print(f"Client disconnected: {sid}")

# Event nhận tin nhắn từ client
@sio.event
async def message(sid, data):
    text = data.get("text", "")
    print(f"Received message from {sid}: {text}")
    
    # Phát tin nhắn đến tất cả client khác
    for conn_sid in connections:
        if conn_sid != sid:
            await sio.emit('broadcast', f'From {sid}: {text}', to=conn_sid)

app.mount("/", socket_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("socketio_text:app", host="0.0.0.0", port=8002, reload=True)
