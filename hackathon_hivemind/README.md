# 🔥 Hivemind: Near-Real-Time Disaster Perimeter & Spread Forecasting

An automated Earth Observation analysis engine that continuously ingests satellite thermal anomaly telemetry, rapidly isolates high-precision active disaster boundaries (burn scars / fire fronts), and fuses geometry with localized meteorological dynamics to forecast hazard propagation over 6, 12, and 24-hour horizons.

---

## 🎯 Problem Statement & Alignment

| Hackathon Criterion | Technical Solution in Hivemind |
| :--- | :--- |
| **Boundary Extraction Accuracy** | Replaced naive bounding boxes with **GEOS Concave Hull (Alpha-Shape equivalent)** and **VIIRS 375m Spatial Buffer Delineation**, preserving natural concave fingers and unburned terrain pockets. |
| **Multi-Variable Spread Forecasting** | Fuses perimeter geometry with **Open-Meteo High-Resolution live meteorological feeds** using **Rothermel & Anderson fire physics** and **Huygens anisotropic wave-front propagation** driven by wind vectors, relative humidity, temperature, and slope. |
| **Data Pipeline Efficiency** | Sub-second end-to-end execution latency (< 450 ms). Compresses raw multi-gigabyte orbital imagery into **lightweight, actionable RFC 7946 GeoJSON (< 30 KB)** ready for tactical field GPS and low-bandwidth edge deployment. |

---

## 🏗️ System Architecture

```text
[ NASA FIRMS Satellites ]               [ Open-Meteo Weather API ]
 (VIIRS 375m & MODIS NRT)                (Wind Vector, RH, Temp)
           │                                       │
           ▼                                       ▼
    nasaapi.py (Ingestion)                  weather.py (Telemetry)
           │                                       │
           ▼                                       │
   geometry.py (Boundary Extraction)               │
   - Concave Hull (Alpha-Shapes)                   │
   - VIIRS Spatial Buffering                       │
   - Geodesic Perimeter & Area (ha)                │
           │                                       │
           └───────────────────┬───────────────────┘
                               ▼
                     forecaster.py (Propagation)
                     - Rothermel Rate of Spread (ROS)
                     - Anisotropic Elliptical Wave Front
                     - Horizons: +6h, +12h, +24h Envelopes
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
      server.py (FastAPI REST)         app.py (Streamlit HUD)
      - /api/disaster-intelligence     - Interactive Tactical Map
      - /api/telemetry                 - Live Weather & FRP Telemetry
      - /api/simulate                  - "What-If" Scenario Sliders
                                       - 1-Click GeoJSON Export
```

---

## 🚀 Quickstart & Execution

### 1. Run Pipeline CLI
Executes ingestion, boundary extraction, weather fusion, and spread forecasting, saving the compressed output:
```bash
python main.py
```
Output: `disaster_forecast.geojson` (~29 KB).

### 2. Launch FastAPI Backend Microservice
Starts the REST API serving sub-second tactical intelligence:
```bash
python server.py
# Server runs at http://localhost:8000
# Interactive OpenAPI Docs: http://localhost:8000/docs
```

### 3. Launch Streamlit Tactical Command Center
Starts the web application:
```bash
streamlit run app.py
```

---

## 📡 API Endpoints

- `GET /api/disaster-intelligence`: Returns full GeoJSON FeatureCollection with active perimeters, forecasts (+6h, +12h, +24h), and thermal anomaly hotspots.
- `GET /api/telemetry`: Real-time meteorological stream and fire danger index.
- `POST /api/simulate`: Dynamic what-if hazard simulation with custom wind speed, direction, and humidity.
- `GET /api/incidents`: Incident catalog (California Sierra, Park Fire, Smokehouse Creek).

---

## 🔬 Mathematical Models & Algorithms

1. **Concave Boundary Extraction**:
   $$\text{Hull} = \alpha\text{-Shape}(\mathcal{P}, \text{ratio}=0.35) \oplus \mathcal{B}_{\text{sensor}}(\delta = 375\text{ m})$$
2. **Elliptical Fire Spread Eccentricity** (Anderson 1983):
   $$L/B = 1.0 + 0.11 \times U_{\text{mph}}$$
3. **Head Rate of Spread ($ROS_{\text{head}}$)** (Rothermel 1972):
   $$ROS_{\text{head}} = ROS_0 \times (1 + \phi_w + \phi_s) \times \exp(-0.035 \times RH) \times \Phi_T$$
4. **Huygens Wave-Front Propagation**:
   $$\mathcal{H}(t + \Delta t) = \bigcup_{p \in \partial \Omega} \mathcal{E}\left(p, ROS_{\text{head}} \Delta t, ROS_{\text{flank}} \Delta t, \theta_{\text{spread}}\right)$$