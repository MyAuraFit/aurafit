from datetime import datetime
from os import makedirs
from os.path import join, exists
from shutil import rmtree

import requests
from urllib.parse import urlencode

from kivy import platform
from kivy.storage.dictstore import DictStore
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def create_google_maps_session(api_key, map_type="roadmap", language="en-US", region="NG", styles=None):
    """
    Creates a session with Google Maps using the Tile API.

    Sends a POST request to create a Google Maps session with the provided parameters. You can customize the
    map type, language, region, and optional map styles.

    Args:
        api_key (str): Your Google Maps API key.
        map_type (str, optional): The type of map. Defaults to "streetview".
        language (str, optional): Language for map labels. Defaults to "en-US".
        region (str, optional): Region for the map. Defaults to "US".
        styles (list of dict, optional): Optional map styles. If provided, must follow Google Maps styling format.

    Returns:
        dict: The JSON response from the API if the request is successful.
        str: Error message or raw response text if the request fails.

    Raises:
        requests.exceptions.RequestException: If the request fails due to a network error.
        ValueError: If the response cannot be parsed as JSON.

    Example:
        >>> api_key = "YOUR_API_KEY"
        >>> result = create_google_maps_session(api_key)
        >>> print(result)

        >>> styles = [
        ...     {"featureType": "road", "elementType": "geometry", "stylers": [{"color": "#000000"}]},
        ...     {"featureType": "landscape", "elementType": "geometry", "stylers": [{"color": "#00FF00"}]}
        ... ]
        >>> result = create_google_maps_session(api_key, styles=styles)
        >>> print(result)
    """
    url = f"https://tile.googleapis.com/v1/createSession?key={api_key}"
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "mapType": map_type,
        "language": language,
        "region": region,
        "highDpi": True,
        "scale": "scaleFactor2x",
    }

    if styles:
        data["styles"] = styles
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    while True:
        try:
            response = session.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            break
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}. Retrying...")
    return response.json()


def generate_tiles_api_url(api_key, session_token, orientation=0):
    """
    Generates a URL for Google Tiles API with the specified session and API key.

    Args:
        session_token (str): Your session key.
        api_key (str): Your API key.
        orientation (int, optional): The orientation of the tiles. Defaults to 0.

    Returns:
        str: The formatted URL for the Google Tiles API.
    """
    base_url = "https://tile.googleapis.com/v1/2dtiles/{z}/{x}/{y}"

    # Create the query parameters
    params = {
        'session': session_token,
        'key': api_key,
        'orientation': orientation
    }

    # Encode the parameters
    query_string = urlencode(params)

    # Construct the full URL with placeholders for z, x, y
    full_url = f"{base_url}?{query_string}"
    print(full_url)

    return full_url


def create_map_tile_url(api_key, map_type="roadmap", language="en-US", region="NG", styles=None, orientation=0):
    """
    Creates a map tile URL by generating a Google Maps session and formatting the tile URL.

    Args:
        api_key (str): Your Google Maps API key.
        map_type (str, optional): The type of map. Defaults to "roadmap".
        language (str, optional): Language for map labels. Defaults to "en-US".
        region (str, optional): Region for the map. Defaults to "NG".
        styles (list of dict, optional): Optional map styles.
        orientation (int, optional): The orientation of the tiles. Defaults to 0.

    Returns:
        str: The formatted URL for the Google Tiles API.
    """
    session_response = create_google_maps_session(api_key, map_type, language, region, styles)
    session_token = session_response["session"]
    return generate_tiles_api_url(api_key, session_token, orientation)


def load_google_map_session():
    api_key = "AIzaSyBCmRIZYu43pGDQqSXLqtxbkWVg67w9PTw"

    if platform == "android":
        _cache_path = join("..", "..", "cache")
    else:
        _cache_path = ""
    store = DictStore(join(_cache_path, "session.dict"))
    map_cache_dir = join(_cache_path, "map")
    if not store.exists("session"):
        if exists(map_cache_dir):
            rmtree(map_cache_dir)
        result = create_google_maps_session(
            api_key=api_key,
            styles=None
        )
        store.put("session", **result)  # noqa
    session_expiry = store.get("session")["expiry"]
    if datetime.fromtimestamp(float(session_expiry)) < datetime.today():
        if exists(map_cache_dir):
            rmtree(map_cache_dir)
        result = create_google_maps_session(
            api_key=api_key,
            styles=None
        )
        store.put("session", **result)  # noqa
    if not exists(map_cache_dir):
        makedirs(map_cache_dir)
    url = generate_tiles_api_url(
        api_key=api_key,
        session_token=store.get("session")["session"]
    )
    return url
