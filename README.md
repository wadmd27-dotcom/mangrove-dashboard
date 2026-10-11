# GCC Mangrove Stress Radar & Blue Carbon Monitor
# Planet Tanager Hyperspectral Explorer: Ecosystem Health, Biodiversity & Blue Carbon

**Team:** TAIF  
**Theme:** Ecosystem Health & Biodiversity / Blue Carbon (Arab Youth Space Hackathon: 813 Challenge)  
**Summary:** A reproducible proof-of-concept pipeline leveraging Planet Tanager hyperspectral satellite data to map coastal blue carbon habitats, monitor mangrove health, and track aquatic biodiversity proxies.

---

## 1. The Business Use Case
* **End Users:** Environmental protection agencies, coastal zone managers, marine conservation NGOs, and carbon credit project developers.
* **Decisions Made:** Prioritizing conservation and restoration sites, verifying blue carbon offset credits, monitoring mangrove stress from industrial runoff or storms, and assessing coastal ecosystem resilience.
* **Current Alternatives:** Traditional field surveys (costly, slow, limited spatial coverage) or standard multispectral satellites (Landsat, Sentinel-2) which lack the fine spectral resolution needed to detect subtle biochemical changes, species-level stress, or dense aquatic chlorophyll variations.

## 2. The Problem
Blue carbon ecosystems—including mangroves, seagrass beds, and coastal wetlands—store up to 5 times more carbon per hectare than tropical forests, protect coastlines from storm surges, and serve as vital nursery habitats for marine life. Despite their immense ecological value, these habitats are rapidly degrading due to coastal development, pollution, and climate change. Traditional broad-band satellite data often misclassifies littoral vegetation and fails to capture early-stage ecological stress, making high-resolution hyperspectral monitoring an essential instrument for timely intervention.

## 3. Data Used
* **Product Name:** Planet Tanager Hyperspectral Surface Reflectance (`coastal-water-bodies` collection via Microsoft Planetary Computer STAC API).
* **Spectral Resolution:** ~426 contiguous spectral bands spanning from ~376 nm to 2499 nm[cite: 2].
* **Spatial Resolution:** Ground Sample Distance (GSD) of ~32.85 m[cite: 2].
* **Quality Bands:** `beta_cloud_mask`, `beta_cirrus_mask`, and `nodata_pixels` for rigorous cloud and artifact masking[cite: 2].
* **Licence:** Open research and hackathon access via Microsoft Planetary Computer & Planet partnership.

## 4. Technical Approach
The analysis workflow executes in the following ordered steps:
1. **STAC Discovery & Authentication:** Connects securely to the Planet STAC API using `pystac-client` and `planetary-computer` signed assets[cite: 2].
2. **Data Ingestion & Cleansing:** Loads the HDF5 surface reflectance asset (`ortho_sr_hdf5`) using `stackstac` and `rasterio`, filtering out invalid pixels, cloud artifacts, and negative reflectance values into `np.nan`[cite: 2].
3. **Band Extraction & Index Computation:** Extracts critical wavelengths (443 nm, 560 nm, 665 nm, 708 nm, 800 nm, 860 nm)[cite: 2] to compute specialized ecological indices with mathematical safeguards (`eps = 1e-6` to prevent division-by-zero errors)[cite: 2]:
   * **NDVI:** General vegetation health and vigor[cite: 2].
   * **NDWI:** Open water body delineation[cite: 2].
   * **NDCI (Normalized Difference Chlorophyll Index):** Algal bloom and aquatic vegetation density[cite: 2].
   * **Turbidity Proxy:** Suspended sediment dynamics in coastal waters[cite: 2].
   * **Mangrove Proxy:** Multi-threshold mask combining NDVI, NDWI, and NDCI signatures to isolate blue carbon habitats[cite: 2].

## 5. Installation

Requires **Python 3.11**.

```bash
git clone [https://github.com/your-team/planet-tanager-blue-carbon.git](https://github.com/your-team/planet-tanager-blue-carbon.git)
cd planet-tanager-blue-carbon
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
