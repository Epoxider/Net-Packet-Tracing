import os
import re
import json

class Config():
    def __init__(self, destination: str):
        self.destination = destination
        self.report_flag = False
        self.trace_cmd = f"tracert -h 100 -d {self.destination}"
        self.km_to_miles = 0.621371
        self.earth_radius_km = 6371
        self.short_dest_name = re.sub(r'\W+', '_', self.destination.split('.')[0]) if any(char.isalpha() for char in self.destination) else self.destination
        self.csv_path = os.path.join(os.path.dirname(__file__), f'/RouteData{self.short_dest_name}_route.csv')
        self.map_path = os.path.join(os.path.dirname(__file__), f'/Maps/{self.short_dest_name}_map.html')

    def set_destination(self, destination: str) -> None:
        self.destination = destination
    
    def set_report_flag(self, report_flag: bool) -> None:
        self.report_flag = report_flag