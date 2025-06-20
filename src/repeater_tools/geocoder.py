"""
geocoder.py
Contains helper functions to pull location information for a given lat/lon coordinate point
"""
import os
import googlemaps

API_KEY = os.getenv('MAPS_API_KEY')
gmaps = googlemaps.Client(key=API_KEY)
def get_state(lat: float, lon: float) -> str:
    """Reverse-geocode and return the two-letter state code."""
    results = gmaps.reverse_geocode((lat, lon), result_type=['administrative_area_level_1'])
    return results[0]['address_components'][0]['short_name']

