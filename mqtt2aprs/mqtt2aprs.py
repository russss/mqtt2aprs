import click
import aprs
import paho.mqtt.client as mqtt
import logging
import json
from pint import UnitRegistry
from datetime import datetime, timedelta
from aprsutil import build_weather_message

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

aprs_client = None

ureg = UnitRegistry()
Q = ureg.Quantity

last_send = None


def on_message(_client, userdata, message):
    global last_send
    log.debug("Received message: %s", message.payload.decode("utf-8"))

    if last_send is not None and last_send > datetime.now() - timedelta(minutes=5):
        return

    data = json.loads(message.payload.decode("utf-8"))
    msg = f"{userdata['callsign']}-{userdata['ssid']}>APRS,TCPIP*:"

    msg += build_weather_message(
        datetime.utcnow(),
        userdata["lat"],
        userdata["lon"],
        data["winddir"] * ureg.degree,
        data["windspeed"] * ureg.kph,
        data["windgust"] * ureg.kph,
        Q(data["temp"], ureg.degC),
        data["humidity"],
        data["baromabs"] * ureg.mbar,
        data["hourlyrain"] * ureg.mm,
        data["dailyrain"] * ureg.mm,
        data["solarradiation_lux"] * ureg.lux,
        ambiguity=userdata["ambiguity"],
    )
    frame = aprs.parse_frame(msg)
    log.info("Sending message: " + msg)
    aprs_client.send(bytes(frame))
    last_send = datetime.now()


@click.command()
@click.option("--mqtt-host", default="localhost", help="MQTT host")
@click.option("--mqtt-port", default=1883, help="MQTT port")
@click.option("--topic", default="weatherstation", help="MQTT topic")
@click.option("--aprs-server", default="rotate.aprs.net", help="APRS server")
@click.option("--aprs-callsign", required=True, help="APRS callsign")
@click.option("--aprs-passcode", default="", help="APRS passcode")
@click.option("--aprs-ssid", default=13, type=int, help="APRS SSID")
@click.option(
    "--latitude", required=True, type=float, help="Latitude in decimal degrees"
)
@click.option(
    "--longitude", required=True, type=float, help="Longitude in decimal degrees"
)
@click.option(
    "--position-ambiguity",
    default=0,
    type=int,
    help="Number of digits to omit from broadcasted lat/lon",
)
def main(
    mqtt_host,
    mqtt_port,
    topic,
    aprs_server,
    aprs_callsign,
    aprs_passcode,
    aprs_ssid,
    latitude,
    longitude,
    position_ambiguity,
):
    global aprs_client
    log.info(f"Connecting to APRS with callsign {aprs_callsign}...")
    aprs_client = aprs.TCP(
        aprs_callsign.encode("ascii"),
        aprs_passcode,
        servers=[aprs_server.encode("ascii")],
    )
    aprs_client.start()

    client = mqtt.Client(
        userdata={
            "lat": latitude,
            "lon": longitude,
            "ambiguity": position_ambiguity,
            "callsign": aprs_callsign,
            "ssid": aprs_ssid,
        }
    )
    client.connect(mqtt_host, mqtt_port)
    client.subscribe(topic)
    client.on_message = on_message
    client.loop_forever()


if __name__ == "__main__":
    main()
