# ------------------------------
# repeater_route/repeater.py
# ------------------------------
import csv
import sys
import argparse
from typing import List, Tuple

from .cities import extract_cities_hybrid


def get_hybrid_coords(origin: str, dest: str) -> List[Tuple[float, float]]:
    """
    Retrieve the RAW hybrid-step coordinates between origin and destination.
    """
    # The hybrid extractor typically returns List[(lat, lon)]
    return extract_cities_hybrid(origin, dest)


def get_interval_coords(origin: str, dest: str, interval_miles: float) -> List[Tuple[float, float]]:
    """
    Retrieve coordinates sampled every `interval_miles` miles along the route.
    """
    return extract_cities_hybrid(origin, dest, interval_miles)


def output_coords_csv(coords: List[Tuple[float, float]], header: Tuple[str, str]) -> None:
    """
    Print coordinates to stdout in CSV format with given header names.
    """
    writer = csv.writer(sys.stdout)
    writer.writerow([header[0], header[1]])
    for lat, lon in coords:
        writer.writerow([lat, lon])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate route coordinate lists: hybrid step and interval sampling."
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Output both hybrid-step coords and interval coords (default interval=5mi).",
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=5.0,
        help="Sampling interval in miles for interval coords (default: 5)."
    )
    parser.add_argument("origin", type=str, help="Origin location string")
    parser.add_argument("destination", type=str, help="Destination location string")
    args = parser.parse_args()

    origin = args.origin
    dest = args.destination

    if args.all:
        # 1) Hybrid-step coordinates
        hybrid = get_hybrid_coords(origin, dest)
        output_coords_csv(hybrid, header=("hybrid_lat", "hybrid_lon"))
        print()  # blank line
        # 2) Interval coordinates
        interval_coords = get_interval_coords(origin, dest, args.interval)
        output_coords_csv(interval_coords, header=(f"interval_{int(args.interval)}mi_lat", f"interval_{int(args.interval)}mi_lon"))
    else:
        # Default: hybrid-step only
        coords = get_hybrid_coords(origin, dest)
        output_coords_csv(coords, header=("lat", "lon"))

