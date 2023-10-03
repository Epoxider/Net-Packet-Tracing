## Net-Packet-Tracing
### Tool for network administrators or developers to diagnose network issues and gather information about the geolocation of IP addresses along a network route.

#### Requirements
- Windows
- API token from [IPinfo](https://ipinfo.io/) (as of 10/03/2023 there is a basic plan for personal use).
- Python 3.x
- pandas
- requests
#### Usage
Save your API token a file called "token.json" inside this folder. The token.json file should look something like:\
```{"token": "YOUR TOKEN HERE"}```\
\
To run the script, simply execute the following command:\
```python trace_packets.py [destination]```

Replace [destination] with the IP address or domain name of the destination you want to trace. If no destination is specified, the script will default to tracing the route to youtube.com.

#### Output
The script outputs a CSV file named trace_results.csv in the same directory as the script. The file contains the following columns:

- ip: The IP address of the hop.
- city: The city where the hop is located.
- region: The region where the hop is located.
- country: The country where the hop is located.
- distance_miles: The distance in miles from the previous hop to this hop.

Example:\
| country                   | region  | city   | loc      | org                                        | ip        | avg_ms | distance_miles |
|---------------------------|---------|--------|----------|--------------------------------------------|-----------|--------|----------------|
| US                        | State   | City   | lat,lon  | Organization 1                             | IP Address|        |                |
| Information not available |         |        |          |                                            |           |        |                |
| US                        | State   | City   | lat,lon  | Organization 2                             | IP Address| 2      |                |
| US                        | State   | City   | lat,lon  | Organization 2                             | IP Address| 16     | 45.72          |
| US                        | State   | City   | lat,lon  | Organization 2                             | IP Address| 13     | 0.0            |
| US                        | State   | City   | lat,lon  | Organization 2                             | IP Address| 22     | 0.0            |
| US                        | State   | City   | lat,lon  | Organization 2                             | IP Address| 19     | 1732.8         |
| US                        | State   | City   | lat,lon  | Organization 1                             | IP Address| 20     | 1732.8         |
| US                        | State   | City   | lat,lon  | Organization 1                             | IP Address| 19     | 0.0            |


#### License
This script is licensed under the MIT License. See the LICENSE file for details.