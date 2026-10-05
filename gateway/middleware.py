import time
from collections import defaultdict

class SecurityFirewall:
    def __init__(self):
        # Common automated scanner bots we want to block instantly
        self.blacklist = ["sqlmap", "nikto", "nmap", "dirbuster"]

    def is_safe(self, payload: str) -> bool:
        """Inspects raw packet text for common web vulnerabilities."""
        raw_text = payload.lower()
        
        # Quick check for obvious SQL injection or XSS scripting attempts
        if "select " in raw_text or "union select" in raw_text or "<script>" in raw_text:
            return False
            
        # Block unauthorized security scrapers
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
        """Simple token bucket tracking to prevent basic DDoS floods."""
        now = time.time()
        user_history = self.traffic_logs[ip_address]

        # Clean out old timestamps outside our 60-second window
        while user_history and user_history[0] < now - self.window:
            user_history.pop(0)

        if len(user_history) < self.limit:
            user_history.append(now)
            return True
            
        return False  # Throttled!