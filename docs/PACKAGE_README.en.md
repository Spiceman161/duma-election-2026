# State Duma 2026 — research snapshot, 2026-09-30

Repository and updates: https://github.com/Spiceman161/duma-election-2026

Two ordinary Deflate ZIPs are available: CSV and SQLite. Each represents the complete snapshot; choose your preferred format. Python and Git are not needed to extract them. If downloading both, extract into separate directories.

CSV: all tables are at the archive root, encoded as UTF-8 with headers. Large tables may exceed spreadsheet row limits; use data analysis tools.

SQLite: open elections.sqlite with a SQLite application. A query example is in examples/er_by_region.sql. docs/source_ledger.csv additionally preserves source attribution.

Both formats preserve all parties, candidates, both ballot types, DEG and protocol line records. This is a collected research snapshot, not certified final official results. The election label and year were inherited from the supplied collection; the election card was not independently rechecked. preliminary/recounted statuses occur; raw service responses are not included. Do not automatically join DEG to physical precincts.

docs/schema.json describes fields; docs/manifest.json and docs/validation_summary.json preserve original delivery metadata. docs/SOURCE_README.ru.md is the original Russian documentation: its LZMA packaging notes refer to the original delivery, while these two ZIPs use Deflate. Original table bytes and voting records are unchanged. The root SHA256SUMS covers the files in this package.

Inherited geography was not independently reassessed; an empty accuracy flag does not establish precision. Historical geography sources: RED (https://doi.org/10.1038/s41597-026-07590-9) and Harvard Dataverse (https://doi.org/10.7910/DVN/DFGNTP), CC BY 4.0 for the respective materials. No new blanket licence is assigned to third-party data. Cite the repository, snapshot date and sources used.
