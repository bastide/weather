#!/usr/bin/env python3
"""
Standalone LED display loop for SenseHAT.
Shows temperature, humidity, and pressure on the 8x8 LED matrix,
alternating every DISPLAY_INTERVAL seconds.
"""

import os
import time
import random

try:
    from sense_hat import SenseHat
    SENSEHAT_AVAILABLE = True
except (ImportError, RuntimeError):
    SENSEHAT_AVAILABLE = False
    SenseHat = None  # type: ignore
    print("WARNING: SenseHAT not available, running in console-only mode")

DISPLAY_INTERVAL = int(os.getenv("LED_DISPLAY_INTERVAL", "10"))
SCROLL_SPEED = float(os.getenv("LED_SCROLL_SPEED", "0.05"))

# RGB color map per metric
COLORS = {
    "temp": (255, 120, 0),      # orange
    "humidity": (0, 150, 255),  # blue
    "pressure": (0, 220, 120),  # green
}


def get_mock_readings():
    temp = 20 + random.gauss(0, 2)
    pressure = 1013 + random.gauss(0, 5)
    humidity = 50 + random.gauss(0, 10)
    return temp, pressure, humidity


def read_sensors(sensor: "SenseHat | None"):
    if sensor is None:
        return get_mock_readings()

    try:
        temp = sensor.get_temperature()
        pressure = sensor.get_pressure()
        humidity = sensor.get_humidity()
        return temp, pressure, humidity
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading sensors: {exc}")
        return get_mock_readings()


def show_message(sensor: "SenseHat | None", text: str, color: tuple[int, int, int]):
    if sensor is None:
        print(text)
        return

    try:
        sensor.show_message(text, text_colour=color, scroll_speed=SCROLL_SPEED)
    except Exception as exc:  # noqa: BLE001
        print(f"Error displaying on LED: {exc}")


def run_display_loop():
    sensor = None
    if SENSEHAT_AVAILABLE:
        try:
            sensor = SenseHat()
            sensor.low_light = True
        except Exception as exc:  # noqa: BLE001
            print(f"Error initializing SenseHAT: {exc}")
            sensor = None

    modes = ["temp", "humidity", "pressure"]
    idx = 0

    print(f"Starting LED display loop (interval={DISPLAY_INTERVAL}s)")
    print("Press Ctrl+C to stop")

    try:
        while True:
            mode = modes[idx]
            temp, pressure, humidity = read_sensors(sensor)

            if mode == "temp":
                text = f"T:{temp:.1f}C"
            elif mode == "humidity":
                text = f"H:{humidity:.0f}%"
            else:
                text = f"P:{pressure:.0f}"

            show_message(sensor, text, COLORS[mode])

            idx = (idx + 1) % len(modes)
            time.sleep(DISPLAY_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping LED display loop")
    finally:
        if sensor:
            try:
                sensor.clear()
            except Exception as exc:  # noqa: BLE001
                print(f"Error clearing LED: {exc}")


if __name__ == "__main__":
    run_display_loop()
