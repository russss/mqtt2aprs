import math
from pint import UnitRegistry

ureg = UnitRegistry()


def dd2ddm(dd: float):
    fraction, degrees = math.modf(dd)
    return (int(degrees), abs(fraction * 60))


def format_position(lat: float, lon: float, ambiguity: int = 0):
    lat_degrees, lat_minutes = dd2ddm(lat)
    if lat < 0:
        lat_degrees = -lat_degrees
        lat_hemisphere = "S"
    else:
        lat_hemisphere = "N"

    lon_degrees, lon_minutes = dd2ddm(lon)
    if lon < 0:
        lon_degrees = -lon_degrees
        lon_hemisphere = "W"
    else:
        lon_hemisphere = "E"

    lat_value = f"{lat_degrees:02d}{round(lat_minutes, 2):05.2f}"
    lon_value = f"{lon_degrees:03d}{round(lon_minutes, 2):05.2f}"

    lat_value = lat_value[0 : len(lat_value) - ambiguity] + " " * ambiguity
    lon_value = lon_value[0 : len(lon_value) - ambiguity] + " " * ambiguity

    return f"{lat_value}{lat_hemisphere}/{lon_value}{lon_hemisphere}"


def build_weather_message(
    timestamp,
    lat,
    lon,
    wind_dir,
    wind_speed,
    wind_gust,
    temperature,
    humidity,
    pressure,
    rain_hour,
    rain_since_midnight,
    solar_radiation,
    ambiguity=0,
):
    msg = "@" + timestamp.strftime("%H%M%S") + "h"
    msg += format_position(lat, lon, ambiguity)
    msg += f"_{wind_dir.to(ureg.degree).magnitude:03.0f}/{wind_speed.to(ureg.mph).magnitude:03.0f}"
    msg += f"g{wind_gust.to(ureg.mph).magnitude:03.0f}"
    temp_f = temperature.to(ureg.degF).magnitude
    if temp_f < 0:
        msg += f"t{temp_f:02.0f}"
    else:
        msg += f"t{temp_f:03.0f}"
    msg += f"r{rain_hour.to(ureg.inch).magnitude * 100:03.0f}"
    msg += f"p..."
    msg += f"P{rain_since_midnight.to(ureg.inch).magnitude * 100:03.0f}"
    msg += f"h{humidity:02.0f}"
    msg += f"b{round(pressure.magnitude * 10, 0):05.0f}"

    # Pint doesn't like doing this conversion itself
    radiation_wsm = solar_radiation.to(ureg.lux).magnitude * 0.0079
    if radiation_wsm < 1000:
        msg += f"L{radiation_wsm:03.0f}"
    else:
        msg += f"l{radiation_wsm:04.0f}"

    msg += ".Ecowitt WS69"
    return msg
