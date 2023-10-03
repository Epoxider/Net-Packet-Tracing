import json
import os
import re
import logging
import math
import sys
import queue
import threading
import subprocess
from datetime import datetime
from typing import Tuple, Dict, Optional, Any
import pandas as pd

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Constants
CONFIG = {
    "TOKEN_PATH": os.path.join(os.path.dirname(__file__), 'token.json'),
    "KM_TO_MILES": 0.621371,
    "EARTH_RADIUS_KM": 6371
}

# Read API token
with open(CONFIG["TOKEN_PATH"], 'r') as f:
    TOKEN = json.load(f)['token']

def fetch_geolocation(ip_address: str) -> Dict[str, Any]:
    """
    Fetches geolocation information of a given IP address.

    Parameters:
        ip_address (str): The IP address.

    Returns:
        dict: A dictionary containing geolocation information.
    """
    from requests import get

    url = f"https://ipinfo.io/{ip_address}/json?token={TOKEN}"
    try:
        response = get(url)
        data = response.json()
    except Exception as e:
        logging.error(f"Error fetching geolocation: {e}")
        return {}

    return {key: data.get(key, 'N/A') for key in ['country', 'region', 'city', 'loc', 'org']}

def calculate_haversine_distance(origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
    """
    Calculates the haversine distance between two geographical points.

    Parameters:
        origin (tuple): A tuple containing the latitude and longitude of the origin.
        destination (tuple): A tuple containing the latitude and longitude of the destination.

    Returns:
        float: The haversine distance in miles.
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = CONFIG["EARTH_RADIUS_KM"] * c
    return round(distance_km * CONFIG["KM_TO_MILES"], 2)

def run_tracert(destination: str, q: queue.Queue) -> None:
    """
    Runs a traceroute to the specified destination and puts the results in a queue.

    Parameters:
        destination (str): The IP address or domain name of the destination to trace.
        q (Queue): The queue to put the traceroute results in.
    """
    cmd = f"tracert -d {destination}"
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)

        for line in iter(proc.stdout.readline, ''):
            ip_match = re.search(r"([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", line)
            ms_match = re.search(r'(\d+)\sms', line)

            ip_address = ip_match.group() if ip_match else None
            avg_ms = ms_match.group(1) if ms_match else None

            if ip_address or avg_ms:
                q.put({'ip': ip_address, 'avg_ms': avg_ms})

        q.put(None)  # Signal that traceroute is complete
    except Exception as e:
        logging.error(f"Error running traceroute: {e}")
        q.put(None)

def main(destination: str) -> None:
    """
    The main function that coordinates the traceroute and geolocation fetching.

    Parameters:
        destination (str): The destination IP or URL.
    """
    parent_path = os.path.dirname(__file__)
    dest_name = re.sub(r'\W+', '_', destination.split('.')[0]) if any(char.isalpha() for char in destination) else destination
    csv_filename = os.path.join(parent_path, f'{dest_name}_route.csv')

    prev_coords: Optional[Tuple[float, float]] = None
    q = queue.Queue()
    df = pd.DataFrame()

    logging.info("Starting traceroute operation...")
    tracert_thread = threading.Thread(target=run_tracert, args=(destination, q))
    tracert_thread.start()

    try:
        while True:
            logging.info("Waiting for response from traceroute...")
            item = q.get()
            
            if item is None:
                logging.info("Traceroute operation completed.")
                break

            if item.get('ip'):
                logging.info(f"Fetching geolocation information for IP: {item['ip']}")
                current_time = datetime.now().isoformat()[:-3] + "Z"
                geo_data = fetch_geolocation(item['ip'])
                geo_data['current_time'] = current_time

                try:
                    current_coords = tuple(map(float, geo_data['loc'].split(',')))
                except ValueError:
                    current_coords = None

                if prev_coords and current_coords:
                    distance = calculate_haversine_distance(prev_coords, current_coords)
                    geo_data['distance_miles'] = distance

                prev_coords = current_coords
                geo_data.update(item)
                logging.info(geo_data)
                df = pd.concat([df, pd.DataFrame([geo_data])], ignore_index=True)

        df.to_csv(csv_filename, mode='w', index=False)
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Cleaning up...")
        tracert_thread.join()

if __name__ == "__main__":
    destination = sys.argv[1] if len(sys.argv) > 1 else "youtube.com"
    main(destination)

