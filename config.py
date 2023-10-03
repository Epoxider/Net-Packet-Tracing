import os
import re

class Config():
    def __init__(self, destination='youtube.com'):
        self.TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
        self.destination = destination
        self.TRACE_CMD = f"tracert -d {self.destination}"
        self.KM_TO_MILES = 0.621371
        self.EARTH_RADIUS_KM = 6371
        self.set_file_paths()

    def set_destination(self, destination: str) -> None:
        self.destination = destination
        self.set_file_paths()

    def set_file_paths(self) -> None:
        self.short_dest_name = re.sub(r'\W+', '_', self.destination.split('.')[0]) if any(char.isalpha() for char in self.destination) else self.destination
        self.CSV_PATH = os.path.join(os.path.dirname(__file__), f'{self.short_dest_name}_route.csv')
        self.MAP_PATH = os.path.join(os.path.dirname(__file__), f'{self.short_dest_name}_map.html')