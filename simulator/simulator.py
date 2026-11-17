"""
Simulated SensorHub device.

    python simulator.py SH-000123 [--host localhost] [--port 1883]

- publishes telemetry every sampling_sec seconds
- announces itself on <root>/<serial>/status, with a Last Will for ungraceful disconnections
- applies the configuration received on <root>/<serial>/config and confirms it on <root>/<serial>/ack
- keeps the applied configuration in state_<serial>.json, like the flash memory of a real device

Press Ctrl+C to simulate a power failure: the process exits WITHOUT a clean disconnect,
so the broker publishes the Last Will after the keep-alive timeout.
"""
import argparse
import json
import os
import random
import time
from pathlib import Path

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

ROOT = "sensorhub"
KEEPALIVE = 10  # seconds: the broker declares the device dead after about 1.5 x KEEPALIVE


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"version": 0, "min_temp": 10.0, "max_temp": 30.0, "sampling_sec": 5}


def main():
    parser = argparse.ArgumentParser(description="Simulated SensorHub device")
    parser.add_argument("serial")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--tls", action="store_true")
    args = parser.parse_args()

    serial = args.serial
    state_file = Path(__file__).with_name(f"state_{serial}.json")
    state = load_state(state_file)
    t = {"status": f"{ROOT}/{serial}/status", "config": f"{ROOT}/{serial}/config",
         "ack": f"{ROOT}/{serial}/ack", "telemetry": f"{ROOT}/{serial}/telemetry"}

    # clean_session=False: the broker keeps the subscription and queues QoS 1 messages while offline
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=serial, clean_session=False)
    if args.username:
        client.username_pw_set(args.username, args.password)
    if args.tls:
        client.tls_set()
    # Last Will: published by the broker if the device disappears without saying goodbye
    client.will_set(t["status"], json.dumps({"online": False}), qos=1, retain=True)

    def on_connect(cl, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"[{serial}] connection refused: {reason_code}")
            return
        print(f"[{serial}] online, running configuration v{state['version']}")
        cl.publish(t["status"], json.dumps({"online": True, "config_version": state["version"]}), qos=1, retain=True)
        cl.subscribe(t["config"], qos=1)

    def on_message(cl, userdata, msg):
        config = json.loads(msg.payload)
        if config["version"] <= state["version"]:
            # Idempotency: the same configuration may arrive twice (QoS 1, retained, reconciliation)
            print(f"[{serial}] configuration v{config['version']} already applied: ignored")
        else:
            state.update(config)
            state_file.write_text(json.dumps(state))
            print(f"[{serial}] applied configuration v{state['version']}: {config}")
        ack = {"version": state["version"]}
        cl.publish(t["ack"], json.dumps(ack), qos=1)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(args.host, args.port, keepalive=KEEPALIVE)
    client.loop_start()

    temperature = random.uniform(18, 24)
    try:
        while True:
            time.sleep(state["sampling_sec"])
            temperature += random.uniform(-0.4, 0.5)
            reading = {"temperature": round(temperature, 1), "humidity": round(random.uniform(55, 70), 1)}
            if client.is_connected():
                client.publish(t["telemetry"], json.dumps(reading), qos=0)
                alarm = " ALARM" if not state["min_temp"] <= temperature <= state["max_temp"] else ""
                print(f"[{serial}] telemetry {reading}{alarm}")
    except KeyboardInterrupt:
        print(f"\n[{serial}] simulated power failure: no clean disconnect, the broker will publish the Last Will")
        os._exit(1)


if __name__ == "__main__":
    main()
