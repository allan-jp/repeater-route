# ------------------------------
# repeater_route/cities.py
# ------------------------------
from .sampler import sample_route
from .state_lookup import latlon_to_fips
from .repeater import fetch_repeaters_for_state, filter_repeaters

def extract_cities_hybrid(client, origin, dest, interval):
    pts = sample_route(client, origin, dest, interval)
    seen_states = {}
    results = []
    for lat, lon in pts:
        sid = latlon_to_fips(client, lat, lon)
        if not sid:
            continue
        if sid not in seen_states:
            seen_states[sid] = fetch_repeaters_for_state(sid)
        for r in filter_repeaters(lat, lon, seen_states[sid]):
            results.append(r)
    return results
