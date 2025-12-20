#!/usr/bin/env python3
"""
Test script for Enviro+ LCD display
Tests the LCD screen functionality
"""

import time
from enviro_sensors import EnviroSensors


def test_lcd():
    """Test LCD display with sensor data"""
    print("=" * 60)
    print("Enviro+ LCD Display Test")
    print("=" * 60)
    print()
    
    # Initialize sensors
    print("Initializing sensors and LCD...")
    sensors = EnviroSensors()
    print()
    
    if not sensors.lcd and not sensors.use_mock:
        print("ERROR: LCD not available!")
        print("Make sure the ST7735 library is installed and the display is connected.")
        return
    
    print("LCD initialized successfully!")
    print()
    print("Displaying sensor data on LCD for 30 seconds...")
    print("(Updates every 5 seconds)")
    print()
    
    try:
        # Display data 6 times (30 seconds total)
        for i in range(6):
            # Read all sensors
            data = sensors.read_all()
            
            print(f"Update {i+1}/6:")
            print(f"  Temperature: {data['temperature']:.1f}°C")
            print(f"  Humidity: {data['humidity']:.1f}%")
            print(f"  Pressure: {data['pressure']:.1f} hPa")
            
            if data['particulates']:
                pm25 = data['particulates']['pm2_5']
                pm10 = data['particulates']['pm10']
                print(f"  PM2.5: {pm25:.1f} µg/m³")
                print(f"  PM10: {pm10:.1f} µg/m³")
                
                # Air quality assessment
                if pm25 <= 12:
                    quality = "BON"
                elif pm25 <= 35:
                    quality = "MODÉRÉ"
                else:
                    quality = "MAUVAIS"
                print(f"  Qualité de l'air: {quality}")
            
            print()
            
            # Display on LCD
            sensors.display_on_lcd(data)
            
            if i < 5:  # Don't sleep after last iteration
                time.sleep(5)
        
        print("-" * 60)
        print()
        print("Test completed!")
        print("Clearing LCD...")
        sensors.clear_lcd()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        print("Clearing LCD...")
        sensors.clear_lcd()
    
    finally:
        sensors.cleanup()
        print("Cleanup completed")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    test_lcd()
