# ------------------------------
# repeater_route/geo.py
# ------------------------------
from math import radians, sin, cos, asin, sqrt

EARTH_RADIUS_MILES = 3959.0

def haversine(a, b):
    """Miles between two (lat, lon) points."""
    lat1, lon1 = a
    lat2, lon2 = b
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return EARTH_RADIUS_MILES * 2 * asin(sqrt(h))


def interpolate(p1, p2, frac):
    """Linear interpolation p1→p2 at fraction [0..1]."""
    return (p1[0] + (p2[0] - p1[0]) * frac,
            p1[1] + (p2[1] - p1[1]) * frac)
