#!/usr/bin/env python3
"""
Air Quality monitoring application for Raspberry Pi with Pimoroni Enviro+ and PMS5003
Polls environmental and air quality sensors every 10 minutes
Displays time series data in interactive charts
"""

import logging

# Configure logging first, before other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

import os
import json
from datetime import datetime, timedelta
from threading import Thread, Lock
import time
from collections import deque

from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import plotly.utils

from enviro_sensors import EnviroSensors

logger = logging.getLogger(__name__)


app = Flask(__name__)


class SensorDataManager:
    """Manages sensor data collection and storage with memory rotation"""

    def __init__(self, max_samples=1000, polling_interval=600):
        """
        Initialize sensor data manager

        Args:
            max_samples: Maximum number of samples to keep in memory
            polling_interval: Time between polls in seconds (default 10 minutes)
        """
        self.max_samples = max_samples
        self.polling_interval = polling_interval
        self.lock = Lock()

        # Deques maintain order and allow efficient rotation
        self.timestamps = deque(maxlen=max_samples)
        self.temperatures = deque(maxlen=max_samples)
        self.pressures = deque(maxlen=max_samples)
        self.humidities = deque(maxlen=max_samples)
        self.light_levels = deque(maxlen=max_samples)
        self.proximities = deque(maxlen=max_samples)
        self.gas_oxidising = deque(maxlen=max_samples)
        self.gas_reducing = deque(maxlen=max_samples)
        self.gas_nh3 = deque(maxlen=max_samples)
        self.pm1 = deque(maxlen=max_samples)
        self.pm2_5 = deque(maxlen=max_samples)
        self.pm10 = deque(maxlen=max_samples)

        # Initialize sensors
        self.sensors = EnviroSensors()

        self.running = False
        self.thread = None

    def read_sensors(self):
        """Read current sensor values"""
        try:
            data = self.sensors.read_all()

            # Extract values with default fallbacks
            temp = data.get('temperature', 0)
            pressure = data.get('pressure', 0)
            humidity = data.get('humidity', 0)
            light = data.get('light', 0)
            proximity = data.get('proximity', 0)

            gas = data.get('gas') or {}
            gas_ox = gas.get('oxidising', 0)
            gas_red = gas.get('reducing', 0)
            gas_nh3 = gas.get('nh3', 0)

            pm = data.get('particulates') or {}
            pm1 = pm.get('pm1', 0)
            pm2_5 = pm.get('pm2_5', 0)
            pm10 = pm.get('pm10', 0)

            return {
                'temperature': temp,
                'pressure': pressure,
                'humidity': humidity,
                'light': light,
                'proximity': proximity,
                'gas_oxidising': gas_ox,
                'gas_reducing': gas_red,
                'gas_nh3': gas_nh3,
                'pm1': pm1,
                'pm2_5': pm2_5,
                'pm10': pm10
            }
        except Exception as e:
            logger.error(f"Error reading sensors: {e}")
            return None

    def add_sample(self, data):
        """Add a new sensor sample"""
        if not data:
            return

        with self.lock:
            now = datetime.now()
            self.timestamps.append(now)
            self.temperatures.append(data['temperature'])
            self.pressures.append(data['pressure'])
            self.humidities.append(data['humidity'])
            self.light_levels.append(data['light'])
            self.proximities.append(data['proximity'])
            self.gas_oxidising.append(data['gas_oxidising'])
            self.gas_reducing.append(data['gas_reducing'])
            self.gas_nh3.append(data['gas_nh3'])
            self.pm1.append(data['pm1'])
            self.pm2_5.append(data['pm2_5'])
            self.pm10.append(data['pm10'])

    def get_data(self):
        """Get all current data"""
        with self.lock:
            return {
                'timestamps': list(self.timestamps),
                'temperatures': list(self.temperatures),
                'pressures': list(self.pressures),
                'humidities': list(self.humidities),
                'light_levels': list(self.light_levels),
                'proximities': list(self.proximities),
                'gas_oxidising': list(self.gas_oxidising),
                'gas_reducing': list(self.gas_reducing),
                'gas_nh3': list(self.gas_nh3),
                'pm1': list(self.pm1),
                'pm2_5': list(self.pm2_5),
                'pm10': list(self.pm10),
            }

    def polling_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                data = self.read_sensors()
                if data:
                    self.add_sample(data)
                    logger.info("{}: T={:.1f}°C, P={:.1f}hPa, H={:.1f}%, Light={:.1f}lux, PM2.5={:.1f}µg/m³".format(
                        datetime.now(),
                        data['temperature'],
                        data['pressure'],
                        data['humidity'],
                        data['light'],
                        data['pm2_5']
                    ))

                    # Display data on LCD
                    display_data = {
                        'temperature': data['temperature'],
                        'humidity': data['humidity'],
                        'pressure': data['pressure'],
                        'particulates': {
                            'pm2_5': data['pm2_5'],
                            'pm10': data['pm10']
                        }
                    }
                    self.sensors.display_on_lcd(display_data)

                time.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(5)

    def start(self):
        """Start the polling thread"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.polling_loop, daemon=True)
            self.thread.start()
            logger.info("Sensor polling started")

    def stop(self):
        """Stop the polling thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.sensors.cleanup()
        logger.info("Sensor polling stopped")


# Initialize the sensor data manager
# Use 10-minute polling interval (600 seconds) and 1000 sample capacity
sensor_manager = SensorDataManager(max_samples=20000, polling_interval=60)


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('enviro.html')


@app.route('/api/data')
def get_data():
    """API endpoint to get sensor data"""
    data = sensor_manager.get_data()

    # Convert datetime objects to ISO format strings for JSON serialization
    timestamps = [ts.isoformat() for ts in data['timestamps']]

    return jsonify({
        'timestamps': timestamps,
        'temperatures': data['temperatures'],
        'pressures': data['pressures'],
        'humidities': data['humidities'],
        'light_levels': data['light_levels'],
        'proximities': data['proximities'],
        'gas_oxidising': data['gas_oxidising'],
        'gas_reducing': data['gas_reducing'],
        'gas_nh3': data['gas_nh3'],
        'pm1': data['pm1'],
        'pm2_5': data['pm2_5'],
        'pm10': data['pm10'],
        'sample_count': len(data['timestamps']),
        'max_samples': sensor_manager.max_samples,
    })


@app.route('/api/stats')
def get_stats():
    """Get statistics about the data"""
    data = sensor_manager.get_data()

    if not data['temperatures']:
        return jsonify({
            'message': 'No data available yet',
            'sample_count': 0
        })

    def calc_stats(values):
        """Calculate min, max, avg for a list of values"""
        if not values:
            return {'current': 0, 'min': 0, 'max': 0, 'avg': 0}
        return {
            'current': values[-1],
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
        }

    stats = {
        'temperature': calc_stats(data['temperatures']),
        'pressure': calc_stats(data['pressures']),
        'humidity': calc_stats(data['humidities']),
        'light': calc_stats(data['light_levels']),
        'proximity': calc_stats(data['proximities']),
        'gas_oxidising': calc_stats(data['gas_oxidising']),
        'gas_reducing': calc_stats(data['gas_reducing']),
        'gas_nh3': calc_stats(data['gas_nh3']),
        'pm1': calc_stats(data['pm1']),
        'pm2_5': calc_stats(data['pm2_5']),
        'pm10': calc_stats(data['pm10']),
        'sample_count': len(data['timestamps']),
        'max_samples': sensor_manager.max_samples,
        'first_sample': data['timestamps'][0].isoformat() if data['timestamps'] else None,
        'last_sample': data['timestamps'][-1].isoformat() if data['timestamps'] else None,
    }

    return jsonify(stats)


@app.route('/api/chart/temperature')
def chart_temperature():
    """Generate temperature chart"""
    data = sensor_manager.get_data()

    if not data['timestamps']:
        return jsonify({'error': 'No data available'}), 204

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['temperatures'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title='Temperature Time Series',
        xaxis_title='Time',
        yaxis_title='Temperature (°C)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/api/chart/pressure')
def chart_pressure():
    """Generate pressure chart"""
    data = sensor_manager.get_data()

    if not data['timestamps']:
        return jsonify({'error': 'No data available'}), 204

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['pressures'],
        mode='lines+markers',
        name='Pressure',
        line=dict(color='#4ECDC4', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title='Barometric Pressure Time Series',
        xaxis_title='Time',
        yaxis_title='Pressure (hPa)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/api/chart/humidity')
def chart_humidity():
    """Generate humidity chart"""
    data = sensor_manager.get_data()

    if not data['timestamps']:
        return jsonify({'error': 'No data available'}), 204

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['humidities'],
        mode='lines+markers',
        name='Humidity',
        line=dict(color='#95E1D3', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title='Humidity Time Series',
        xaxis_title='Time',
        yaxis_title='Humidity (%)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/api/chart/light')
def chart_light():
    """Generate light level chart"""
    data = sensor_manager.get_data()

    if not data['timestamps']:
        return jsonify({'error': 'No data available'}), 204

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['light_levels'],
        mode='lines+markers',
        name='Light',
        line=dict(color='#FFD93D', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title='Light Level Time Series',
        xaxis_title='Time',
        yaxis_title='Light (Lux)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/api/chart/particulates')
def chart_particulates():
    """Generate particulate matter chart"""
    data = sensor_manager.get_data()

    if not data['timestamps']:
        return jsonify({'error': 'No data available'}), 204

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['pm1'],
        mode='lines+markers',
        name='PM1.0',
        line=dict(color='#A8E6CF', width=2),
        marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['pm2_5'],
        mode='lines+markers',
        name='PM2.5',
        line=dict(color='#FFD3B6', width=2),
        marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['pm10'],
        mode='lines+markers',
        name='PM10',
        line=dict(color='#FFAAA5', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title='Particulate Matter Time Series',
        xaxis_title='Time',
        yaxis_title='Concentration (µg/m³)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/api/chart/gas')
def chart_gas():
    """Generate gas sensors chart"""
    data = sensor_manager.get_data()

    if not data['timestamps']:
        return jsonify({'error': 'No data available'}), 204

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['gas_oxidising'],
        mode='lines+markers',
        name='Oxidising',
        line=dict(color='#FF6B9D', width=2),
        marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['gas_reducing'],
        mode='lines+markers',
        name='Reducing',
        line=dict(color='#6BCF7F', width=2),
        marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['gas_nh3'],
        mode='lines+markers',
        name='NH3',
        line=dict(color='#6B9BCF', width=2),
        marker=dict(size=4)
    ))

    fig.update_layout(
        title='Gas Sensors Time Series',
        xaxis_title='Time',
        yaxis_title='Resistance (Ohms)',
        template='plotly_white',
        hovermode='x unified',
        height=400,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == '__main__':
    # Start sensor polling
    sensor_manager.start()

    try:
        # Run Flask app on all interfaces, port 5001
        app.run(host='0.0.0.0', port=5001, debug=False)
    finally:
        sensor_manager.stop()
