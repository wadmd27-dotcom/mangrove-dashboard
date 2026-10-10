import folium
import json
import streamlit as st
from streamlit_folium import st_folium

# --- Page Configuration ---
st.set_page_config(
    page_title="GCC Mangrove Interactive Monitor", page_icon="🌿", layout="wide"
)

st.title("🌿 GCC Mangrove Interactive Monitoring Dashboard")
st.markdown(
    "**Click on any polygon on the map** to inspect its Mangrove Mapping, precise Health Scores, Median NDVI, and Change Detection analysis."
)

# --- Define Interactive GCC Mangrove Sites with Specific Metrics ---
gcc_sites_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[54.37, 24.46], [54.38, 24.47], [54.39, 24.45], [54.37, 24.46]]],
            },
            "properties": {
                "name": "Eastern Mangroves (Abu Dhabi, UAE)",
                "status": "Green: Healthy Mangrove",
                "color": "green",
                "mapping": "Confirmed continuous canopy matching Global Mangrove Watch (GMW) baseline.",
                "health_score_text": "Optimal canopy density and leaf moisture levels via Tanager hyperspectral bands.",
                "health_score_num": "84.2 / 100",
                "median_ndvi": "0.6850",
                "possible_decrease": "0.05%",
                "stable_area": "99.95%",
            },
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[54.40, 24.47], [54.41, 24.48], [54.42, 24.46], [54.40, 24.47]]],
            },
            "properties": {
                "name": "Al Jubail Island Fringes (Abu Dhabi, UAE)",
                "status": "Yellow: Possible Stress",
                "color": "orange",
                "mapping": "Inland landward fringe within GMW historical boundary.",
                "health_score_text": "Early-stage high salinity/osmotic stress detected.",
                "health_score_num": "52.4 / 100",
                "median_ndvi": "0.3120",
                "possible_decrease": "4.50%",
                "stable_area": "95.50%",
            },
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[38.20, 24.10], [38.22, 24.12], [38.21, 24.08], [38.20, 24.10]]],
            },
            "properties": {
                "name": "Red Sea Coast Mangrove Stand (Saudi Arabia)",
                "status": "Red: Degraded / Change Area",
                "color": "red",
                "mapping": "Significant canopy recession compared to baseline reference.",
                "health_score_text": "Leaf necrosis & severe water deficit indicators.",
                "health_score_num": "27.6 / 100",
                "median_ndvi": "0.0039",
                "possible_decrease": "0.37%",
                "stable_area": "99.63%",
            },
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[57.70, 20.50], [57.73, 20.52], [57.72, 20.48], [57.70, 20.50]]],
            },
            "properties": {
                "name": "Al Qurm Intertidal Flat (Muscat / Al Wusta, Oman)",
                "status": "Blue: Restoration Priority",
                "color": "blue",
                "mapping": "Historical GMW footprint with favorable intertidal mudflat characteristics.",
                "health_score_text": "Bare tidal flat primed for reforestation initiative.",
                "health_score_num": "N/A",
                "median_ndvi": "0.1450",
                "possible_decrease": "0.00%",
                "stable_area": "100.0% (Bare Flat)",
            },
        },
    ],
}

# --- Sidebar Filters ---
st.sidebar.header("Interactive Controls")
selected_status = st.sidebar.multiselect(
    "Filter Layers by Status",
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

filtered_features = [
    f for f in gcc_sites_geojson["features"] if f["properties"]["status"] in selected_status
]
filtered_geojson = {"type": "FeatureCollection", "features": filtered_features}

# --- Initialize Folium Map ---
m = folium.Map(location=[24.0, 52.0], zoom_start=6, tiles="OpenStreetMap")


def style_fn(feature):
  return {
      "fillColor": feature["properties"]["color"],
      "color": feature["properties"]["color"],
      "weight": 2,
      "fillOpacity": 0.6,
  }


folium.GeoJson(
    filtered_geojson,
    style_function=style_fn,
    tooltip=folium.GeoJsonTooltip(fields=["name", "status"], aliases=["Site:", "Status:"]),
).add_to(m)

# --- Render Map and Capture Clicks ---
st.markdown("### Interactive Map (Click any colored polygon below)")
map_data = st_folium(m, width=1150, height=450, returned_objects=["last_object_clicked"])

# --- Dynamic Site Inspector Section ---
st.markdown("---")
st.subheader("📍 Site Inspector & Detailed Analysis")

if map_data and map_data.get("last_object_clicked"):
  props = map_data["last_object_clicked"]["properties"]

  st.success(f"**Selected Location:** {props['name']} ({props['status']})")

  # Metrics Row using Streamlit columns
  col_m1, col_m2, col_m3, col_m4 = st.columns(4)
  col_m1.metric("Mangrove Health Score", props["health_score_num"])
  col_m2.metric("Median NDVI", props["median_ndvi"])
  col_m3.metric("Possible Decrease", props["possible_decrease"])
  col_m4.metric("Stable Area", props["stable_area"])

  st.markdown("---")

  # 3 Core Capabilities Breakdown
  c1, c2, c3 = st.columns(3)
  with c1:
    st.markdown("#### 1. Mangrove Mapping")
    st.info(props["mapping"])

  with c2:
    st.markdown("#### 2. Health Scoring")
    st.warning(props["health_score_text"])

  with c3:
    st.markdown("#### 3. Change Detection")
    st.error(
        f"Change analysis comparing baseline vs current Sentinel-2/Tanager data. (Decrease: {props['possible_decrease']} | Stable: {props['stable_area']})"
    )

else:
  st.info(
      "👉 **Tip:** Click on any colored polygon on the map above to inspect its health score, median NDVI, and change metrics."
  )

# --- Custom Legend ---
legend_html = """
    <div style="position: fixed; 
                bottom: 20px; right: 20px; width: 230px; height: 150px; 
                background-color: white; z-index:9999; font-size:12px;
                border:2px solid grey; border-radius: 6px; padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);">
      <b>GCC Health Legend</b><br>
      <i style="background:green; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> Green: Healthy Mangrove<br>
      <i style="background:orange; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> Yellow: Possible Stress<br>
      <i style="background:red; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> Red: Degraded / Change<br>
      <i style="background:blue; width:12px; height:12px; display:inline-block; margin-right:5px;"></i> Blue: Restoration Priority<br>
    </div>
"""
m.get_root().html.add_child(folium.Element(legend_html))
