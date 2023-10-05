import colorsys
import math
from folium import Map, Marker, PolyLine
from typing import Tuple, Optional

class FoliumMap():
    def __init__(self):
        self.folium_map = Map(location=[0, 0], zoom_start=3)
        self.line_coords = []
        self.prev_coords: Optional[Tuple[float, float]] = None
        self.min_hue_step = 0.05
    
    def update_prev_coords(self, current_coords):
        self.prev_coords = current_coords

    def update_line_coords(self, current_coords):
        self.line_coords.append(current_coords)

    def add_marker(self, current_coords):
         Marker(current_coords).add_to(self.folium_map)
        
    def save_map(self, map_path):
        self.folium_map.save(map_path)

    def add_line(self, current_coords):
        # change color of line based on number of lines already drawn
        line_color = self.calc_color_hue(len(self.line_coords))
        PolyLine([current_coords[-2], current_coords[-1]], color=line_color, weight=2.5).add_to(self.folium_map)

    def calc_color_hue(self, line_count):
        #hue = line_count / 40 # 
        hue = self.min_hue_step * line_count
        # Convert to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        # Convert to HEX
        color_hex = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
        return color_hex