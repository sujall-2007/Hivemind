import math
import numpy as np
from shapely.geometry import Point, MultiPoint, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
import shapely

def calculate_geodesic_metrics(poly: Polygon):
    """
    Computes real-world perimeter (km) and area (hectares, km2)
    using ellipsoidal projection around centroid latitude.
    """
    if poly.is_empty:
        return {"area_km2": 0.0, "area_hectares": 0.0, "perimeter_km": 0.0}
        
    centroid = poly.centroid
    lat_center = centroid.y
    
    # Degrees to meters conversion factors
    m_per_deg_lat = 111132.954 - 559.822 * math.cos(2 * math.radians(lat_center))
    m_per_deg_lon = 111412.84 * math.cos(math.radians(lat_center))
    
    # Project polygon vertices to metric planar coordinates
    def to_metric(lon, lat):
        return (lon * m_per_deg_lon, lat * m_per_deg_lat)
        
    exterior_coords = [to_metric(x, y) for x, y in poly.exterior.coords]
    metric_poly = Polygon(exterior_coords)
    
    area_sq_m = metric_poly.area
    perimeter_m = metric_poly.length
    
    return {
        "area_sq_m": round(area_sq_m, 2),
        "area_km2": round(area_sq_m / 1_000_000.0, 3),
        "area_hectares": round(area_sq_m / 10_000.0, 2),
        "perimeter_km": round(perimeter_m / 1_000.0, 2)
    }

def create_boundary_polygon(raw_coords, concavity_ratio: float = 0.35, buffer_km: float = 0.4):
    """
    Member 2 Core Algorithm:
    Transforms raw [lon, lat] satellite anomaly points into a high-precision,
    concave boundary polygon using GEOS concave hull and geodesic buffer smoothing.
    """
    if not raw_coords or len(raw_coords) < 3:
        return None
        
    pts = MultiPoint([Point(p[0], p[1]) for p in raw_coords])
    
    # Step 1: Compute Concave Hull (Alpha-Shape equivalent in GEOS)
    try:
        hull = shapely.concave_hull(pts, ratio=concavity_ratio, allow_holes=False)
    except Exception:
        hull = pts.convex_hull
        
    # Step 2: Buffer by sensor ground sampling distance (VIIRS is ~375m)
    lat_center = pts.centroid.y
    deg_buffer = buffer_km / 111.0 # Approximate degrees
    
    # Smooth buffered polygon to close pixel gaps
    buffered_poly = hull.buffer(deg_buffer, resolution=16)
    
    # Simplify slightly to compress GeoJSON payload size (<25KB) for tactical deployment
    simplified_poly = buffered_poly.simplify(0.0008, preserve_topology=True)
    
    if isinstance(simplified_poly, MultiPolygon):
        # Pick the largest polygon or keep unified
        simplified_poly = max(simplified_poly.geoms, key=lambda p: p.area)
        
    return simplified_poly

def extract_hazard_feature(raw_points, concavity_ratio: float = 0.35, buffer_km: float = 0.4):
    """
    Extracts full boundary geometry, aggregates sensor radiative power (FRP),
    and formats as an RFC 7946 GeoJSON Feature.
    """
    coords = [[p["longitude"], p["latitude"]] for p in raw_points] if isinstance(raw_points[0], dict) else raw_points
    poly = create_boundary_polygon(coords, concavity_ratio, buffer_km)
    
    if poly is None or poly.is_empty:
        return None
        
    metrics = calculate_geodesic_metrics(poly)
    centroid = poly.centroid
    
    # Aggregate thermal sensor statistics if metadata present
    total_frp = 0.0
    max_frp = 0.0
    avg_brightness = 310.0
    
    if isinstance(raw_points[0], dict):
        frp_vals = [p.get("frp", 0.0) for p in raw_points]
        bright_vals = [p.get("brightness", 310.0) for p in raw_points]
        total_frp = sum(frp_vals)
        max_frp = max(frp_vals) if frp_vals else 0.0
        avg_brightness = sum(bright_vals) / len(bright_vals) if bright_vals else 310.0

    return {
        "type": "Feature",
        "properties": {
            "type": "current_perimeter",
            "hazard": "wildfire_active_front",
            "status": "active_hazard",
            "area_km2": metrics["area_km2"],
            "area_hectares": metrics["area_hectares"],
            "perimeter_km": metrics["perimeter_km"],
            "centroid": [round(centroid.x, 5), round(centroid.y, 5)],
            "active_hotspot_count": len(raw_points),
            "total_frp_mw": round(total_frp, 1),
            "peak_frp_mw": round(max_frp, 1),
            "mean_brightness_kelvin": round(avg_brightness, 1),
            "extraction_method": "GEOS Concave Hull (Alpha-Shape) + VIIRS 375m Spatial Buffer"
        },
        "geometry": mapping(poly)
    }
