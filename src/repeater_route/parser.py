# ------------------------------
# repeater_route/parser.py
# ------------------------------
from urllib.parse import urlparse, parse_qs, unquote

def parse_maps_url(url):
    """Extract origin and destination from Maps URL."""
    u = urlparse(url)
    qs = parse_qs(u.query)
    if 'origin' in qs and 'destination' in qs:
        return unquote(qs['origin'][0]), unquote(qs['destination'][0])
    parts = u.path.split('/dir/')
    if len(parts) > 1:
        segs = [s for s in parts[1].split('/') if s and not s.startswith('@')]
        if len(segs) >= 2:
            orig = unquote(segs[0].replace('+', ' '))
            dest = unquote(segs[-1].replace('+', ' '))
            return orig, dest
    raise ValueError('Invalid Maps URL')
