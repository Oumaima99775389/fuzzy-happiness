import json
import logging
import os
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "smartbox/telemetry")
JOURNEY_ID = os.getenv("SMARTBOX_JOURNEY_ID")

API_URL = "http://127.0.0.1:8000/api/v1/telemetry"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        logger.info("Subscribed to topic: %s", MQTT_TOPIC)
    else:
        logger.error("MQTT connection failed: %s", reason_code)


def on_message(client, userdata, message):
    try:
        sensor_data = json.loads(message.payload.decode("utf-8"))

        telemetry = {
            "device_id": sensor_data["device_id"],
            "journey_id": JOURNEY_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": sensor_data["temperature_c"],
            "vibration_g": sensor_data["vibration_g"],
        }

        response = requests.post(
            API_URL,
            json=telemetry,
            timeout=10,
        )

        response.raise_for_status()

        logger.info(
            "Telemetry stored: device=%s, journey=%s",
            telemetry["device_id"],
            telemetry["journey_id"],
        )

    except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as error:
        logger.error("Invalid MQTT message: %s", error)

    except requests.RequestException as error:
        logger.error("API request failed: %s", error)


def main():
    if not MQTT_USERNAME or not MQTT_PASSWORD or not JOURNEY_ID:
        raise RuntimeError("Missing MQTT credentials or journey configuration in .env")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="smartbox-pi-subscriber",
    )

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    logger.info("Connecting to MQTT broker at %s:%s", BROKER_HOST, BROKER_PORT)

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
