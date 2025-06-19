# ------------------------------
# repeater_route/cities.py
# ------------------------------
# ------------------------------
# repeater_route/cities.py
# ------------------------------
from .sampler import sample_route


def extract_cities_hybrid(client, origin: str, dest: str, interval: float) -> list[tuple[float, float]]:
    """
    Retrieve coordinates along the route from origin to dest.

    - Uses a hybrid sampling (turn-by-turn waypoints) when interval is None or 0.
    - When interval > 0, returns points sampled every `interval` miles.

    :param client:      HTTP or routing client for sample_route
    :param origin:      Origin location string (address or place name)
    :param dest:        Destination location string
    :param interval:    Sampling interval in miles; if 0 or None, hybrid-step only
    :return:            List of (latitude, longitude) tuples
    """
    # Delegate to sampler.sample_route: handles both hybrid and interval sampling
    return sample_route(client, origin, dest, interval)
