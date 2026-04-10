from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


# The Google Weather API returns deeply nested JSON. To keep the client flexible and
# resilient to API changes, we model the common/important structures while also
# preserving the original payload in an "raw" field where appropriate.
#
# Parsing is done via from_dict classmethods that tolerate missing keys.


@dataclass
class TimeZone:
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "TimeZone":
        data = data or {}
        return cls(id=data.get("id"))


@dataclass
class Interval:
    startTime: Optional[str] = None
    endTime: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Interval":
        data = data or {}
        return cls(
            startTime=data.get("startTime"),
            endTime=data.get("endTime"),
        )


@dataclass
class DisplayDate:
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "DisplayDate":
        data = data or {}
        return cls(
            year=data.get("year"),
            month=data.get("month"),
            day=data.get("day"),
        )


@dataclass
class Quantity:
    quantity: Optional[float] = None
    unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Quantity":
        data = data or {}
        # Some APIs use value instead of quantity; keep flexible
        q = data.get("quantity", data.get("value"))
        return cls(quantity=q, unit=data.get("unit"))


@dataclass
class Probability:
    percent: Optional[float] = None
    type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Probability":
        data = data or {}
        return cls(percent=data.get("percent"), type=data.get("type"))


@dataclass
class Precipitation:
    probability: Optional[Probability] = None
    qpf: Optional[Quantity] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Precipitation":
        data = data or {}
        return cls(
            probability=Probability.from_dict(data.get("probability")),
            qpf=Quantity.from_dict(data.get("qpf")),
        )


@dataclass
class Direction:
    degrees: Optional[int] = None
    cardinal: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Direction":
        data = data or {}
        return cls(
            degrees=data.get("degrees"),
            cardinal=data.get("cardinal"),
        )


@dataclass
class Speed:
    value: Optional[float] = None
    unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Speed":
        data = data or {}
        return cls(value=data.get("value"), unit=data.get("unit"))


@dataclass
class Wind:
    direction: Optional[Direction] = None
    speed: Optional[Speed] = None
    gust: Optional[Speed] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Wind":
        data = data or {}
        return cls(
            direction=Direction.from_dict(data.get("direction")),
            speed=Speed.from_dict(data.get("speed")),
            gust=Speed.from_dict(data.get("gust")),
        )


@dataclass
class WeatherDescription:
    text: Optional[str] = None
    languageCode: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WeatherDescription":
        data = data or {}
        return cls(text=data.get("text"), languageCode=data.get("languageCode"))


@dataclass
class WeatherCondition:
    iconBaseUri: Optional[str] = None
    description: Optional[WeatherDescription] = None
    type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WeatherCondition":
        data = data or {}
        return cls(
            iconBaseUri=data.get("iconBaseUri"),
            description=WeatherDescription.from_dict(data.get("description")),
            type=data.get("type"),
        )


@dataclass
class PartForecast:
    interval: Optional[Interval] = None
    weatherCondition: Optional[WeatherCondition] = None
    relativeHumidity: Optional[float] = None
    uvIndex: Optional[float] = None
    precipitation: Optional[Precipitation] = None
    thunderstormProbability: Optional[float] = None
    wind: Optional[Wind] = None
    cloudCover: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PartForecast":
        data = data or {}
        return cls(
            interval=Interval.from_dict(data.get("interval")),
            weatherCondition=WeatherCondition.from_dict(data.get("weatherCondition")),
            relativeHumidity=data.get("relativeHumidity"),
            uvIndex=data.get("uvIndex"),
            precipitation=Precipitation.from_dict(data.get("precipitation")),
            thunderstormProbability=data.get("thunderstormProbability"),
            wind=Wind.from_dict(data.get("wind")),
            cloudCover=data.get("cloudCover"),
        )


@dataclass
class Temperature:
    degrees: Optional[float] = None
    unit: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Temperature":
        data = data or {}
        return cls(degrees=data.get("degrees"), unit=data.get("unit"))


@dataclass
class ForecastDay:
    interval: Optional[Interval] = None
    displayDate: Optional[DisplayDate] = None
    daytimeForecast: Optional[PartForecast] = None
    nighttimeForecast: Optional[PartForecast] = None
    maxTemperature: Optional[Temperature] = None
    minTemperature: Optional[Temperature] = None
    feelsLikeMaxTemperature: Optional[Temperature] = None
    feelsLikeMinTemperature: Optional[Temperature] = None
    maxHeatIndex: Optional[Temperature] = None
    iceThickness: Optional[Quantity] = None
    # Preserve unknown/extra fields
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ForecastDay":
        data = data or {}
        known_keys = {
            "interval",
            "displayDate",
            "daytimeForecast",
            "nighttimeForecast",
            "maxTemperature",
            "minTemperature",
            "feelsLikeMaxTemperature",
            "feelsLikeMinTemperature",
            "maxHeatIndex",
            "iceThickness",
        }
        extra = {k: v for k, v in data.items() if k not in known_keys}
        return cls(
            interval=Interval.from_dict(data.get("interval")),
            displayDate=DisplayDate.from_dict(data.get("displayDate")),
            daytimeForecast=PartForecast.from_dict(data.get("daytimeForecast")),
            nighttimeForecast=PartForecast.from_dict(data.get("nighttimeForecast")),
            maxTemperature=Temperature.from_dict(data.get("maxTemperature")),
            minTemperature=Temperature.from_dict(data.get("minTemperature")),
            feelsLikeMaxTemperature=Temperature.from_dict(
                data.get("feelsLikeMaxTemperature")
            ),
            feelsLikeMinTemperature=Temperature.from_dict(
                data.get("feelsLikeMinTemperature")
            ),
            maxHeatIndex=Temperature.from_dict(data.get("maxHeatIndex")),
            iceThickness=Quantity.from_dict(data.get("iceThickness")),
            extra=extra,
        )


@dataclass
class ForecastHour:
    interval: Optional[Interval] = None
    weatherCondition: Optional[WeatherCondition] = None
    temperature: Optional[Temperature] = None
    feelsLikeTemperature: Optional[Temperature] = None
    precipitation: Optional[Precipitation] = None
    wind: Optional[Wind] = None
    relativeHumidity: Optional[float] = None
    cloudCover: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ForecastHour":
        data = data or {}
        known_keys = {
            "interval",
            "weatherCondition",
            "temperature",
            "feelsLikeTemperature",
            "precipitation",
            "wind",
            "relativeHumidity",
            "cloudCover",
        }
        extra = {k: v for k, v in data.items() if k not in known_keys}
        return cls(
            interval=Interval.from_dict(data.get("interval")),
            weatherCondition=WeatherCondition.from_dict(data.get("weatherCondition")),
            temperature=Temperature.from_dict(data.get("temperature")),
            feelsLikeTemperature=Temperature.from_dict(
                data.get("feelsLikeTemperature")
            ),
            precipitation=Precipitation.from_dict(data.get("precipitation")),
            wind=Wind.from_dict(data.get("wind")),
            relativeHumidity=data.get("relativeHumidity"),
            cloudCover=data.get("cloudCover"),
            extra=extra,
        )


@dataclass
class CurrentConditions:
    interval: Optional[Interval] = None
    weatherCondition: Optional[WeatherCondition] = None
    temperature: Optional[Temperature] = None
    feelsLikeTemperature: Optional[Temperature] = None
    wind: Optional[Wind] = None
    relativeHumidity: Optional[float] = None
    cloudCover: Optional[float] = None
    precipitation: Optional[Precipitation] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CurrentConditions":
        data = data or {}
        known_keys = {
            "interval",
            "weatherCondition",
            "temperature",
            "feelsLikeTemperature",
            "wind",
            "relativeHumidity",
            "cloudCover",
            "precipitation",
        }
        extra = {k: v for k, v in data.items() if k not in known_keys}
        return cls(
            interval=Interval.from_dict(data.get("interval")),
            weatherCondition=WeatherCondition.from_dict(data.get("weatherCondition")),
            temperature=Temperature.from_dict(data.get("temperature")),
            feelsLikeTemperature=Temperature.from_dict(
                data.get("feelsLikeTemperature")
            ),
            wind=Wind.from_dict(data.get("wind")),
            relativeHumidity=data.get("relativeHumidity"),
            cloudCover=data.get("cloudCover"),
            precipitation=Precipitation.from_dict(data.get("precipitation")),
            extra=extra,
        )


@dataclass
class WeatherResponse:
    # Depending on endpoint, either forecastDays, forecastHours, or currentConditions-like payload
    forecastDays: List[ForecastDay] = field(default_factory=list)
    forecastHours: List[ForecastHour] = field(default_factory=list)
    current: Optional[CurrentConditions] = None
    timeZone: Optional[TimeZone] = None
    # The API may include nextPageToken, but we usually remove it after aggregation.
    nextPageToken: Optional[str] = None
    # Keep any additional top-level data (e.g., currentConditions fields)
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WeatherResponse":
        data = data or {}
        tz = (
            TimeZone.from_dict(data.get("timeZone"))
            if isinstance(data.get("timeZone"), dict)
            else (
                TimeZone(id=data.get("timeZone"))
                if isinstance(data.get("timeZone"), str)
                else None
            )
        )
        days = [ForecastDay.from_dict(x) for x in (data.get("forecastDays") or [])]
        hours = [ForecastHour.from_dict(x) for x in (data.get("forecastHours") or [])]
        # Some responses may inline current conditions at top-level under various keys.
        # Prefer a key named "current" if present, otherwise use the remaining fields
        # as a current-conditions-like structure when no days/hours lists exist.
        current_payload: Optional[Dict[str, Any]] = None
        if isinstance(data.get("current"), dict):
            current_payload = data.get("current")
        elif not days and not hours:
            # Treat the whole payload (minus known keys) as current-like
            current_payload = data
        known_keys = {
            "forecastDays",
            "forecastHours",
            "timeZone",
            "nextPageToken",
            "current",
        }
        extra = {k: v for k, v in data.items() if k not in known_keys}
        return cls(
            forecastDays=days,
            forecastHours=hours,
            current=(
                CurrentConditions.from_dict(current_payload)
                if current_payload is not None
                else None
            ),
            timeZone=tz,
            nextPageToken=data.get("nextPageToken"),
            extra=extra,
        )

    def to_dict(self) -> Dict[str, Any]:
        # Convert back to dict, merging known fields and extra payload.
        d: Dict[str, Any] = {}
        if self.forecastDays:
            d["forecastDays"] = [asdict(fd) for fd in self.forecastDays]
        if self.forecastHours:
            d["forecastHours"] = [asdict(fh) for fh in self.forecastHours]
        if self.current is not None:
            d["current"] = asdict(self.current)
        if self.timeZone is not None:
            d["timeZone"] = asdict(self.timeZone)
        if self.nextPageToken is not None:
            d["nextPageToken"] = self.nextPageToken
        d.update(self.extra)
        return d


__all__ = [
    "TimeZone",
    "Interval",
    "DisplayDate",
    "Quantity",
    "Probability",
    "Precipitation",
    "Direction",
    "Speed",
    "Wind",
    "WeatherDescription",
    "WeatherCondition",
    "PartForecast",
    "Temperature",
    "ForecastDay",
    "ForecastHour",
    "CurrentConditions",
    "WeatherResponse",
]
