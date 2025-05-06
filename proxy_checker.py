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

# Example usage
proxy = "190.2.130.11:9999:bbtuowari6-corp.mobile.res-country-US-state-4138106-city-4140963-hold-session-session-68166d2722971:n01WWjrk5A30NSdU"
formatted = format_proxy_auth(proxy)
print(formatted)