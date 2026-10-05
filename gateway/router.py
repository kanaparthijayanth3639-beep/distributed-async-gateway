import asyncio

class ClusterManager:
    def __init__(self):
        # Target internal app node registration mapping
        self.servers = [
            {"host": "127.0.0.1", "port": 8001, "active": True},
            {"host": "127.0.0.1", "port": 8002, "active": True}
        ]
        self.current_index = 0

    async def check_infrastructure_health(self):
        """Asynchronous background worker polling backend pool status updates."""
        while True:
            for server in self.servers:
                try:
                    # Execute rapid connection handshake evaluation
                    reader, writer = await asyncio.open_connection(server["host"], server["port"])
                    writer.close()
                    await writer.wait_closed()
                    
                    if not server["active"]:
                        print(f"Node recovery detected on port: {server['port']}")
                        server["active"] = True
                except Exception:
                    if server["active"]:
                        print(f"Node failure detected on port: {server['port']}. Evicting from pool.")
                        server["active"] = False
            
            await asyncio.sleep(5)

    async def get_next_healthy_node(self):
        """Resolves target backend node using a Round-Robin pattern selection."""
        for _ in range(len(self.servers)):
            target = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            
            if target["active"]:
                return target["host"], target["port"]
                
        raise Exception("All backend cluster services are down.")
