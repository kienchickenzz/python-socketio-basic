import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="WebSocket Chain Communication")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

connections = set()

@sio.event
async def connect(sid, environ):
    connections.add(sid)
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    connections.remove(sid)
    print(f"Client disconnected: {sid}")

@sio.event
async def image_data(sid, data):
    """
    Nhận file ảnh trực tiếp
    """
    try:
        image_base64 = data.get('image', '')

        # Phát ảnh đến tất cả client khác
        receivers = [conn_sid for conn_sid in connections if conn_sid != sid]

        for conn_sid in receivers:
            await sio.emit('image_data', {
                'image': image_base64,
                'format': 'base64',
                'sender': sid
            }, to=conn_sid)

    except Exception as e:
        print(f"[SERVER ERROR] Error processing image file from {sid}: {e}")
        import traceback
        traceback.print_exc()

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
    uvicorn.run("socketio_image:app", host="0.0.0.0", port=8002, reload=True)
