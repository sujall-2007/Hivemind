import json
import sys
from nasaapi import fetch_active_fires, get_fire_coordinates, GLOBAL_SECTORS
from geometry import extract_hazard_feature, create_boundary_polygon
from weather import fetch_live_weather, enrich_weather_telemetry
from forecaster import forecast_hazard_spread

def generate_disaster_intelligence(incident_preset="global_all", weather_override=None):
    """
    End-to-End Automated Earth Observation Analysis Engine:
    Supports full planetary Earth (3,500+ live NASA FIRMS hotspots) 
    as well as continental & regional tactical sectors.
    """
    print(f"[*] Ingesting satellite thermal anomaly stream (Sector/Incident: {incident_preset})...")
    raw_points = fetch_active_fires(incident_preset=incident_preset)
    
    if not raw_points or len(raw_points) < 3:
        return {"error": "Insufficient thermal anomaly points to form a perimeter"}

    print(f"[*] Retrieved {len(raw_points)} active orbital observation detections.")

    # If planetary view, select the highest-FRP local cluster to anchor the focal perimeter
    if incident_preset == "global_all":
        # Sort by FRP and take the cluster around the highest radiative power epicenter
        top_hotspot = max(raw_points, key=lambda p: p.get("frp", 0.0))
        top_lat = top_hotspot["latitude"]
        top_lon = top_hotspot["longitude"]
        
        # Filter cluster within 1.5 degrees (~160 km) of epicenter for perimeter delineation
        focal_points = [
            p for p in raw_points 
            if abs(p["latitude"] - top_lat) < 1.5 and abs(p["longitude"] - top_lon) < 1.5
        ]
        if len(focal_points) < 3:
            focal_points = raw_points[:50]
    else:
        focal_points = raw_points

    coords = [[p["longitude"], p["latitude"]] for p in focal_points]

    # 1. High-precision boundary delineation of the focal sector
    current_feature = extract_hazard_feature(focal_points)
    if not current_feature:
        # Fallback to general multi-point bounding
        current_feature = extract_hazard_feature(focal_points[:15])
        
    current_poly = create_boundary_polygon(coords)
    centroid = current_feature["properties"]["centroid"] if current_feature else [top_lon, top_lat]
    print(f"[*] Active Sector Perimeter delineated: {current_feature['properties']['area_hectares']} ha ({current_feature['properties']['perimeter_km']} km perimeter)")

    # 2. Meteorological and environmental ingestion for the focal centroid
    if weather_override:
        print("[*] Applying tactical weather simulation parameters...")
        weather_telemetry = enrich_weather_telemetry(
            wind_speed_mph=weather_override.get("wind_speed_mph", 15.0),
            wind_direction_deg=weather_override.get("wind_direction_deg", 315.0),
            gusts_mph=weather_override.get("gusts_mph", 22.0),
            temp_c=weather_override.get("temp_c", 28.0),
            humidity_percent=weather_override.get("humidity", 18.0),
            source="Tactical Simulation Override"
        )
    else:
        print(f"[*] Querying live meteorological stream at coordinates {centroid}...")
        weather_telemetry = fetch_live_weather(centroid[1], centroid[0])

    print(f"[*] Weather Ingestion Complete: Wind {weather_telemetry['wind_speed_mph']} mph from {weather_telemetry['cardinal_direction']} ({weather_telemetry['wind_direction_deg']}°), RH {weather_telemetry['relative_humidity']}%, Threat: {weather_telemetry['risk_level']}")

    # 3. Multi-variable spread forecasting
    print("[*] Computing physical Rothermel & Huygens propagation wave fronts (+6h, +12h, +24h)...")
    forecast_features = forecast_hazard_spread(
        current_polygon=current_poly,
        weather_telemetry=weather_telemetry,
        forecast_hours=[6, 12, 24]
    )

    # 4. Thermal hotspot points layer across the globe
    hotspot_features = []
    for p in raw_points:
        hotspot_features.append({
            "type": "Feature",
            "properties": {
                "type": "thermal_hotspot",
                "frp_mw": p.get("frp", 15.0),
                "brightness_k": p.get("brightness", 315.0),
                "confidence": p.get("confidence", "nominal"),
                "satellite": p.get("satellite", "VIIRS"),
                "acq_time": p.get("acq_time", "0830")
            },
            "geometry": {
                "type": "Point",
                "coordinates": [p["longitude"], p["latitude"]]
            }
        })

    sector_info = GLOBAL_SECTORS.get(incident_preset, {})

    # Assemble complete intelligence payload
    geojson_payload = {
        "type": "FeatureCollection",
        "metadata": {
            "incident": incident_preset,
            "incident_name": sector_info.get("name", "Planetary Stream"),
            "region_code": sector_info.get("region_code", "GLOBAL"),
            "total_global_hotspots": len(raw_points),
            "engine": "Hivemind Planetary Earth Observation Engine v2.5",
            "telemetry": weather_telemetry,
            "current_perimeter": current_feature["properties"] if current_feature else {},
            "forecast_summary": [
                {
                    "horizon": f"+{f['properties']['time_horizon_hours']}h",
                    "projected_area_ha": f["properties"]["area_hectares"],
                    "projected_growth": f"+{f['properties']['growth_percent']}%",
                    "advance_distance_km": f"{f['properties']['head_advance_distance_km']} km",
                    "priority": f["properties"]["evacuation_priority"]
                }
                for f in forecast_features
            ]
        },
        "features": [
            *( [current_feature] if current_feature else [] ),
            *forecast_features,
            *hotspot_features
        ]
    }

    return geojson_payload

if __name__ == "__main__":
    intel = generate_disaster_intelligence("global_all")
    out_file = "disaster_forecast.geojson"
    with open(out_file, "w") as f:
        json.dump(intel, f, indent=2)
    print(f"\n[SUCCESS] Planetary pipeline executed successfully. Tactical GeoJSON output written to {out_file} ({len(json.dumps(intel))/1024:.1f} KB)")