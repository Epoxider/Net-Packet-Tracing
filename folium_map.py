from folium import Map, Marker, PolyLine, IFrame, Popup
from typing import Tuple, Optional
from folium.plugins import FloatImage
import branca

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
        self.add_legend()
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

    def add_legend(self):
        # HTML and CSS for the legend
        legend_html = '''
        {% macro html(this, kwargs) %}
        <div style="position: fixed; 
            bottom: 50px; left: 50px; width: 200px; height: 150px; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white; opacity: 0.85;">
            &nbsp; <b>Legend</b> <br>
            &nbsp; avg ms < 20ms &nbsp; <i class="fa fa-circle" style="color:green"></i><br>
            &nbsp; avg ms < 30ms &nbsp; <i class="fa fa-circle" style="color:yellow"></i><br>
            &nbsp; avg ms > 40ms nbsp; <i class="fa fa-circle" style="color:red"></i><br>
            &nbsp; no data &nbsp; <i class="fa fa-circle" style="color:blue"></i><br>
        </div>
        {% endmacro %}
        '''

        legend = branca.element.MacroElement()
        legend._template = branca.element.Template(legend_html)

        # Add the legend to the map
        self.folium_map.get_root().add_child(legend)