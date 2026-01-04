import asyncio
import sys
import socketio


URL = "http://localhost:8002/"

async def socketio_client(url: str):
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        print("✅ Connected to server")
    
    @sio.event
    async def disconnect():
        print("❌ Disconnected from server")
    
    @sio.event
    async def message(data):
        print(f"[Message] {data}")
    
    @sio.event
    async def broadcast(data):
        print(f"[Broadcast] {data}")
    
    try:
        await sio.connect(url=url)
        
        # Tạo task để nhận input từ stdin
        while True:
            # Đọc input không blocking
            text = await asyncio.to_thread(sys.stdin.readline)
            if not text.strip():
                continue
            
            # Gửi event 'message' tới server
            await sio.emit('message', {"text": text.strip()})
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nDisconnecting...")
        await sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")

def main(url: str):
    try:
        asyncio.run(socketio_client(url))
    except KeyboardInterrupt:
        print("\nClient stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main(URL)