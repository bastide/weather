#!/usr/bin/env python3
"""
Weather monitoring application for Raspberry Pi with SenseHAT
Polls temperature, pressure, and humidity every 10 minutes
Displays time series data in interactive charts
"""

import os
import json
from datetime import datetime, timedelta
from threading import Thread, Lock
import time
from collections import deque

from flask import Flask, render_template, jsonify
import plotly.graph_objects as go
import plotly.utils

# Try to import SenseHAT, fall back to mock if not available (for development)
try:
    from sense_hat import SenseHat
    SENSEHAT_AVAILABLE = True
except (ImportError, RuntimeError):
    SENSEHAT_AVAILABLE = False
    print("WARNING: SenseHAT not available, using mock data")


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
        
        # Initialize SenseHAT
        if SENSEHAT_AVAILABLE:
            try:
                self.sensor = SenseHat()
                # Enable IMU (needed for humidity on some models)
                self.sensor.set_imu_config(True, True, True)
                # Set low light for LED matrix
                self.sensor.low_light = True
            except Exception as e:
                print(f"Error initializing SenseHAT: {e}")
                self.sensor = None
        else:
            self.sensor = None
        
        self.running = False
        self.thread = None
        self.display_thread = None
        self.display_running = False
        
        # Current sensor values for display
        self.current_temp = None
        self.current_pressure = None
        self.current_humidity = None
    
    def read_sensors(self):
        """Read current sensor values"""
        if self.sensor:
            try:
                temp = self.sensor.get_temperature()
                pressure = self.sensor.get_pressure()
                humidity = self.sensor.get_humidity()
                return temp, pressure, humidity
            except Exception as e:
                print(f"Error reading sensors: {e}")
                return self._get_mock_data()
        else:
            return self._get_mock_data()
    
    def _get_mock_data(self):
        """Generate mock data for testing (removes after 10 seconds in demo)"""
        import random
        temp = 20 + random.gauss(0, 2)
        pressure = 1013 + random.gauss(0, 5)
        humidity = 50 + random.gauss(0, 10)
        return temp, pressure, humidity
    
    def add_sample(self, temp, pressure, humidity):
        """Add a new sensor sample"""
        with self.lock:
            now = datetime.now()
            self.timestamps.append(now)
            self.temperatures.append(temp)
            self.pressures.append(pressure)
            self.humidities.append(humidity)
            
            # Update current values for LED display
            self.current_temp = temp
            self.current_pressure = pressure
            self.current_humidity = humidity
    
    def get_data(self):
        """Get all current data"""
        with self.lock:
            return {
                'timestamps': list(self.timestamps),
        display_on_led(self, text, color):
        """Display text on SenseHAT LED matrix"""
        if self.sensor:
            try:
                self.sensor.show_message(text, text_colour=color, scroll_speed=0.05)
            except Exception as e:
                print(f"Error displaying on LED: {e}")
    
    def led_display_loop(self):
        """Display measurements on LED matrix, alternating every 10 seconds"""
        display_modes = ['temp', 'humidity', 'pressure']
        current_mode = 0
        
        while self.display_running:
            try:
                mode = display_modes[current_mode]
                
                if mode == 'temp' and self.current_temp is not None:
                    text = f"and LED display threads"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.polling_loop, daemon=True)
            self.thread.start()
            print("Sensor polling started")
            
        if not self.display_running and self.sensor:
            self.display_runand LED display threads"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Sensor polling stopped")
        
        self.display_running = False
        if self.display_thread:
            self.display_thread.join(timeout=5)
        
        # Clear LED display
        if self.sensor:
            try:
                self.sensor.clear()
            except Exception as e:
                print(f"Error clearing LED: {e}")
        print("LED displaylay_on_led(text, color)
                elif mode == 'pressure' and self.current_pressure is not None:
                    text = f"P:{self.current_pressure:.0f}"
                    color = (0, 255, 100)  # Green
                    self.display_on_led(text, color)
                else:
                    # No data yet, show waiting message
                    if self.sensor:
                        self.sensor.show_message("...", text_colour=(100, 100, 100), scroll_speed=0.05)
                
                # Move to next display mode
                current_mode = (current_mode + 1) % len(display_modes)
                
                # Wait 10 seconds before switching
                time.sleep(10)
                
            except Exception as e:
                print(f"Error in LED display loop: {e}")
                time.sleep(5)
    
    def         'temperatures': list(self.temperatures),
                'pressures': list(self.pressures),
                'humidities': list(self.humidities),
            }
    
    def polling_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                temp, pressure, humidity = self.read_sensors()
                self.add_sample(temp, pressure, humidity)
                print(f"{datetime.now()}: T={temp:.1f}°C, P={pressure:.1f}hPa, H={humidity:.1f}%")
                time.sleep(self.polling_interval)
            except Exception as e:
                print(f"Error in polling loop: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the polling thread"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.polling_loop, daemon=True)
            self.thread.start()
            print("Sensor polling started")
    
    def stop(self):
        """Stop the polling thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Sensor polling stopped")


# Initialize the sensor data manager
# Use 10-minute polling interval (600 seconds) and 1000 sample capacity
sensor_manager = SensorDataManager(max_samples=1000, polling_interval=600)


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


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
        'sample_count': len(data['timestamps']),
        'max_samples': sensor_manager.max_samples,
    })


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


@app.route('/api/stats')
def get_stats():
    """Get statistics about the data"""
    data = sensor_manager.get_data()
    
    if not data['temperatures']:
        return jsonify({
            'message': 'No data available yet',
            'sample_count': 0
        })
    
    temps = data['temperatures']
    pressures = data['pressures']
    humidities = data['humidities']
    
    stats = {
        'temperature': {
            'current': temps[-1],
            'min': min(temps),
            'max': max(temps),
            'avg': sum(temps) / len(temps),
        },
        'pressure': {
            'current': pressures[-1],
            'min': min(pressures),
            'max': max(pressures),
            'avg': sum(pressures) / len(pressures),
        },
        'humidity': {
            'current': humidities[-1],
            'min': min(humidities),
            'max': max(humidities),
            'avg': sum(humidities) / len(humidities),
        },
        'sample_count': len(temps),
        'max_samples': sensor_manager.max_samples,
        'first_sample': data['timestamps'][0].isoformat() if data['timestamps'] else None,
        'last_sample': data['timestamps'][-1].isoformat() if data['timestamps'] else None,
    }
    
    return jsonify(stats)


if __name__ == '__main__':
    # Start sensor polling
    sensor_manager.start()
    
    try:
        # Run Flask app on all interfaces, port 5000
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        sensor_manager.stop()
