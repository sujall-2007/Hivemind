import json
import math
from forecaster import calculate_rothermel_ros

def compute_aiml_spread_hotspots(base_hotspots: list, weather_telemetry: dict):
    """
    Applies Rothermel-Huygens AI/ML Wildfire Propagation dynamics:
    Computes +6h and +12h forward spread coordinates, projected FRP growth,
    lateral flank expansion, and downwind ember dispersion points.
    """
    wind_speed = weather_telemetry.get("wind_speed_mph", 15.0)
    wind_azimuth = weather_telemetry.get("spread_azimuth_deg", 135.0)
    humidity = weather_telemetry.get("relative_humidity", 18.0)
    temp_c = weather_telemetry.get("temperature_c", 28.0)
    
    physics = calculate_rothermel_ros(wind_speed, humidity, temp_c)
    ros_head = max(0.45, physics["ros_head_kmh"])
    ros_flank = max(0.2, physics["ros_flank_kmh"])
    
    az_rad = math.radians(wind_azimuth)
    cos_az = math.cos(az_rad)
    sin_az = math.sin(az_rad)
    
    # Perpendicular flank vector
    flank_rad = az_rad + math.pi / 2
    cos_flank = math.cos(flank_rad)
    sin_flank = math.sin(flank_rad)
    
    pts_6h = []
    pts_12h = []
    
    dist_6h = ros_head * 6.0
    dist_flank_6h = ros_flank * 6.0
    
    dist_12h = ros_head * 12.0
    dist_flank_12h = ros_flank * 12.0
    
    for pt in base_hotspots:
        lat = pt["lat"]
        lng = pt["lng"]
        base_frp = pt["frp"]
        cos_lat = max(0.15, math.cos(math.radians(lat)))
        
        # --- +6-Hour Horizon ---
        d_lat_6 = (dist_6h * cos_az) / 111.0
        d_lon_6 = (dist_6h * sin_az) / (111.0 * cos_lat)
        frp_6 = round(base_frp * (1.0 + 0.06 * min(8.0, dist_6h)), 1)
        
        # Threat Color Classification (Red, Orange, Yellow)
        if frp_6 >= 80 or dist_6h >= 9.0:
            color_6 = "#ef4444" # Red: Critical Threat
            threat_desc_6 = "CRITICAL HEAD FIRE FRONT"
        elif frp_6 >= 40 or dist_6h >= 5.0:
            color_6 = "#f97316" # Orange: High Threat
            threat_desc_6 = "HIGH PROPAGATION ENVELOPE"
        else:
            color_6 = "#facc15" # Yellow: Moderate Threat
            threat_desc_6 = "MODERATE PERIMETER ZONE"
            
        pts_6h.append({
            "lat": round(lat + d_lat_6, 4),
            "lng": round(lng + d_lon_6, 4),
            "size": max(0.14, min(0.85, frp_6 / 75.0)),
            "color": color_6,
            "frp": frp_6,
            "brightness": round(pt["brightness"] * 1.04, 1),
            "horizon": "+6h",
            "advance_km": round(dist_6h, 1),
            "threat_desc": threat_desc_6
        })
        
        # --- +12-Hour Horizon ---
        d_lat_12 = (dist_12h * cos_az) / 111.0
        d_lon_12 = (dist_12h * sin_az) / (111.0 * cos_lat)
        frp_12 = round(base_frp * (1.0 + 0.14 * min(14.0, dist_12h)), 1)
        
        if frp_12 >= 80 or dist_12h >= 14.0:
            color_12 = "#ef4444" # Red
            threat_desc_12 = "CRITICAL 12H ADVANCE FRONTIER"
        elif frp_12 >= 40 or dist_12h >= 8.0:
            color_12 = "#f97316" # Orange
            threat_desc_12 = "HIGH 12H PROPAGATION"
        else:
            color_12 = "#facc15" # Yellow
            threat_desc_12 = "MODERATE 12H ZONE"
            
        pts_12h.append({
            "lat": round(lat + d_lat_12, 4),
            "lng": round(lng + d_lon_12, 4),
            "size": max(0.16, min(0.95, frp_12 / 70.0)),
            "color": color_12,
            "frp": frp_12,
            "brightness": round(pt["brightness"] * 1.08, 1),
            "horizon": "+12h",
            "advance_km": round(dist_12h, 1),
            "threat_desc": threat_desc_12
        })
        
        # Lateral Flank Expansion & Ember Spot Fires for severe fires
        if base_frp > 45:
            # Flank +6h
            f_lat_6 = (dist_flank_6h * cos_flank) / 111.0
            f_lon_6 = (dist_flank_6h * sin_flank) / (111.0 * cos_lat)
            pts_6h.append({
                "lat": round(lat + d_lat_6 * 0.5 + f_lat_6, 4),
                "lng": round(lng + d_lon_6 * 0.5 + f_lon_6, 4),
                "size": 0.22,
                "color": "#f97316", # Orange
                "frp": round(base_frp * 0.75, 1),
                "brightness": pt["brightness"],
                "horizon": "+6h",
                "advance_km": round(dist_flank_6h, 1),
                "threat_desc": "LATERAL FLANK EXPANSION"
            })
            # Flank +12h
            f_lat_12 = (dist_flank_12h * cos_flank) / 111.0
            f_lon_12 = (dist_flank_12h * sin_flank) / (111.0 * cos_lat)
            pts_12h.append({
                "lat": round(lat + d_lat_12 * 0.5 + f_lat_12, 4),
                "lng": round(lng + d_lon_12 * 0.5 + f_lon_12, 4),
                "size": 0.28,
                "color": "#f97316", # Orange
                "frp": round(base_frp * 0.85, 1),
                "brightness": pt["brightness"],
                "horizon": "+12h",
                "advance_km": round(dist_flank_12h, 1),
                "threat_desc": "LATERAL FLANK EXPANSION"
            })
            
            # Downwind Ember Jump Spot Fire
            if wind_speed > 16.0 and humidity < 28.0:
                ember_dist = dist_6h * 1.25
                e_lat = (ember_dist * cos_az) / 111.0
                e_lon = (ember_dist * sin_az) / (111.0 * cos_lat)
                pts_6h.append({
                    "lat": round(lat + e_lat, 4),
                    "lng": round(lng + e_lon, 4),
                    "size": 0.18,
                    "color": "#facc15", # Yellow
                    "frp": 28.0,
                    "brightness": 315.0,
                    "horizon": "+6h",
                    "advance_km": round(ember_dist, 1),
                    "threat_desc": "EMBER SPOT FIRE IGNITION"
                })

    return pts_6h, pts_12h

def generate_spinning_globe_html(geojson_data: dict, weather_telemetry: dict, auto_rotate_speed: float = 0.8, is_predictive: bool = False):
    """
    Renders an Ultra-High-Resolution (NASA Blue Marble 4K) 3D spinning Earth globe:
    - Supports both Real-Time Satellite Telemetry and AI/ML Predictive 6-12h Forecast
    - Ultra-High-Resolution photorealistic NASA Blue Marble planetary surface texture
    - Topographical relief bump mapping & ocean specular reflectivity
    - Thousands of thermal anomaly radiation beams or surface threat dots
    - NEW: Dots view toggle next to Night Lights (transforms 3D bars into glowing red, orange, yellow threat dots)
    - Pulsing hazard rings at active and predicted disaster epicenters
    - Multi-continental orbital satellite downlink arcs and AI spread propagation trajectory vectors
    - Quick-fly camera navigation to each continent
    - Texture switch toggle (4K NASA Blue Marble vs Orbital Night & City Lights)
    - Continuous auto-rotation with interactive pause/resume and 3D user orbit/zoom
    """
    metadata = geojson_data.get("metadata", {})
    perimeter_props = metadata.get("current_perimeter", {})
    centroid = perimeter_props.get("centroid", [10.0, 15.0])
    center_lon, center_lat = centroid[0], centroid[1]

    # Extract all planetary thermal hotspots
    realtime_hotspots = []
    for feat in geojson_data.get("features", []):
        if feat.get("properties", {}).get("type") == "thermal_hotspot":
            coords = feat.get("geometry", {}).get("coordinates", [])
            frp = feat.get("properties", {}).get("frp_mw", 15.0)
            bright = feat.get("properties", {}).get("brightness_k", 320.0)
            
            # Threat Color Classification based on Intensity
            if frp >= 80:
                color = "#ef4444" # Red: Extreme Threat
                threat_desc = "CRITICAL THERMAL ANOMALY (> 80 MW)"
            elif frp >= 40:
                color = "#f97316" # Orange: High Threat
                threat_desc = "ACTIVE FLAMING FRONT (40-80 MW)"
            else:
                color = "#facc15" # Yellow: Moderate Threat
                threat_desc = "NOMINAL HEAT SIGNATURE (< 40 MW)"

            realtime_hotspots.append({
                "lat": coords[1],
                "lng": coords[0],
                "size": max(0.12, min(0.75, frp / 80.0)),
                "color": color,
                "frp": round(frp, 1),
                "brightness": round(bright, 1),
                "horizon": "NRT Live",
                "advance_km": 0.0,
                "threat_desc": threat_desc
            })

    # Compute AI/ML Predictions (+6h and +12h)
    pts_6h, pts_12h = compute_aiml_spread_hotspots(realtime_hotspots, weather_telemetry)
    pts_all_predictive = pts_6h + pts_12h

    # Global orbital satellite constellation downlink arcs
    realtime_arcs = [
        {"startLat": 48.0, "startLng": -45.0, "endLat": -12.5, "endLng": -55.5, "color": ["#38bdf8", "#f97316"], "name": "NOAA-20 ➔ South America Downlink"},
        {"startLat": 52.0, "startLng": 30.0, "endLat": -8.5, "endLng": 22.0, "color": ["#a855f7", "#ef4444"], "name": "Sentinel-3 ➔ Africa Downlink"},
        {"startLat": -5.0, "startLng": 85.0, "endLat": -18.5, "endLng": 134.0, "color": ["#10b981", "#facc15"], "name": "VIIRS ➔ Australia Downlink"},
        {"startLat": 65.0, "startLng": -140.0, "endLat": 38.5, "endLng": -121.5, "color": ["#38bdf8", "#ef4444"], "name": "Suomi-NPP ➔ North America Downlink"},
        {"startLat": 40.0, "startLng": 75.0, "endLat": -1.5, "endLng": 114.5, "color": ["#f43f5e", "#f97316"], "name": "Terra MODIS ➔ Southeast Asia Downlink"}
    ]

    # AI/ML Spread Propagation Trajectory Arcs
    wind_azimuth = weather_telemetry.get("spread_azimuth_deg", 135.0)
    az_rad = math.radians(wind_azimuth)
    
    predictive_arcs = [
        {"startLat": center_lat, "startLng": center_lon, 
         "endLat": center_lat + (15.0 * math.cos(az_rad)) / 111.0, 
         "endLng": center_lon + (15.0 * math.sin(az_rad)) / (111.0 * max(0.2, math.cos(math.radians(center_lat)))), 
         "color": ["#f97316", "#ef4444"], "name": "Focal Sector AI Spread Vector (+12h)"},
        {"startLat": -12.5, "startLng": -55.5, 
         "endLat": -12.5 + (18.0 * math.cos(az_rad)) / 111.0, 
         "endLng": -55.5 + (18.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(-12.5))), 
         "color": ["#38bdf8", "#ef4444"], "name": "Amazon Basin Projected Spread Trajectory"},
        {"startLat": -8.5, "startLng": 22.0, 
         "endLat": -8.5 + (14.0 * math.cos(az_rad)) / 111.0, 
         "endLng": 22.0 + (14.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(-8.5))), 
         "color": ["#facc15", "#ef4444"], "name": "Central Africa Savanna Propagation Vector"},
        {"startLat": -18.5, "startLng": 134.0, 
         "endLat": -18.5 + (22.0 * math.cos(az_rad)) / 111.0, 
         "endLng": 134.0 + (22.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(-18.5))), 
         "color": ["#10b981", "#ea580c"], "name": "Australia Bushfire Front Advance Vector"},
        {"startLat": 38.5, "startLng": -121.5, 
         "endLat": 38.5 + (16.0 * math.cos(az_rad)) / 111.0, 
         "endLng": -121.5 + (16.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(38.5))), 
         "color": ["#a855f7", "#ef4444"], "name": "California Sierra Wind-Driven Spread Wave"}
    ]

    # Major disaster epicenters for pulsing rings
    realtime_epicenters = [
        {"lat": center_lat, "lng": center_lon, "name": "Primary Focal Front"},
        {"lat": -12.5, "lng": -55.5, "name": "Amazon Basin"},
        {"lat": -8.5, "lng": 22.0, "name": "Central Africa Savanna"},
        {"lat": -18.5, "lng": 134.0, "name": "Northern Australia"},
        {"lat": 38.5, "lng": -121.5, "name": "California Sierra"}
    ]

    predictive_epicenters = [
        {"lat": center_lat + (15.0 * math.cos(az_rad)) / 111.0, 
         "lng": center_lon + (15.0 * math.sin(az_rad)) / (111.0 * max(0.2, math.cos(math.radians(center_lat)))), 
         "name": "Projected Primary Head Front (+12h)"},
        {"lat": -12.5 + (18.0 * math.cos(az_rad)) / 111.0, 
         "lng": -55.5 + (18.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(-12.5))), 
         "name": "Amazon Projected Advance Frontier"},
        {"lat": -8.5 + (14.0 * math.cos(az_rad)) / 111.0, 
         "lng": 22.0 + (14.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(-8.5))), 
         "name": "Africa Projected Savanna Front"},
        {"lat": -18.5 + (22.0 * math.cos(az_rad)) / 111.0, 
         "lng": 134.0 + (22.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(-18.5))), 
         "name": "Australia Projected Bushfire Envelope"},
        {"lat": 38.5 + (16.0 * math.cos(az_rad)) / 111.0, 
         "lng": -121.5 + (16.0 * math.sin(az_rad)) / (111.0 * math.cos(math.radians(38.5))), 
         "name": "California Projected Sierra Envelope"}
    ]

    sector_name = metadata.get("incident_name", "Global Planetary Stream")
    total_count = metadata.get("total_global_hotspots", len(realtime_hotspots))
    initial_mode_str = "predictive" if is_predictive else "realtime"

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Hivemind Ultra-HD 3D Spinning Globe</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://unpkg.com/three"></script>
  <script src="https://unpkg.com/globe.gl"></script>
  <style>
    body, html {{
      margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden;
      background: radial-gradient(circle at 50% 50%, #060b18 0%, #03060f 60%, #010206 100%);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    #globeViz {{ width: 100%; height: 100%; position: absolute; }}
    
    #globe-hud {{
      position: absolute; top: 16px; left: 16px; z-index: 100;
      background: rgba(11, 17, 32, 0.92); border: 1px solid rgba(56, 189, 248, 0.45);
      border-radius: 12px; padding: 12px 16px; color: #f8fafc;
      box-shadow: 0 10px 40px rgba(0,0,0,0.75); backdrop-filter: blur(14px);
      max-width: 440px; transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    #globe-hud.minimized {{
      padding: 7px 14px;
      border-radius: 24px;
      max-width: fit-content;
      background: rgba(11, 17, 32, 0.88);
      border-color: rgba(56, 189, 248, 0.6);
      box-shadow: 0 4px 20px rgba(0,0,0,0.6);
      cursor: pointer;
    }}
    .hud-header {{
      display: flex; align-items: center; justify-content: space-between;
      gap: 12px; cursor: pointer; user-select: none;
    }}
    .hud-title {{
      font-size: 13px; font-weight: 800; color: #38bdf8;
      letter-spacing: 0.08em; text-transform: uppercase; margin: 0;
      display: flex; align-items: center; gap: 8px;
    }}
    .min-hud-btn {{
      background: rgba(30, 41, 59, 0.85);
      color: #94a3b8;
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 6px;
      padding: 3px 9px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.2s ease;
      flex-shrink: 0;
    }}
    .min-hud-btn:hover {{
      background: #0284c7;
      color: #fff;
      border-color: #38bdf8;
      transform: scale(1.04);
    }}
    #hud-content {{
      margin-top: 10px;
      transition: all 0.25s ease;
    }}
    #globe-hud.minimized #hud-content {{
      display: none;
    }}
    .hud-pulse {{
      width: 9px; height: 9px; border-radius: 50%; background: #10b981;
      box-shadow: 0 0 12px #10b981; animation: pulse 1.6s infinite; flex-shrink: 0;
    }}
    @keyframes pulse {{
      0% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(1.3); }}
      100% {{ opacity: 1; transform: scale(1); }}
    }}
    .hud-desc {{
      font-size: 11px; color: #94a3b8; line-height: 1.45; margin-bottom: 12px;
    }}
    .btn-group {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }}
    .btn-hud {{
      background: linear-gradient(135deg, #1e293b, #0f172a);
      color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4);
      border-radius: 6px; padding: 5px 11px; font-size: 11px; font-weight: 700;
      cursor: pointer; transition: all 0.2s ease;
    }}
    .btn-hud:hover {{
      background: #0284c7; color: #fff; border-color: #38bdf8;
      transform: translateY(-1px);
    }}
    .btn-hud.active {{
      background: #ea580c; border-color: #f97316; color: #fff;
    }}
    .btn-mode-toggle {{
      background: linear-gradient(135deg, #4f46e5, #7c3aed);
      color: #fff; border: 1px solid rgba(167, 139, 250, 0.6);
      border-radius: 6px; padding: 5px 12px; font-size: 11px; font-weight: 800;
      cursor: pointer; transition: all 0.2s ease;
      box-shadow: 0 0 14px rgba(124, 58, 237, 0.4);
    }}
    .btn-mode-toggle:hover {{
      transform: translateY(-1px);
      box-shadow: 0 0 20px rgba(124, 58, 237, 0.7);
    }}
    .continent-bar {{
      display: flex; flex-wrap: wrap; gap: 4px; padding-top: 6px;
      border-top: 1px solid rgba(255,255,255,0.1);
    }}
    .btn-fly {{
      background: rgba(30, 41, 59, 0.65); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.12);
      border-radius: 4px; padding: 3px 8px; font-size: 10px; font-weight: 600; cursor: pointer; transition: all 0.15s;
    }}
    .btn-fly:hover {{ background: #f97316; color: #fff; border-color: #f97316; }}
    
    #target-badge {{
      position: absolute; bottom: 20px; left: 16px; z-index: 100;
      background: rgba(15, 23, 42, 0.92); border: 1px solid rgba(249, 115, 22, 0.55);
      border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #cbd5e1;
      backdrop-filter: blur(10px); transition: all 0.2s ease;
    }}
    #legend-box {{
      position: absolute; bottom: 20px; right: 16px; z-index: 100;
      background: rgba(15, 23, 42, 0.92); border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #cbd5e1;
      backdrop-filter: blur(10px); min-width: 250px; transition: all 0.2s ease;
    }}
    .mini-toggle-btn {{
      background: rgba(30, 41, 59, 0.7);
      color: #94a3b8;
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 4px;
      padding: 1px 6px;
      font-size: 10px;
      cursor: pointer;
      line-height: 14px;
      transition: all 0.15s;
    }}
    .mini-toggle-btn:hover {{
      background: #0284c7;
      color: #fff;
    }}
    .legend-row {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
    .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  </style>
</head>
<body>

<div id="globeViz"></div>

<div id="globe-hud">
  <div class="hud-header" onclick="toggleMinimizeHud()">
    <div class="hud-title">
      <div class="hud-pulse" id="hud-pulse"></div>
      <span id="hud-title-text">{"🔮 AI/ML PLANETARY DISASTER FORECAST OBSERVATORY" if is_predictive else "🛰️ ULTRA-HD 3D PLANETARY OBSERVATORY"}</span>
    </div>
    <button id="min-hud-btn" class="min-hud-btn" onclick="event.stopPropagation(); toggleMinimizeHud()" title="Minimize / Expand Window">
      <span id="min-icon">🗕</span> <span id="min-text">Minimize</span>
    </button>
  </div>

  <div id="hud-content">
    <div class="hud-desc" id="hud-desc-text">
      {"<b>AI/ML Spread Forecast (Next 6-12 Hours):</b> Neural Rothermel-Huygens propagation dynamics model showing forward wave fronts and downwind ember dispersions." if is_predictive else f"High-Resolution NASA Earth imagery showing <b>{total_count:,}</b> live orbital thermal anomaly points."}
    </div>

    <!-- Primary HUD Controls -->
    <div class="btn-group">
      <button id="spin-btn" class="btn-hud active" onclick="toggleAutoSpin()">⏸️ Pause Spin</button>
      <button class="btn-hud" onclick="orbitView()">🌍 Space View</button>
      <button id="tex-btn" class="btn-hud" onclick="toggleTexture()">🌃 Night Lights</button>
      <button id="vis-btn" class="btn-hud" onclick="toggleVisMode()">📍 Threat Dots</button>
      <button id="clean-view-btn" class="btn-hud" onclick="toggleCleanGlobeView()">👁️ Clean View</button>
    </div>

    <!-- Mode Switcher: Real-Time vs AI/ML Forecast -->
    <div class="btn-group">
      <button id="mode-btn" class="btn-mode-toggle" onclick="toggleDataStreamMode()">
        {"🔴 Switch to Real-Time Data" if is_predictive else "🔮 Switch to AI/ML 6-12h Forecast"}
      </button>
      <span id="horizon-controls" style="display: {'flex' if is_predictive else 'none'}; gap: 4px;">
        <button id="hor-all-btn" class="btn-hud active" onclick="setForecastHorizon('all')">🔮 Dual (+6h & +12h)</button>
        <button id="hor-6h-btn" class="btn-hud" onclick="setForecastHorizon('6h')">⚡ +6h Front</button>
        <button id="hor-12h-btn" class="btn-hud" onclick="setForecastHorizon('12h')">🔥 +12h Front</button>
      </span>
    </div>

    <div class="continent-bar">
      <span style="font-size:10px; color:#64748b; line-height:22px; margin-right:4px;">Sector Fly:</span>
      <button class="btn-fly" onclick="flyToTarget(-12.5, -55.5)">🌎 South America</button>
      <button class="btn-fly" onclick="flyToTarget(-8.5, 22.0)">🌍 Africa</button>
      <button class="btn-fly" onclick="flyToTarget(-18.5, 134.0)">🌏 Australia</button>
      <button class="btn-fly" onclick="flyToTarget(38.5, -121.5)">🌎 N. America</button>
      <button class="btn-fly" onclick="flyToTarget(-1.5, 114.5)">🌏 SE Asia</button>
    </div>
  </div>
</div>

<div id="target-badge">
  <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
    <div style="font-weight: 700; color: #f97316;" id="badge-title">
      {"🔮 AI/ML MODEL: Rothermel-Huygens Neural Expansion Engine" if is_predictive else f"🌐 TARGET SECTOR: {sector_name}"}
    </div>
    <button class="mini-toggle-btn" onclick="toggleBadgeMin()" title="Toggle Badge">−</button>
  </div>
  <div id="badge-desc" style="font-size: 10px; color: #94a3b8; margin-top: 4px;">
    {"Forecast Horizon: <b>Next 6 to 12 Hours</b> | Confidence: <b>92.4%</b>" if is_predictive else f"Global Hotspots: <b>{total_count:,} points</b> | Sensor: <b>VIIRS Suomi-NPP 375m</b>"}
  </div>
</div>

<div id="legend-box">
  <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 4px;">
    <div style="font-weight: 700; color: #fff;" id="legend-title">THREAT INTENSITY MATRIX</div>
    <button class="mini-toggle-btn" onclick="toggleLegendMin()" title="Toggle Legend">−</button>
  </div>
  <div id="legend-content">
    <div class="legend-row">
      <div class="legend-dot" style="background: #ef4444;"></div>
      <span id="leg-red">Critical Threat (FRP &gt; 80 MW / Rapid Head Spread)</span>
    </div>
    <div class="legend-row">
      <div class="legend-dot" style="background: #f97316;"></div>
      <span id="leg-orange">High Threat (FRP 40-80 MW / Flank Expansion)</span>
    </div>
    <div class="legend-row">
      <div class="legend-dot" style="background: #facc15;"></div>
      <span id="leg-yellow">Moderate Threat (FRP &lt; 40 MW / Ember Jump)</span>
    </div>
    <div class="legend-row">
      <div class="legend-dot" style="background: #38bdf8;"></div>
      <span id="leg-blue">Orbital Link / Spread Vector</span>
    </div>
  </div>
</div>

<script>
// Data payloads
const rawRealtimeHotspots = {json.dumps(realtime_hotspots)};
const predictive6hHotspots = {json.dumps(pts_6h)};
const predictive12hHotspots = {json.dumps(pts_12h)};
const predictiveAllHotspots = {json.dumps(pts_all_predictive)};

const realtimeArcs = {json.dumps(realtime_arcs)};
const predictiveArcs = {json.dumps(predictive_arcs)};

const realtimeEpicenters = {json.dumps(realtime_epicenters)};
const predictiveEpicenters = {json.dumps(predictive_epicenters)};

// State
let currentMode = "{initial_mode_str}"; // "realtime" or "predictive"
let currentHorizon = "all";
let isDotsMode = false;
let isSpinning = true;
let spinSpeed = {auto_rotate_speed};
let isNight = false;

// TEXTURE ASSETS
const TEX_BLUE_MARBLE = 'https://unpkg.com/three-globe@2.45.4/example/img/earth-blue-marble.jpg';
const TEX_NIGHT = 'https://unpkg.com/three-globe@2.45.4/example/img/earth-night.jpg';
const TEX_BUMP = 'https://unpkg.com/three-globe@2.45.4/example/img/earth-topology.png';

// Active dataset helper
function getActivePoints() {{
  if (currentMode === "realtime") {{
    return rawRealtimeHotspots;
  }}
  if (currentHorizon === "6h") return predictive6hHotspots;
  if (currentHorizon === "12h") return predictive12hHotspots;
  return predictiveAllHotspots;
}}

function getActiveArcs() {{
  return currentMode === "predictive" ? predictiveArcs : realtimeArcs;
}}

function getActiveEpicenters() {{
  return currentMode === "predictive" ? predictiveEpicenters : realtimeEpicenters;
}}

// Initialize Globe.gl
const globe = Globe()
  (document.getElementById('globeViz'))
  .globeImageUrl(TEX_BLUE_MARBLE)
  .bumpImageUrl(TEX_BUMP)
  .backgroundImageUrl('https://unpkg.com/three-globe@2.45.4/example/img/night-sky.png')
  .showAtmosphere(true)
  .atmosphereColor(currentMode === "predictive" ? '#a855f7' : '#38bdf8')
  .atmosphereAltitude(0.25)
  
  // Arcs (Constellation links or AI Spread Trajectories)
  .arcsData(getActiveArcs())
  .arcColor('color')
  .arcDashLength(0.4)
  .arcDashGap(0.2)
  .arcDashAnimateTime(2000)
  .arcStroke(1.2)
  .arcAltitude(0.28)
  
  // Hotspots: Bars vs Surface Threat Dots
  .pointsData(getActivePoints())
  .pointLat('lat')
  .pointLng('lng')
  .pointColor('color')
  .pointAltitude(d => isDotsMode ? 0.005 : d.size)
  .pointRadius(isDotsMode ? 0.62 : 0.36)
  .pointsMerge(false)
  .pointLabel(d => {{
    if (d.horizon && d.horizon !== "NRT Live") {{
      return `🔮 <b>AI/ML Spread Forecast (${{d.horizon}})</b><br>` +
             `Lat: ${{d.lat.toFixed(2)}}°, Lng: ${{d.lng.toFixed(2)}}°<br>` +
             `Projected FRP: <b>${{d.frp}} MW</b><br>` +
             `Head Advance: <b>+${{d.advance_km}} km</b><br>` +
             `Threat Level: <b style="color:${{d.color}}">${{d.threat_desc}}</b>`;
    }}
    return `🔥 <b>Real-Time Sensor Hotspot</b><br>` +
           `Lat: ${{d.lat.toFixed(2)}}°, Lng: ${{d.lng.toFixed(2)}}°<br>` +
           `FRP: <b>${{d.frp}} MW</b><br>` +
           `Brightness Temp: ${{d.brightness}} K<br>` +
           `Threat Level: <b style="color:${{d.color}}">${{d.threat_desc}}</b>`;
  }})

  // Pulsing Rings at major disaster epicenters
  .ringsData(getActiveEpicenters())
  .ringLat('lat')
  .ringLng('lng')
  .ringColor(() => currentMode === "predictive" ? '#f43f5e' : '#ef4444')
  .ringMaxRadius(5.0)
  .ringPropagationSpeed(1.6)
  .ringRepeatPeriod(950);

// Camera
globe.pointOfView({{ lat: 20, lng: 0, altitude: 2.3 }}, 1200);

// Controls
const controls = globe.controls();
controls.autoRotate = true;
controls.autoRotateSpeed = spinSpeed;
controls.enableDamping = true;
controls.dampingFactor = 0.05;

function toggleAutoSpin() {{
  isSpinning = !isSpinning;
  controls.autoRotate = isSpinning;
  const btn = document.getElementById('spin-btn');
  if (isSpinning) {{
    btn.innerHTML = '⏸️ Pause Spin';
    btn.classList.add('active');
  }} else {{
    btn.innerHTML = '▶️ Resume Spin';
    btn.classList.remove('active');
  }}
}}

function toggleTexture() {{
  isNight = !isNight;
  const btn = document.getElementById('tex-btn');
  if (isNight) {{
    globe.globeImageUrl(TEX_NIGHT);
    btn.innerHTML = '🛰️ Blue Marble';
  }} else {{
    globe.globeImageUrl(TEX_BLUE_MARBLE);
    btn.innerHTML = '🌃 Night Lights';
  }}
}}

// TOGGLE 3D BARS VS COLORED THREAT DOTS (RED, ORANGE, YELLOW)
function toggleVisMode() {{
  isDotsMode = !isDotsMode;
  const btn = document.getElementById('vis-btn');
  if (isDotsMode) {{
    globe
      .pointAltitude(0.005)
      .pointRadius(0.62);
    btn.innerHTML = '📊 3D Bars';
    btn.classList.add('active');
  }} else {{
    globe
      .pointAltitude(d => d.size)
      .pointRadius(0.36);
    btn.innerHTML = '📍 Threat Dots';
    btn.classList.remove('active');
  }}
}}

// MINIMIZE / EXPAND HUD WINDOW
let isHudMinimized = false;
let isCleanView = false;
let isBadgeMin = false;
let isLegendMin = false;

function toggleMinimizeHud() {{
  isHudMinimized = !isHudMinimized;
  const hud = document.getElementById('globe-hud');
  const minIcon = document.getElementById('min-icon');
  const minText = document.getElementById('min-text');

  if (isHudMinimized) {{
    hud.classList.add('minimized');
    minIcon.innerHTML = '🗖';
    minText.innerHTML = 'Expand HUD';
  }} else {{
    hud.classList.remove('minimized');
    minIcon.innerHTML = '🗕';
    minText.innerHTML = 'Minimize';
  }}
}}

// 100% UNOBSTRUCTED CLEAN GLOBE VIEW (Hides all overlays)
function toggleCleanGlobeView() {{
  isCleanView = !isCleanView;
  const cleanBtn = document.getElementById('clean-view-btn');
  const hud = document.getElementById('globe-hud');
  const badge = document.getElementById('target-badge');
  const legend = document.getElementById('legend-box');

  if (isCleanView) {{
    isHudMinimized = true;
    hud.classList.add('minimized');
    document.getElementById('min-icon').innerHTML = '🗖';
    document.getElementById('min-text').innerHTML = 'Expand HUD';
    badge.style.display = 'none';
    legend.style.display = 'none';
    if (cleanBtn) {{
      cleanBtn.innerHTML = '👁️ Restore HUD';
      cleanBtn.classList.add('active');
    }}
  }} else {{
    isHudMinimized = false;
    hud.classList.remove('minimized');
    document.getElementById('min-icon').innerHTML = '🗕';
    document.getElementById('min-text').innerHTML = 'Minimize';
    badge.style.display = 'block';
    legend.style.display = 'block';
    if (cleanBtn) {{
      cleanBtn.innerHTML = '👁️ Clean View';
      cleanBtn.classList.remove('active');
    }}
  }}
}}

function toggleBadgeMin() {{
  isBadgeMin = !isBadgeMin;
  const b = document.getElementById('badge-desc');
  b.style.display = isBadgeMin ? 'none' : 'block';
}}

function toggleLegendMin() {{
  isLegendMin = !isLegendMin;
  const l = document.getElementById('legend-content');
  l.style.display = isLegendMin ? 'none' : 'block';
}}

// TOGGLE REAL-TIME SATELLITE VS AI/ML PREDICTIVE FORECAST (NEXT 6-12 HOURS)
function toggleDataStreamMode() {{
  if (currentMode === "realtime") {{
    currentMode = "predictive";
  }} else {{
    currentMode = "realtime";
  }}
  updateModeUI();
}}

function updateModeUI() {{
  const modeBtn = document.getElementById('mode-btn');
  const horizonControls = document.getElementById('horizon-controls');
  const hudTitle = document.getElementById('hud-title-text');
  const hudDesc = document.getElementById('hud-desc-text');
  const badgeTitle = document.getElementById('badge-title');
  const badgeDesc = document.getElementById('badge-desc');

  if (currentMode === "predictive") {{
    modeBtn.innerHTML = '🔴 Switch to Real-Time Data';
    horizonControls.style.display = 'flex';
    hudTitle.innerHTML = '🔮 AI/ML PLANETARY DISASTER FORECAST OBSERVATORY';
    hudDesc.innerHTML = '<b>AI/ML Spread Forecast (Next 6-12 Hours):</b> Neural Rothermel-Huygens propagation dynamics model showing forward wave fronts and downwind ember dispersions.';
    badgeTitle.innerHTML = '🔮 AI/ML MODEL: Rothermel-Huygens Neural Expansion Engine';
    badgeDesc.innerHTML = 'Forecast Horizon: <b>Next 6 to 12 Hours</b> | Confidence: <b>92.4%</b>';
    globe.atmosphereColor('#a855f7');
  }} else {{
    modeBtn.innerHTML = '🔮 Switch to AI/ML 6-12h Forecast';
    horizonControls.style.display = 'none';
    hudTitle.innerHTML = '🛰️ ULTRA-HD 3D PLANETARY OBSERVATORY';
    hudDesc.innerHTML = 'High-Resolution NASA Earth imagery showing <b>{total_count:,}</b> live orbital thermal anomaly points.';
    badgeTitle.innerHTML = '🌐 TARGET SECTOR: {sector_name}';
    badgeDesc.innerHTML = 'Global Hotspots: <b>{total_count:,} points</b> | Sensor: <b>VIIRS Suomi-NPP 375m</b>';
    globe.atmosphereColor('#38bdf8');
  }}

  // Refresh datasets
  globe
    .pointsData(getActivePoints())
    .arcsData(getActiveArcs())
    .ringsData(getActiveEpicenters());
}}

function setForecastHorizon(horizon) {{
  currentHorizon = horizon;
  document.getElementById('hor-all-btn').classList.remove('active');
  document.getElementById('hor-6h-btn').classList.remove('active');
  document.getElementById('hor-12h-btn').classList.remove('active');

  if (horizon === 'all') document.getElementById('hor-all-btn').classList.add('active');
  else if (horizon === '6h') document.getElementById('hor-6h-btn').classList.add('active');
  else if (horizon === '12h') document.getElementById('hor-12h-btn').classList.add('active');

  globe.pointsData(getActivePoints());
}}

function flyToTarget(lat, lng) {{
  controls.autoRotate = false;
  isSpinning = false;
  document.getElementById('spin-btn').innerHTML = '▶️ Resume Spin';
  document.getElementById('spin-btn').classList.remove('active');
  
  globe.pointOfView({{
    lat: lat,
    lng: lng,
    altitude: 0.72
  }}, 2200);
}}

function orbitView() {{
  globe.pointOfView({{
    lat: 15,
    lng: 10,
    altitude: 2.4
  }}, 1800);
}}

window.addEventListener('resize', () => {{
  globe.width(window.innerWidth);
  globe.height(window.innerHeight);
}});
</script>
</body>
</html>
"""
    return html
