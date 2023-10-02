import requests, json, subprocess, re, os, sys, math, queue, threading

path = os.path.dirname(__file__)

# read token from token.json
with open(path+'/token.json', 'r') as f:
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
def tracert(ip_dest, q):
    """
    Performs a traceroute to a given IP destination and returns the response times for each IP address along the route.

    Parameters:
        ip_dest (str): The IP address or domain name to perform the traceroute to.

    Returns:
        ip_ms_dict (dict): A dictionary containing the response times for each IP address along the route. The
        dictionary contains the IP addresses as keys and a dictionary with the average response time in milliseconds
        as the value. The dictionary has the following format:
            {
                'ip_address_1': {'avg_ms': response_time_1},
                'ip_address_2': {'avg_ms': response_time_2},
                ...
            }
    """
    ipv6_pattern = r"\d+\s+\d+\sms\s+(?P<time2>\d+)\sms\s+\d+\sms\s+(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}"
    avg_ms_pattern =  r"\d+\s+\d+\sms\s+(?P<avg_ms>\d+)\sms\s+\d+\sms\s+([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}"
    cmd = f"tracert -d {ip_dest}"
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)

    for line in iter(proc.stdout.readline, ''):
        ip_address = None
        avg_ms = None

        ip_match = re.search(ipv6_pattern, line)
        ms_match = re.search(avg_ms_pattern, line)

        if ip_match:
            ip_address = ip_match.group().split()[-1]
        if ms_match:
            avg_ms = ms_match.group("avg_ms")
            
        if ip_address or avg_ms:
            q.put({'ip': ip_address, 'avg_ms': avg_ms})

    q.put(None) # Signal that tracert is done

def main(destination):
    try:
        prev_coords = None  # Initialize prev_coords
        q = queue.Queue()  # Initialize the queue to hold tracert data

        # Start tracert in a separate thread
        tracert_thread = threading.Thread(target=tracert, args=(destination, q))
        tracert_thread.start()

        tracert_done = False  # Flag to indicate if tracert is done

        while not (tracert_done and q.empty()):  # Continue until tracert is done and the queue is empty
            try:
                ms_data = q.get(timeout=10)  # Adjust the timeout as needed

                if ms_data is None:  # Check for the signal that tracert is done
                    tracert_done = True
                    continue  # Skip the rest of the loop for this iteration

                ip = ms_data['ip']
                result = ip_geo(ip)

                # Get latitude and longitude for the current IP address
                try:
                    current_coords = tuple(map(float, result['loc'].split(','))) if 'loc' in result else None
                except ValueError:
                    current_coords = None

                # If both prev_coords and current_coords are available, calculate the haversine distance
                if prev_coords and current_coords:
                    distance = haversine_distance(prev_coords, current_coords)
                    result['distance_miles'] = distance * 0.621371  # Convert km to miles

                # Update prev_coords for the next iteration
                prev_coords = current_coords

                result.update(ms_data)  # Add avg_ms to the result dictionary
                result['ip'] = ip  # Add the IP address to the result dictionary

                print(result)

            except queue.Empty:
                if not tracert_done:
                    continue  # Just continue if the queue is empty but tracert isn't done yet

        tracert_thread.join()  # Wait for the tracert_thread to finish

    except KeyboardInterrupt:
        print('Exiting... Please wait for the tracert thread to finish.')
        tracert_thread.join()  # Wait for the tracert_thread to finish
        exit(0)

# Main program execution starts here
if __name__ == '__main__':
    if len(sys.argv) > 1:
        destination = sys.argv[1]
    else:
        destination = 'youtube.com' # or ipv4/6 address

    main(destination) # Call main() function