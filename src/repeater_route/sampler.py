# ------------------------------
# repeater_route/sampler.py
# ------------------------------
import googlemaps, polyline
from .geo import haversine, interpolate
from googlemaps.exceptions import ApiError
import sys

def sample_route(client, origin, dest, interval):
    """Sample points every `interval` miles along route."""
    try:
        routes = client.directions(origin, dest, mode='driving')
    except ApiError as e:
        sys.exit(f"Directions API error: {e}")
    if not routes:
        sys.exit('No route found')
    pts = polyline.decode(routes[0]['overview_polyline']['points'])
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + haversine(a, b))
    total = cum[-1]
    out = []
    d = 0.0
    while d <= total:
        for i in range(len(cum) - 1):
            if cum[i] <= d <= cum[i+1]:
                frac = (d - cum[i]) / (cum[i+1] - cum[i])
                out.append(interpolate(pts[i], pts[i+1], frac))
                break
        d += interval
    return out
