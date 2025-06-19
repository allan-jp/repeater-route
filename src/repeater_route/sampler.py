
# ------------------------------
# repeater_route/sampler.py
# ------------------------------
import sys
import googlemaps
import polyline
from .geo import haversine, interpolate
from googlemaps.exceptions import ApiError


def sample_route(client: googlemaps.Client, origin: str, dest: str, interval: float = 0) -> list[tuple[float, float]]:
    """
    Sample route points between origin and dest.

    - If interval <= 0: return all detailed polyline points for every step in each leg.
    - If interval > 0: sample points every `interval` miles along the overview path.

    :param client:   Google Maps client
    :param origin:   Starting location string
    :param dest:     Ending location string
    :param interval: Sampling interval in miles; if <=0, return all step polyline points
    :return:         List of (lat, lon) tuples
    """
    try:
        routes = client.directions(origin, dest, mode='driving')
    except ApiError as e:
        sys.exit(f"Directions API error: {e}")
    if not routes:
        sys.exit('No route found')

    route = routes[0]

    # Hybrid-step: decode every step's full polyline for detailed points
    if interval is None or interval <= 0:
        detailed_pts: list[tuple[float, float]] = []
        for leg in route.get('legs', []):
            for step in leg.get('steps', []):
                step_poly = step.get('polyline', {}).get('points')
                if step_poly:
                    decoded = polyline.decode(step_poly)
                    detailed_pts.extend(decoded)
        return detailed_pts

    # Interval sampling: use overview path
    overview_poly = route.get('overview_polyline', {}).get('points')
    if not overview_poly:
        sys.exit('No overview polyline available')

    overview_pts = polyline.decode(overview_poly)
    # Compute cumulative distances along overview
    cum: list[float] = [0.0]
    for a, b in zip(overview_pts, overview_pts[1:]):
        cum.append(cum[-1] + haversine(a, b))
    total = cum[-1]

    sampled: list[tuple[float, float]] = []
    d = 0.0
    # Sample every `interval` miles
    while d <= total:
        # find the segment containing distance d
        for i in range(len(cum) - 1):
            if cum[i] <= d <= cum[i+1]:
                # avoid zero-length segments
                denom = cum[i+1] - cum[i] or 1
                frac = (d - cum[i]) / denom
                sampled.append(interpolate(overview_pts[i], overview_pts[i+1], frac))
                break
        d += interval
    return sampled

