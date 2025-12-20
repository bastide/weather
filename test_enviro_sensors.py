#!/usr/bin/env python3
"""
Test script for Enviro+ sensors module
Tests hardware abstraction layer functionality
"""

import time
from enviro_sensors import EnviroSensors


def test_sensors():
    """Test all sensor readings"""
    print("=" * 60)
    print("Enviro+ Sensors Test")
    print("=" * 60)
    print()
    
    # Initialize sensors (will use mock data if hardware not available)
    print("Initializing sensors...")
    sensors = EnviroSensors()
    print()
    
    # Test individual sensor readings
    print("Testing individual sensor readings:")
    print("-" * 60)
    
    print("Temperature:", sensors.read_temperature(), "°C")
    print("Pressure:", sensors.read_pressure(), "hPa")
    print("Humidity:", sensors.read_humidity(), "%")
    print("Light:", sensors.read_light(), "Lux")
    print("Proximity:", sensors.read_proximity())
    
    print()
    gas = sensors.read_gas()
    if gas:
        print("Gas - Oxidising:", gas['oxidising'], "Ohms")
        print("Gas - Reducing:", gas['reducing'], "Ohms")
        print("Gas - NH3:", gas['nh3'], "Ohms")
    
    print()
    pm = sensors.read_particulates()
    if pm:
        print("PM1.0:", pm['pm1'], "µg/m³")
        print("PM2.5:", pm['pm2_5'], "µg/m³")
        print("PM10:", pm['pm10'], "µg/m³")
    
    print()
    print("-" * 60)
    print()
    
    # Test reading all sensors at once
    print("Testing read_all() method:")
    print("-" * 60)
    all_data = sensors.read_all()
    
    for key, value in all_data.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    
    print()
    print("-" * 60)
    print()
    
    # Test continuous reading
    print("Testing continuous reading (5 samples, 2 seconds interval):")
    print("-" * 60)
    
    for i in range(5):
        data = sensors.read_all()
        print(f"Sample {i+1}:")
        print(f"  Temp: {data['temperature']:.1f}°C, "
              f"Humidity: {data['humidity']:.1f}%, "
              f"PM2.5: {data['particulates']['pm2_5']:.1f}µg/m³")
        
        if i < 4:  # Don't sleep after last sample
            time.sleep(2)
    
    print()
    print("-" * 60)
    print()
    
    # Cleanup
    sensors.cleanup()
    print("Sensors cleaned up")
    print()
    print("=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_sensors()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
