import aiohttp
import asyncio
from datetime import datetime
import os
import socket
from bot.loader import PROXIES_FILE

async def check_proxy(session, proxy, timeout=5, test_url="http://httpbin.org/ip"):
    """
    Asynchronously check if a proxy is working.
    
    Args:
        session: aiohttp ClientSession
        proxy (str): Proxy in format 'ip:port' or 'ip:port:username:password'
        timeout (int): Timeout in seconds
        test_url (str): URL to test against
        
    Returns:
        dict: Proxy check results
    """
    proxy_parts = proxy.split(':')
    result = {
        'proxy': proxy,
        'working': False,
        'response_time': None,
        'error': None,
        'external_ip': None,
        'checked_at': datetime.now().isoformat()
    }
    
    try:
        # Validate proxy format
        if len(proxy_parts) not in (2, 4):
            result['error'] = "Invalid proxy format"
            return result

        # Basic IP validation
        try:
            socket.inet_aton(proxy_parts[0])
        except socket.error:
            result['error'] = "Invalid IP address"
            return result

        # Prepare proxy URL
        if len(proxy_parts) == 2:  # ip:port
            proxy_url = f"http://{proxy}"
        else:  # ip:port:username:password
            proxy_url = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"

        conn = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
        proxy_dict = {
            'http': proxy_url,
            'https': proxy_url
        }

        start_time = datetime.now()
        
        try:
            async with session.get(
                test_url,
                proxy=proxy_url if 'http://' in proxy_url else f'http://{proxy_url}',
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=False
            ) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                result['response_time'] = round(response_time, 2)
                
                if response.status == 200:
                    result['working'] = True
                    try:
                        data = await response.json()
                        result['external_ip'] = data.get('origin', 'Unknown')
                    except:
                        result['external_ip'] = 'Unknown'
                else:
                    result['error'] = f"Status code: {response.status}"
        except asyncio.TimeoutError:
            result['error'] = "Timeout"
        except Exception as e:
            result['error'] = str(e)
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

async def check_proxies(proxies, max_concurrent=100):
    """
    Check multiple proxies concurrently with async.
    
    Args:
        proxies (list): List of proxy strings
        max_concurrent (int): Maximum concurrent checks
        
    Returns:
        list: List of results
    """
    results = []
    connector = aiohttp.TCPConnector(limit=max_concurrent, force_close=True)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_proxy(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=False)
    
    return results

def load_proxies(filename="proxies.txt"):
    """
    Load proxies from file.
    
    Args:
        filename (str): Path to proxy file
        
    Returns:
        list: List of proxies
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return []
    
    with open(filename, 'r') as f:
        return [line.strip() for line in f 
                if line.strip() and not line.startswith('#')]

def save_results_txt(proxies, filename="proxies.txt"):
    """
    Save results to text file.
    
    Args:
        results (list): List of proxy results
        filename (str): Output filename
    """
    if not proxies:
        return
    with open(filename, 'w') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")
    print(f"Results saved to {filename}")

def save_results_csv(results, filename="proxy_results.csv"):
    """
    Save results to CSV file.
    
    Args:
        results (list): List of proxy results
        filename (str): Output filename
    """
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'proxy', 'working', 'response_time', 'external_ip', 'error', 'checked_at'
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filename}")

async def get_active_proxies(update_existing_file=True) -> list[str]:
    proxies = load_proxies(PROXIES_FILE)
    
    print(f"Loaded {len(proxies)} proxies.")
    
    if not proxies:
        print("No proxies found to check.")
        return
    
    print(f"Checking {len(proxies)} proxies...")
    start_time = datetime.now()
    
    # Run checks
    results = await check_proxies(proxies)
    
    # Calculate stats
    duration = (datetime.now() - start_time).total_seconds()
    working = sum(1 for r in results if r['working'])
    avg_time = (sum(r['response_time'] for r in results if r['working']) / working) if working else 0
    
    # Print summary
    print(f"\nCompleted in {duration:.2f} seconds")
    print(f"Working proxies: {working}/{len(proxies)} ({working/len(proxies)*100:.1f}%)")
    print(f"Average response time: {avg_time:.2f}s")
    
    proxies = [r['proxy'] for r in results if r['working']]
    if update_existing_file:
        print(f"Saving results to {PROXIES_FILE}")
        save_results_txt(proxies, PROXIES_FILE)
    return proxies

async def main():
    await get_active_proxies()


def format_proxy_auth(proxy_str):
    """
    Convert complex proxy string to standard http auth format.
    
    Example Input:
    "190.2.130.11:9999:bbtuowari6-corp.mobile.res-country-US-state-4138106-city-4140963-hold-session-session-68166d2722971:n01WWjrk5A30NSdU"
    
    Example Output:
    "http://bbtuowari6-corp.mobile.res-country-US-state-4138106-city-4140963-hold-session-session-68166d2722971:n01WWjrk5A30NSdU@190.2.130.11:9999"
    """
    parts = proxy_str.split(':')
    if len(parts) >= 4:
        ip = parts[0]
        port = parts[1]
        username = ':'.join(parts[2:-1])  # Handle usernames that might contain colons
        password = parts[-1]
        return f"http://{username}:{password}@{ip}:{port}"
    return None


if __name__ == "__main__":
    # Windows requires this for asyncio
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())