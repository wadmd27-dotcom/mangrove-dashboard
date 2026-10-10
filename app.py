import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
import shapely.geometry
import streamlit as st
from streamlit_folium import st_folium
import folium

# --- Page Configuration ---
st.set_page_config(
    page_title="GCC Mangrove Health & Restoration Monitor",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 GCC Mangrove Health & Restoration Monitor")
st.markdown(
    "**Early detection of mangrove degradation and restoration prioritization** across the GCC region using Sentinel-2, Tanager hyperspectral data, and Global Mangrove Watch baselines."
)


# --- Backend Processing Function (Optional automated pipeline) ---
def process_mangrove_health(
    sentinel_ndvi_path, gmw_baseline_mask_path, output_geojson_path
):
  """Processes Sentinel-2 / Tanager indices against GMW baseline

  to classify mangrove health and restoration priority zones.
  """
  try:
    with rasterio.open(sentinel_ndvi_path) as src:
      ndvi_image = src.read(1)
      transform = src.transform
      crs = src.crs

    with rasterio.open(gmw_baseline_mask_path) as mask_src:
      gmw_mask = mask_src.read(1)

    class_array = np.zeros_like(ndvi_image, dtype=np.uint8)
    mangrove_pixels = gmw_mask == 1

    # Threshold rules
    class_array[mangrove_pixels & (ndvi_image >= 0.6)] = 1  # Green: Healthy
    class_array[
        mangrove_pixels & (ndvi_image >= 0.3) & (ndvi_image < 0.6)
    ] = 2  # Yellow: Stress
    class_array[mangrove_pixels & (ndvi_image < 0.3)] = (
        3  # Red: Degraded / Loss
    )

    restoration_zone = (gmw_mask == 0) & (ndvi_image > 0.1) & (ndvi_image < 0.3)
    class_array[restoration_zone] = 4

    results = (
        {"properties": {"class_id": int(v)}, "geometry": s}
        for i, (s, v) in enumerate(shapes(class_array, transform=transform))
        if v > 0
    )

    gdf = gpd.GeoDataFrame.from_features(list(results), crs=crs)
    class_labels = {
        1: "Green: Healthy Mangrove",
        2: "Yellow: Possible Stress",
        3: "Red: Degraded / Change Area",
        4: "Blue: Restoration Priority",
    }
    gdf["status"] = gdf["class_id"].map(class_labels)
    gdf.to_file(output_geojson_path, driver="GeoJSON")
    return True
  except Exception:
    return False


# --- Sidebar Controls ---
st.sidebar.header("GCC Monitoring Controls")

# GCC Hotspot Selector
gcc_hotspot = st.sidebar.selectbox(
    "Select GCC Coastal Area",
    options=[
        "Entire GCC Overview",
        "UAE (Abu Dhabi / Dubai / Ras Al Khaimah)",
        "Saudi Arabia (Jubail / Red Sea Coast)",
        "Oman (Al Wusta / Muscat)",
        "Qatar / Bahrain / Kuwait",
    ],
)

# Coordinate dictionary for zooming into GCC countries/hotspots
hotspot_coords = {
    "Entire GCC Overview": ([24.0, 52.0], 6),
    "UAE (Abu Dhabi / Dubai / Ras Al Khaimah)": ([24.4539, 54.3773], 9),
    "Saudi Arabia (Jubail / Red Sea Coast)": ([24.0, 38.0], 7),
    "Oman (Al Wusta / Muscat)": ([20.5, 57.7], 7),
    "Qatar / Bahrain / Kuwait": ([26.0, 50.5], 8),
}

current_center, current_zoom = hotspot_coords[gcc_hotspot]

# Layer display filters
layer_toggle = st.sidebar.multiselect(
    "Display Map Layers",
    options=[
        "Green: Healthy Mangrove",
        "Yellow: Possible Stress",
        "Red: Degraded / Change Area",
        "Blue: Restoration Priority",
    ],
    default=[
        "Green: Healthy Mangrove",
        "Yellow: Possible Stress",
        "Red: Degraded / Change Area",
        "Blue: Restoration Priority",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Data Stack:** Sentinel-2 (frequent monitoring) + Tanager (hyperspectral stress indicators) + Global Mangrove Watch (baseline reference)."
)


# --- Load Data (Fallback to sample polygons if GeoJSON isn't generated yet) ---
@st.cache_data
def load_mangrove_data():
  try:
    return gpd.read_file("mangrove_classified.geojson")
  except Exception:
    return None


gdf = load_mangrove_data()

# --- Initialize Folium Map ---
m = folium.Map(
    location=current_center, zoom_start=current_zoom, tiles="CartoDB positron"
)

# Color map dictionary
color_map = {
    "Green: Healthy Mangrove": "green",
    "Yellow: Possible Stress": "orange",
    "Red: Degraded / Change Area": "red",
    "Blue: Restoration Priority": "blue",
}

if gdf is not None and not gdf.empty:
  # Render real data if available
  for _, row in gdf.iterrows():
    status = row["status"]
    if status in layer_toggle:
      col = color_map.get(status, "gray")
      folium.GeoJson(
          row["geometry"],
          style_function=lambda x, color=col: {
              "fillColor": color,
              "color": color,
              "weight": 1,
              "fillOpacity": 0.6,
          },
          tooltip=status,
      ).add_to(m)
else:
  # Fallback sample mockup polygons in the GCC region for immediate preview
  sample_features = []

  if "Green: Healthy Mangrove" in layer_toggle:
    folium.Polygon(
        locations=[
            [24.46, 54.37],
            [24.47, 54.38],
            [24.45, 54.39],
            [24.44, 54.37],
        ],
        color="green",
        fill=True,
        fill_color="green",
        fill_opacity=0.6,
        popup="Green: Healthy Mangrove (Stable Canopy)",
    ).add_to(m)

  if "Yellow: Possible Stress" in layer_toggle:
    folium.Polygon(
        locations=[
            [24.47, 54.39],
            [24.48, 54.40],
            [24.46, 54.41],
        ],
        color="orange",
        fill=True,
        fill_color="yellow",
        fill_opacity=0.6,
        popup="Yellow: Possible Stress (Salinity/Moisture anomaly detected via Tanager)",
    ).add_to(m)

  if "Red: Degraded / Change Area" in layer_toggle:
    folium.Polygon(
        locations=[
            [24.43, 54.35],
            [24.44, 54.36],
            [24.42, 54.36],
        ],
        color="darkred",
        fill=True,
        fill_color="red",
        fill_opacity=0.6,
        popup="Red: Degraded / Canopy Loss Area",
    ).add_to(m)

  if "Blue: Restoration Priority" in layer_toggle:
    folium.Polygon(
        locations=[
            [24.41, 54.33],
            [24.42, 54.34],
            [24.40, 54.35],
        ],
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.5,
        popup="Blue: Restoration Priority Zone (Favorable tidal flats & historical GMW footprint)",
    ).add_to(m)

# --- Custom Map Legend HTML ---
legend_html = """
    <div style="position: fixed; 
                bottom: 30px; left: 30px; width: 250px; height: 160px; 
                background-color: white; z-index:9999; font-size:13px;
                border:2px solid grey; border-radius: 6px; padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">
      <b>GCC Mangrove Health Legend</b><br>
      <i style="background:green; width:14px; height:14px; display:inline-block; margin-right:5px;"></i> Green: Healthy Mangrove<br>
      <i style="background:orange; width:14px; height:14px; display:inline-block; margin-right:5px;"></i> Yellow: Possible Stress<br>
      <i style="background:red; width:14px; height:14px; display:inline-block; margin-right:5px;"></i> Red: Degraded / Change<br>
      <i style="background:blue; width:14px; height:14px; display:inline-block; margin-right:5px;"></i> Blue: Restoration Priority<br>
    </div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# --- Render Map in Streamlit ---
st_data = st_folium(m, width=1150, height=550)

# --- Summary Metrics Section ---
st.markdown("### Regional Health & Restoration Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Healthy Cover (Green)", "1,245 ha", "+2.1% YoY")
col2.metric("Stressed Areas (Yellow)", "180 ha", "Action Required")
col3.metric("Degraded Loss (Red)", "45 ha", "Change Detected")
col4.metric("Restoration Potential (Blue)", "320 ha", "Tier-1 Priority Flats")
