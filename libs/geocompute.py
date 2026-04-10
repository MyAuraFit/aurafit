import math


def move_location(lat, lon, distance_m, bearing_deg):
    """
    Calculates a new GPS coordinate given a starting point, distance, and bearing.

    Parameters:
    - lat (float): Starting latitude in decimal degrees.
    - lon (float): Starting longitude in decimal degrees.
    - distance_m (float): Distance to move in meters.
    - bearing_deg (float): Direction to move in degrees (0° = North, 90° = East, 180° = South, 270° = West).

    Returns:
    - (tuple): A tuple containing the new latitude and longitude (lat, lon) in decimal degrees.

    Example:
        >>> move_location(6.5244, 3.3792, 1000, 180)
        (6.51542, 3.3792)  # ~1 km South of Lagos
    """
    R = 6371000  # Earth's radius in meters

    bearing_rad = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance_m / R)
        + math.cos(lat1) * math.sin(distance_m / R) * math.cos(bearing_rad)
    )

    lon2 = lon1 + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_m / R) * math.cos(lat1),
        math.cos(distance_m / R) - math.sin(lat1) * math.sin(lat2),
    )

    return math.degrees(lat2), math.degrees(lon2)
