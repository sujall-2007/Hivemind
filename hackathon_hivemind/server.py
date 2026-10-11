from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from main import generate_disaster_intelligence
from nasaapi import PRESET_INCIDENTS
from weather import fetch_live_weather, enrich_weather_telemetry

app = FastAPI(
    title="Hivemind: Earth Observation Disaster Intelligence API",
    description="Automated near-real-time satellite thermal anomaly perimeter delineation and hazard spread forecasting engine.",
    version="2.0.0"
)

# Enable CORS for tactical dashboards & web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    incident: str = "california_fire"
    wind_speed_mph: float = 25.0
    wind_direction_deg: float = 315.0
    gusts_mph: float = 35.0
    humidity: float = 12.0
    temp_c: float = 32.0
    slope_deg: float = 8.0

@app.get("/")
def root():
    return {
        "system": "Hivemind Disaster Perimeter & Spread Forecasting Engine",
        "status": "operational",
        "endpoints": {
            "disaster_intelligence": "/api/disaster-intelligence",
            "telemetry": "/api/telemetry",
            "simulate": "/api/simulate",
            "incidents": "/api/incidents"
        }
    }

@app.get("/api/disaster-intelligence")
def get_disaster_intelligence(
    incident: str = Query("california_fire", description="Incident ID or preset"),
    wind_speed: Optional[float] = Query(None, description="Optional override wind speed in mph"),
    wind_dir: Optional[float] = Query(None, description="Optional override wind direction in degrees"),
    humidity: Optional[float] = Query(None, description="Optional override relative humidity %")
):
    """
    Ingests satellite data, delineates perimeter, and computes multi-variable spread forecast.
    Returns RFC 7946 GeoJSON FeatureCollection.
    """
    weather_override = None
    if wind_speed is not None and wind_dir is not None:
        weather_override = {
            "wind_speed_mph": wind_speed,
            "wind_direction_deg": wind_dir,
            "humidity": humidity if humidity is not None else 18.0
        }
        
    data = generate_disaster_intelligence(incident_preset=incident, weather_override=weather_override)
    return data

@app.get("/api/telemetry")
def get_telemetry(lat: float = 37.38, lon: float = -121.85):
    """
    Returns live meteorological telemetry and computed fire risk metrics.
    """
    return fetch_live_weather(lat, lon)

@app.get("/api/incidents")
def list_incidents():
    """
    Returns catalog of active disaster benchmark incidents.
    """
    return PRESET_INCIDENTS

@app.post("/api/simulate")
def simulate_spread(payload: SimulationRequest):
    """
    Runs a dynamic 'what-if' tactical scenario simulating changing wind vectors and humidity.
    """
    weather_override = {
        "wind_speed_mph": payload.wind_speed_mph,
        "wind_direction_deg": payload.wind_direction_deg,
        "gusts_mph": payload.gusts_mph,
        "humidity": payload.humidity,
        "temp_c": payload.temp_c
    }
    return generate_disaster_intelligence(
        incident_preset=payload.incident,
        weather_override=weather_override
    )

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
