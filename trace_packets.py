import os
import json
import logging
import math
import queue
import threading
import subprocess
import argparse
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Optional, Any
from folium_map import FoliumMap
from config import Config

# Initialize logging
logging.basicConfig(level=logging.INFO)


# Read API token
token_path = os.path.join(os.path.dirname(__file__), 'token.json')
with open(token_path, 'r') as f:
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
    ret = {key: data.get(key, 'N/A') for key in ['country', 'region', 'city', 'loc', 'org']}
    return ret

def calculate_haversine_distance(config, origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
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
    distance_km = config.earth_radius_km * c
    return round(distance_km * config.km_to_miles, 2)

def run_tracert(config, q: queue.Queue) -> None:
    """
    Runs a traceroute to the specified destination and puts the results in a queue.

    Parameters:
        destination (str): The IP address or domain name of the destination to trace.
        q (Queue): The queue to put the traceroute results in.
    """
    cmd = config.get_cmd()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, text=True)
        for line in iter(proc.stdout.readline, ''):
            ip_pattern, ms_pattern = config.get_regex(line)
            ip_address = ip_pattern.group() if ip_pattern else None
            avg_ms = ms_pattern.group(1) if ms_pattern else None
            if ip_address or avg_ms:
                q.put({'ip': ip_address, 'avg_ms': avg_ms})
        q.put(None)  # Signal that traceroute is complete

    except Exception as e:
        logging.error(f"Error running traceroute: {e}")
        q.put(None)

def main(config) -> None:
    """
    The main function that coordinates the traceroute and geolocation fetching.

    Parameters:
        destination (str): The destination IP or URL.
    """
    q = queue.Queue()
    df = pd.DataFrame()
    folium_map = FoliumMap()
    prev_coords: Optional[Tuple[float, float]] = None
    logging.info("Starting traceroute operation...")
    tracert_thread = threading.Thread(target=run_tracert, args=(config, q,))
    tracert_thread.start()
    try:
        while True:
            logging.info("Waiting for response from traceroute...")
            item = q.get()
            if item is None:
                logging.info("Traceroute operation completed.")
                break
            if item.get('ip'):
                current_time = datetime.now().isoformat()[:-3] + "Z"
                geo_data = fetch_geolocation(item['ip'])
                geo_data['current_time'] = current_time
                try:
                    current_coords = tuple(map(float, geo_data['loc'].split(',')))
                except ValueError:
                    current_coords = None
                if prev_coords and current_coords:
                    distance = calculate_haversine_distance(config, prev_coords, current_coords)
                    geo_data['distance_miles'] = distance
                prev_coords = current_coords
                geo_data.update(item)
                logging.info(f"city = {geo_data['city']} \t org = {geo_data['org']} \t ms = {geo_data['avg_ms']}")
                df = pd.concat([df, pd.DataFrame([geo_data])], ignore_index=True)
                 # Add Marker for current location
                if current_coords:
                    folium_map.add_marker(current_coords)
                    # Add these coordinates for PolyLine
                    folium_map.update_line_coords(current_coords)
                    # Draw PolyLine
                    if len(folium_map.line_coords) > 1:
                        # change color of line based on avg_ms of item, green for < 10ms, yellow for < 20ms, red for > 30ms
                        folium_map.add_line(folium_map.line_coords)
                    # Save or Refresh Map
                    folium_map.save_map(config.map_path)
        if config.report_flag:
            df.to_csv(config.csv_path, mode='w', index=False)

    except KeyboardInterrupt:
        if config.report_flag:
            df.to_csv(config.csv_path, mode='w', index=False)
        logging.info("Interrupted by user. Cleaning up...")
        tracert_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Traceroute geolocation tool.')
    parser.add_argument('--destination', type=str, default=default_dest, help='Destination IP or URL')
    parser.add_argument('--tool', type=str, default='tracert', help='Specify tracert (windows) or traceroute (unix)')
    parser.add_argument('--gen_report', action='store_true', help='Generate a CSV file')
    args = parser.parse_args()
    config = Config(args.destination, args.tool)
    if args.gen_report:
        config.set_report_flag(True)
    print(config.destination)
    main(config=config)

