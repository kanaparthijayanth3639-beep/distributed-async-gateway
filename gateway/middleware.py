import time
from collections import defaultdict

class SecurityFirewall:
    def __init__(self):
        # Target user-agents to intercept at ingress
        self.blacklist = ["sqlmap", "nikto", "nmap", "dirbuster"]

    def is_safe(self, payload: str) -> bool:
        """Evaluates inbound packet payload data for basic injection patterns."""
        raw_text = payload.lower()
        
        # Check for obvious SQLi or XSS patterns
        if "select " in raw_text or "union select" in raw_text or "<script>" in raw_text:
            return False
            
        for bot in self.blacklist:
            if f"user-agent: {bot}" in raw_text:
                return False
        return True

class RateLimiter:
    def __init__(self, max_reqs=10, timeframe=60):
        self.limit = max_reqs
        self.window = timeframe
        self.traffic_logs = defaultdict(list)

    async def allow_request(self, ip_address) -> bool:
        """Sliding window log architecture to track request velocity limits."""
        now = time.time()
        user_history = self.traffic_logs[ip_address]

        # Prune outdated logs outside current sliding timeline
        while user_history and user_history[0] < now - self.window:
            user_history.pop(0)

        if len(user_history) < self.limit:
            user_history.append(now)
            return True
            
        return False
