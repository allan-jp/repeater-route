# ------------------------------
# repeater_route/repeater.py
# ------------------------------
import requests
import requests_cache
from .config import QUERY_RANGE
from .geo import haversine

# Enable persistent HTTP caching for all requests
requests_cache.install_cache('gmaps_cache', backend='sqlite', expire_after=None)

# RepeaterBook JSON export endpoint
_RB_URL = "https://www.repeaterbook.com/api/export.php"

def fetch_repeaters_for_state(sid):
    """
    Fetch all repeaters for a given state FIPS code via RepeaterBook API.
    Returns a list of repeater dicts.
    """
    params = {
        'state_id': sid,
        'country': 'United States'
    }
    resp = requests.get(_RB_URL, params=params)
    resp.raise_for_status()
    return resp.json()


def filter_repeaters(lat, lon, reps):
    """
    Filter a list of repeaters to those within QUERY_RANGE miles
    of (lat, lon). Returns a sublist of matching repeater dicts.
    """
    return [r for r in reps
            if haversine((lat, lon), (r.get('latitude'), r.get('longitude'))) <= QUERY_RANGE]
