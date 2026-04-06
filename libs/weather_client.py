from __future__ import annotations

import json
from typing import Optional

import requests

from libs.weather_models import WeatherResponse


class WeatherClientError(Exception):
    """Raised when the weather Cloud Function call fails or returns invalid data."""


def fetch_weather(
    function_url: str,
    bearer_token: str,
    *,
    latitude: float,
    longitude: float,
    days: Optional[int] = None,
    hours: Optional[int] = None,
    timeout: Optional[float] = None,
) -> WeatherResponse:
    """
    Call the Cloud Function get_weather_data and parse the result into WeatherResponse.

    Parameters:
    - function_url: Full HTTPS URL to your deployed Cloud Function endpoint
      for get_weather_data. Example:
      https://<region>-<project>.cloudfunctions.net/get_weather_data
      or Firebase v2 URL.
    - bearer_token: OAuth/ID token to send as Authorization: Bearer <token> (required).
    - latitude, longitude: Coordinates for the request.
    - days: If provided, requests daily forecast for N days.
    - hours: If provided, requests hourly forecast for N hours.
      If neither is provided, current conditions are returned.
    - timeout: seconds for the HTTP request timeout. If None, no explicit
      timeout is set and the request may wait indefinitely.

    Returns: WeatherResponse (parsed model). The model preserves extra fields
    in .extra.

    Raises: WeatherClientError on HTTP or parsing errors.
    """

    if days is not None and hours is not None:
        raise ValueError("Provide either days or hours, not both.")

    if not bearer_token:
        raise ValueError("bearer_token is required and must be a non-empty string")

    payload = {
        "latitude": latitude,
        "longitude": longitude,
    }
    if days is not None:
        payload["days"] = days
    if hours is not None:
        payload["hours"] = hours

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {bearer_token}"}

    try:
        if timeout is None:
            resp = requests.post(
                function_url,
                data=json.dumps(payload),
                headers=headers,
            )
        else:
            resp = requests.post(
                function_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=timeout,
            )
    except requests.RequestException as e:
        raise WeatherClientError(f"Request to weather function failed: {e}") from e

    # The Firebase https_fn returns JSON automatically; handle status codes
    if resp.status_code >= 400:
        # Try to surface server-provided error message if any
        try:
            detail = resp.json()
        except ValueError:
            # If response is not JSON, fall back to plain text body
            detail = resp.text
        raise WeatherClientError(
            f"Weather function returned {resp.status_code}: {detail}"
        )

    try:
        data = resp.json()
    except ValueError as e:
        raise WeatherClientError(f"Invalid JSON from weather function: {e}") from e

    # Parse into model
    return WeatherResponse.from_dict(data)


def fetch_current_weather(
    function_url: str,
    bearer_token: str,
    *,
    latitude: float,
    longitude: float,
    timeout: Optional[float] = None,
) -> WeatherResponse:
    """Convenience wrapper to get current conditions."""
    return fetch_weather(
        function_url,
        bearer_token,
        latitude=latitude,
        longitude=longitude,
        timeout=timeout,
    )


def fetch_daily_weather(
    function_url: str,
    bearer_token: str,
    *,
    latitude: float,
    longitude: float,
    days: int,
    timeout: Optional[float] = None,
) -> WeatherResponse:
    """Convenience wrapper to get daily forecast for N days."""
    if days <= 0:
        raise ValueError("days must be > 0")
    return fetch_weather(
        function_url,
        bearer_token,
        latitude=latitude,
        longitude=longitude,
        days=days,
        timeout=timeout,
    )


def fetch_hourly_weather(
    function_url: str,
    bearer_token: str,
    *,
    latitude: float,
    longitude: float,
    hours: int,
    timeout: Optional[float] = None,
) -> WeatherResponse:
    """Convenience wrapper to get hourly forecast for N hours."""
    if hours <= 0:
        raise ValueError("hours must be > 0")
    return fetch_weather(
        function_url,
        bearer_token,
        latitude=latitude,
        longitude=longitude,
        hours=hours,
        timeout=timeout,
    )


__all__ = (
    "fetch_current_weather",
    "fetch_hourly_weather",
    "fetch_daily_weather",
    "WeatherClientError",
    "fetch_weather"
)
