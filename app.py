from flask import Flask, render_template
import osmnx as ox
import folium
import json
import networkx as nx
from geopy.geocoders import Nominatim

app = Flask(__name__)

@app.route("/")
def map():
    api_key = "AIzaSyBKBoDDpBC0sWmDqtAdV__gghUPZuywTHc"
    north, south, east, west = 41.9181, 41.8474, -87.6243, -87.7405
    graph = ox.graph_from_bbox(north, south, east, west, network_type="walk")
    ###################################################
    start_address = "1250 S Halsted St, Chicago, IL 60607" #919 S Aberdeen St, Chicago, IL 60607
    end_address = "801 S Morgan St, Chicago, IL 60607"
    geolocator = Nominatim(user_agent="myGeocoder", timeout=3)
    start_location = geolocator.geocode(start_address, timeout=3)
    end_location = geolocator.geocode(end_address, timeout=3)
    start = (start_location.latitude, start_location.longitude)
    end = (end_location.latitude, end_location.longitude)
    start_node = ox.distance.nearest_nodes(graph, X=[start[1]], Y=[start[0]], return_dist=False)
    end_node = ox.distance.nearest_nodes(graph, X=[end[1]], Y=[end[0]], return_dist=False)
    route = nx.shortest_path(graph, start_node[0], end_node[0], weight='length')
    route_json = ox.plot_route_folium(graph, route, route_color='blue', route_opacity=0.8, route_weight=5, popup_attribute=None)
    route_data = ox.utils_graph.graph_to_gdfs(graph.subgraph(route), nodes=False, fill_edge_geometry=True).to_json()
    marker_fg = folium.FeatureGroup(name="Markers")
    ######################################################
    # Add the start and end markers to the marker FeatureGroup
    folium.Marker(location=start, popup="Start").add_to(marker_fg)
    folium.Marker(location=end, popup="End").add_to(marker_fg)
    custom_tile_layer = folium.FeatureGroup(name="Custom Tile Layer").add_child(folium.GeoJson(json.loads(route_data)))
    m = folium.Map(location=start, zoom_start=12, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google")
    marker_fg.add_to(m)
    custom_tile_layer.add_to(m)
    folium.LayerControl().add_to(m)
    m.save("./templates/map.html")
    return render_template("map.html", api_key=api_key)
if __name__ == "__main__":
    app.run(debug=True)
