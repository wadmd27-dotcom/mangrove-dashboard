import streamlit as st

st.set_page_config(
    page_title="Mangrove Health Dashboard",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 Mangrove Health and Blue Carbon Dashboard")

st.write(
    "This dashboard explores mangrove and coastal ecosystem health "
    "using Tanager hyperspectral satellite indicators."
)

st.header("Satellite Analysis Maps")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ecosystem Health Indices")
    st.image("images/image 4.png", use_container_width=True)

with col2:
    st.subheader("RGB and Coastal Indicators")
    st.image("images/image 3.png", use_container_width=True)

st.header("Spectral Analysis")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Spectral Signatures")
    st.image("images/image 1.png", use_container_width=True)

with col4:
    st.subheader("Mean Spectrum")
    st.image("images/image 2.png", use_container_width=True)

st.header("Initial Interpretation")

a, b, c = st.columns(3)

with a:
    st.metric("Vegetation indicator", "NDVI")

with b:
    st.metric("Water indicator", "NDWI")

with c:
    st.metric("Chlorophyll indicator", "NDCI")

st.info(
    "These maps are indicators, not confirmed measurements of carbon storage "
    "or mangrove health. Further validation with reference data is required."
)
