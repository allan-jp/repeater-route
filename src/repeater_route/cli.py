import sys
import argparse
import googlemaps
from .config import API_KEY, DEFAULT_INTERVAL, ROUTE_URI
from .parser import parse_maps_url
from .cities import extract_cities_hybrid
from .sampler import sample_route

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-u', '--url', help='Maps URL (overrides ROUTE_URI)')
    p.add_argument('-i', '--interval', type=float, help='miles interval')
    p.add_argument('-a', '--all-cities', action='store_true', help='hybrid repeater lookup')
    args = p.parse_args()

    url = args.url or ROUTE_URI or sys.exit('No URL provided')
    origin, dest = parse_maps_url(url)
    client = googlemaps.Client(key=API_KEY)
    interval = args.interval or DEFAULT_INTERVAL

    if args.all_cities:
        reps = extract_cities_hybrid(client, origin, dest, interval)
        for r in reps:
            print(r)
    else:
        for lat, lon in sample_route(client, origin, dest, interval):
            print(f"{lat:.6f},{lon:.6f}")

if __name__ == '__main__':
    main()
