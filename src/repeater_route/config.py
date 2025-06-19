import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('MAPS_API_KEY')
if not API_KEY:
    raise RuntimeError('MAPS_API_KEY not set in environment')

DEFAULT_INTERVAL = float(os.getenv('MAP_INTERVAL_MILES', '10'))
QUERY_RANGE = float(os.getenv('QUERY_RANGE', '15'))  # miles
ROUTE_URI = os.getenv('ROUTE_URI')
