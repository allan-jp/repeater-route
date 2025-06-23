# repeater_tools/route_sampler.py
import googlemaps, polyline, os, sys
from .utils import haversine, interpolate
from urllib.parse import urlparse, parse_qs, unquote
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('MAPS_API_KEY') or sys.exit("Set MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

# -----------------------------------------------------------------------------
# Parse Google Maps directions URL
# -----------------------------------------------------------------------------
def parse_maps_url(url):
    u = urlparse(url)
    qs = parse_qs(u.query)
    # case A: ?api=1&origin=...&destination=...
    if 'origin' in qs and 'destination' in qs:
        return unquote(qs['origin'][0]), unquote(qs['destination'][0])
    # case B: /maps/dir/Origin/.../Destination
    parts = u.path.split('/dir/')
    if len(parts) > 1:
        segs = [s for s in parts[1].split('/') if s and not s.startswith('@')]
        if len(segs) >= 2:
            orig = unquote(segs[0].replace('+',' '))
            dest = unquote(segs[-1].replace('+',' '))
            return orig, dest
    raise ValueError("Cannot parse origin/destination from URL")

# -----------------------------------------------------------------------------
# Google Maps client & sampling
# -----------------------------------------------------------------------------
gmaps = googlemaps.Client(key=API_KEY)

def sample_route(origin, destination, interval):
    """
    Fetch driving directions and sample points every `interval` miles.
    Returns a list of (lat, lon) tuples.
    """
    routes = gmaps.directions(origin, destination, mode='driving')
    if not routes:
        sys.exit("No route found between origin and destination.")
    pts = polyline.decode(routes[0]['overview_polyline']['points'])
    # build cumulative distances
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + haversine(a, b))
    total = cum[-1]
    samples = []
    d = 0.0
    while d <= total:
        # find segment containing distance d
        for i in range(len(cum) - 1):
            if cum[i] <= d <= cum[i+1]:
                frac = (d - cum[i]) / (cum[i+1] - cum[i])
                samples.append(interpolate(pts[i], pts[i+1], frac))
                break
        d += interval
    return samples


