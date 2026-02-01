import asyncio
import websockets

async def test_connection():
    uri = "ws://localhost:8000/ws/conversation"
    print(f"🚀 Attempting connection to: {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ BACKEND IS LISTENING (Connection Successful)")
            await websocket.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
