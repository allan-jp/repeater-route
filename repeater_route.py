#!/usr/bin/env python3
"""
Sample a Google Maps route by fixed mile intervals, cities at those intervals,
or all cities/towns along the route.

You may supply the route URL via the ROUTE_URI environment variable
or with the `-u/--url` flag.

Usage examples:
    # default: sample every MAP_INTERVAL_MILES (from .env)
    repeater_route.py -u "https://...maps/dir/.../..."

    # override interval to 25 miles
    repeater_route.py -u "https://...maps/dir/.../..." -i 25

    # only cities at the interval points
    repeater_route.py -u "https://...maps/dir/.../..." -c

    # every distinct city/town along the route
    repeater_route.py -u "https://...maps/dir/.../..." -a
"""
import os
import sys
import argparse
from urllib.parse import urlparse, parse_qs, unquote
from math import radians, sin, cos, asin, sqrt

import googlemaps
import polyline
from googlemaps.exceptions import ApiError
from dotenv import load_dotenv

EARTH_RADIUS_MILES = 3959.0


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distance in miles between two (lat, lon) points."""
    lat1, lon1 = a
    lat2, lon2 = b
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return EARTH_RADIUS_MILES * 2 * asin(sqrt(h))


def interpolate(p1: tuple[float, float],
                p2: tuple[float, float],
                fraction: float) -> tuple[float, float]:
    """Linear interpolation between p1 and p2 by fraction [0..1]."""
    lat = p1[0] + (p2[0] - p1[0]) * fraction
    lon = p1[1] + (p2[1] - p1[1]) * fraction
    return (lat, lon)


def parse_maps_url(url: str) -> tuple[str, str]:
    """Extract origin and destination from a Google Maps directions URL."""
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
            orig = unquote(segs[0].replace('+', ' '))
            dest = unquote(segs[-1].replace('+', ' '))
            return orig, dest

    raise ValueError('Cannot parse origin/destination from URL')


def sample_route(client: googlemaps.Client,
                 origin: str,
                 destination: str,
                 interval_miles: float
                 ) -> list[tuple[float, float]]:
    """Fetch the driving route and sample points at fixed mile intervals."""
    try:
        routes = client.directions(origin, destination, mode='driving')
    except ApiError as e:
        sys.exit(f"Google Maps API error: {e.status} – {e.message or ''}")
    if not routes:
        sys.exit('ERROR: no route found.')

    pts = polyline.decode(routes[0]['overview_polyline']['points'])
    cumdist = [0.0]
    for a, b in zip(pts, pts[1:]):
        cumdist.append(cumdist[-1] + haversine(a, b))

    total = cumdist[-1]
    samples = []
    d = 0.0
    while d <= total:
        for i in range(len(cumdist) - 1):
            if cumdist[i] <= d <= cumdist[i + 1]:
                frac = (d - cumdist[i]) / (cumdist[i + 1] - cumdist[i])
                samples.append(interpolate(pts[i], pts[i + 1], frac))
                break
        d += interval_miles
    return samples


def extract_cities(client: googlemaps.Client,
                   coords: list[tuple[float, float]]
                   ) -> list[tuple[str, tuple[float, float]]]:
    """Reverse-geocode coords, returning unique city names with coordinates."""
    seen = set()
    cities = []
    for lat, lon in coords:
        res = client.reverse_geocode((lat, lon))
        if not res:
            continue
        for comp in res[0]['address_components']:
            if 'locality' in comp['types'] or 'postal_town' in comp['types']:
                name = comp['long_name']
                if name not in seen:
                    seen.add(name)
                    cities.append((name, (lat, lon)))
                break
    return cities


def extract_all_cities(client: googlemaps.Client,
                       directions_result: list[dict]
                       ) -> list[tuple[str, tuple[float, float]]]:
    """
    Reverse-geocode the end_location of each step in the first leg,
    returning unique city names with coordinates in encounter order.
    """
    seen = set()
    cities = []
    legs = directions_result[0].get('legs', [])
    if not legs:
        return cities

    for step in legs[0].get('steps', []):
        lat = step['end_location']['lat']
        lon = step['end_location']['lng']
        res = client.reverse_geocode((lat, lon))
        if not res:
            continue
        for comp in res[0]['address_components']:
            if 'locality' in comp['types'] or 'postal_town' in comp['types']:
                name = comp['long_name']
                if name not in seen:
                    seen.add(name)
                    cities.append((name, (lat, lon)))
                break
    return cities


def main() -> None:
    load_dotenv()

    api_key = os.getenv('MAPS_API_KEY')
    if not api_key:
        sys.exit('ERROR: set MAPS_API_KEY in your .env or environment')

    interval_env = os.getenv('MAP_INTERVAL_MILES', '10')
    try:
        default_interval = float(interval_env)
    except ValueError:
        sys.exit('ERROR: MAP_INTERVAL_MILES must be a number')

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-u', '--url',
        help='Google Maps directions URL (overrides ROUTE_URI env)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-i', '--interval',
        type=float,
        help='sampling interval in miles (overrides MAP_INTERVAL_MILES)')
    group.add_argument(
        '-c', '--by-cities',
        action='store_true',
        help='return one coord per city/town at each interval point')
    group.add_argument(
        '-a', '--all-cities',
        action='store_true',
        help='return all distinct cities/towns along the route')
    args = parser.parse_args()

    route_url = args.url or os.getenv('ROUTE_URI')
    if not route_url:
        sys.exit('ERROR: supply a URL with -u/--url or set ROUTE_URI in env')

    interval = args.interval if args.interval is not None else default_interval
    client = googlemaps.Client(key=api_key)

    try:
        origin, destination = parse_maps_url(route_url)
    except ValueError as e:
        sys.exit(f'ERROR: {e}')

    print(f'Origin: {origin}\nDestination: {destination}\n')

    if args.all_cities:
        try:
            routes = client.directions(origin, destination, mode='driving')
        except ApiError as e:
            sys.exit(f"Google Maps API error: {e.status} – {e.message or ''}")
        if not routes:
            sys.exit('ERROR: no route found.')
        all_towns = extract_all_cities(client, routes)
        for name, (lat, lon) in all_towns:
            print(f'{name}: {lat:.6f}, {lon:.6f}')
    else:
        # interval- or interval-with-cities mode both sample the route
        points = sample_route(client, origin, destination, interval)
        if args.by_cities:
            towns = extract_cities(client, points)
            for name, (lat, lon) in towns:
                print(f'{name}: {lat:.6f}, {lon:.6f}')
        else:
            for lat, lon in points:
                print(f'{lat:.6f}, {lon:.6f}')


if __name__ == '__main__':
    main()

