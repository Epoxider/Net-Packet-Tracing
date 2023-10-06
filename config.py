import os
import re

class Config():
    def __init__(self, destination: str, trace_tool: str):
        self.destination = destination
        self.report_flag = False
        self.km_to_miles = 0.621371
        self.earth_radius_km = 6371
        self.short_dest_name = re.sub(r'\W+', '_', self.destination.split('.')[0]) if any(char.isalpha() for char in self.destination) else self.destination
        self.csv_path = os.path.join(os.path.dirname(__file__), f'{self.short_dest_name}_route.csv')
        self.map_path = os.path.join(os.path.dirname(__file__), f'{self.short_dest_name}_map.html')
        self.trace_tool = trace_tool

    def set_destination(self, destination: str) -> None:
        self.destination = destination
    
    def set_report_flag(self, report_flag: bool) -> None:
        self.report_flag = report_flag

    def get_regex(self, line):
        if self.trace_tool=='tracert':
            ip_pattern = re.search(r"([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", line)
            ms_pattern = re.search(r'(\d+)\sms', line)
        else:
            ip_pattern = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            ms_pattern = re.search(r'(\d+\.\d+) ms', line)

        return (ip_pattern, ms_pattern)

    def get_cmd(self):
        if self.trace_tool=='tracert':
            self.trace_cmd = f'tracert -h 100 -d {self.destination}'
        else:
            self.trace_cmd = f'traceroute -n {self.destination}'
        return self.trace_cmd