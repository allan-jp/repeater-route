# ------------------------------
# src/repeater_route/state_lookup.py
# ------------------------------
from googlemaps.exceptions import ApiError
from .geo import haversine

# Mapping of state abbreviations to FIPS codes
_state_abbrev_to_fips = {
    'AL': 1,  'AK': 2,  'AZ': 4,  'AR': 5,  'CA': 6,
    'CO': 8,  'CT': 9,  'DE': 10, 'FL': 12, 'GA': 13,
    'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19,
    'KS': 20, 'KY': 21, 'LA': 22, 'ME': 23, 'MD': 24,
    'MA': 25, 'MI': 26, 'MN': 27, 'MS': 28, 'MO': 29,
    'MT': 30, 'NE': 31, 'NV': 32, 'NH': 33, 'NJ': 34,
    'NM': 35, 'NY': 36, 'NC': 37, 'ND': 38, 'OH': 39,
    'OK': 40, 'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45,
    'SD': 46, 'TN': 47, 'TX': 48, 'UT': 49, 'VT': 50,
    'VA': 51, 'WA': 53, 'WV': 54, 'WI': 55, 'WY': 56
}

def latlon_to_fips(client, lat, lon):
    """
    Reverse-geocode (lat, lon) to find the state abbreviation,
    then map to its FIPS code.
    Returns an int FIPS or None if not found.
    """
    try:
        res = client.reverse_geocode((lat, lon))
    except ApiError:
        return None

    for comp in res[0]['address_components']:
        if 'administrative_area_level_1' in comp['types']:
            abbr = comp['short_name']
            return _state_abbrev_to_fips.get(abbr)
    return None
