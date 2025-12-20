# Enviro+ Air Quality Monitor

Application de surveillance de la qualité de l'air pour Raspberry Pi avec Pimoroni Enviro+ et capteur de particules PMS5003.

## Caractéristiques

Cette application surveille et affiche en temps réel :

### Affichage
- 📺 **Écran LCD ST7735** - Affichage local des données en temps réel
- 🌐 **Interface Web** - Dashboard avec graphiques interactifs

### Capteurs Environnementaux (BME280)
- 🌡️ **Température** (°C)
- 🔽 **Pression atmosphérique** (hPa)
- 💧 **Humidité relative** (%)

### Capteur de Luminosité (LTR559)
- 💡 **Luminosité ambiante** (Lux)
- 📏 **Proximité**

### Capteur de Particules (PMS5003)
- 🫁 **PM1.0** - Particules fines (µg/m³)
- 🫁 **PM2.5** - Particules fines (µg/m³) avec indicateur de qualité de l'air
- 🌫️ **PM10** - Particules en suspension (µg/m³)

### Capteurs de Gaz (MICS6814)
- 💨 **Gaz oxydants** (NO2)
- 💨 **Gaz réducteurs** (CO)
- 💨 **Ammoniac** (NH3)

## Architecture

Le projet est structuré avec une séparation claire entre la logique métier et le matériel :

### Fichiers principaux

1. **`enviro_sensors.py`** - Module d'abstraction matérielle
   - Encapsule toute l'interaction avec les capteurs
   - Fournit des données simulées si le matériel n'est pas disponible
   - Facilite les tests en mode développement

2. **`app_enviro.py`** - Application Flask principale
   - Gestion des données et polling des capteurs
   - API REST pour les données en temps réel
   - Génération de graphiques avec Plotly

3. **`templates/enviro.html`** - Interface web
   - Dashboard responsive avec cartes de statistiques
   - Graphiques interactifs en temps réel
   - Indicateur de qualité de l'air basé sur PM2.5

### Affichage LCD

L'application affiche automatiquement les données sur l'écran LCD intégré de l'Enviro+ :
- **Température et Humidité** (ligne 1)
- **Pression atmosphérique** (ligne 2)
- **PM2.5** avec code couleur selon la qualité de l'air (ligne 3)
- **PM10 et indicateur de qualité** (ligne 4)

**Code couleur de qualité de l'air :**
- 🟢 **VERT** : Bon (PM2.5 ≤ 12 µg/m³)
- 🟡 **JAUNE** : Modéré (PM2.5 12-35 µg/m³)
- 🟠 **ORANGE** : Mauvais (PM2.5 > 35 µg/m³)

L'écran est mis à jour automatiquement à chaque cycle de polling (toutes les 10 minutes par défaut).

## Installation

### Prérequis

```bash
# Installer les dépendances système
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Activer I2C et Serial (nécessaire pour les capteurs)
sudo raspi-config
# Naviguer vers: Interface Options > I2C > Enable
# Naviguer vers: Interface Options > Serial Port > Enable
```

### Installation de l'application

```bash
# Cloner le projet
cd /home/pi
git clone <votre-repo>
cd weather

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements_enviro.txt
```

## Utilisation

### Lancement manuel

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python3 app_enviro.py
```

L'application sera accessible à l'adresse : `http://<ip-du-raspberry>:5001`

### Mode développement (sans matériel)

L'application fonctionne automatiquement en mode simulation si les capteurs ne sont pas détectés. Cela permet le développement et les tests sans matériel physique.

### Test de l'écran LCD

Pour tester uniquement l'écran LCD :

```bash
python3 test_lcd.py
```

Ce script affiche les données des capteurs sur l'écran LCD pendant 30 secondes avec des mises à jour toutes les 5 secondes.

### Installation comme service systemd

Créer le fichier `/etc/systemd/system/enviro-monitor.service` :

```ini
[Unit]
Description=Enviro+ Air Quality Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/weather
Environment="PATH=/home/pi/weather/venv/bin"
ExecStart=/home/pi/weather/venv/bin/python3 /home/pi/weather/app_enviro.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activer et démarrer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable enviro-monitor.service
sudo systemctl start enviro-monitor.service

# Vérifier le statut
sudo systemctl status enviro-monitor.service

# Voir les logs
sudo journalctl -u enviro-monitor.service -f
```

## Configuration

### Intervalle de polling

Par défaut, les capteurs sont interrogés toutes les 10 minutes (600 secondes). Pour modifier cet intervalle, éditez `app_enviro.py` :

```python
sensor_manager = SensorDataManager(max_samples=1000, polling_interval=600)
```

### Capacité de stockage

Par défaut, l'application conserve 1000 échantillons en mémoire. Pour modifier cette valeur :

```python
sensor_manager = SensorDataManager(max_samples=2000, polling_interval=600)
```

### Port de l'application

Par défaut, l'application écoute sur le port 5001. Pour changer le port, éditez la dernière ligne de `app_enviro.py` :

```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

## API REST

L'application expose plusieurs endpoints :

- `GET /` - Interface web principale
- `GET /api/data` - Données brutes de tous les capteurs
- `GET /api/stats` - Statistiques (min, max, moyenne, valeur actuelle)
- `GET /api/chart/temperature` - Graphique de température
- `GET /api/chart/pressure` - Graphique de pression
- `GET /api/chart/humidity` - Graphique d'humidité
- `GET /api/chart/light` - Graphique de luminosité
- `GET /api/chart/particulates` - Graphique des particules (PM1, PM2.5, PM10)
- `GET /api/chart/gas` - Graphique des gaz

## Indicateurs de Qualité de l'Air (PM2.5)

L'application utilise les standards EPA pour évaluer la qualité de l'air :

- **Bon** : 0-12 µg/m³ (vert)
- **Modéré** : 12-35 µg/m³ (jaune)
- **Mauvais pour groupes sensibles** : 35-55 µg/m³ (orange)
- **Dangereux** : >55 µg/m³ (violet)

## Dépannage

### L'écran LCD n'affiche rien

```bash
# Vérifier que SPI est activé
ls -l /dev/spidev*

# Si absent, activer SPI
sudo raspi-config
# Interface Options > SPI > Enable
```

Si l'écran reste noir après l'activation du SPI, redémarrez le Raspberry Pi.

### Les capteurs ne sont pas détectés

```bash
# Vérifier que I2C est activé
i2cdetect -y 1

# Vérifier les ports série
ls -l /dev/ttyAMA0
```

### Erreurs de lecture des capteurs

Les erreurs de lecture sont normales occasionnellement. L'application réessaiera automatiquement. Si les erreurs persistent, vérifiez :
- Les connexions physiques
- L'alimentation (certains capteurs nécessitent 5V)
- Les permissions sur les ports série

### L'application ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u enviro-monitor.service -n 50

# Tester manuellement
cd /home/pi/weather
source venv/bin/activate
python3 app_enviro.py
```

## Structure du Code

### Module `enviro_sensors.py`

Ce module fournit une abstraction propre du matériel :

```python
from enviro_sensors import EnviroSensors

# Initialiser les capteurs
sensors = EnviroSensors()

# Lire toutes les valeurs
data = sensors.read_all()

# Ou lire des valeurs individuelles
temp = sensors.read_temperature()
pm25 = sensors.read_particulates()['pm2_5']
```

### Classe `SensorDataManager`

Gère la collecte et le stockage des données :
- Polling automatique en arrière-plan
- Rotation automatique des anciennes données
- Thread-safe avec verrous
- Gestion gracieuse des erreurs
- **Affichage automatique sur l'écran LCD**

### Méthodes LCD dans `enviro_sensors.py`

- `display_on_lcd(data)` - Affiche les données sur l'écran
- `clear_lcd()` - Efface l'écran
- Les méthodes gèrent automatiquement les erreurs et le mode simulation

## Licence

Ce projet est fourni tel quel, libre d'utilisation et de modification.

## Ressources

- [Documentation Pimoroni Enviro+](https://learn.pimoroni.com/article/getting-started-with-enviro-plus)
- [Spécifications PMS5003](https://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf)
- [Standards EPA pour la qualité de l'air](https://www.epa.gov/pm-pollution)
