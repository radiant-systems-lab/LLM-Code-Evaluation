# Geolocation and Mapping
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
import requests
import json

def geocoding_operations():
    """Geocoding with geopy"""
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        
        # Geocode addresses
        addresses = [
            "New York City, NY, USA",
            "London, UK",
            "Tokyo, Japan",
            "Sydney, Australia"
        ]
        
        locations = []
        for address in addresses:
            try:
                location = geolocator.geocode(address, timeout=10)
                if location:
                    locations.append({
                        'address': address,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'full_address': location.address
                    })
            except Exception as e:
                locations.append({
                    'address': address,
                    'error': str(e)
                })
        
        # Calculate distances between cities
        distances = []
        if len(locations) >= 2:
            for i in range(len(locations)-1):
                if 'latitude' in locations[i] and 'latitude' in locations[i+1]:
                    point1 = (locations[i]['latitude'], locations[i]['longitude'])
                    point2 = (locations[i+1]['latitude'], locations[i+1]['longitude'])
                    distance = geodesic(point1, point2).kilometers
                    distances.append({
                        'from': locations[i]['address'],
                        'to': locations[i+1]['address'],
                        'distance_km': distance
                    })
        
        return {
            'addresses_processed': len(addresses),
            'successful_geocodes': len([loc for loc in locations if 'latitude' in loc]),
            'distances_calculated': len(distances),
            'locations': locations,
            'distances': distances
        }
        
    except Exception as e:
        return {'error': str(e)}

def reverse_geocoding():
    """Reverse geocoding - coordinates to address"""
    try:
        geolocator = Nominatim(user_agent="reverseGeocode")
        
        # Famous locations coordinates
        coordinates = [
            (40.7589, -73.9851),  # Times Square, NYC
            (51.5074, -0.1278),   # London
            (35.6762, 139.6503),  # Tokyo
            (-33.8688, 151.2093)  # Sydney
        ]
        
        reverse_locations = []
        for lat, lon in coordinates:
            try:
                location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
                if location:
                    reverse_locations.append({
                        'coordinates': (lat, lon),
                        'address': location.address,
                        'country': location.raw.get('address', {}).get('country', 'Unknown')
                    })
            except Exception as e:
                reverse_locations.append({
                    'coordinates': (lat, lon),
                    'error': str(e)
                })
        
        return {
            'coordinates_processed': len(coordinates),
            'successful_reverse_geocodes': len([loc for loc in reverse_locations if 'address' in loc]),
            'locations': reverse_locations
        }
        
    except Exception as e:
        return {'error': str(e)}

def create_folium_map():
    """Create interactive map with folium"""
    try:
        # Create base map
        center_lat, center_lon = 40.7128, -74.0060  # NYC
        map_obj = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add markers for various locations
        locations = [
            {'name': 'Central Park', 'coords': [40.7829, -73.9654], 'color': 'green'},
            {'name': 'Empire State Building', 'coords': [40.7484, -73.9857], 'color': 'blue'},
            {'name': 'Brooklyn Bridge', 'coords': [40.7061, -73.9969], 'color': 'red'},
            {'name': 'Statue of Liberty', 'coords': [40.6892, -74.0445], 'color': 'orange'}
        ]
        
        for loc in locations:
            folium.Marker(
                location=loc['coords'],
                popup=loc['name'],
                tooltip=f"Click for {loc['name']}",
                icon=folium.Icon(color=loc['color'])
            ).add_to(map_obj)
        
        # Add a circle
        folium.Circle(
            location=[center_lat, center_lon],
            radius=5000,  # 5km radius
            popup='5km from center',
            color='purple',
            fill=True,
            opacity=0.3
        ).add_to(map_obj)
        
        # Save map
        map_filename = '/tmp/interactive_map.html'
        map_obj.save(map_filename)
        
        return {
            'map_file': map_filename,
            'center': (center_lat, center_lon),
            'markers_added': len(locations),
            'shapes_added': 1
        }
        
    except Exception as e:
        return {'error': str(e)}

def weather_api_integration():
    """Weather API integration (simulation)"""
    try:
        # Simulate weather API response
        locations = [
            {'city': 'New York', 'lat': 40.7128, 'lon': -74.0060},
            {'city': 'London', 'lat': 51.5074, 'lon': -0.1278},
            {'city': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503}
        ]
        
        weather_data = []
        for loc in locations:
            # Simulate weather data
            import random
            weather_data.append({
                'city': loc['city'],
                'temperature': random.randint(-10, 35),
                'humidity': random.randint(30, 90),
                'wind_speed': random.randint(0, 30),
                'condition': random.choice(['sunny', 'cloudy', 'rainy', 'snowy'])
            })
        
        return {
            'cities_processed': len(locations),
            'weather_data': weather_data
        }
        
    except Exception as e:
        return {'error': str(e)}

def geospatial_calculations():
    """Various geospatial calculations"""
    # Define some coordinates
    points = {
        'new_york': (40.7128, -74.0060),
        'los_angeles': (34.0522, -118.2437),
        'chicago': (41.8781, -87.6298),
        'houston': (29.7604, -95.3698)
    }
    
    calculations = {}
    
    # Calculate center point (centroid)
    lat_sum = sum(point[0] for point in points.values())
    lon_sum = sum(point[1] for point in points.values())
    center = (lat_sum / len(points), lon_sum / len(points))
    calculations['center_point'] = center
    
    # Calculate all pairwise distances
    distances = {}
    city_names = list(points.keys())
    for i, city1 in enumerate(city_names):
        for city2 in city_names[i+1:]:
            dist = geodesic(points[city1], points[city2]).kilometers
            distances[f"{city1}_to_{city2}"] = dist
    
    calculations['distances'] = distances
    
    # Find closest and farthest pairs
    min_distance = min(distances.values())
    max_distance = max(distances.values())
    
    closest_pair = [pair for pair, dist in distances.items() if dist == min_distance][0]
    farthest_pair = [pair for pair, dist in distances.items() if dist == max_distance][0]
    
    calculations['closest_cities'] = closest_pair
    calculations['farthest_cities'] = farthest_pair
    calculations['min_distance'] = min_distance
    calculations['max_distance'] = max_distance
    
    return calculations

def coordinate_transformations():
    """Coordinate system transformations"""
    # Decimal degrees to degrees, minutes, seconds
    def dd_to_dms(decimal_degrees):
        degrees = int(decimal_degrees)
        minutes_float = abs(decimal_degrees - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return degrees, minutes, seconds
    
    # Test coordinates
    test_coords = [
        40.7589,  # NYC latitude
        -73.9851, # NYC longitude
        51.5074,  # London latitude
        -0.1278   # London longitude
    ]
    
    transformations = []
    for coord in test_coords:
        deg, min_val, sec = dd_to_dms(coord)
        transformations.append({
            'decimal': coord,
            'degrees': deg,
            'minutes': min_val,
            'seconds': round(sec, 2)
        })
    
    # Calculate bounding box for a set of points
    lats = [40.7589, 51.5074, 35.6762]
    lons = [-73.9851, -0.1278, 139.6503]
    
    bounding_box = {
        'min_lat': min(lats),
        'max_lat': max(lats),
        'min_lon': min(lons),
        'max_lon': max(lons)
    }
    
    return {
        'coordinate_transformations': transformations,
        'bounding_box': bounding_box
    }

if __name__ == "__main__":
    print("Geolocation and mapping operations...")
    
    # Geocoding
    geocoding_result = geocoding_operations()
    if 'error' not in geocoding_result:
        print(f"Geocoding: {geocoding_result['successful_geocodes']}/{geocoding_result['addresses_processed']} addresses")
    
    # Reverse geocoding
    reverse_result = reverse_geocoding()
    if 'error' not in reverse_result:
        print(f"Reverse geocoding: {reverse_result['successful_reverse_geocodes']}/{reverse_result['coordinates_processed']} coordinates")
    
    # Folium map
    map_result = create_folium_map()
    if 'error' not in map_result:
        print(f"Folium map: {map_result['markers_added']} markers added to {map_result['map_file']}")
    
    # Weather API
    weather_result = weather_api_integration()
    if 'error' not in weather_result:
        print(f"Weather API: {weather_result['cities_processed']} cities processed")
    
    # Geospatial calculations
    calc_result = geospatial_calculations()
    print(f"Calculations: Closest cities {calc_result['min_distance']:.0f}km apart")
    
    # Coordinate transformations
    transform_result = coordinate_transformations()
    print(f"Transformations: {len(transform_result['coordinate_transformations'])} coordinates converted")