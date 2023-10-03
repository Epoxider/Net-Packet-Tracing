from folium import Map, Marker, PolyLine
from typing import Tuple, Optional

class FoliumMap():
    def __init__(self):
        self.folium_map = Map(location=[0, 0], zoom_start=3)
        self.line_coords = []
        self.marker_counter = 0
        self.prev_coords: Optional[Tuple[float, float]] = None
    
    def update_prev_coords(self, current_coords):
        self.prev_coords = current_coords

    def update_line_coords(self, current_coords):
        self.line_coords.append(current_coords)

    def add_marker(self, current_coords):
         Marker(current_coords).add_to(self.folium_map)
        
    def save_map(self, map_path):
        self.folium_map.save(map_path)

    def add_line(self, current_coords, q_item):
        # change color of line based on avg_ms of q_item, green for < 10ms, yellow for < 20ms, red for > 30ms
        if q_item['avg_ms'] and int(q_item['avg_ms']) < 20:
            PolyLine([current_coords[-2], current_coords[-1]], color="green", weight=2.5).add_to(self.folium_map)
        elif q_item['avg_ms'] and int(q_item['avg_ms']) < 30:
            PolyLine([current_coords[-2], current_coords[-1]], color="yellow", weight=2.5).add_to(self.folium_map)
        elif q_item['avg_ms'] and int(q_item['avg_ms']) > 40:
            PolyLine([current_coords[-2], current_coords[-1]], color="red", weight=2.5).add_to(self.folium_map)
        else:
            PolyLine([current_coords[-2], current_coords[-1]], color="blue", weight=2.5).add_to(self.folium_map)