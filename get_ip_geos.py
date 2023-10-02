import requests, json, subprocess, re, sys, math

# add the path of this file to the system path
sys.path.append('./tracert_proj')

# read token from token.json
with open('./tracert_proj/token.json', 'r') as f:
    token = json.load(f)['token']

# Function to fetch geolocation data for a given IP address
def ip_geo(ip_address):
    """
    Fetches geolocation data for a given IP address using the ipinfo.io API.

    Parameters:
        ip_address (str): The IP address to fetch geolocation data for.

    Returns:
        filtered_data (dict): A dictionary containing the geolocation data for the IP address. The dictionary
        contains the following keys:
            - 'country': The country where the IP address is located.
            - 'region': The region where the IP address is located.
            - 'city': The city where the IP address is located.
            - 'loc': The latitude and longitude of the IP address in the format 'latitude,longitude'.
    """
    url = f"https://ipinfo.io/{ip_address}/json?token={token}"
    response = requests.get(url)
    data = response.json()
    filtered_data = {key: data.get(key, 'Information not available') for key in ['country', 'region', 'city', 'loc']}
    return filtered_data

# Function to calculate haversize distance between two points on earth
def haversine_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return round(d, 2)

# Function to perform a traceroute to a given IP destination
def tracert(ip_dest):
    ipv6_pattern = r"\d+\s+\d+\sms\s+(?P<time2>\d+)\sms\s+\d+\sms\s+(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}"
    cmd = f"tracert -d {ip_dest}"
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    
    matches = re.finditer(ipv6_pattern, output)
    ip_ms_dict = {}
    
    for match in matches:
        parts = match.group().split()
        time2_ms = match.group("time2")
        ip_address = parts[-1]
        ip_ms_dict[ip_address] = {'avg_ms': time2_ms}   

    return ip_ms_dict

def main():
    ip_ms_data = tracert('8.8.8.8')

    for ip, ms_data in ip_ms_data.items():
        result = ip_geo(ip)
        result.update(ms_data)  # Add avg_ms to the result dictionary
        result['ip'] = ip  # Add the IP address to the result dictionary
        print(result)


# Main program execution starts here
if __name__ == '__main__':
    main()