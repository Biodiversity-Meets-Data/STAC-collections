# STAC Collections and Items

How to write STAC Collections with FAIR and Data Space principles for BMD. 

Examples: See the [Natura 2000 collection](https://github.com/Biodiversity-Meets-Data/STAC-collections/tree/main/natura2000), and the [ChecklistBank species-lists collection](https://github.com/Biodiversity-Meets-Data/STAC-collections/tree/main/checklistbank).


## Core rule

A STAC Item describes what the data (or datasets, collection of things) is and where to get it. License, provenance, and description live outside STAC and are referenced via links, ideally not embedded.

Per the [DSSC Blueprint](https://archive.dssc.eu/space/Glossary/176554052/2.+Core+Concepts), a Data Space separates these into distinct standards: 

- Data & Service Description (like DCAT)
- Discovery (catalog like STAC), 
- Provenance (like PROV-O), 
- Access & Usage Policies (like ODRL).

Operational metadata (checksum, file size, auth scheme, endpoint) idally stays on the Item as these are fetched programmatically. 


## Collection / Item fields

### Required

- `license` — SPDX id (`CC-BY-4.0`) or a `license` link to actual terms. Not a placeholder.
- `providers` — distinct roles for source producer/licensor vs. processor/host, in provenance order. Chains can run longer than two or three parties (see the ChecklistBank worked example) — order still matters even when it does.
- Link to source — `derived_from` or `via`, pointing to the original dataset, ideally a DOI. **If an Item aggregates data from many source datasets, don't force a single link to one of them**. See Pitfalls below.

### Recommended

- `processing:lineage` — what was done to the data, and what was actually verified (or "not yet verified"). An honest "processed via internal scripts, method not yet fully written up" beats an invented level of detail — see the ChecklistBank worked example.
- `sci:doi` / `sci:citation` — attribution and an unambiguous pointer to the exact source version.
- `describedby` / `agents` links — human docs and agent-facing docs, as separate markdown files, not embedded JSON.

### Optional

- `file:size` / `file:checksum` — integrity checks; must match the actual file described, not a similar one.
- Custom namespace fields: this is only needed for facts not already present elsewhere in the same document.

## Templates

Starting points for a new Collection or Item live in `templates/`:

- `templates/collection.template.jsonc`
- `templates/item.template.jsonc`

These are JSONC (JSON + `//` comments), not plain JSON — each field is annotated `[REQUIRED]`, `[RECOMMENDED]`, or `[OPTIONAL]`. They are **not** meant to be fed to a STAC server or validator as-is: copy from them, strip the comments, and replace every `<PLACEHOLDER>` first. 

For an example that's actually spec-valid and testable in a browser, use the worked examples below, not the templates.

## Worked example: Natura 2000

Actual metadata for `eea-natura2000-2024-polygons` / `natura2000`, checked against the EEA's SDI catalogue record and ISO metadata XML.

**Providers** — three parties, three roles, in provenance order:

```json
"providers": [
  {
    "name": "European Environment Agency (EEA)",
    "roles": ["licensor", "producer"],
    "url": "https://sdi.eea.europa.eu/catalogue/srv/api/records/91357f39-7866-41ce-b447-43905c364ec8",
    "email": "sdi@eea.europa.eu"
  },
  {
    "name": "Biodiversity Meets Data (BMD) Project",
    "roles": ["processor"],
    "url": "https://doi.org/10.3030/101181294"
  },
  {
    "name": "Sharif Islam / Naturalis Biodiversity Center",
    "roles": ["processor", "host"],
    "url": "https://www.naturalis.nl/"
  }
]
```

**License and citation:**

```json
"license": "CC-BY-4.0",
"sci:doi": "10.2909/91357f39-7866-41ce-b447-43905c364ec8",
"sci:citation": "European Environment Agency (2025). Natura 2000 (vector), version end 2024, edition 01.00. https://doi.org/10.2909/91357f39-7866-41ce-b447-43905c364ec8"
```

**Lineage — names the method and what was checked:**
Snippet. 

```json
"processing:lineage": "Using a script we read the 'NaturaSite_polygon' layer with geopandas.read_file() and wrote it directly to GeoParquet.."
```

**Docs as links:**

```json
"links": [
  { "rel": "describedby", "href": "https://raw.githubusercontent.com/.../README.md", "type": "text/markdown" },
  { "rel": "agents", "href": "https://raw.githubusercontent.com/.../AGENTS.md", "type": "text/markdown" },
  { "rel": "license", "href": "https://www.eea.europa.eu/legal/copyright", "type": "text/html" },
  { "rel": "via", "href": "https://doi.org/10.2909/91357f39-7866-41ce-b447-43905c364ec8", "type": "text/html" }
]
```

## Worked example: ChecklistBank species lists (many-to-one provenance)

`checklistbank` / `checklistbank-species-lists` is a non-spatial logical dataset: one Item bundling 10 tables (Birds/Habitats Directive annexes, GRIIS, IAS Union Concern, plus a `clb_datasets` lookup table) built from data ChecklistBank aggregates from many underlying source datasets — not one.

**Providers** — same three-tier shape as Natura2000, but note `ChecklistBank` sits in the middle as a publisher, not a processor:

```json
"providers": [
  { "name": "The European Environment Agency (EEA)", "roles": ["licensor", "producer"] },
  { "name": "ChecklistBank", "roles": ["publisher"], "url": "https://api.checklistbank.org" },
  { "name": "BMD Project", "roles": ["processor", "host"], "url": "https://doi.org/10.3030/101181294" }
]
```

**Many-to-one provenance — don't force a single `via` link.** 

We might have mutiple data sources converging into a file. For example, 46 distinct ChecklistBank datasets list with IDs and URLs. We can then write something like this: 


   ```json
   "clb_datasets": {
     "description": "Provenance manifest: the ChecklistBank dataset key, title, version, and country/iso codes for every source dataset used to build this Item's other tables. This is the authoritative per-source record — the top-level 'via' link points only to the ChecklistBank platform in general."
   }
   ```
and also add **Lineage**

```json
"processing:lineage": "Extracted from ChecklistBank and transformed into Parquet/CSV via internal BMD Python scripts."
```


## Extensions used in this project

These are STAC community maintained extensions: 

| Extension | Version | Schema URL |
|---|---|---|
| File Info | v2.1.0 | `https://stac-extensions.github.io/file/v2.1.0/schema.json` |
| Table | v1.2.0 | `https://stac-extensions.github.io/table/v1.2.0/schema.json` |
| Processing | v1.2.0 | `https://stac-extensions.github.io/processing/v1.2.0/schema.json` |

Declare only the ones a given document actually uses (`file:*`, `table:*`, `processing:*` respectively) in its `stac_extensions` array — see Pitfalls.

## Keep a copy of the JSON in the repo

The live server's copy (absolute links, `self`/`parent`/`root` rewritten) is what STAC Browser and API clients hit. It is not the only copy that should exist.

Commit the Collection/Item JSON into this repo too, mirroring the layout:

    collections/natura2000/collection.json
    collections/natura2000/items/*.json
    collections/checklistbank/collection.json
    collections/checklistbank/items/*.json

More on how to implement git-backed-catalog: 
https://github.com/portolan-sdi/portolan-spec/blob/v0.2.0/specs/best-practices/git-backed-catalogs.md

## Test in a browser

A generic STAC Browser rendering a published Collection/Item correctly, with no custom code, is evidence the JSON is valid.

- [https://browser.moregeo.it/external/bmd-stac.dryrun.link/](https://browser.moregeo.it/external/bmd-stac.dryrun.link) — catalog root
- [https://browser.moregeo.it/external/bmd-stac.dryrun.link/collections/natura2000](https://browser.moregeo.it/external/bmd-stac.dryrun.link/collections/natura2000) — the `natura2000` collection specifically
- [https://stac-view-quest.base44.app/](https://stac-view-quest.base44.app/) — separate demo browser instance (vide coded with base44)

Check: map extent matches the real bbox, every asset lists with the right type and downloads, license and providers display, `describedby`/`agents` links resolve when clicked (browsers render core rels only — they don't follow custom rels themselves, so click through by hand).



## AGENTS.md

Each collections can also include an `AGENTS.md` via a custom `agents` rel:

```json
{ "rel": "agents", "href": "https://raw.githubusercontent.com/.../AGENTS.md", "type": "text/markdown" }
```

`README.md` and `AGENTS.md` answer different questions, for different readers:

- **`README.md`** — for a human: what is this dataset, why does it exist, how was it produced. Narrative, context.
- 
- **`AGENTS.md`** — for an agent or automated client consuming this STAC data programmatically: what's safe to assume, what isn't, and how to use it correctly without a human in the loop. For example. things like: this Item is non-spatial and its `bbox`/`geometry` are a global placeholder for indexing, not a real extent — don't use them for spatial filtering; 
 any rate limits or auth quirks on the S3 endpoints.

Same absolute-URL rule applies as for `describedby` — this is a custom rel, so a STAC server won't rewrite it; keep it pointed at the raw file directly.


Use of AGENTS.md is increasing and it follows the same separation-of-concerns logic as the Core Rule at the top of this doc. STAC describes what the data is and where to get it, and everything richer lives outside, referenced by link rather than embedded. `README.md`/`AGENTS.md` just extends that split one step further, separating the *human-readable* rich description from the *agent-readable* operational one. 


## Pitfalls


- Relative links (`./README.md`) break once a static file is served through an API — STAC servers rewrite core rels (`self`, `parent`, `root`, `item`) but not custom rels (`describedby`, `agents`, `license`). Use absolute URLs for custom rels. 
- **Many-to-one provenance can't fit in one `via`/`derived_from` link.** When an Item is built from several source datasets rather than one (the ChecklistBank case above), a single link to any one of them misrepresents the rest. Point `via` at the general source platform instead, and put the actual per-source detail in a clearly-described asset (or a dedicated manifest link) rather than picking one record to stand in for all of them.
- Duplicating one asset at both Collection and Item level creates two places that can disagree. If the Collection has one Item, point to it instead of re-describing its asset. *(this is not an explicit spec rule — the spec doesn't address Collection/Item asset duplication directly.)*
- A manifest-style custom field that repeats what's already in `assets` (name, type, row count) is a second place for the same fact to go stale — true even when it's a deliberate, repeated house convention rather than a one-off mistake (see `bmd:tables` above). Accepting the tradeoff is fine; forgetting you made it isn't — update the manifest whenever the underlying asset changes.
- Every extension-namespaced field (`table:`, `file:`, `proj:`, `sci:`, `processing:`) needs its schema URL declared in `stac_extensions`. *(Spec-required.)* This project has twice shipped a document that used `file:`/`table:` fields without declaring the extension — check this every time, it's an easy miss.

Note on `providers`/license/lineage generally: `license` is a required Collection field in core STAC; `providers` and rich provenance are not required by the spec, which explicitly puts a "comprehensive provenance model" out of scope and only suggests `derived_from`. Requiring them here (see Required/Recommended above) is this project's own bar, set higher than the spec's minimum, for FAIR/Data Space reasons — not a claim that bare STAC demands it.

## Checklist

- [ ] `license` is a real SPDX id or link, not a placeholder
- [ ] `providers` has distinct roles for source vs. current processor/host, in order
- [ ] A link (`derived_from`/`via`) points back to the original source — and if there are multiple sources, it points at a general platform plus a clearly-labeled manifest, not one cherry-picked record
- [ ] `processing:lineage` names the method and what was verified, or honestly says it isn't documented yet
- [ ] `describedby`/`agents`/custom-rel links use absolute URLs
- [ ] The Collection doesn't re-describe an asset its Item already describes
- [ ] Every extension-namespaced field has its schema URL in `stac_extensions` (check against the Extensions table above)
- [ ] Renders correctly in a STAC Browser (see Test in a browser)
- [ ] The Collection/Item JSON is committed to this repo, not just served live

## Reference

- STAC spec: https://github.com/radiantearth/stac-spec
- STAC best practices: https://github.com/radiantearth/stac-spec/blob/master/best-practices.md
- Extensions: https://stac-extensions.github.io/
- DSSC Blueprint: https://archive.dssc.eu/space/Glossary/176554052/2.+Core+Concepts
- STAC Browser (generic client): https://github.com/radiantearth/stac-browser
