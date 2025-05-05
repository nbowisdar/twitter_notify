import httpx


async def check_proxy(proxy_url: str) -> bool:

    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=5) as client:
            response = await client.get(
                "http://httpbin.org/ip"
            )  # A simple site to check IP
            response.raise_for_status()  # Raise an exception for bad status codes
            print(f"Proxy {proxy_url} is working.")
            return True
    except httpx.HTTPError as e:
        print(f"Proxy {proxy_url} failed with HTTP error: {e}")
        return False
    except httpx.ConnectError as e:
        print(f"Could not connect to proxy {proxy_url}: {e}")
        return False
    except httpx.TimeoutException:
        print(f"Connection to proxy {proxy_url} timed out.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking proxy {proxy_url}: {e}")
        return False


async def main():

    proxy_string_new_auth = "http://login:pass@example.com:8080"
    await check_proxy(proxy_string_new_auth)

    proxy_string_no_auth = "192.168.1.100:8080"
    await check_proxy(proxy_string_no_auth)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
