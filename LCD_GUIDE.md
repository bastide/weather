# Guide Affichage LCD Enviro+

## 📺 Disposition de l'écran LCD (160x80 pixels)

```
┌────────────────────────────────────────┐
│  T: 22.3°C          H: 54%             │ ← Ligne 1
│  P: 1013 hPa                           │ ← Ligne 2
│  PM2.5: 8.5                            │ ← Ligne 3 (colorée)
│  PM10: 12.3         BON                │ ← Ligne 4
└────────────────────────────────────────┘
```

## 🎨 Codes Couleur PM2.5

L'affichage de PM2.5 change de couleur selon la qualité de l'air :

| Niveau PM2.5 | Couleur | Texte | Signification |
|--------------|---------|-------|---------------|
| 0-12 µg/m³   | 🟢 VERT | BON | Air de bonne qualité |
| 12-35 µg/m³  | 🟡 JAUNE | MODERE | Qualité acceptable |
| 35-55 µg/m³  | 🟠 ORANGE | MAUVAIS | Groupes sensibles affectés |
| > 55 µg/m³   | 🟣 VIOLET | MAUVAIS | Dangereux pour tous |

## 🔄 Mise à jour automatique

- L'écran se met à jour **automatiquement** à chaque cycle de polling
- Par défaut : **toutes les 10 minutes**
- Pas besoin d'intervention manuelle

## 🧪 Test de l'écran

### Test rapide (30 secondes)
```bash
python3 test_lcd.py
```

### Test avec l'application complète
```bash
python3 app_enviro.py
```

L'écran affichera les données dès la première lecture des capteurs.

## ⚙️ Configuration

### Changer la fréquence de mise à jour

Dans [app_enviro.py](app_enviro.py), modifiez :

```python
# Ligne ~172
sensor_manager = SensorDataManager(
    max_samples=1000, 
    polling_interval=600  # ← 600 secondes = 10 minutes
)
```

**Exemples :**
- `polling_interval=60` → Mise à jour chaque minute
- `polling_interval=300` → Mise à jour toutes les 5 minutes
- `polling_interval=1800` → Mise à jour toutes les 30 minutes

### Personnaliser l'affichage

Éditez la méthode `display_on_lcd()` dans [enviro_sensors.py](enviro_sensors.py) (lignes ~190-264) pour :
- Changer les couleurs
- Modifier la disposition
- Ajouter d'autres informations
- Changer la taille des polices

## 🛠️ Dépannage LCD

### L'écran reste noir

1. **Vérifier que SPI est activé :**
   ```bash
   ls -l /dev/spidev*
   ```
   
   Si absent :
   ```bash
   sudo raspi-config
   # Interface Options > SPI > Enable
   sudo reboot
   ```

2. **Vérifier les connexions physiques :**
   - L'Enviro+ doit être correctement monté sur les GPIO
   - Pas de faux contacts

3. **Vérifier les dépendances :**
   ```bash
   pip list | grep -i st7735
   pip list | grep -i pillow
   ```

### Erreurs lors de l'affichage

Si vous voyez des erreurs "Error displaying on LCD", vérifiez :

```bash
# Logs de l'application
sudo journalctl -u enviro-monitor.service -f

# Permissions SPI
ls -l /dev/spidev0.1
```

L'utilisateur doit faire partie du groupe `spi` ou `gpio` :
```bash
sudo usermod -a -G spi,gpio $USER
```

Puis redémarrez la session ou le Raspberry Pi.

## 📝 Fonctionnalités du module

Le module `enviro_sensors.py` expose trois méthodes pour l'LCD :

### `display_on_lcd(data)`
Affiche les données sur l'écran. Paramètre `data` est un dictionnaire :

```python
data = {
    'temperature': 22.3,
    'humidity': 54.0,
    'pressure': 1013.2,
    'particulates': {
        'pm2_5': 8.5,
        'pm10': 12.3
    }
}
sensors.display_on_lcd(data)
```

### `clear_lcd()`
Efface complètement l'écran (noir) :

```python
sensors.clear_lcd()
```

### `cleanup()`
Nettoie les ressources et efface l'écran :

```python
sensors.cleanup()
```

## 💡 Conseils

- **Luminosité :** L'écran LCD du Enviro+ est assez lumineux, idéal pour un affichage permanent
- **Durée de vie :** L'écran LCD peut rester allumé en continu sans problème
- **Visibilité :** Meilleure visibilité en intérieur, peut être difficile à lire en plein soleil
- **Économie d'énergie :** Si nécessaire, vous pouvez éteindre le rétroéclairage via le GPIO 12

## 🔗 Ressources

- [Documentation ST7735](https://github.com/pimoroni/st7735-python)
- [Documentation Pillow](https://pillow.readthedocs.io/)
- [Exemples Pimoroni](https://github.com/pimoroni/enviroplus-python/tree/master/examples)
