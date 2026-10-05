import urllib.request
import urllib.error
import time
import sys

TARGET_URL = "http://127.0.0.1:8080"

def send_request(name, custom_headers=None, print_body=False):
    """Helper tool to send raw HTTP packets and catch gateway responses."""
    print(f"\n--- Triggering: {name} ---")
    req = urllib.request.Request(TARGET_URL)
    
    if custom_headers:
        for key, value in custom_headers.items():
            req.add_header(key, value)
            
    try:
        with urllib.request.urlopen(req, timeout=2) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            print(f"[SUCCESS] Gateway Response Code: {status}")
            if print_body:
                print(f"[DATA] {body.strip()}")
    except urllib.error.HTTPError as e:
        print(f"[BLOCKED] Gateway intercepted threat! Code: {e.code}")
        # Read the error message sent by our firewall middleware
        print(f"[REASON] {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    print("====================================================")
    print("      LAUNCHING INLINE SECURITY ATTACK SIMULATOR     ")
    print("====================================================")

    # 1. Test a perfectly normal, safe user request
    send_request(
        name="Normal User Traffic Session", 
        custom_headers={"User-Agent": "Mozilla/5.0"}, 
        print_body=True
    )

    # 2. Test a Cyber Attack payload (SQL Injection fingerprint)
    # Our WAF detects the word 'select ' in the stream and blocks it
    send_request(
        name="Malicious Layer-7 SQL Injection Attack", 
        custom_headers={"User-Agent": "Mozilla/5.0", "X-Query": "SELECT * FROM users;"}
    )

    # 3. Test an automated hacking scanner bot signature
    # Our WAF blacklisted 'sqlmap' inside gateway/middleware.py
    send_request(
        name="Vulnerability Scanner Bot Exploitation (sqlmap)", 
        custom_headers={"User-Agent": "sqlmap/1.8.2"}
    )

    # 4. Test a high-velocity DDoS flood attack
    # Spams requests instantly to exhaust the token bucket rate limiter
    print("\n--- Triggering: High-Velocity DDoS Flood (15 Rapid Requests) ---")
    success_count = 0
    blocked_count = 0
    
    for i in range(15):
        req = urllib.request.Request(TARGET_URL)
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            with urllib.request.urlopen(req, timeout=1) as response:
                success_count += 1
        except urllib.error.HTTPError as e:
            if e.code == 429:
                blocked_count += 1
        time.sleep(0.01) # Ultra fast spam delay
        
    print(f"[DDOS RESULT] Attack Finished.")
    print(f" -> Successful Tunnels Passed: {success_count}")
    print(f" -> High-Frequency Requests Blocked (429 Throttled): {blocked_count}")
    print("====================================================")
