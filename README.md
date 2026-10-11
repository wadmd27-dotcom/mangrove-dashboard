# GCC Mangrove Stress Radar & Blue Carbon Monitor

A proof-of-concept dashboard for detecting possible early mangrove stress and supporting field verification across the GCC.

**Team:** TAIF  
**Theme:** Ecosystem Health & Biodiversity / Blue Carbon  
**Challenge:** Arab Youth Space Hackathon — 813 Challenge

## 1. Business Use Case

The intended users are environmental protection agencies, coastal managers, marine conservation organizations, and blue-carbon project developers.

The tool supports decisions such as:

- Prioritizing mangrove conservation and restoration sites
- Identifying areas requiring field inspection
- Monitoring possible vegetation stress
- Supporting blue-carbon monitoring and reporting

Current approaches often depend on expensive field surveys or manually reviewing satellite imagery. This proof of concept provides a faster regional screening tool.

## 2. Problem

Mangroves are important blue-carbon ecosystems that store carbon, protect coastlines, and provide habitat for marine life. They may experience stress from coastal development, pollution, storms, and climate change before visible habitat loss occurs.

This project explores whether satellite-derived vegetation and water indicators can help identify possible emerging stress signals for further field verification.

## 3. Data Used

### Sentinel-2 Level-2A

- Provider: Copernicus Data Space / Microsoft Planetary Computer
- Use: Preliminary NDVI and NDWI comparison
- Dates: 2024 and 2025 scenes
- Processing level: Level-2A surface reflectance
- Bands used: B03, B04, and B08
- Cloud filtering and scene classification masking are applied

### Planet Tanager Hyperspectral Data

- Collection: `coastal-water-bodies`
- Provider: Planet / Microsoft Planetary Computer STAC
- Use: Exploratory hyperspectral indices and spectral inspection
- Approximate spectral range: 376–2499 nm
- Approximate spatial resolution: 32.85 m
- Quality information: cloud, cirrus, and nodata masks

### Global Mangrove Watch 2020

- Use: Reference mangrove extent and spatial mask
- Dataset year: 2020
- Use in this project: Constrains the Sentinel-2 analysis to known reference mangrove areas

All indicators are preliminary and require field or UAV validation.

## 4. Technical Approach

The workflow:

1. Searches Sentinel-2 Level-2A imagery using STAC.
2. Selects comparable scenes from 2024 and 2025.
3. Uses the same Sentinel-2 tile and shared spatial grid.
4. Applies cloud, shadow, cirrus, and invalid-pixel masking.
5. Calculates NDVI and NDWI.
6. Reprojects the Global Mangrove Watch 2020 layer onto the Sentinel-2 grid.
7. Calculates change only within reference mangrove pixels.
8. Exports summary statistics and GeoJSON points for the dashboard.
9. Displays the results through a Streamlit/Folium dashboard.

The NDVI change is interpreted as a possible stress signal. It is not a confirmed ecological health classification.

## 5. Installation

Requires Python 3.11.

```bash
git clone https://github.com/wadmd27-dotcom/mangrove-dashboard.git
cd mangrove-dashboard

python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
