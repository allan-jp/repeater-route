# ------------------------------
# repeater_route/repeater.py
# ------------------------------
import requests_cache
from .config import QUERY_RANGE
from repeaterbook import RepeaterBook
from .geo import haversine

# install cache for HTTP requests
requests_cache.install_cache('gmaps_cache', backend='sqlite', expire_after=None)

_rb = RepeaterBook()

def fetch_repeaters_for_state(sid):
    return _rb.list_repeaters(country='United States', state_id=sid)

def filter_repeaters(lat, lon, reps):
    return [r for r in reps if haversine((lat, lon), (r['latitude'], r['longitude'])) <= QUERY_RANGE]
