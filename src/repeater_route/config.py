# ------------------------------
# src/repeater_route/config.py
# ------------------------------
import os
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('MAPS_API_KEY') or sys.exit('MAPS_API_KEY not set')
DEFAULT_INTERVAL = float(os.getenv('MAP_INTERVAL_MILES', '5'))

USER_EMAIL = os.getenv('USER_EMAIL')
PROGRAM_NAME = os.getenv('PROGRAM_NAME')
PROGRAM_VERSION = os.getenv('PROGRAM_VERSION')

QUERY_RANGE = float(os.getenv('QUERY_RANGE', '15'))  # miles

# Comma-separated list of bands in MHz, e.g. 144,440
QUERY_BANDS = [float(b) for b in os.getenv('QUERY_BANDS', '').split(',') if b]
# Comma-separated list of modes, e.g. FM,DMR
QUERY_MODES = [m.strip().upper() for m in os.getenv('QUERY_MODES', '').split(',') if m]

ROUTE_URI = os.getenv('ROUTE_URI')


