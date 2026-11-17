"""
Bridge between the MQTT broker and the application.

paho-mqtt runs its network loop in a background thread (loop_start): the callbacks below are executed
in that thread, not in the FastAPI event loop. Each message therefore opens its own database session.

Topics (one subtree per device serial):
    sensorhub/<serial>/telemetry  device -> server  {"temperature": 24.3, "humidity": 61}
    sensorhub/<serial>/status     device -> server  {"online": true, "config_version": 3}  (LWT: {"online": false})
    sensorhub/<serial>/config     server -> device  {"version": 4, "min_temp": 12, ...}   retained, QoS 1
    sensorhub/<serial>/ack        device -> server  {"version": 4}
"""
import json
import logging

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from sqlmodel import Session

from modules.crud import device as crud
from modules.database import engine
from modules.events import bus
from modules.models.device import DeviceConfigSql, DeviceSql
from utils.settings import settings

logger = logging.getLogger(__name__)


class MqttBridge:
    def __init__(self):
        self.root = settings.MQTT_TOPIC_ROOT
        self.client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="sensorhub-backend")
        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        if settings.MQTT_TLS:
            self.client.tls_set()  # verify the broker certificate with the system CAs
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    # ---------- lifecycle ----------
    def start(self) -> None:
        # connect_async + loop_start: the app starts even if the broker is down, paho retries in background
        self.client.connect_async(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=30)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.disconnect()
        self.client.loop_stop()

    # ---------- callbacks (paho thread) ----------
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            logger.error("MQTT connection refused: %s", reason_code)
            return
        logger.info("Connected to MQTT broker %s:%s", settings.MQTT_HOST, settings.MQTT_PORT)
        # Subscribing in on_connect restores the subscriptions after every reconnection
        client.subscribe([(f"{self.root}/+/telemetry", 0), (f"{self.root}/+/status", 1), (f"{self.root}/+/ack", 1)])

    def _on_message(self, client, userdata, msg):
        try:
            with Session(engine) as session:
                self.handle(session, msg.topic, msg.payload)
        except Exception:  # never let an exception kill the network thread
            logger.exception("Error handling MQTT message on %s", msg.topic)

    # ---------- application logic (testable without a broker) ----------
    def handle(self, session: Session, topic: str, raw: bytes) -> None:
        try:
            _, serial, kind = topic.split("/")
            payload = json.loads(raw or b"{}")
        except ValueError:
            logger.warning("Malformed message on %s", topic)
            return

        device = crud.get_device_by_serial(session, serial)
        if device is None:
            logger.info("Message from unknown device %s ignored", serial)
            return

        if kind == "telemetry":
            reading = crud.add_reading(session, device, payload)
            bus.publish("telemetry", {"device_id": str(device.id), "serial": serial, "ts": reading.ts.isoformat(),
                                      "temperature": reading.temperature, "humidity": reading.humidity})
        elif kind == "status":
            online = bool(payload.get("online"))
            crud.set_online(session, device, online, payload.get("config_version"))
            self._publish_status(device)
            if online:
                self.reconcile(session, device)
        elif kind == "ack":
            crud.set_reported_version(session, device, int(payload.get("version", 0)))
            self._publish_status(device)

    @staticmethod
    def _publish_status(device: DeviceSql) -> None:
        """Live event for the dashboards: online flag and applied configuration version."""
        bus.publish("status", {"device_id": str(device.id), "serial": device.serial, "online": device.online,
                               "reported_version": device.reported_version})

    def reconcile(self, session: Session, device: DeviceSql) -> bool:
        """Desired vs reported: if the device runs an older configuration, send the latest one."""
        config = session.get(DeviceConfigSql, device.id)
        if config is not None and device.reported_version < config.version:
            logger.info("%s runs v%s, desired v%s: resending", device.serial, device.reported_version, config.version)
            self.publish_config(device.serial, config)
            return True
        return False

    def publish_config(self, serial: str, config: DeviceConfigSql) -> None:
        if not self.client.is_connected():
            # Nothing is lost: the DB keeps the desired version, reconcile() sends it when the device reconnects
            logger.warning("Broker not connected: config v%s for %s not sent now", config.version, serial)
            return
        payload = json.dumps({"version": config.version, "min_temp": config.min_temp,
                              "max_temp": config.max_temp, "sampling_sec": config.sampling_sec})
        self.client.publish(f"{self.root}/{serial}/config", payload, qos=1, retain=True)


# One bridge for the whole application (started and stopped in the lifespan of app.py)
bridge = MqttBridge()
