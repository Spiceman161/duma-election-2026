# State Duma · 2026 — research dataset

**[Русский](README.md)** · [Results map](https://uiks.top) · [Data schema](docs/schema.json) · [Original delivery documentation, Russian](docs/SOURCE_README.ru.md)

A snapshot of collected election records **as of 30 September 2026**, enriched with addresses, localities and coordinates from previously matched precincts. It is intended for reproducible analysis and further data collection.

This repository contains **2026 data**, documentation and extraction tools. The uiks.top website source code is maintained separately.

> This is a research snapshot of saved materials, not certified final official results. The election label and year were inherited from the supplied collection; the official election card was not independently rechecked. Protocol coverage and coordinate coverage are separate measures of completeness.

## Coverage

| Measure | Count |
| --- | ---: |
| Registered precincts | 91,381 |
| Precincts with addresses | 86,001 |
| Precincts with coordinates | 85,999 |
| Precincts with locality names | 85,995 |
| Ordinary precinct protocols | 177,931 |
| Remote electronic voting (DEG) protocols | 194 |
| Protocol line records | 3,661,494 |
| Party result rows | 892,290 |
| Candidate result rows | 631,704 |

The snapshot preserves **all parties, all candidates, both ballot types and DEG**. The map's focus on United Russia does not restrict this research dataset.

## Getting started

Requirements: Git and Python 3 with its standard `lzma` module. No additional Python packages or Git LFS are required.

```bash
git clone https://github.com/Spiceman161/duma-election-2026.git
cd duma-election-2026
python3 scripts/prepare_data.py
```

The script reconstructs the original ZIP, verifies the SHA-256 of every part and the entire archive, extracts all **20 files** into `data/`, and verifies the contents against `SHA256SUMS`. Allow approximately **2.5 GB of free disk space**. On Windows, use `python` instead of `python3`.

To reconstruct and verify the ZIP without extracting:

```bash
python3 scripts/prepare_data.py --archive-only
```

The ZIP uses LZMA compression and can also be opened with 7-Zip. Some operating systems' built-in ZIP extractors do not support this compression method.

## Files and joins

CSV files use UTF-8 and contain headers. SQLite contains the corresponding tables. Column names and types are listed in [schema.json](docs/schema.json).

| Extracted file | Contents |
| --- | --- |
| `precincts.csv` | Complete precinct register, addresses, geography and provenance |
| `map_geodata.csv` | 85,999 geolocated precincts with geographic provenance |
| `protocols.csv` | Protocol identifiers, statuses, turnout and ballot totals |
| `party_results.csv` | Votes for all parties on party-list ballots |
| `candidate_results.csv` | Votes for single-member district candidates |
| `protocol_lines.csv`, `line_labels.csv` | All saved protocol line records and label dictionary |
| `parties.csv`, `districts.csv` | Party and district dictionaries |
| `missing_protocols.csv`, `collection_issues.csv` | Missing protocols and collection issues |
| `address_enrichment.csv` | Original log of 5,427 address lookup attempts |
| `source_ledger.csv` | Source inventory |
| `validation_issues.csv`, `validation_summary.json` | Validation issues and checks |
| `elections.sqlite` | Complete SQLite database containing the same data |
| `manifest.json`, `schema.json`, `SHA256SUMS`, `README.md` | Inventory, schema, checksums and original documentation |

Use `uik_id` as the precinct key. Join result tables to protocols using `protocol_key`, then to precincts using `uik_id`. A precinct number is not nationally unique. Remote electronic voting records are identified by `dataset=deg`; do not automatically join them to physical precincts or combine them with ordinary voting.

## Geography and uncertainty

**83,372** historical map coordinates were added; **2,627** supplied Yandex coordinates were preserved. Matching used **region + precinct number**, with a unique match on both sides. District membership was not a matching requirement.

Existing nonempty addresses and coordinates were retained. No new geocoding was performed. Synthetic points without confirmed precinct geography were excluded.

| Field | Interpretation |
| --- | --- |
| `address_origin` | `cik_commission_service`: supplied CEC address; `historical_map`: inherited map address |
| `coordinate_source` | `supplied_yandex_geocoding` or `historical_map` |
| `locality_source` | Origin of the locality name |
| `geography_match_method` | `unique_region_and_uik_number`: one unambiguous match |
| `coordinate_approximate` | 0/1 for supplied Yandex coordinates; empty/NULL for inherited coordinates without a fresh accuracy assessment |

325 Yandex points lack the `exact` + `house` combination and are marked `coordinate_approximate=1`. Historical coordinates were not independently reassessed; an empty flag does not establish precision. The original `address_status` describes the CEC lookup rather than the quality of an address subsequently inherited from the map.

## Known gaps

- **5,382 precincts lack coordinates:** 2,800 ordinary precincts with party-list protocols, 333 outside the ordinary regional map layer, and 2,249 registered precincts in the four regions without party-list protocols.
- **4,831 missing protocols**, counting both ballot types, are listed in `missing_protocols.csv`.
- Party-list protocols were not collected for Luhansk People's Republic, Donetsk People's Republic, Zaporizhzhia and Kherson regions. Known precincts remain in the register.
- Original raw service responses are not included (`raw_included=false`); the snapshot preserves extracted tables, provenance and aggregate hashes of original inputs.
- Many protocols are labelled `preliminary`; repeated protocols are marked `recounted`. Inspect status explicitly and do not interpret this snapshot as certification of final results.

There are 89,132 ordinary party-list protocols: 88,799 in 85 regions and 333 outside the ordinary regional layer. 41 have a zero denominator for the map's vote-share formula.

## Analysis example

The map calculates **United Russia votes / (valid + invalid ballots) × 100%**. Regional totals include precincts without coordinates. A zero denominator yields NULL. Researchers may explicitly adopt a different methodology.

Run [examples/er_by_region.sql](examples/er_by_region.sql) against `data/elections.sqlite`:

```sql
SELECT p.region_name,
       SUM(r.votes) AS er_votes,
       SUM(p.valid_ballots + p.invalid_ballots) AS ballots,
       100.0 * SUM(r.votes) /
       NULLIF(SUM(p.valid_ballots + p.invalid_ballots), 0) AS er_percent
FROM protocols AS p
JOIN party_results AS r USING (protocol_key)
WHERE p.dataset = 'uik'
  AND p.ballot_type = 'party_list'
  AND r.party_id LIKE '%edinaya-rossiya%'
GROUP BY p.region_name;
```

## Reproducibility

`snapshot/` contains nine parts of **one unchanged final ZIP**, plus `archive.json` specifying their order, sizes and SHA-256 checksums. This stores the complete SQLite database and large CSV files in Git without individual files over 100 MiB. Splitting changes only storage, not dataset contents.

SHA-256 of the reconstructed ZIP:

```text
e04ec13769fb97de7e40d967c6e027903075a1e7a8bf6c209f512f0f082d7e99
```

SQLite integrity, foreign keys, table counts, vote sums and CSV/SQLite geographic values were checked. See [validation_summary.json](docs/validation_summary.json). Adding geography did not change the original voting tables.

## Sources, attribution and contributions

Election record provenance is documented in `source_ledger.csv` and [manifest.json](docs/manifest.json). Historical map sources include [RED](https://doi.org/10.1038/s41597-026-07590-9) and [Harvard Dataverse](https://doi.org/10.7910/DVN/DFGNTP), CC BY 4.0. Those terms apply to the respective source materials; this repository does not assign a new blanket licence to all third-party data.

When citing, include this repository, the snapshot date **2026-09-30**, and the sources used. When extending the collection, preserve `uik_id`, `protocol_key`, provenance and modification dates; keep corrections separate from the original snapshot. Issues and Pull Requests documenting additions or corrections should include a supporting source.
