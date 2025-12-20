# Comparaison des Applications de Monitoring

Ce projet contient maintenant deux applications de monitoring complémentaires :

## 1. Weather Monitor (SenseHAT) - `app.py`

### Matériel
- Raspberry Pi avec SenseHAT

### Capteurs
- Température
- Pression atmosphérique
- Humidité

### Port par défaut
- 5000

### Fichiers
- `app.py` - Application principale
- `templates/index.html` - Interface web
- `requirements.txt` - Dépendances
- `install-service.sh` - Script d'installation du service

---

## 2. Air Quality Monitor (Enviro+) - `app_enviro.py`

### Matériel
- Raspberry Pi avec Pimoroni Enviro+
- Capteur PMS5003

### Capteurs
- **Environnementaux (BME280)**
  - Température
  - Pression atmosphérique
  - Humidité
  
- **Luminosité (LTR559)**
  - Luminosité ambiante (Lux)
  - Proximité
  
- **Particules (PMS5003)**
  - PM1.0
  - PM2.5 (avec indicateur de qualité de l'air)
  - PM10
  
- **Gaz (MICS6814)**
  - Gaz oxydants (NO2)
  - Gaz réducteurs (CO)
  - Ammoniac (NH3)

### Port par défaut
- 5001

### Fichiers
- `app_enviro.py` - Application principale
- `enviro_sensors.py` - **Module d'abstraction matérielle**
- `templates/enviro.html` - Interface web
- `requirements_enviro.txt` - Dépendances spécifiques
- `install-enviro-service.sh` - Script d'installation du service
- `test_enviro_sensors.py` - Script de test des capteurs
- `README_ENVIRO.md` - Documentation complète

---

## Architecture : Séparation du Code Matériel

### Application SenseHAT (`app.py`)
Le code matériel est intégré dans l'application principale avec un fallback simple :

```python
try:
    from sense_hat import SenseHat
    SENSEHAT_AVAILABLE = True
except (ImportError, RuntimeError):
    SENSEHAT_AVAILABLE = False
```

### Application Enviro+ (`app_enviro.py` + `enviro_sensors.py`)

**Séparation claire en deux couches :**

#### 1. Couche Matériel - `enviro_sensors.py`
- **Responsabilité unique** : Interface avec les capteurs physiques
- **Abstraction complète** : Toute la logique matérielle est isolée
- **Mode simulation** : Données mock pour développement/test
- **API propre** : Méthodes claires (`read_temperature()`, `read_all()`, etc.)
- **Indépendant** : Peut être utilisé dans d'autres projets

```python
# Exemple d'utilisation
from enviro_sensors import EnviroSensors

sensors = EnviroSensors()
data = sensors.read_all()  # Lit tous les capteurs
temp = sensors.read_temperature()  # Lit un capteur spécifique
```

#### 2. Couche Application - `app_enviro.py`
- **Logique métier** : Collecte, stockage, et visualisation des données
- **Indépendant du matériel** : N'importe pas directement les bibliothèques hardware
- **Flask et API REST** : Gestion web et endpoints
- **Visualisation** : Génération des graphiques Plotly

### Avantages de la Séparation

1. **Testabilité**
   - Test du matériel indépendamment avec `test_enviro_sensors.py`
   - Développement possible sans hardware physique
   
2. **Maintenabilité**
   - Modifications matérielles isolées
   - Code application non affecté par les changements hardware
   
3. **Réutilisabilité**
   - Module `enviro_sensors.py` utilisable dans d'autres projets
   - Facile de créer une CLI, un logger, etc.
   
4. **Clarté**
   - Responsabilités bien définies
   - Code plus facile à comprendre et maintenir

---

## Installation et Utilisation

### Les deux applications peuvent tourner simultanément

```bash
# SenseHAT sur port 5000
python3 app.py

# Enviro+ sur port 5001 (dans un autre terminal)
python3 app_enviro.py
```

### Installation comme services

```bash
# Installer SenseHAT
./install-service.sh

# Installer Enviro+
./install-enviro-service.sh
```

Les deux services peuvent coexister et démarrer automatiquement au boot.

---

## Accès aux Applications

Une fois lancées, les applications sont accessibles via :

- **SenseHAT** : http://[IP-RASPBERRY]:5000
- **Enviro+** : http://[IP-RASPBERRY]:5001

---

## Choix de l'Application

### Utiliser `app.py` (SenseHAT) si :
- ✅ Vous avez un Raspberry Pi avec SenseHAT
- ✅ Vous voulez mesurer température, pression, humidité de base
- ✅ Vous voulez une solution simple et intégrée

### Utiliser `app_enviro.py` (Enviro+) si :
- ✅ Vous avez un Pimoroni Enviro+ avec PMS5003
- ✅ Vous voulez surveiller la qualité de l'air
- ✅ Vous avez besoin de mesures de particules fines
- ✅ Vous voulez des données sur les gaz et la luminosité
- ✅ Vous voulez une architecture modulaire et testable

---

## Tests

### Tester le module matériel Enviro+

```bash
python3 test_enviro_sensors.py
```

Ce script teste toutes les fonctionnalités du module matériel de manière indépendante.

---

## Structure du Projet

```
weather/
├── app.py                      # Application SenseHAT
├── app_enviro.py               # Application Enviro+
├── enviro_sensors.py           # Module abstraction matériel Enviro+
├── test_enviro_sensors.py      # Tests du module matériel
├── requirements.txt            # Dépendances SenseHAT
├── requirements_enviro.txt     # Dépendances Enviro+
├── install-service.sh          # Installation service SenseHAT
├── install-enviro-service.sh   # Installation service Enviro+
├── README.md                   # Documentation principale
├── README_ENVIRO.md            # Documentation détaillée Enviro+
├── COMPARISON.md               # Ce fichier
└── templates/
    ├── index.html              # Interface SenseHAT
    └── enviro.html             # Interface Enviro+
```
