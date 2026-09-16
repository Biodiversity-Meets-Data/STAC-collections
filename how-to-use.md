## Querying this API

How to use AGENTS.md 

https://bmd-stac.dryrun.link/collections/natura2000/items
(returns JSON) 

Read the Item's `agents` link before touching any asset. 
it's where details live (what an asset does and doesn't contain, units, CRS, join keys, known data gaps) 
instead of being left for an agent to infer from field names.

Pattern:

1. GET the Collection's `/items` endpoint.
2. Find the `agents` rel in the Item's `links` (a custom rel, so it's already an absolute URL — not rewritten by the server).
3. Fetch and read it *before* parsing any asset.
4. To identify a specific file, look it up by `href` in the Item's `assets` dict. don't infer identity from a filename or from what AGENTS.md says exists elsewhere; confirm it's actually documented there first.
5. If it isn't documented, say so rather than guessing its schema — inspect the file directly (`duckdb`'s `DESCRIBE`, or `pyarrow.parquet.read_schema`) and consider whether it should be added as a proper asset with its own `title`/`type`/`file:size`.

