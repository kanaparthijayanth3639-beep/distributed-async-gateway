import asyncio
import os
import json

SERVER_ID = os.getenv("SERVER_ID", "NODE_DEV_LOCAL")
PORT = int(os.getenv("PORT", 8001))

async def process_incoming_stream(reader, writer):
    """Processes reverse-proxied request payloads and yields structured responses."""
    try:
        await reader.read(4096)
        
        mock_data = {
            "status": "healthy",
            "node_id": SERVER_ID,
            "region": "local-cluster-1",
            "execution_status": "success"
        }
        
        json_payload = json.dumps(mock_data, indent=2)
        
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
        print(f"Microservice transaction error: {e}")
    finally:
        writer.close()

async def start_node():
    server = await asyncio.start_server(process_incoming_stream, '127.0.0.1', PORT)
    print(f"Application node {SERVER_ID} bound to port {PORT}")
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(start_node())
