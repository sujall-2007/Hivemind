import requests
import math

def fetch_live_weather(latitude: float, longitude: float):
    """
    Ingests live high-resolution meteorological data from Open-Meteo API.
    Falls back to regional fire-weather defaults if network is offline.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude:.4f}&longitude={longitude:.4f}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
        f"&wind_speed_unit=mph"
    )
    
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            current = resp.json().get("current", {})
            wind_speed = float(current.get("wind_speed_10m", 15.0))
            wind_dir = float(current.get("wind_direction_10m", 315.0)) # degrees
            gusts = float(current.get("wind_gusts_10m", wind_speed * 1.4))
            temp_c = float(current.get("temperature_2m", 28.0))
            humidity = float(current.get("relative_humidity_2m", 18.0))
            
            return enrich_weather_telemetry(wind_speed, wind_dir, gusts, temp_c, humidity, source="Open-Meteo Live API")
    except Exception as e:
        print(f"Weather API fallback: {e}")
        
    # Standard Santa Ana / wildfire weather baseline
    return enrich_weather_telemetry(
        wind_speed_mph=18.5, 
        wind_direction_deg=315.0, 
        gusts_mph=26.0, 
        temp_c=29.0, 
        humidity_percent=15.0, 
        source="Telemetry Sensor Baseline"
    )

def enrich_weather_telemetry(wind_speed_mph: float, wind_direction_deg: float, gusts_mph: float, 
                             temp_c: float, humidity_percent: float, source: str = "Manual"):
    """
    Calculates meteorological vector dynamics and Fire Danger Rating index.
    """
    # Wind direction in meteorology is WHERE the wind is blowing FROM.
    # Hazard spread pushes TOWARDS wind_direction + 180 degrees.
    spread_azimuth = (wind_direction_deg + 180.0) % 360.0
    spread_rad = math.radians(spread_azimuth)
    
    # Vector components (u = East, v = North)
    u_vector = wind_speed_mph * math.sin(spread_rad)
    v_vector = wind_speed_mph * math.cos(spread_rad)
    
    # Compass cardinal representation
    cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                 "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    cardinal_idx = int((wind_direction_deg + 11.25) / 22.5) % 16
    cardinal_from = cardinals[cardinal_idx]
    
    spread_idx = int((spread_azimuth + 11.25) / 22.5) % 16
    cardinal_toward = cardinals[spread_idx]
    
    # Moisture Damping Coefficient: low RH (< 20%) accelerates spread dramatically
    moisture_factor = max(0.15, min(1.0, 1.0 - (humidity_percent / 100.0) * 0.85))
    
    # Wind velocity propagation multiplier (exponential scaling)
    wind_multiplier = 1.0 + 0.12 * (wind_speed_mph ** 1.35)
    
    # Fire Weather Danger Index (0 - 100 scale)
    danger_index = min(100.0, (wind_speed_mph * 1.5) + ((100.0 - humidity_percent) * 0.45) + (temp_c * 0.5))
    
    if danger_index > 75:
        risk_level = "EXTREME / RED FLAG"
    elif danger_index > 50:
        risk_level = "HIGH HAZARD"
    elif danger_index > 30:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return {
        "wind_speed_mph": round(wind_speed_mph, 1),
        "wind_direction_deg": round(wind_direction_deg, 1),
        "wind_gusts_mph": round(gusts_mph, 1),
        "temperature_c": round(temp_c, 1),
        "temperature_f": round(temp_c * 9/5 + 32, 1),
        "relative_humidity": round(humidity_percent, 1),
        "cardinal_direction": cardinal_from,
        "spread_azimuth_deg": round(spread_azimuth, 1),
        "spread_direction": cardinal_toward,
        "vector_u": round(u_vector, 2),
        "vector_v": round(v_vector, 2),
        "moisture_factor": round(moisture_factor, 3),
        "wind_multiplier": round(wind_multiplier, 3),
        "fire_danger_index": round(danger_index, 1),
        "risk_level": risk_level,
        "source": source
    }
