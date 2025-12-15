# Weather Monitor for Raspberry Pi with SenseHAT

A Python web application that polls SenseHAT sensors (temperature, barometric pressure, humidity) every 10 minutes and displays the data in real-time interactive charts.

## Features

- **Automatic Sensor Polling**: Collects temperature, pressure, and humidity data every 10 minutes
- **Memory-Efficient Storage**: Keeps up to 1000 samples in memory with automatic rotation
- **Interactive Charts**: Beautiful Plotly-based time series visualizations
- **Real-time Dashboard**: Live statistics and current sensor values
- **Web-Based Interface**: Accessible from any device on the network
- **Mock Data Support**: Runs without SenseHAT (for development/testing)

## Requirements

- Raspberry Pi (with SenseHAT module optional for testing)
- Python 3.7+
- Flask
- sense-hat
- plotly

## Installation

1. Clone or download this project to your Raspberry Pi

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The web interface will be available at `http://<raspberry-pi-ip>:5000`

## Running as a Systemd Service

To run the application automatically on system startup, use the provided systemd configuration.

### Quick Installation

1. Make the installer executable:
```bash
chmod +x install-service.sh
```

2. Run the installer:
```bash
./install-service.sh
```

This will automatically:
- Copy the service file to `/etc/systemd/system/`
- Enable the service to start on boot
- Start the service immediately

### Manual Installation

If you prefer to install manually:

1. Copy the service file:
```bash
sudo cp weather-monitor.service /etc/systemd/system/
```

2. Reload systemd:
```bash
sudo systemctl daemon-reload
```

3. Enable the service:
```bash
sudo systemctl enable weather-monitor.service
```

4. Start the service:
```bash
sudo systemctl start weather-monitor.service
```

### Service Management

Check the service status:
```bash
sudo systemctl status weather-monitor.service
```

View real-time logs:
```bash
sudo journalctl -u weather-monitor.service -f
```

Restart the service:
```bash
sudo systemctl restart weather-monitor.service
```

Stop the service:
```bash
sudo systemctl stop weather-monitor.service
```

Disable from startup:
```bash
sudo systemctl disable weather-monitor.service
```

### Service Configuration

The systemd service is configured with:
- **Auto-restart**: Restarts automatically if it crashes (every 10 seconds)
- **User**: Runs as `pi` user
- **Working directory**: `/home/pi/weather`
- **Memory limit**: 256 MB
- **CPU limit**: 50% of one core
- **Logging**: Automatic logging to journalctl

### Troubleshooting Services

If the service won't start, check the logs:
```bash
sudo journalctl -u weather-monitor.service -n 50
```

Common issues:
- **Permission denied**: Ensure the service runs as the correct user
- **Module not found**: Verify all dependencies are installed for the correct Python user
- **Port 5000 in use**: Change the port in `app.py` or stop conflicting services



## API Endpoints

- `GET /` - Main dashboard
- `GET /api/data` - Raw sensor data (JSON)
- `GET /api/stats` - Statistics and current values
- `GET /api/chart/temperature` - Temperature chart (Plotly JSON)
- `GET /api/chart/pressure` - Pressure chart (Plotly JSON)
- `GET /api/chart/humidity` - Humidity chart (Plotly JSON)

## Data Structure

The application maintains circular buffers (deques) for each measurement type with a maximum capacity of 1000 samples. When memory becomes tight, oldest samples are automatically discarded.

- **Polling Interval**: 10 minutes (600 seconds)
- **Max Capacity**: 1000 samples (~7 days of data)
- **Thread-Safe**: Uses locks for concurrent access

## Configuration

Edit the parameters in `app.py`:

```python
# Change polling interval (in seconds)
sensor_manager = SensorDataManager(max_samples=1000, polling_interval=600)

# For 5-minute intervals:
sensor_manager = SensorDataManager(max_samples=1000, polling_interval=300)
```

## Development/Testing Without SenseHAT

The application automatically falls back to mock data if SenseHAT is not available. This allows testing the web interface and functionality without hardware.

## Troubleshooting

### SenseHAT not found
- Ensure `python3-sense-hat` is installed: `sudo apt-get install python3-sense-hat`
- The app will use mock data if not available

### Permission errors
- Run with appropriate user permissions or sudo
- For systemd service, ensure the user has access to `/dev/i2c-*`

### Port already in use
- Change the port in the code: `app.run(host='0.0.0.0', port=5001)`

## Author

Created for weather monitoring on Raspberry Pi with SenseHAT
