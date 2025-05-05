import asyncio
import os

import httpx

# Test URL to check proxy (returns JSON with IP)
TEST_URL = "http://httpbin.org/ip"
TIMEOUT = 5  # Timeout for each request in seconds
MAX_CONCURRENT = 10  # Max concurrent proxy checks

def parse_proxy(line):
    """Parse a proxy line into IP, port, username, and password."""
    try:
        parts = line.strip().split(":")
        if len(parts) != 4:
            return None
        ip, port = parts[0], parts[1]
        username, password = parts[2], parts[3]
        return {
            "ip": ip,
            "port": port,
            "username": username,
            "password": password
        }
    except ValueError:
        return None

async def check_proxy(proxy, sem):
    """Check if a proxy is working by making an async request."""
    proxy_str = f"{proxy['ip']}:{proxy['port']}"
    proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
    
    async with sem:
        try:
            print(f"Checking proxy {proxy_str}...")
            async with httpx.AsyncClient(proxy=proxy_url, timeout=TIMEOUT) as client:
                response = await client.get(TEST_URL)
                if response.status_code == 200:
                    # Optionally verify the proxy IP in the response
                    ip = response.json().get("origin", "")
                    print(f"Proxy {proxy_str} is WORKING (IP: {ip})")
                else:
                    print(f"Proxy {proxy_str} FAILED (Status: {response.status_code})")
        except (httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
            print(f"Error checking proxy {proxy_str}: {str(e)}")
            return f"Proxy {proxy_str} FAILED (Error: {str(e)})"

async def main(proxy_file="proxies.txt"):
    """Main function to check proxies from a file."""
    print("Starting async proxy checker...")
    proxies = []
    
    # Check if proxy file exists and is readable
    if not os.path.exists(proxy_file):
        print(f"Error: Proxy file '{proxy_file}' does not exist")
        return
    if not os.path.isfile(proxy_file):
        print(f"Error: '{proxy_file}' is not a file")
        return
    
    # Read proxies from file
    try:
        with open(proxy_file, "r", encoding="utf-8") as f:
            for line in f:
                proxy = parse_proxy(line)
                if proxy:
                    proxies.append(proxy)
                else:
                    print(f"Invalid proxy format: {line.strip()}")
    except PermissionError:
        print(f"Error: Permission denied accessing '{proxy_file}'")
        return
    except UnicodeDecodeError:
        print(f"Error: '{proxy_file}' is not a valid text file (encoding error)")
        return
    except Exception as e:
        print(f"Error reading '{proxy_file}': {str(e)}")
        return
    
    if not proxies:
        print("No valid proxies found in file")
        return
    
    # Create semaphore to limit concurrency
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    
    # Check proxies concurrently using TaskGroup
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(check_proxy(proxy, sem)) for proxy in proxies]
    
    # Print results (tasks are already completed due to TaskGroup)
    for task in tasks:
        print(task.result())
    
    print("Proxy checking completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProxy checker stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")