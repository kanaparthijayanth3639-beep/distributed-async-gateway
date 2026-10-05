import asyncio

class ClusterManager:
    def __init__(self):
        # Localhost target nodes for our backend servers
        self.servers = [
            {"host": "127.0.0.1", "port": 8001, "active": True},
            {"host": "127.0.0.1", "port": 8002, "active": True}
        ]
        self.current_index = 0

    async def check_infrastructure_health(self):
        """Background loop that continually pings our microservices."""
        while True:
            for server in self.servers:
                try:
                    # Attempt a rapid low-overhead network handshake check
                    reader, writer = await asyncio.open_connection(server["host"], server["port"])
                    writer.close()
                    await writer.wait_closed()
                    
                    if not server["active"]:
                        print(f"[RECOVERY] Server on port {server['port']} is healthy again!")
                        server["active"] = True
                except Exception:
                    if server["active"]:
                        print(f"[ALERT] Server on port {server['port']} went down! Removing from pool.")
                        server["active"] = False
            
            # Re-evaluate the infrastructure landscape every 5 seconds
            await asyncio.sleep(5)

    async def get_next_healthy_node(self):
        """Rotates through active machines using Round-Robin logic."""
        for _ in range(len(self.servers)):
            target = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            
            if target["active"]:
                return target["host"], target["port"]
                
        raise Exception("502 Service Outage: All backend servers are completely down!")
