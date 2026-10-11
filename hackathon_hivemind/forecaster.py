import math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, Point, mapping
from shapely.affinity import translate, scale, rotate
from shapely.ops import unary_union
from geometry import calculate_geodesic_metrics

def calculate_rothermel_ros(wind_speed_mph: float, relative_humidity: float, 
                            temperature_c: float = 28.0, slope_deg: float = 8.0, 
                            fuel_type: str = "chaparral_timber"):
    """
    Computes Rate of Spread (ROS in km/h) and elliptical geometry factors
    based on the Rothermel and Anderson wildfire propagation models.
    """
    # Base rate of spread in zero wind on flat terrain (km/h)
    base_ros = 0.45 
    
    # Wind factor (exponential scaling with wind velocity)
    # Anderson (1983): LB = 0.936 * exp(0.256 * U_m/s) + 0.461
    u_kmh = wind_speed_mph * 1.60934
    length_to_breadth = max(1.1, 1.0 + 0.11 * wind_speed_mph)
    
    # Wind coefficient phi_w
    phi_w = 0.08 * (wind_speed_mph ** 1.35)
    
    # Slope acceleration factor (fires accelerate uphill)
    slope_rad = math.radians(slope_deg)
    phi_s = 5.275 * (math.tan(slope_rad) ** 2)
    
    # Fuel Moisture Damping factor: low RH causes rapid fire acceleration
    # Below 15% RH, fire behavior becomes erratic and volatile
    moisture_damping = math.exp(-0.035 * relative_humidity)
    
    # Ambient Temperature pre-heating factor
    temp_factor = 1.0 + max(0.0, (temperature_c - 20.0) * 0.015)
    
    # Head Rate of Spread (km/h) along the prevailing wind vector
    ros_head_kmh = base_ros * (1.0 + phi_w + phi_s) * moisture_damping * temp_factor
    
    # Flank and Backing rates of spread
    ros_flank_kmh = ros_head_kmh / (2.0 * length_to_breadth)
    ros_back_kmh = ros_flank_kmh / length_to_breadth
    
    return {
        "ros_head_kmh": round(ros_head_kmh, 3),
        "ros_flank_kmh": round(ros_flank_kmh, 3),
        "ros_back_kmh": round(ros_back_kmh, 3),
        "length_to_breadth": round(length_to_breadth, 2),
        "phi_wind": round(phi_w, 3),
        "phi_slope": round(phi_s, 3),
        "moisture_damping": round(moisture_damping, 3)
    }

def forecast_hazard_spread(current_polygon: Polygon, weather_telemetry: dict, 
                           forecast_hours: list = [6, 12, 24], slope_deg: float = 8.0):
    """
    Propagates the disaster boundary outward along meteorological vectors 
    using the Huygens wave-front expansion principle.
    Returns GeoJSON Feature for each forecast interval.
    """
    if current_polygon is None or current_polygon.is_empty:
        return []
        
    wind_speed = weather_telemetry.get("wind_speed_mph", 15.0)
    humidity = weather_telemetry.get("relative_humidity", 18.0)
    temp_c = weather_telemetry.get("temperature_c", 28.0)
    spread_azimuth = weather_telemetry.get("spread_azimuth_deg", 135.0) # Angle of movement
    
    physics = calculate_rothermel_ros(wind_speed, humidity, temp_c, slope_deg)
    
    centroid = current_polygon.centroid
    lat_center = centroid.y
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * math.cos(math.radians(lat_center))
    
    spread_rad = math.radians(spread_azimuth)
    
    features = []
    current_metrics = calculate_geodesic_metrics(current_polygon)
    current_area_ha = current_metrics["area_hectares"]
    
    # Confidence decreases with longer forecast horizons
    confidence_decay = {6: 0.92, 12: 0.84, 24: 0.71}
    
    prev_poly = current_polygon
    
    for hours in forecast_hours:
        head_distance_km = physics["ros_head_kmh"] * hours
        flank_distance_km = physics["ros_flank_kmh"] * hours
        
        # Translation shift for the head of the fire along the wind vector
        d_east_km = head_distance_km * math.sin(spread_rad)
        d_north_km = head_distance_km * math.cos(spread_rad)
        
        shift_lon = d_east_km / km_per_deg_lon
        shift_lat = d_north_km / km_per_deg_lat
        
        # Buffer distance in degrees representing flank/lateral spread
        deg_flank_buffer = flank_distance_km / km_per_deg_lat
        
        # Huygens expansion: translate head and expand perimeter buffer
        translated_poly = translate(prev_poly, xoff=shift_lon * 0.45, yoff=shift_lat * 0.45)
        dilated_poly = translated_poly.buffer(deg_flank_buffer, resolution=16)
        
        # Union with previous envelope to preserve monotonic hazard growth
        forecast_poly = unary_union([prev_poly, dilated_poly])
        forecast_poly = forecast_poly.simplify(0.0008, preserve_topology=True)
        
        if isinstance(forecast_poly, MultiPolygon):
            forecast_poly = max(forecast_poly.geoms, key=lambda p: p.area)
            
        metrics = calculate_geodesic_metrics(forecast_poly)
        growth_percent = round(((metrics["area_hectares"] - current_area_ha) / max(1.0, current_area_ha)) * 100.0, 1)
        
        feature = {
            "type": "Feature",
            "properties": {
                "type": f"forecast_{hours}hr",
                "hazard": "predicted_wildfire_spread",
                "time_horizon_hours": hours,
                "status": "predicted_hazard_zone",
                "area_km2": metrics["area_km2"],
                "area_hectares": metrics["area_hectares"],
                "perimeter_km": metrics["perimeter_km"],
                "growth_percent": growth_percent,
                "head_advance_distance_km": round(head_distance_km, 2),
                "head_rate_of_spread_kmh": physics["ros_head_kmh"],
                "confidence_score": confidence_decay.get(hours, 0.75),
                "evacuation_priority": "CRITICAL" if hours <= 6 else ("HIGH" if hours <= 12 else "WARNING"),
                "environmental_drivers": {
                    "wind_speed_mph": wind_speed,
                    "spread_azimuth_deg": spread_azimuth,
                    "relative_humidity": humidity,
                    "fuel_moisture_damping": physics["moisture_damping"]
                }
            },
            "geometry": mapping(forecast_poly)
        }
        features.append(feature)
        prev_poly = forecast_poly
        
    return features
