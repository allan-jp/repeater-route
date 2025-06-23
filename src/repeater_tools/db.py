# db.py

import math
import os
import sqlite3
from typing import List, Tuple

from models.repeater import Repeater
from .utils import haversine

DB_PATH = os.getenv("DB_PATH", "repeater_route.sqlite")

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_repeaters_within_range(
    center: Tuple[float, float],
    radius_miles: float
) -> List[Repeater]:
    """
    Return all repeaters within `radius_miles` of `center=(lat, lon)`.
    First applies a bounding‐box in SQL, then precise Haversine in Python.
    """
    lat, lon = center

    # approximate degree deltas
    lat_delta = radius_miles / 69.0
    lon_delta = radius_miles / (abs(math.cos(math.radians(lat))) * 69.0)

    sql = """
    SELECT *
      FROM repeaters
     WHERE 
       fm_analog = 'Yes' 
       AND latitude  BETWEEN ? AND ?
       AND longitude BETWEEN ? AND ?
    """
    params = (lat - lat_delta, lat + lat_delta,
              lon - lon_delta, lon + lon_delta)

    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql, params)

    results: List[Repeater] = []
    for row in cur.fetchall():
        if haversine((lat, lon), (row["latitude"], row["longitude"])) <= radius_miles:
            results.append(Repeater.from_row(row))

    conn.close()
    return results

