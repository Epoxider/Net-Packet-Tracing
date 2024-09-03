import os
import json
import pandas as pd
from requests import get

def extract_ip_addresses_from_csv(file_path: str):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Extract the 'ip' column into a list
    ip_addresses = df['ip'].tolist()
    
    return ip_addresses

token_path = os.path.join(os.path.dirname(__file__), 'token.json')
with open(token_path, 'r') as f:
    TOKEN = json.load(f)['token']

def get_info(ip_address):
    url = f"https://ipinfo.io/{ip_address}/json?token={TOKEN}"
    try:
        response = get(url)
        data = response.json()
    except Exception as e:
        return {}
    ret = {key: data.get(key, 'N/A') for key in ['country', 'region', 'city', 'loc', 'org']}
    return ret

f = './youtube_route.csv'
ip_addresses = extract_ip_addresses_from_csv(f)
print(ip_addresses)

for ip in ip_addresses:
    r = get_info(ip)
    #test comment
    #print(r)