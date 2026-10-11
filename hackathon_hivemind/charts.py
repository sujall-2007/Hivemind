import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Dark tactical styling tokens
TACTICAL_TEMPLATE = "plotly_dark"
COLOR_CRITICAL = "#ef4444"
COLOR_WARNING = "#f97316"
COLOR_AMBER = "#f59e0b"
COLOR_CYAN = "#38bdf8"
BG_DARK = "#0d1117"
BG_CARD = "#161b22"
BORDER_COLOR = "#30363d"

def create_spread_expansion_chart(forecasts_summary: list, current_area_ha: float):
    """
    Renders an interactive hazard footprint expansion curve over 0h, 6h, 12h, 24h horizons.
    """
    horizons = ["Current (0h)"]
    areas = [current_area_ha]
    growths = ["0%"]
    advances = ["0 km"]
    priorities = ["ACTIVE FOOTPRINT"]

    for f in forecasts_summary:
        horizons.append(f.get("horizon", ""))
        areas.append(f.get("projected_area_ha", 0))
        growths.append(f.get("projected_growth", "0%"))
        advances.append(f.get("advance_distance_km", "0 km"))
        priorities.append(f.get("priority", "WARNING"))

    fig = go.Figure()

    # Fill area curve
    fig.add_trace(go.Scatter(
        x=horizons,
        y=areas,
        mode="lines+markers+text",
        name="Projected Burn Area (ha)",
        line=dict(color=COLOR_WARNING, width=4, shape="spline"),
        marker=dict(size=12, color=[COLOR_CRITICAL, COLOR_AMBER, COLOR_WARNING, "#b91c1c"],
                    line=dict(color="#ffffff", width=2)),
        text=[f"<b>{a:,.0f} ha</b><br>({g})" for a, g in zip(areas, growths)],
        textposition="top center",
        fill="tozeroy",
        fillcolor="rgba(249, 115, 22, 0.18)",
        hovertemplate="<b>%{x}</b><br>Area: %{y:,.1f} hectares<br>Advance: %{customdata}<extra></extra>",
        customdata=advances
    ))

    # Critical evacuation threshold line
    threshold = current_area_ha * 1.5
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color=COLOR_CRITICAL,
        annotation_text="Critical Evacuation Trigger (+50%)",
        annotation_position="bottom right",
        annotation_font=dict(color=COLOR_CRITICAL, size=11)
    )

    fig.update_layout(
        template=TACTICAL_TEMPLATE,
        title=dict(text="<b>📈 Hazard Perimeter Propagation Curve</b>", font=dict(size=15, color="#f8fafc")),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=40, r=40, t=50, b=40),
        height=320,
        xaxis=dict(gridcolor=BORDER_COLOR, title="Forecast Horizon"),
        yaxis=dict(gridcolor=BORDER_COLOR, title="Surface Area (Hectares)"),
        showlegend=False
    )
    return fig

def create_wind_radar_compass(telemetry: dict):
    """
    Renders a polar radar compass displaying wind velocity vector vs hazard propagation heading.
    """
    wind_from_deg = telemetry.get("wind_direction_deg", 315.0)
    spread_to_deg = telemetry.get("spread_azimuth_deg", 135.0)
    wind_speed = telemetry.get("wind_speed_mph", 15.0)
    gusts = telemetry.get("wind_gusts_mph", 22.0)

    fig = go.Figure()

    # 1. Incoming Wind Vector
    fig.add_trace(go.Barpolar(
        r=[wind_speed],
        theta=[wind_from_deg],
        width=[18],
        marker_color=COLOR_CYAN,
        marker_line_color="#ffffff",
        marker_line_width=1.5,
        opacity=0.85,
        name=f"Wind Origin ({wind_from_deg:.0f}° @ {wind_speed} mph)"
    ))

    # 2. Forward Spread Heading Vector (Where fire expands)
    fig.add_trace(go.Barpolar(
        r=[gusts * 1.15],
        theta=[spread_to_deg],
        width=[32],
        marker_color=COLOR_CRITICAL,
        marker_line_color=COLOR_WARNING,
        marker_line_width=2,
        opacity=0.9,
        name=f"Hazard Spread Heading ({spread_to_deg:.0f}°)"
    ))

    fig.update_layout(
        template=TACTICAL_TEMPLATE,
        title=dict(text="<b>🧭 Dynamic Wind & Spread Polar Vector</b>", font=dict(size=14, color="#f8fafc")),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        margin=dict(l=30, r=30, t=45, b=30),
        height=300,
        polar=dict(
            radialaxis=dict(showticklabels=False, ticks="", gridcolor=BORDER_COLOR),
            angularaxis=dict(
                direction="clockwise",
                period=360,
                gridcolor=BORDER_COLOR,
                linecolor=BORDER_COLOR,
                tickfont=dict(size=11, color="#94a3b8")
            ),
            bgcolor=BG_DARK
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=10))
    )
    return fig

def create_danger_gauge(danger_index: float, risk_level: str):
    """
    Renders an interactive Fire Danger Rating speedometer gauge.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=danger_index,
        title=dict(text=f"<b>Fire Danger Index</b><br><span style='font-size:12px;color:#f97316'>{risk_level}</span>", font=dict(size=14, color="#f8fafc")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor="#94a3b8"),
            bar=dict(color=COLOR_WARNING, thickness=0.3),
            bgcolor=BG_DARK,
            borderwidth=1,
            bordercolor=BORDER_COLOR,
            steps=[
                dict(range=[0, 30], color="rgba(16, 185, 129, 0.4)"),
                dict(range=[30, 50], color="rgba(245, 158, 11, 0.4)"),
                dict(range=[50, 75], color="rgba(249, 115, 22, 0.5)"),
                dict(range=[75, 100], color="rgba(239, 68, 68, 0.65)")
            ],
            threshold=dict(
                line=dict(color="#ffffff", width=3),
                thickness=0.75,
                value=danger_index
            )
        )
    ))

    fig.update_layout(
        template=TACTICAL_TEMPLATE,
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        margin=dict(l=25, r=25, t=35, b=20),
        height=200
    )
    return fig

def create_humidity_gauge(relative_humidity: float):
    """
    Renders a Relative Humidity gauge with volatile dry-fuel warning threshold.
    """
    bar_color = COLOR_CRITICAL if relative_humidity < 20 else (COLOR_AMBER if relative_humidity < 35 else "#10b981")
    status = "VOLATILE DRY" if relative_humidity < 20 else "MODERATE MOISTURE"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=relative_humidity,
        number=dict(suffix="%"),
        title=dict(text=f"<b>Relative Humidity (RH)</b><br><span style='font-size:12px;color:{bar_color}'>{status}</span>", font=dict(size=14, color="#f8fafc")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor="#94a3b8"),
            bar=dict(color=bar_color, thickness=0.3),
            bgcolor=BG_DARK,
            borderwidth=1,
            bordercolor=BORDER_COLOR,
            steps=[
                dict(range=[0, 20], color="rgba(239, 68, 68, 0.6)"),
                dict(range=[20, 50], color="rgba(245, 158, 11, 0.4)"),
                dict(range=[50, 100], color="rgba(16, 185, 129, 0.4)")
            ],
            threshold=dict(
                line=dict(color="#ffffff", width=3),
                thickness=0.75,
                value=relative_humidity
            )
        )
    ))

    fig.update_layout(
        template=TACTICAL_TEMPLATE,
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        margin=dict(l=25, r=25, t=35, b=20),
        height=200
    )
    return fig

def create_frp_distribution_chart(features: list):
    """
    Renders an FRP (Fire Radiative Power) thermal intensity distribution chart.
    """
    frp_vals = []
    brightness_vals = []
    
    for f in features:
        if f.get("properties", {}).get("type") == "thermal_hotspot":
            frp = f.get("properties", {}).get("frp_mw", 0)
            bright = f.get("properties", {}).get("brightness_k", 300)
            frp_vals.append(frp)
            brightness_vals.append(bright)

    if not frp_vals:
        frp_vals = [25.0, 45.0, 75.0, 110.0]

    df = pd.DataFrame({"FRP_MW": frp_vals})
    
    fig = px.histogram(
        df,
        x="FRP_MW",
        nbins=12,
        title="<b>🔥 Satellite Thermal Radiative Power (FRP) Spectrum</b>",
        color_discrete_sequence=[COLOR_WARNING],
        labels={"FRP_MW": "Radiative Power (Megawatts)", "count": "Hotspot Count"}
    )

    fig.update_layout(
        template=TACTICAL_TEMPLATE,
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_DARK,
        margin=dict(l=40, r=30, t=50, b=40),
        height=280,
        xaxis=dict(gridcolor=BORDER_COLOR),
        yaxis=dict(gridcolor=BORDER_COLOR)
    )
    return fig
