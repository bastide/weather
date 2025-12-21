#!/usr/bin/env python3
"""
Hardware abstraction layer for Pimoroni Enviro+ with PMS5003 sensor
Isolates hardware dependencies from main application logic
"""

import logging
import random
from PIL import Image, ImageDraw, ImageFont
import time

logger = logging.getLogger(__name__)


class EnviroSensors:
    """Interface for Pimoroni Enviro+ sensors with PMS5003"""

    def __init__(self, use_mock=False):
        """
        Initialize Enviro+ sensors

        Args:
            use_mock: If True, use mock data instead of real sensors
        """
        self.use_mock = use_mock
        self.bme280 = None
        self.ltr559 = None
        self.pms5003 = None
        self.gas_sensor = None
        self.lcd = None
        self.lcd_width = 160
        self.lcd_height = 80

        if not use_mock:
            try:
                # Import Enviro+ libraries
                from bme280 import BME280
                from ltr559 import LTR559
                from enviroplus import gas
                from pms5003 import PMS5003, ReadTimeoutError

                # Initialize BME280 (temperature, pressure, humidity)
                try:
                    from smbus2 import SMBus
                    self.bme280 = BME280(i2c_dev=SMBus(1))
                    logger.info("BME280 sensor initialized")
                except Exception as e:
                    logger.warning(f"BME280 not available: {e}")

                # Initialize LTR559 (light and proximity)
                try:
                    self.ltr559 = LTR559()
                    logger.info("LTR559 sensor initialized")
                except Exception as e:
                    logger.warning(f"LTR559 not available: {e}")

                # Initialize PMS5003 (particulate matter)
                try:
                    self.pms5003 = PMS5003()
                    logger.info("PMS5003 sensor initialized")
                except Exception as e:
                    logger.warning(f"PMS5003 not available: {e}")

                # Gas sensor is available through enviroplus.gas module
                self.gas_sensor = gas
                logger.info("Gas sensors initialized")

                # Initialize LCD display
                try:
                    from ST7735 import ST7735
                    self.lcd = ST7735(
                        port=0,
                        cs=1,
                        dc=9,
                        backlight=12,
                        rotation=270,
                        spi_speed_hz=10000000
                    )
                    self.lcd.begin()
                    logger.info("LCD display initialized")
                except Exception as e:
                    logger.warning(f"LCD not available: {e}")

            except ImportError as e:
                logger.warning(f"Enviro+ libraries not available: {e}")
                logger.info("Using mock data instead")
                self.use_mock = True

        if self.use_mock:
            logger.info("Using mock sensor data")

    def read_temperature(self):
        """
        Read temperature in Celsius, adjusted for CPU heat

        Returns:
            float: Temperature in °C
        """
        if self.use_mock or not self.bme280:
            return 20 + random.gauss(0, 2)

        try:
            # Get CPU temperature
            cpu_temp = self._get_cpu_temperature()

            # Read raw temperature from sensor
            raw_temp = self.bme280.get_temperature()
            logger.info(f"Raw temp: {raw_temp:.2f}C, CPU temp: {cpu_temp:.2f}C")
            # Compensate for CPU heat influence
            # The compensation factor can be tuned based on your setup
            compensation_factor = 4.9
            compensated_temp = raw_temp - ((cpu_temp - raw_temp) / compensation_factor)

            return compensated_temp
        except Exception as e:
            logger.error(f"Error reading temperature: {e}")
            return None

    def read_pressure(self):
        """
        Read barometric pressure in hPa

        Returns:
            float: Pressure in hPa
        """
        if self.use_mock or not self.bme280:
            return 1013 + random.gauss(0, 5)

        try:
            return self.bme280.get_pressure()
        except Exception as e:
            logger.error(f"Error reading pressure: {e}")
            return None

    def read_humidity(self):
        """
        Read relative humidity in %

        Returns:
            float: Humidity in %
        """
        if self.use_mock or not self.bme280:
            return 50 + random.gauss(0, 10)

        try:
            return self.bme280.get_humidity()
        except Exception as e:
            logger.error(f"Error reading humidity: {e}")
            return None

    def read_light(self):
        """
        Read light level in Lux

        Returns:
            float: Light level in Lux
        """
        if self.use_mock or not self.ltr559:
            return 100 + random.gauss(0, 20)

        try:
            return self.ltr559.get_lux()
        except Exception as e:
            logger.error(f"Error reading light: {e}")
            return None

    def read_proximity(self):
        """
        Read proximity sensor value (0-65535)

        Returns:
            int: Proximity value
        """
        if self.use_mock or not self.ltr559:
            return int(100 + random.gauss(0, 50))

        try:
            return self.ltr559.get_proximity()
        except Exception as e:
            logger.error(f"Error reading proximity: {e}")
            return None

    def read_gas(self):
        """
        Read gas sensor values

        Returns:
            dict: Dictionary with oxidising, reducing, and nh3 values
        """
        if self.use_mock or not self.gas_sensor:
            return {
                'oxidising': 15000 + random.gauss(0, 1000),
                'reducing': 150000 + random.gauss(0, 10000),
                'nh3': 120000 + random.gauss(0, 8000)
            }

        try:
            readings = self.gas_sensor.read_all()
            return {
                'oxidising': readings.oxidising,
                'reducing': readings.reducing,
                'nh3': readings.nh3
            }
        except Exception as e:
            logger.error(f"Error reading gas sensors: {e}")
            return None

    def read_particulates(self):
        """
        Read particulate matter from PMS5003

        Returns:
            dict: Dictionary with PM1.0, PM2.5, PM10 values in µg/m³
        """
        if self.use_mock or not self.pms5003:
            return {
                'pm1': 5 + random.gauss(0, 2),
                'pm2_5': 10 + random.gauss(0, 3),
                'pm10': 15 + random.gauss(0, 4)
            }

        try:
            data = self.pms5003.read()
            return {
                'pm1': data.pm_ug_per_m3(1.0),
                'pm2_5': data.pm_ug_per_m3(2.5),
                'pm10': data.pm_ug_per_m3(10)
            }
        except Exception as e:
            logger.error(f"Error reading particulates: {e}")
            return None

    def read_all(self):
        """
        Read all sensor values at once

        Returns:
            dict: Dictionary with all sensor readings
        """
        return {
            'temperature': self.read_temperature(),
            'pressure': self.read_pressure(),
            'humidity': self.read_humidity(),
            'light': self.read_light(),
            'proximity': self.read_proximity(),
            'gas': self.read_gas(),
            'particulates': self.read_particulates()
        }

    def display_on_lcd(self, data):
        """
        Display sensor data on the LCD screen

        Args:
            data: Dictionary with sensor readings
        """
        if self.use_mock or not self.lcd:
            return

        try:
            # Create image
            img = Image.new('RGB', (self.lcd_width, self.lcd_height), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Try to load a font, fallback to default
            try:
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                font_small = ImageFont.load_default()
                font_large = ImageFont.load_default()

            # Extract data
            temp = data.get('temperature', 0)
            humidity = data.get('humidity', 0)
            pressure = data.get('pressure', 0)

            particulates = data.get('particulates') or {}
            pm25 = particulates.get('pm2_5', 0)
            pm10 = particulates.get('pm10', 0)

            # Define colors
            color_white = (255, 255, 255)
            color_cyan = (0, 255, 255)
            color_yellow = (255, 255, 0)
            color_green = (0, 255, 0)

            # Determine air quality color based on PM2.5
            if pm25 <= 12:
                pm_color = color_green
                quality = "BON"
            elif pm25 <= 35:
                pm_color = color_yellow
                quality = "MODERE"
            else:
                pm_color = (255, 100, 0)  # Orange
                quality = "MAUVAIS"

            # Draw data on screen
            y_offset = 2

            # Temperature and Humidity
            draw.text((5, y_offset), f"T: {temp:.1f}C", font=font_large, fill=color_cyan)
            draw.text((90, y_offset), f"H: {humidity:.0f}%", font=font_large, fill=color_cyan)

            # Pressure
            y_offset += 20
            draw.text((5, y_offset), f"P: {pressure:.0f} hPa", font=font_small, fill=color_white)

            # Particulates
            y_offset += 18
            draw.text((5, y_offset), f"PM2.5: {pm25:.1f}", font=font_large, fill=pm_color)

            y_offset += 20
            draw.text((5, y_offset), f"PM10: {pm10:.1f}", font=font_small, fill=color_white)
            draw.text((90, y_offset), quality, font=font_small, fill=pm_color)

            # Display the image
            self.lcd.display(img)

        except Exception as e:
            logger.error(f"Error displaying on LCD: {e}")

    def clear_lcd(self):
        """Clear the LCD screen"""
        if self.lcd:
            try:
                img = Image.new('RGB', (self.lcd_width, self.lcd_height), color=(0, 0, 0))
                self.lcd.display(img)
            except Exception as e:
                logger.error(f"Error clearing LCD: {e}")

    def cleanup(self):
        """Clean up sensor resources"""
        if self.pms5003:
            try:
                # PMS5003 may have cleanup methods depending on version
                pass
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

        # Clear LCD on exit
        self.clear_lcd()

    def _get_cpu_temperature(self):
        """
        Get CPU temperature from Raspberry Pi

        Returns:
            float: CPU temperature in °C
        """
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
                return temp
        except Exception as e:
            logger.error(f"Error reading CPU temperature: {e}")
            return 0.0
