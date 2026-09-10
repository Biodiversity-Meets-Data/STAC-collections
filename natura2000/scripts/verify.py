"""
Verify that output.parquet faithfully represents the NaturaSite_polygon layer
of the source GeoPackage.

Run: python verify_natura2000.py
"""

import geopandas as gpd
import pyogrio

GPKG = "eea_v_3035_100_k_natura2000_p_2024_v01_r00/Natura2000_end2024.gpkg"
LAYER = "NaturaSite_polygon"
PARQUET = "NaturaSite_polygon.parquet"

print("=" * 60)
print("1. Source layer info (fast metadata read, no full load)")
print("=" * 60)
info = pyogrio.read_info(GPKG, layer=LAYER)
print(info)

print("\n" + "=" * 60)
print("2. Load parquet and check basics")
print("=" * 60)
gdf = gpd.read_parquet(PARQUET)
print("Row count:      ", len(gdf))
print("CRS:            ", gdf.crs)
print("Columns:        ", list(gdf.columns))
print("Geometry types: ", gdf.geom_type.value_counts().to_dict())
print("Total bounds:   ", gdf.total_bounds)  # should be within EPSG:3035 Europe extent

print("\n" + "=" * 60)
print("3. Row count sanity check vs source")
print("=" * 60)
expected = info["features"]
actual = len(gdf)
print(f"Source feature count: {expected}")
print(f"Parquet row count:    {actual}")
assert expected == actual, "MISMATCH: row counts differ!"
print("OK: row counts match")

print("\n" + "=" * 60)
print("4. Geometry validity / nulls")
print("=" * 60)
n_null_geom = gdf.geometry.isna().sum()
n_empty_geom = gdf.geometry.is_empty.sum()
n_invalid = (~gdf.geometry.is_valid).sum()
print(f"Null geometries:    {n_null_geom}")
print(f"Empty geometries:   {n_empty_geom}")
print(f"Invalid geometries: {n_invalid}")

print("\n" + "=" * 60)
print("5. Spot-check a few attribute values against the source")
print("=" * 60)
# Read the same handful of rows directly from the gpkg (cheap, uses row filter)
sample_ids = gdf.index[:3]
gdf_src_sample = gpd.read_file(GPKG, layer=LAYER, rows=slice(0, 3))
cols_to_compare = [c for c in gdf.columns if c != "geometry"][:5]
print(gdf.iloc[:3][cols_to_compare])
print("---- vs source ----")
print(gdf_src_sample[cols_to_compare])

print("\nDone. If the assert above passed and the spot-check values line up, "
      "the parquet file is a faithful copy of the NaturaSite_polygon layer.")
