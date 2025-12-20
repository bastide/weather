#!/bin/bash
# Installation script for Enviro+ Air Quality Monitor Service

SERVICE_NAME="enviro-monitor"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER="$USER"

echo "Installing Enviro+ Air Quality Monitor as a systemd service..."

# Create systemd service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Enviro+ Air Quality Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python3 $APP_DIR/app_enviro.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at $SERVICE_FILE"

# Reload systemd daemon
sudo systemctl daemon-reload
echo "Systemd daemon reloaded"

# Enable service to start on boot
sudo systemctl enable "$SERVICE_NAME.service"
echo "Service enabled to start on boot"

# Start the service
sudo systemctl start "$SERVICE_NAME.service"
echo "Service started"

# Show status
echo ""
echo "Service installation complete!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status $SERVICE_NAME    - Check service status"
echo "  sudo systemctl stop $SERVICE_NAME      - Stop the service"
echo "  sudo systemctl start $SERVICE_NAME     - Start the service"
echo "  sudo systemctl restart $SERVICE_NAME   - Restart the service"
echo "  sudo journalctl -u $SERVICE_NAME -f    - View live logs"
echo ""
echo "Current status:"
sudo systemctl status "$SERVICE_NAME.service" --no-pager
