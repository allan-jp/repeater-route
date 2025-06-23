# repeater_tools/utils.py
import math
from typing import Tuple

def haversine(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Return distance in miles between two (lat, lon) points.
    """
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 3959.0 * 2 * math.asin(math.sqrt(h))

def interpolate(p1, p2, frac):
    """Linear interpolation between p1 and p2 by fraction [0..1]."""
    return (
        p1[0] + (p2[0] - p1[0]) * frac,
        p1[1] + (p2[1] - p1[1]) * frac,
    )

