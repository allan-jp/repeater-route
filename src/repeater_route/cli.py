import sys
import argparse
import googlemaps
from .config import API_KEY, DEFAULT_INTERVAL, ROUTE_URI
from .parser import parse_maps_url
from .sampler import sample_route

def main():
    p = argparse.ArgumentParser(description="Generate route coordinates: hybrid or interval sampling.")
    p.add_argument('-u', '--url', help='Maps URL (overrides ROUTE_URI)')
    p.add_argument('-i', '--interval', type=float, help='miles interval sampling')
    p.add_argument('-a', '--hybrid', action='store_true', help='use hybrid (turn-by-turn) sampling')
    args = p.parse_args()

    url = args.url or ROUTE_URI or sys.exit('No URL provided')
    origin, dest = parse_maps_url(url)
    client = googlemaps.Client(key=API_KEY)

    # Determine sampling mode
    if args.hybrid:
        print("HYBRID MODE")
        # Hybrid: use turn-by-turn step points
        coords = sample_route(client, origin, dest, interval=5)
    else:
        # Interval sampling: use provided interval or default
        interval = args.interval if args.interval is not None else DEFAULT_INTERVAL
        coords = sample_route(client, origin, dest, interval)

    # Output CSV to stdout
    for lat, lon in coords:
        print(f"{lat:.6f},{lon:.6f}")

if __name__ == '__main__':
    main()

