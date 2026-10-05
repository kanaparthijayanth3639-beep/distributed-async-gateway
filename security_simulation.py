import urllib.request
import urllib.error
import time

TARGET_URL = "http://127.0.0.1:8080"

def execute_test_packet(test_name, headers=None, inspect_body=False):
    print(f"\n[Test Setup] Running case: {test_name}")
    req = urllib.request.Request(TARGET_URL)
    
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
            
    try:
        with urllib.request.urlopen(req, timeout=2) as res:
            print(f"-> Response: {res.getcode()}")
            if inspect_body:
                print(f"-> Data: {res.read().decode('utf-8').strip()}")
    except urllib.error.HTTPError as err:
        print(f"-> Dropped by Edge Layer. Code: {err.code}")
        print(f"-> Message: {err.read().decode('utf-8')}")
    except Exception as err:
        print(f"-> Connectivity Error: {err}")

if __name__ == "__main__":
    # 1. Base network traffic path verification
    execute_test_packet(
        test_name="Standard Baseline Ingress Request", 
        headers={"User-Agent": "Mozilla/5.0"}, 
        inspect_body=True
    )

    # 2. SQLi injection string signature test
    execute_test_packet(
        test_name="Layer-7 SQLi Pattern Interception", 
        headers={"User-Agent": "Mozilla/5.0", "X-Query": "SELECT * FROM storage;"}
    )

    # 3. Known automated scanner agent identification check
    execute_test_packet(
        test_name="Malicious User-Agent Footprint Rejection", 
        headers={"User-Agent": "sqlmap/1.8.2"}
    )

    # 4. Rate-limiter flood volume check
    print("\n[Test Setup] Running case: High Volume Inbound Velocity Check")
    passed, dropped = 0, 0
    
    for _ in range(15):
        req = urllib.request.Request(TARGET_URL)
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            with urllib.request.urlopen(req, timeout=1) as res:
                passed += 1
        except urllib.error.HTTPError as err:
            if err.code == 429:
                dropped += 1
        time.sleep(0.01)
        
    print(f"-> Completed. Metrics -> Successful: {passed} | Rate-Limited: {dropped}")
