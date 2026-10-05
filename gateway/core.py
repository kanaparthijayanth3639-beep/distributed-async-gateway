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
        """Streams continuous network packets between client browser and backend servers."""
        try:
            while not source_reader.at_eof():
                chunk = await source_reader.read(8192)
                if not chunk:
                    break
                target_writer.write(chunk)
                await target_writer.drain()
        except Exception:
            pass # Silent ignore for dropped client tabs or connection resets
        finally:
            target_writer.close()

    async def handle_request(self, client_reader, client_writer):
        """Validates security boundaries and tunnels traffic across open sockets."""
        client_info = client_writer.get_extra_info('peername')
        
        # 1. DoS Mitigation Check
        if not await self.limiter.allow_request(client_info[0]):
            print(f"[SECURITY] Rate limit hit for incoming IP: {client_info[0]}")
            client_writer.write(b"HTTP/1.1 429 Too Many Requests\r\nConnection: close\r\n\r\nRate limit hit.")
            await client_writer.drain()
            client_writer.close()
            return

        try:
            # 2. Extract and inspect initial text headers (WAF Protection)
            headers = await client_reader.read(4096)
            payload_text = headers.decode('utf-8', errors='ignore')

            if not self.firewall.is_safe(payload_text):
                print(f"[SECURITY WARNING] Blocked suspicious request packet from {client_info}")
                client_writer.write(b"HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\nRequest blocked by WAF.")
                await client_writer.drain()
                client_writer.close()
                return

            # 3. Fetch Next Operational Application Server Node
            try:
                dest_host, dest_port = await self.router.get_next_healthy_node()
            except Exception as routing_error:
                print(f"[CRITICAL OUTAGE] {routing_error}")
                client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n502 Bad Gateway")
                await client_writer.drain()
                client_writer.close()
                return

            print(f"[PROXY ROUTE] Tunneling request data stream -> {dest_host}:{dest_port}")

            # 4. Bind conduits and stream data asynchronously
            server_reader, server_writer = await asyncio.open_connection(dest_host, dest_port)
            server_writer.write(headers)
            await server_writer.drain()

            await asyncio.gather(
                self.pipe_data(client_reader, server_writer),
                self.pipe_data(server_reader, client_writer)
            )
        except Exception as system_error:
            print(f"[SYSTEM ERROR] Connection processing failed: {system_error}")
            if not client_writer.is_closing():
                client_writer.close()

    async def start(self):
        # Fire up our active background health checker daemon
        asyncio.create_task(self.router.check_infrastructure_health())
        
        server = await asyncio.start_server(self.handle_request, self.ip, self.port)
        print(f"[*] Custom API Gateway successfully launched on http://{self.ip}:{self.port}")
        
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    gateway = ProxyGateway()
    asyncio.run(gateway.start())
