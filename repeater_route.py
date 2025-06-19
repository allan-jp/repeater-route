#!/usr/bin/env python3
import argparse
import yaml
import sys
from urllib.parse import urlparse, parse_qs, unquote
import googlemaps
import polyline
from math import radians, cos, sin, asin, sqrt

# -----------------------------------------------------------------------------
# Helpers: distance (Haversine) & linear interpolation
# -----------------------------------------------------------------------------
def haversine(a, b):
    """Return distance in miles between two (lat, lon) points."""
    lat1, lon1 = a; lat2, lon2 = b
    # convert degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1; dlon = lon2 - lon1
    hav = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 3959 * 2 * asin(sqrt(hav))

def interpolate(p1, p2, fraction):
    """Linear interp between p1 and p2 by fraction [0..1]."""
    lat = p1[0] + (p2[0] - p1[0]) * fraction
    lon = p1[1] + (p2[1] - p1[1]) * fraction
    return (lat, lon)

# -----------------------------------------------------------------------------
# Parse the Google Maps URL for origin/destination
# -----------------------------------------------------------------------------
def parse_maps_url(url: str):
    u = urlparse(url)
    # Case A: URL with ?api=1&origin=...&destination=...
    qs = parse_qs(u.query)
    if "origin" in qs and "destination" in qs:
        orig = unquote(qs["origin"][0])
        dest = unquote(qs["destination"][0])
        return orig, dest

    # Case B: /maps/dir/Origin/Waypoint/.../Destination
    parts = u.path.split("/dir/")
    if len(parts) > 1:
        segments = parts[1].split("/")
        # first and last segments are origin and dest
        orig = unquote(segments[0].replace("+", " "))
        dest = unquote(segments[-1].replace("+", " "))
        return orig, dest

    raise ValueError("Cannot parse origin/destination from URL")

# -----------------------------------------------------------------------------
# Main functionality
# -----------------------------------------------------------------------------
def sample_route(client, origin, destination, interval_miles):
    # 1) fetch directions
    routes = client.directions(origin, destination, mode="driving", alternatives=False)
    if not routes:
        sys.exit("No route found.")
    overview = routes[0]["overview_polyline"]["points"]
    waypoints = polyline.decode(overview)

    # 2) build cumulative distances
    cumdist = [0.0]
    for a, b in zip(waypoints, waypoints[1:]):
        cumdist.append(cumdist[-1] + haversine(a, b))

    total = cumdist[-1]
    samples = []
    d = 0.0
    # 3) sample at each interval
    while d <= total:
        # find segment
        for i in range(len(cumdist)-1):
            if cumdist[i] <= d <= cumdist[i+1]:
                frac = (d - cumdist[i]) / (cumdist[i+1] - cumdist[i])
                samples.append(interpolate(waypoints[i], waypoints[i+1], frac))
                break
        d += interval_miles
    return samples

def extract_cities(client, coords):
    seen = set()
    cities = []
    for lat, lon in coords:
        res = client.reverse_geocode((lat, lon))
        # find locality or admin_area_level_2
        for comp in res[0]["address_components"]:
            if "locality" in comp["types"] or "postal_town" in comp["types"]:
                name = comp["long_name"]
                if name not in seen:
                    seen.add(name)
                    cities.append((name, (lat, lon)))
                break
    return cities

def main():
    p = argparse.ArgumentParser(
        description="Sample a Google Maps route at fixed mile intervals or by city."
    )
    p.add_argument("url", help="Google Maps directions URL")
    p.add_argument(
        "--interval", "-i",
        type=float,
        help="sampling interval in miles (default from config)"
    )
    p.add_argument(
        "--by-cities", "-c",
        action="store_true",
        help="instead of fixed interval, return one coord per city/town on route"
    )
    args = p.parse_args()

    # load config
    cfg = yaml.safe_load(open("config.yaml"))
    key = cfg.get("api_key")
    if not key:
        sys.exit("Put your Maps API key into config.yaml under 'api_key'")

    interval = args.interval or cfg.get("map_interval_miles", 10.0)

    # init client
    gmaps = googlemaps.Client(key=key)

    # parse URL
    origin, destination = parse_maps_url(args.url)
    print(f"Origin: {origin}\nDestination: {destination}\n")

    if args.by_cities:
        # decode full route, then extract cities
        raw = sample_route(gmaps, origin, destination, interval_miles=interval)
        towns = extract_cities(gmaps, raw)
        for name, (lat, lon) in towns:
            print(f"{name}: {lat:.6f}, {lon:.6f}")
    else:
        pts = sample_route(gmaps, origin, destination, interval_miles=interval)
        for lat, lon in pts:
            print(f"{lat:.6f}, {lon:.6f}")

if __name__ == "__main__":
    main()
