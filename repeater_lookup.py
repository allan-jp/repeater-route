#!/usr/bin/env python3
"""
repeater_lookup.py

Sample a Google Maps route and lookup nearby HAM repeaters along the way,
then output a CHIRP‐compatible CSV.
"""
import os
import sys
import argparse

from dotenv import load_dotenv
import requests_cache

# ─── ensure env + HTTP caching before anything that calls Google ───────────────
load_dotenv()
requests_cache.install_cache('repeater_route', backend='sqlite', expire_after=None)

# ─── ensure we can import our src/ packages if not installed ────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from repeater_tools.route_sampler import parse_maps_url, sample_route
from repeater_tools.db          import get_repeaters_within_range
from repeater_tools.csv_writer  import CSVWriter

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        '-u', '--url',
        help='Google Maps URL (or set ROUTE_URI in env)')
    p.add_argument(
        '-i', '--interval',
        type=float,
        help='Miles between route samples (default: MAP_INTERVAL_MILES env or 5)')
    p.add_argument(
        '-r', '--radius',
        type=float,
        help='Search radius in miles (default: QUERY_RANGE env or 5)')
    p.add_argument(
        '-o', '--output',
        default='repeaters.csv',
        help='Output CSV filename (default: %(default)s)')
    args = p.parse_args()

    url = args.url or os.getenv('ROUTE_URI')
    if not url:
        p.error("Provide --url or set ROUTE_URI in your .env")

    origin, dest = parse_maps_url(url)
    interval = args.interval or float(os.getenv('MAP_INTERVAL_MILES', '5'))
    radius   = args.radius   or float(os.getenv('QUERY_RANGE',        '5'))

    # 1) sample the driving route
    coords = sample_route(origin, dest, interval)

    # 2) collect all nearby repeaters
    all_reps = []
    for lat, lon in coords:
        reps = get_repeaters_within_range((lat, lon), radius)
        all_reps.extend(reps)

    # 3) dedupe by key fields
    seen = set()
    unique = []
    for rpt in all_reps:
        key = (
            rpt.callsign,
            rpt.notes,
            rpt.frequency,
            rpt.offset,
            rpt.offset_dir,
            rpt.tone_mode,
            rpt.tone
        )
        if key not in seen:
            seen.add(key)
            unique.append(rpt)

    # 4) write CHIRP CSV
    writer = CSVWriter(args.output)
    writer.write_chirp_csv(unique)

    print(f"Wrote {len(unique)} unique repeaters to {args.output}")

if __name__ == '__main__':
    main()

