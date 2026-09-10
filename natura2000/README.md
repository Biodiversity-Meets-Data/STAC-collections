# Naturalis EEA Natura 2000 STAC Catalog

A small STAC catalog around a GeoParquet re-encoding of the EEA's Natura 2000 (vector, version end 2024) site-boundary layer. Metadata and code live here; 

## Structure

```
catalog.json                                        root STAC Catalog
collections/
    collection.json                                 STAC Collection (metadata, license, provenance, S3 asset URL)
    natura2000-end2024-polygons.json                STAC Item
    AGENTS.md                                        field reference + query examples, for AI agents/scripts
    README.md                                        human-oriented documentation
scripts/
  convert_to_parquet.py                              GeoPackage layer -> GeoParquet
  verify_layer.py                                    row-count / CRS / geometry-validity checks vs the source
  verify_site.py                                     deep single-site comparison (attributes + geometry)
  gather_stac_facts.py                                computes the real numbers for the PLACEHOLDER_* fields below

LICENSE                                              code license (MIT)
LICENSE-DATA.md                                      data license (CC BY 4.0, European Environment Agency)
CITATION.cff                                          how to cite this repo and the underlying dataset
```

## Data hosting

The parquet file is not is not committed to this repo. it's uploaded to S3 and referenced by URL from the `data` asset in `collection.json` / the STAC item. 


## Workflow

1. Convert: `python scripts/convert_to_parquet.py` (reads the source `.gpkg`, writes `output.parquet`).
2. Verify: `python scripts/verify_layer.py` and `python scripts/verify_site.py` — checks the parquet against the source GeoPackage before anything gets published.
3. Upload to s3.  
4. Fill in real metadata: `python scripts/gather_stac_facts.py` prints the row count, geometry type, bbox, file size, checksum etc.

## License

Code: MIT (`LICENSE`). Data: CC BY 4.0, European Environment Agency (`LICENSE-DATA.md`) — these are different licenses covering different things; see both files.
