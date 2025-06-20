#!/usr/bin/env python3
"""
repeater_route.py

Sample a Google Maps route and output a contiguous list of latitude/longitude
coordinates spaced at a fixed mile interval along the route.

Usage:
    python repeater_route.py -u "<GOOGLE_MAPS_DIRECTIONS_URL>" [-i N]

Configuration via .env:
    MAPS_API_KEY        Google Maps API key (Directions & Geocoding enabled)
    MAP_INTERVAL_MILES  Default sampling interval in miles (float, default 5)
    ROUTE_URI           Optional default Google Maps URL
"""
import os
import sys
import argparse

from dotenv import load_dotenv
import requests_cache

# -----------------------------------------------------------------------------
# Bootstrap & caching
# -----------------------------------------------------------------------------
#  - load environment variables
#  - install a requests_cache so that all googlemaps calls (including reverse-
#    geocode later on) get cached to 'gmaps_cache.sqlite'
load_dotenv()
requests_cache.install_cache("gmaps_cache", backend="sqlite", expire_after=None)

# -----------------------------------------------------------------------------
# Third‐party / local imports that depend on the env & cache being in place
# -----------------------------------------------------------------------------
from repeater_tools.route_sampler import parse_maps_url, sample_route

# -----------------------------------------------------------------------------
# Config defaults & parsing
# -----------------------------------------------------------------------------
MAP_INTERVAL = float(os.getenv("MAP_INTERVAL_MILES", "5"))
ROUTE_URI    = os.getenv("ROUTE_URI", "").strip()

# -----------------------------------------------------------------------------
# CLI entry point
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "-u", "--url",
        help="Google Maps directions URL (overrides ROUTE_URI env var)"
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        help="sampling interval in miles (default MAP_INTERVAL_MILES)"
    )
    args = parser.parse_args()

    url = args.url or ROUTE_URI
    if not url:
        sys.exit("Provide a Google Maps URL with -u or set ROUTE_URI in .env")

    try:
        origin, destination = parse_maps_url(url)
    except ValueError as e:
        sys.exit(f"URL parse error: {e}")

    print(f"Origin:      {origin}")
    print(f"Destination: {destination}\n")

    interval = args.interval or MAP_INTERVAL
    coords = sample_route(origin, destination, interval)

    for lat, lon in coords:
        print(f"{lat:.6f}, {lon:.6f}")

if __name__ == "__main__":
    main()

