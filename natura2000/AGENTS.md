# AGENTS.md — Natura 2000 Protected Sites (EEA, version end 2024)

This file is for AI agents and scripts querying the data asset directly. The parquet file itself lives on S3, not in this repo — the current URL is always the `data` asset `href` in [collection.json](./collection.json) or [natura2000-end2024-polygons.json](./natura2000-end2024-polygons.json); read it from there rather than assuming a fixed URL. For human-oriented context see [README.md](./README.md).

## What this file is — and isn't

The data asset is **one layer** (`NaturaSite_polygon`) out of ten in the source GeoPackage, converted 1:1 with no transformation. It has boundary geometry and five identifying attributes per site. It does **not** contain species lists, habitat types, designation dates, or conservation status — those live in the source GeoPackage's other layers (`SPECIES`, `HABITATS`, `DESIGNATIONSTATUS`, `HABITATCLASS`, `BIOREGION`, `IMPACT`, `MANAGEMENT`, `OTHERSPECIES`, `METADATA`) and join to this file on `SITECODE`. If a task needs "what species are protected at site X" or "when was this site designated," that data is not in this parquet — say so rather than guessing, or fetch the relevant table from the source GeoPackage or from EEA's live REST services: [species](https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Species/MapServer), [habitats](https://bio.discomap.eea.europa.eu/arcgis/rest/services/ProtectedSites/Natura2000Habitats/MapServer).

Also note a real gap in the upstream data itself, not introduced by this conversion: 19 Member States (AT, BE, CY, EE, FI, FR, DE, EL, IE, IT, LV, LT, LU, MT, PL, PT, SK, ES, SE) withhold species-site associations for sensitive species from the EEA database entirely. A site in one of those countries showing no linked species in `SPECIES` may genuinely host none, or may host species whose location is being protected from disclosure — don't infer "no sensitive species present" from an absence of records there.

## Schema

| Field | Type | Notes |
|---|---|---|
| `SITECODE` | string | Persistent EU site identifier, e.g. `NL3009017`. Unique per site. Join key into the source GeoPackage's other tables. |
| `SITENAME` | string | Official site name, usually in the designating country's language. |
| `MS` | string | Two-letter Member State code (`NL`, `AT`, `FR`, ...). |
| `SITETYPE` | string | `A`/`D`/`F`/`H`/`J` = Birds Directive (SPA) only · `B`/`E`/`G`/`I`/`K` = Habitats Directive (SCI/SAC) only · `C` = both directives, overlapping designation. |
| `INSPIRE_ID` | string | INSPIRE identifier URI, where assigned; frequently blank. |
| `geometry` | binary (WKB) | Site boundary, **CRS EPSG:3035** (ETRS89-extended / LAEA Europe, metres). Not EPSG:4326 — reproject before combining with lon/lat data. |

## Query examples

The examples below use `DATA_URL` as a stand-in for the current `data` asset href from collection.json (an S3 URL) — substitute the real value rather than hardcoding it, since it can change if the file is re-uploaded to a new path.

DuckDB (spatial + httpfs extensions), querying the S3 object directly with no local download and no credentials (the bucket/object is public-read):

```sql
INSTALL spatial; LOAD spatial;
INSTALL httpfs; LOAD httpfs;

-- Look up a site by code
SELECT SITECODE, SITENAME, MS, SITETYPE
FROM 'DATA_URL'
WHERE SITECODE = 'NL3009017';

-- Count sites per Member State
SELECT MS, COUNT(*) AS n_sites
FROM 'DATA_URL'
GROUP BY MS
ORDER BY n_sites DESC;

-- Area (m²) of a site, geometry is already projected (EPSG:3035 is equal-area)
SELECT SITECODE, SITENAME, ST_Area(ST_GeomFromWKB(geometry)) AS area_m2
FROM 'DATA_URL'
WHERE SITECODE = 'NL3009017';
```

Python (geopandas — reads straight from the URL; use a local path instead if you've already downloaded it):

```python
import geopandas as gpd

DATA_URL = "https://<bucket>.s3.<region>.amazonaws.com/eea-natura2000/2024/filename.parquet"

gdf = gpd.read_parquet(DATA_URL)                  # CRS: EPSG:3035
site = gdf[gdf.SITECODE == "NL3009017"]
site_wgs84 = site.to_crs(4326)                     # reproject only when you need lon/lat
```

Joining to a related table for species/habitat detail (requires the source GeoPackage, which is not on S3 alongside this file):

```python
import geopandas as gpd

polygons = gpd.read_parquet(DATA_URL)
species = gpd.read_file("Natura2000_end2024.gpkg", layer="SPECIES")
joined = polygons.merge(species, on="SITECODE", how="left")
```

## Provenance and trust

This parquet was produced by re-encoding a single named layer from a cited, DOI-identified upstream source, with no attribute or geometry transformation, and its row count and two independently-selected site records (`NL3009017`, `AT1101112`) were checked field-by-field and geometry-for-geometry against the source. The full lineage narrative is in `collection.json`'s `processing:lineage` field. Do not present this file as containing more than what's described here (in particular: do not assume it includes habitat/species/status data, and do not assume geometries are in WGS84).

## License and attribution

Source data: European Environment Agency, **CC BY 4.0**. Any reuse — including by an agent generating a downstream report, map, or dataset from this file — must acknowledge the EEA as the original source and must not distort the original meaning of the data. See [collection.json](./collection.json) `providers` and `sci:citation` for the exact citation string, and note the EEA's own caveat: this is general-information data, and only the data held by the competent authorities of the Member States is authentic.

## FAIR and data space context

This collection is published as a small worked example of making a derived dataset independently trustworthy rather than trusting-by-default: a persistent identifier and citation back to the authoritative source (**F**indable, **R**eusable — see `sci:doi`), an open format reachable over plain HTTP with no proprietary client (**A**ccessible), STAC/GeoParquet/Darwin-Core-adjacent conventions rather than a bespoke schema (**I**nteroperable), and an explicit, machine-readable license plus a recorded, checkable transformation chain (**R**eusable). That combination — stable identifiers, declared provenance, and machine-actionable licensing attached to the data itself rather than left in a README a human might not read — is the same pattern that biodiversity data space initiatives rely on to let data cross organizational boundaries without each recipient having to re-verify it from scratch. Treat this file's metadata, not just its rows, as part of what makes it usable.
