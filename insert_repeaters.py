#!/usr/bin/env python3
"""
setup_repeaters_db.py

Creates (or verifies) a `repeaters` table in your existing SQLite DB
(defaults to gmaps_cache.sqlite) and loads all entries from US_Repeaters.json
into it, using (state_id, rptr_id) as the primary key.
"""

import os
import json
import sqlite3

# ─── Configuration ─────────────────────────────────────────────────────────────
DB_PATH    = os.getenv("DB_PATH", "repeater_route.sqlite")
JSON_PATH  = os.getenv("JSON_PATH", "US_Repeaters.json")

# ─── DDL for the repeater table ─────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS repeaters (
    state_id            TEXT,
    rptr_id             INTEGER,
    frequency           REAL,
    input_freq          REAL,
    pl                  REAL,
    tsq                 REAL,
    nearest_city        TEXT,
    landmark            TEXT,
    county              TEXT,
    state               TEXT,
    country             TEXT,
    latitude            REAL,
    longitude           REAL,
    precise             INTEGER,
    callsign            TEXT,
    use                 TEXT,
    operational_status  TEXT,
    ares                TEXT,
    races               TEXT,
    skywarn             TEXT,
    canwarn             TEXT,
    allstar_node        TEXT,
    echolink_node       TEXT,
    irlp_node           TEXT,
    wires_node          TEXT,
    fm_analog           TEXT,
    fm_bandwidth        TEXT,
    dmr                 TEXT,
    dmr_color_code      TEXT,
    dmr_id              TEXT,
    d_star              TEXT,
    nxdn                TEXT,
    apco_p_25           TEXT,
    p_25_nac            TEXT,
    m17                 TEXT,
    m17_can             TEXT,
    tetra               TEXT,
    tetra_mcc           TEXT,
    tetra_mnc           TEXT,
    system_fusion       TEXT,
    notes               TEXT,
    last_update         TEXT,
    PRIMARY KEY (state_id, rptr_id)
);
"""

# ─── Mapping from JSON keys → DB columns ────────────────────────────────────────
FIELDS = [
    ("State ID",           "state_id",           str),
    ("Rptr ID",            "rptr_id",            int),
    ("Frequency",          "frequency",          float),
    ("Input Freq",         "input_freq",         float),
    ("PL",                 "pl",                 float),
    ("TSQ",                "tsq",                float),
    ("Nearest City",       "nearest_city",       str),
    ("Landmark",           "landmark",           str),
    ("County",             "county",             str),
    ("State",              "state",              str),
    ("Country",            "country",            str),
    ("Lat",                "latitude",           float),
    ("Long",               "longitude",          float),
    ("Precise",            "precise",            int),
    ("Callsign",           "callsign",           str),
    ("Use",                "use",                str),
    ("Operational Status", "operational_status", str),
    ("ARES",               "ares",               str),
    ("RACES",              "races",              str),
    ("SKYWARN",            "skywarn",            str),
    ("CANWARN",            "canwarn",            str),
    ("AllStar Node",       "allstar_node",       str),
    ("EchoLink Node",      "echolink_node",      str),
    ("IRLP Node",          "irlp_node",          str),
    ("Wires Node",         "wires_node",         str),
    ("FM Analog",          "fm_analog",          str),
    ("FM Bandwidth",       "fm_bandwidth",       str),
    ("DMR",                "dmr",                str),
    ("DMR Color Code",     "dmr_color_code",     str),
    ("DMR ID",             "dmr_id",             str),
    ("D-Star",             "d_star",             str),
    ("NXDN",               "nxdn",               str),
    ("APCO P-25",          "apco_p_25",          str),
    ("P-25 NAC",           "p_25_nac",           str),
    ("M17",                "m17",                str),
    ("M17 CAN",            "m17_can",            str),
    ("Tetra",              "tetra",              str),
    ("Tetra MCC",          "tetra_mcc",          str),
    ("Tetra MNC",          "tetra_mnc",          str),
    ("System Fusion",      "system_fusion",      str),
    ("Notes",              "notes",              str),
    ("Last Update",        "last_update",        str),
]


def coerce(value, to_type):
    """Convert empty strings to None, else cast."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    try:
        return to_type(value)
    except Exception:
        return None


def main():
    # 1) ensure the table exists
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(DDL)

    # 2) load JSON
    print(f"Loading JSON from {JSON_PATH!r}…")
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    repeaters = data.get("results", data if isinstance(data, list) else [])
    print(f"Found {len(repeaters)} records in JSON.")

    # 3) prepare our INSERT statement
    db_cols = [db_col for _, db_col, _ in FIELDS]
    placeholders = ", ".join("?" for _ in db_cols)
    stmt = f"""
        INSERT OR REPLACE INTO repeaters ({','.join(db_cols)})
        VALUES ({placeholders});
    """

    # 4) upsert all records
    inserted = 0
    for entry in repeaters:
        values = [
            coerce(entry.get(json_key), to_type)
            for json_key, _, to_type in FIELDS
        ]
        cur.execute(stmt, values)
        inserted += 1
        if inserted % 10000 == 0:
            print(f"  … inserted {inserted} rows so far")

    conn.commit()
    conn.close()
    print(f"✓ Done. Inserted or updated {inserted} repeaters into {DB_PATH!r}")

if __name__ == "__main__":
    main()
