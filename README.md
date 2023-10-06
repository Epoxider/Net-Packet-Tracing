# Net-Packet-Tracing
## Tool for network administrators or developers to diagnose network issues and gather information about the geolocation of IP addresses along a network route.

### Requirements
- API token from [IPinfo](https://ipinfo.io/) (as of 10/03/2023 there is a basic plan for personal use).
- Python 3.x
- pandas
- folium
- requests
### Usage
Save your API token a file called "token.json" inside this folder. The token.json file should look something like:\
```{"token": "YOUR TOKEN HERE"}```

Install the required Python packages:\
```pip install -r requirements.txt```

To run the script, simply execute the following command:\
```python main.py --destination [destination] --tool [traceroute|tracert] [--gen_report]```

- Replace [destination] with the IP address or domain name of the destination you want to trace. If no destination is specified, the script will default to tracing the route to youtube.com.
- Use --tool to specify whether to use "traceroute" (Unix/Linux) or "tracert" (Windows).
- Use --gen_report to generate a CSV report.

### Output
The script outputs:
1. CSV file named trace_results.csv in the same directory as the script. The file contains the following columns:
2. An HTML map file named [short_dest_name]_map.html in the same directory as the script.

- country: Country where the hop is located.
- region: Region where the hop is located.
- city: City where the hop is located.
- loc: Latitude & longitude of the hop.
- org: Associated orginzation's infrastructure
- current_time: Date & time (ISO 8601 format)
- ip: IP address of the hop.
- avg_ms: Average round-trip-time between sender & hop's location.
- distance_miles: Distance in miles from the previous hop to this hop.

Example:
| Country  | Region  | City  | Location    | Organization         | Current Time           | IP Address  | Avg MS | Distance (miles) |
|----------|---------|-------|-------------|----------------------|------------------------|-------------|--------|------------------|
| CountryA | RegionA | CityA | LocationA   | OrgA                 | 2023-10-03T08:28:26.068Z | IP_A        | -      | -                |
| CountryB | RegionB | CityB | LocationB   | OrgB                 | 2023-10-03T08:28:26.330Z | IP_B        | 4      | -                |
| CountryC | RegionC | CityC | LocationC   | OrgC                 | 2023-10-03T08:28:27.013Z | IP_C        | 16     | 45.72            |
| CountryD | RegionD | CityD | LocationD   | OrgD                 | 2023-10-03T08:28:28.052Z | IP_D        | 14     | 0.0              |
| CountryE | RegionE | CityE | LocationE   | OrgE                 | 2023-10-03T08:28:29.084Z | IP_E        | 13     | 0.0              |
| CountryF | RegionF | CityF | LocationF   | OrgF                 | 2023-10-03T08:28:45.979Z | IP_F        | 22     | 1732.8           |
| CountryG | RegionG | CityG | LocationG   | OrgG                 | 2023-10-03T08:28:46.932Z | IP_G        | 23     | 1732.8           |
| CountryH | RegionH | CityH | LocationH   | OrgH                 | 2023-10-03T08:28:47.978Z | IP_H        | 17     | 0.0              |



### License
This script is licensed under the MIT License. See the LICENSE file for details.