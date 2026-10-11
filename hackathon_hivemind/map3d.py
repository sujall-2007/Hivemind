import json
import math

def generate_3d_deckgl_map_html(geojson_data: dict, weather_telemetry: dict, initial_pitch: int = 58, initial_bearing: int = 25):
    """
    Builds a high-performance 3D WebGL Deck.gl map:
    - 3D tilted camera (pitch 58°, bearing 25°) with full mouse orbit & tilt controls
    - 3D elevated thermal flame pillars (ColumnLayer) with height scaled to Fire Radiative Power (MW)
    - 3D extruded hazard boundaries (PolygonLayer) for current perimeter and forecast envelopes (+6h, +12h)
    - 3D wind propagation trajectory vector
    - Built-in cinematic 'Auto-Orbit 360°' presentation mode and on-map controls
    """
    metadata = geojson_data.get("metadata", {})
    perimeter_props = metadata.get("current_perimeter", {})
    centroid = perimeter_props.get("centroid", [-121.834, 37.379])
    center_lon, center_lat = centroid[0], centroid[1]

    # Extract 3D thermal hotspot pillars
    hotspots = []
    polygons = []
    
    for feat in geojson_data.get("features", []):
        f_type = feat.get("properties", {}).get("type", "")
        geom = feat.get("geometry", {})
        
        if f_type == "thermal_hotspot" and geom.get("type") == "Point":
            coords = geom.get("coordinates", [])
            frp = feat.get("properties", {}).get("frp_mw", 15.0)
            bright = feat.get("properties", {}).get("brightness_k", 320.0)
            conf = feat.get("properties", {}).get("confidence", "nominal")
            hotspots.append({
                "coordinates": coords,
                "frp": frp,
                "brightness": bright,
                "confidence": conf,
                # Height scaled from 200m to 2500m based on FRP
                "elevation": max(150.0, min(3000.0, frp * 22.0)),
                "radius": 140
            })
        elif geom.get("type") == "Polygon":
            poly_coords = geom.get("coordinates", [[]])[0]
            # Height extrusion in meters
            elev = 220 if f_type == "current_perimeter" else (110 if f_type == "forecast_6hr" else 50)
            
            # Color palettes
            if f_type == "current_perimeter":
                fill_color = [239, 68, 68, 140]
                line_color = [255, 30, 30, 255]
                name = "Active Disaster Perimeter"
            elif f_type == "forecast_6hr":
                fill_color = [245, 158, 11, 100]
                line_color = [245, 158, 11, 230]
                name = "+6h Predicted Spread Envelope"
            elif f_type == "forecast_12hr":
                fill_color = [234, 88, 12, 75]
                line_color = [234, 88, 12, 200]
                name = "+12h Predicted Spread Envelope"
            else:
                fill_color = [124, 45, 18, 50]
                line_color = [124, 45, 18, 160]
                name = "Forecast Zone"

            polygons.append({
                "coordinates": poly_coords,
                "elevation": elev,
                "fillColor": fill_color,
                "lineColor": line_color,
                "type": f_type,
                "name": name,
                "area_ha": feat.get("properties", {}).get("area_hectares", 0)
            })

    # Wind spread vector arrow
    spread_deg = weather_telemetry.get("spread_azimuth_deg", 135.0)
    spread_rad = math.radians(spread_deg)
    arrow_len = 0.045
    dest_lat = center_lat + arrow_len * math.cos(spread_rad)
    dest_lon = center_lon + (arrow_len * math.sin(spread_rad)) / math.cos(math.radians(center_lat))
    
    wind_vector = [
        {"path": [[center_lon, center_lat, 50], [dest_lon, dest_lat, 180]]}
    ]

    hotspots_json = json.dumps(hotspots)
    polygons_json = json.dumps(polygons)
    wind_vector_json = json.dumps(wind_vector)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Hivemind 3D Tactical Map</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://unpkg.com/deck.gl@8.9.33/dist.min.js"></script>
  <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
  <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
  <style>
    body, html {{
      margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden;
      background: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    #map-container {{ width: 100%; height: 100%; position: absolute; }}
    #hud-controls {{
      position: absolute; top: 14px; left: 14px; z-index: 100;
      background: rgba(13, 17, 23, 0.88); border: 1px solid rgba(249, 115, 22, 0.4);
      border-radius: 10px; padding: 12px 16px; color: #f3f4f6;
      box-shadow: 0 8px 32px rgba(0,0,0,0.6); backdrop-filter: blur(10px);
      font-size: 13px;
    }}
    .btn-3d {{
      background: linear-gradient(135deg, #1e293b, #0f172a);
      color: #38bdf8; border: 1px solid #0284c7; border-radius: 6px;
      padding: 6px 12px; font-size: 11px; font-weight: 600; cursor: pointer;
      margin-right: 6px; margin-top: 6px; transition: all 0.2s;
    }}
    .btn-3d:hover {{
      background: #0284c7; color: #fff;
    }}
    .btn-3d.active {{
      background: #ea580c; border-color: #f97316; color: #fff;
    }}
    #legend {{
      position: absolute; bottom: 18px; right: 18px; z-index: 100;
      background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.15);
      border-radius: 8px; padding: 10px 14px; font-size: 11px; color: #cbd5e1;
      backdrop-filter: blur(8px);
    }}
    .legend-item {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
    .legend-color {{ width: 14px; height: 14px; border-radius: 3px; }}
    .deck-tooltip {{
      font-family: monospace; font-size: 12px; line-height: 1.4;
      background: rgba(10, 15, 25, 0.95) !important;
      border: 1px solid #f97316 !important; border-radius: 6px !important;
      color: #f8fafc !important; padding: 8px 12px !important;
    }}
  </style>
</head>
<body>

<div id="map-container"></div>

<div id="hud-controls">
  <div style="font-weight: 700; color: #f97316; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
    <span>🛰️ 3D ORBITAL TACTICAL VIEW</span>
  </div>
  <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
    Right-click drag: <b>Orbit 360° & Tilt 3D</b> | Left-click: <b>Pan</b> | Scroll: <b>Zoom</b>
  </div>
  <div>
    <button id="orbit-btn" class="btn-3d" onclick="toggleAutoOrbit()">🔄 Auto-Orbit 360°</button>
    <button class="btn-3d" onclick="setPitch(65)">📐 65° Horizon Tilt</button>
    <button class="btn-3d" onclick="resetView()">🎯 Center View</button>
  </div>
</div>

<div id="legend">
  <div style="font-weight:700; color:#fff; margin-bottom:4px;">3D TACTICAL LAYERS</div>
  <div class="legend-item"><div class="legend-color" style="background:#ef4444; border:1px solid #ff0000;"></div> Current Perimeter (220m Wall)</div>
  <div class="legend-item"><div class="legend-color" style="background:#f59e0b;"></div> +6h Forecast Zone (110m Wall)</div>
  <div class="legend-item"><div class="legend-color" style="background:#ea580c;"></div> +12h Forecast Zone (50m Wall)</div>
  <div class="legend-item"><div class="legend-color" style="background:#facc15;"></div> Thermal Anomaly (FRP Pillars)</div>
  <div class="legend-item"><div class="legend-color" style="background:#38bdf8;"></div> Spread Trajectory Vector</div>
</div>

<script>
const hotspotsData = {hotspots_json};
const polygonsData = {polygons_json};
const windVectorData = {wind_vector_json};

let currentPitch = {initial_pitch};
let currentBearing = {initial_bearing};
let centerLon = {center_lon};
let centerLat = {center_lat};
let autoOrbit = false;
let orbitInterval = null;

// Initialize DeckGL with MapLibre basemap
const deckgl = new deck.DeckGL({{
  container: 'map-container',
  mapStyle: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
  initialViewState: {{
    longitude: centerLon,
    latitude: centerLat,
    zoom: 12.2,
    pitch: currentPitch,
    bearing: currentBearing,
    maxPitch: 85,
    minPitch: 0
  }},
  controller: true,
  getTooltip: ({{object}}) => {{
    if (!object) return null;
    if (object.frp !== undefined) {{
      return {{
        html: `<b>🔥 SATELLITE THERMAL DETECTION</b><br>` +
              `<b>Fire Radiative Power:</b> ${{object.frp.toFixed(1)}} MW<br>` +
              `<b>Brightness Temp:</b> ${{object.brightness.toFixed(1)}} K<br>` +
              `<b>Confidence:</b> ${{object.confidence}}<br>` +
              `<b>3D Flame Pillar:</b> ${{Math.round(object.elevation)}} meters`
      }};
    }}
    if (object.name !== undefined) {{
      return {{
        html: `<b>🛡️ ${{object.name}}</b><br>` +
              `<b>Footprint:</b> ${{object.area_ha.toFixed(1)}} hectares<br>` +
              `<b>Extrusion Height:</b> ${{object.elevation}} m`
      }};
    }}
    return null;
  }}
}});

function updateLayers() {{
  const layers = [
    // 1. 3D Extruded Polygon Boundaries (Perimeter & Forecasts)
    new deck.PolygonLayer({{
      id: 'hazard-3d-polygons',
      data: polygonsData,
      getPolygon: d => d.coordinates,
      getElevation: d => d.elevation,
      getFillColor: d => d.fillColor,
      getLineColor: d => d.lineColor,
      getLineWidth: 6,
      lineWidthUnits: 'pixels',
      extruded: true,
      wireframe: true,
      pickable: true,
      elevationScale: 1
    }}),

    // 2. 3D Elevated Thermal Anomaly Pillars (FRP Flame Columns)
    new deck.ColumnLayer({{
      id: 'thermal-3d-pillars',
      data: hotspotsData,
      getPosition: d => d.coordinates,
      getElevation: d => d.elevation,
      elevationScale: 1,
      radius: 130,
      getFillColor: d => [
        255, 
        Math.min(220, Math.max(50, 240 - d.frp * 2)), 
        20, 
        225
      ],
      getLineColor: [255, 255, 200, 255],
      lineWidthMinPixels: 1,
      extruded: true,
      pickable: true,
      material: {{
        ambient: 0.65,
        diffuse: 0.8,
        shininess: 32
      }}
    }}),

    // 3. 3D Wind Vector Trajectory Line
    new deck.PathLayer({{
      id: 'wind-vector-3d',
      data: windVectorData,
      getPath: d => d.path,
      getColor: [56, 189, 248, 255],
      getWidth: 6,
      widthUnits: 'pixels',
      capRounded: true,
      jointRounded: true
    }})
  ];

  deckgl.setProps({{ layers }});
}}

updateLayers();

function toggleAutoOrbit() {{
  autoOrbit = !autoOrbit;
  const btn = document.getElementById('orbit-btn');
  if (autoOrbit) {{
    btn.classList.add('active');
    btn.innerText = '⏹️ Stop Orbit';
    orbitInterval = setInterval(() => {{
      currentBearing = (currentBearing + 0.35) % 360;
      deckgl.setProps({{
        viewState: {{
          longitude: centerLon,
          latitude: centerLat,
          zoom: 12.2,
          pitch: currentPitch,
          bearing: currentBearing
        }}
      }});
    }}, 40);
  }} else {{
    btn.classList.remove('active');
    btn.innerText = '🔄 Auto-Orbit 360°';
    clearInterval(orbitInterval);
  }}
}}

function setPitch(p) {{
  currentPitch = p;
  deckgl.setProps({{
    viewState: {{
      longitude: centerLon,
      latitude: centerLat,
      zoom: 12.2,
      pitch: currentPitch,
      bearing: currentBearing
    }}
  }});
}}

function resetView() {{
  currentPitch = {initial_pitch};
  currentBearing = {initial_bearing};
  if (autoOrbit) toggleAutoOrbit();
  deckgl.setProps({{
    viewState: {{
      longitude: centerLon,
      latitude: centerLat,
      zoom: 12.2,
      pitch: currentPitch,
      bearing: currentBearing
    }}
  }});
}}
</script>
</body>
</html>
"""
    return html
