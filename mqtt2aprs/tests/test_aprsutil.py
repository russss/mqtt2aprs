from aprsutil import dd2ddm, format_position, build_weather_message
from datetime import datetime
from pint import UnitRegistry

ureg = UnitRegistry()
Q = ureg.Quantity


def test_dd2ddm():
    deg, mins = dd2ddm(-77.508333)
    assert deg == -77
    assert round(mins, 4) == 30.5


def test_format_position():
    pos = format_position(-77.508333, 164.754167)
    assert pos == "7730.50S/16445.25E"
    assert len(pos) == 9 + 8 + 1

    pos = format_position(51.50610, -0.10820)
    assert pos == "5130.37N/00006.49W"
    assert len(pos) == 9 + 8 + 1

    pos = format_position(51.50610, -0.10820, ambiguity=1)
    assert pos == "5130.3 N/00006.4 W"
    assert len(pos) == 9 + 8 + 1

    pos = format_position(51.50610, -0.10820, ambiguity=2)
    assert pos == "5130.  N/00006.  W"
    assert len(pos) == 9 + 8 + 1


def test_build_message():
    msg = build_weather_message(
        datetime(2022, 7, 3, 16, 23, 32),
        51.50610,
        -0.10820,
        271 * ureg.degree,
        5.5 * ureg.kph,
        10.2 * ureg.kph,
        Q(25.3, ureg.degC),
        45,
        1013.25 * ureg.mbar,
        0.0 * ureg.mm,
        3.2 * ureg.mm,
        30801.3 * ureg.lux,
    )
    assert (
        msg
        == "@162332h5130.37N/00006.49W_271/003g006t078r000p...P013h45b10132L243.Ecowitt WS69"
    )

    msg = build_weather_message(
        datetime(2022, 7, 3, 16, 23, 32),
        51.50610,
        -0.10820,
        271 * ureg.degree,
        5.5 * ureg.kph,
        10.2 * ureg.kph,
        Q(-35, ureg.degC),
        45,
        1013.25 * ureg.mbar,
        2 * ureg.mm,
        3.2 * ureg.mm,
        308301.3 * ureg.lux,
    )
    assert (
        msg
        == "@162332h5130.37N/00006.49W_271/003g006t-31r008p...P013h45b10132l2436.Ecowitt WS69"
    )
