import asyncio
from gateway.router import ClusterManager
from gateway.middleware import SecurityFirewall, RateLimiter

class ProxyGateway:
    def __init__(self, ip='127.0.0.1', port=8080):
        self.ip = ip
        self.port = port
        self.router = ClusterManager()
        self.firewall = SecurityFirewall()
        self.limiter = RateLimiter()

    async def pipe_data(self, source_reader, target_writer):
        """Pipes continuous TCP stream between source and destination sockets."""
        try:
            while not source_reader.at_eof():
                chunk = await source_reader.read(8192)
                if not chunk:
                    break
                target_writer.write(chunk)
                await target_writer.drain()
        except Exception:
            pass  # Handle client/server connection resets silently
        finally:
            if not target_writer.is_closing():
                target_writer.close()

    async def _read_http_request(self, reader):
        """Reads the full incoming HTTP request, ensuring full body retrieval."""
        buffer = bytearray()
        
        # Read the initial header block
        chunk = await reader.read(4096)
        if not chunk:
            return b""
        buffer.extend(chunk)
        
        # Locate end of HTTP headers
        header_end = buffer.find(b"\r\n\r\n")
        if header_end == -1:
            return bytes(buffer)
            
        header_text = buffer[:header_end].decode('utf-8', errors='ignore').lower()
        
        # Parse Content-Length to determine if more data needs to be read from socket
        content_length = 0
        for line in header_text.split("\r\n"):
            if line.startswith("content-length:"):
                try:
                    content_length = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
                break
                
        if content_length > 0:
            body_bytes_read = len(buffer) - (header_end + 4)
            while body_bytes_read < content_length:
                remaining = content_length - body_bytes_read
                chunk = await reader.read(min(remaining, 4096))
                if not chunk:
                    break
                buffer.extend(chunk)
                body_bytes_read += len(chunk)
                
        return bytes(buffer)

    async def handle_request(self, client_reader, client_writer):
        """Validates incoming traffic constraints and routes payload to target node."""
        client_info = client_writer.get_extra_info('peername')
        client_ip = client_info[0] if client_info else '127.0.0.1'
        
        # 1. Rate Limiting Validation
        if not await self.limiter.allow_request(client_ip):
            print(f"Rate limit exceeded for IP: {client_ip}")
            client_writer.write(b"HTTP/1.1 429 Too Many Requests\r\nConnection: close\r\n\r\nRate limit exceeded.")
            await client_writer.drain()
            client_writer.close()
            return

        try:
            # 2. Inspect Inbound Stream
            raw_request = await self._read_http_request(client_reader)
            if not raw_request:
                client_writer.close()
                return
                
            payload_text = raw_request.decode('utf-8', errors='ignore')

            if not self.firewall.is_safe(payload_text):
                print(f"WAF intercepted malicious pattern from: {client_ip}")
                client_writer.write(b"HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\nBlocked by WAF constraints.")
                await client_writer.drain()
                client_writer.close()
                return

            # 3. Resolve Microservice Node Routing
            try:
                dest_host, dest_port = await self.router.get_next_healthy_node()
            except Exception as e:
                print(f"Routing failure: {str(e)}")
                client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n502 Bad Gateway")
                await client_writer.drain()
                client_writer.close()
                return

            # 4. Proxy Bidirectional Data Stream
            server_reader, server_writer = await asyncio.open_connection(dest_host, dest_port)
            server_writer.write(raw_request)
            await server_writer.drain()

            await asyncio.gather(
                self.pipe_data(client_reader, server_writer),
                self.pipe_data(server_reader, client_writer)
            )
        except Exception as e:
            print(f"Error handling connection: {e}")
            if not client_writer.is_closing():
                client_writer.close()

    async def start(self):
        # Initialize the background system health worker loop
        asyncio.create_task(self.router.check_infrastructure_health())
        
        server = await asyncio.start_server(self.handle_request, self.ip, self.port)
        print(f"Proxy Gateway listening on http://{self.ip}:{self.port}")
        
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    gateway = ProxyGateway()
    asyncio.run(gateway.start())
