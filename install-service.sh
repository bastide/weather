#!/bin/bash
# Script d'installation du service systemd pour Weather Monitor

echo "Installation du service Weather Monitor..."

# Copier le fichier de service
sudo cp weather-monitor.service /etc/systemd/system/

# Rechargez la liste des services
sudo systemctl daemon-reload

# Activez le service au démarrage
sudo systemctl enable weather-monitor.service

# Démarrez le service immédiatement
sudo systemctl start weather-monitor.service

# Vérifiez le statut
echo ""
echo "Statut du service:"
sudo systemctl status weather-monitor.service

echo ""
echo "Installation terminée!"
echo ""
echo "Commandes utiles:"
echo "  Voir le statut:        sudo systemctl status weather-monitor.service"
echo "  Voir les logs:         sudo journalctl -u weather-monitor.service -f"
echo "  Redémarrer:            sudo systemctl restart weather-monitor.service"
echo "  Arrêter:               sudo systemctl stop weather-monitor.service"
echo "  Désactiver au démarrage: sudo systemctl disable weather-monitor.service"
echo ""
echo "Accédez à l'interface web: http://<ip-du-pi>:5000"
