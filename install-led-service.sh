#!/bin/bash
# Installer le service systemd pour l'affichage LED SenseHAT
set -euo pipefail

SERVICE_NAME="led-display.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"

if [[ ! -f "${SERVICE_NAME}" ]]; then
  echo "Fichier ${SERVICE_NAME} introuvable dans le répertoire courant." >&2
  exit 1
fi

echo "Copie du service vers ${SERVICE_PATH}"
sudo cp "${SERVICE_NAME}" "${SERVICE_PATH}"

echo "Reload systemd"
sudo systemctl daemon-reload

echo "Activation au démarrage"
sudo systemctl enable "${SERVICE_NAME}"

echo "Démarrage immédiat"
sudo systemctl start "${SERVICE_NAME}"

echo "Statut du service:"
sudo systemctl status "${SERVICE_NAME}" --no-pager

echo "" && echo "Commandes utiles:" && echo "  sudo systemctl status ${SERVICE_NAME}" && echo "  sudo journalctl -u ${SERVICE_NAME} -f" && echo "  sudo systemctl restart ${SERVICE_NAME}" && echo "  sudo systemctl stop ${SERVICE_NAME}" && echo "  sudo systemctl disable ${SERVICE_NAME}"
