import asyncio
import os
import json

# Grab network parameters dynamically from the operating environment variables
SERVER_ID = os.getenv("SERVER_ID", "NODE_DEV_LOCAL")
PORT = int(os.getenv("PORT", 8001))

async def process_incoming_stream(reader, writer):
    """Processes proxied gateway connections and serves data payloads."""
    try:
        # Read the incoming forward headers passed from our proxy engine
        await reader.read(4096)
        
        # Human custom touch: Let's make it look like a real production data api response!
        mock_data = {
            "status": "online",
            "served_by": SERVER_ID,
            "region": "hyd-west-1",
            "message": "Cluster transaction completed successfully."
        }
        
        json_payload = json.dumps(mock_data, indent=2)
        
        # Build standard HTTP/1.1 response string with our custom dataset
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(json_payload)}\r\n"
            "Connection: close\r\n\r\n"
            f"{json_payload}"
        )
        
        writer.write(http_response.encode('utf-8'))
        await writer.drain()
    except Exception as e:
        print(f"[ERROR] Microservice node transaction crashed: {e}")
    finally:
        writer.close()

async def start_node():
    server = await asyncio.start_server(process_incoming_stream, '127.0.0.1', PORT)
    print(f"[NODE STARTED] Microservice cluster server {SERVER_ID} active on port {PORT}...")
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(start_node())
