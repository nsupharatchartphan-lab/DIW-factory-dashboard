# Factory Distribution Dashboard — Design

## Intent & why

The user is responsible for factory oversight across all 17 northern Thailand
provinces and has a DIW export (`list of factories north thailand.xlsx`,
sheet `export1`, 7,405 factory records) covering them. They want a dashboard,
modeled on the Thai PBS election results map
(https://www.thaipbs.or.th/election69/result/geo?region=all&view=area), that
shows where factories are distributed, lets them click into a province/district
to see the factories there, and lets them filter the whole thing by horsepower
and factory type to make finding factories in their cluster easier. Per-factory
map pins (lat/long) are a later phase — out of scope for v1, but the design
should not make that harder to add.

## Goals

- Show factory distribution across the 17 provinces on a real map of
  Thailand, colored by factory count (a choropleth / "colormap"), at
  province level and district (อำเภอ) level.
- Click-through drill-down: province → its districts (with counts) →
  click a district → the factories located there, broken down by
  sub-district (ตำบล).
- A toggle to a plain grid/table view of the same hierarchy, as a
  guaranteed-accurate fallback independent of map-shape data.
- Filters — horsepower range, and factory type — combinable, and live:
  they update the map coloring, the table, and any open drill-down list
  at once.
- Ship as a single self-contained, shareable file; no backend/server.

## Non-goals (v1)

- No per-factory lat/long pin markers. The source data has no
  coordinates; this is explicitly a later phase per the user.
- No live data sync. The dashboard is a snapshot built from the current
  Excel export; refreshing means re-running the build script against a
  new export.
- No official DIW "ประเภทโรงงานจำพวกที่ 1–106" name lookup. v1 filters by
  the type code parsed from the registration number (e.g. `10(3)`) plus
  free-text search over the business description — not verified official
  category names, to avoid asserting names I haven't sourced authoritatively.
- The type filter matches only on each factory's primary parsed type
  code. `ประเภทรอง` (secondary type, populated for ~15% of rows) is not
  used for filtering in v1 — confirmed with the user.
- No auth or hosting infrastructure — delivered as a file.

## Anti-goals

- Don't silently drop or mis-locate the one known malformed row (see
  Data cleaning below) — fix it explicitly, don't drop it.
- Don't let a missing or mismatched district boundary shape silently
  hide factories from the user. If a district's map shape can't be
  sourced/matched, its factories must still be fully correct and
  reachable in the table view and in counts everywhere else.

## Constraints

- The Excel has no map geometry. Thailand administrative boundary
  shapes (province + อำเภอ polygons) must be sourced from an open
  dataset and name-matched to the Excel's text; Thai name spelling can
  vary slightly between sources, so some manual correction should be
  expected.
- Embedded map data should stay within a reasonable single-file size
  (roughly 10–16MB) — polygon precision will be simplified as needed.
- Sub-district (ตำบล) granularity is 1,167 unique province+district+
  sub-district combinations — too fine-grained to responsibly source
  and verify as its own map layer for v1. **Builder's call:** sub-district
  becomes a grouped breakdown inside a district's table/list (sortable,
  not a separate map layer), rather than a third map drill-level. Flagged
  for the user to override if they want tambon shapes on the map too.
- **Data cleaning needed before building:** the row for "บริษัท ทีทีดี
  โซลาร์ 1 จำกัด (ติดตั้งบนพื้นดิน...)" has shifted columns — a comma
  inside its business-description text broke the original export's
  column alignment. Its จังหวัด should read นครสวรรค์ (its อำเภอ,
  ตากฟ้า, is in นครสวรรค์), and its แรงม้า value needs correcting from
  the unaffected source column. This is a one-off, explicit fix, not a
  dropped row.

## Approaches considered

- **A — real map only (choropleth).** Matches the Thai PBS reference
  closely. Risk: any gap or name-mismatch in sourced boundary data
  leaves no fallback — a district could appear to have zero factories
  on the map when it doesn't.
- **B — table/grid only.** Zero geo-sourcing risk, works purely from the
  Excel. Loses the spatial "see it on a map of Thailand" read the user
  specifically asked for.
- **A+B combined — chosen.** Real map (Leaflet.js) as the primary
  colormap view, with a toggle to a grid/table view built from the exact
  same aggregated counts. Any gap in the map's boundary data can never
  hide or miscount a factory, because the table is always correct
  independently. Marginal extra build effort, no real downside — this
  is why it was picked over A alone.

## How it will be built

- **Data pipeline:** a Python script reads the Excel, applies the one
  known data-cleaning fix, parses the DIW type code out of
  เลขทะเบียนเดิม (regex matching the `<type>-<seq>/<year>` pattern,
  tolerant of the different prefix styles seen in the data), and emits
  a compact JSON: per-factory records plus precomputed
  province/district/sub-district aggregate counts.
- **Boundary shapes:** sourced from an open Thai administrative
  boundary dataset, filtered to the 17 provinces and their districts,
  simplified for file size, and name-matched against the Excel's
  จังหวัด/อำเภอ text, with a manual correction list for any mismatches
  found.
- **Frontend:** one static HTML file — Leaflet.js for the map, vanilla
  JS (or a light framework) for filters, the table-toggle view, and the
  drill-down panel. Fully client-side.
- **Filters:** horsepower range (with a toggle between แรงม้า /
  registered and แรงม้าตรวจพบ / inspected — confirmed with the user,
  since the two disagree on ~17% of records) + factory-type multi-select
  (grouped by the parsed main type number, primary type only — see
  Non-goals) + free-text search (factory name / business description) —
  combinable, all live-updating the map coloring, the table, and any
  open drill-down list together.
- **Type-code parsing rule (resolved):** registration numbers
  (เลขทะเบียนเดิม) use inconsistent prefixes (`3-10(3)-...`,
  `จ3-10(1)-...`, `น.53(5)-...`, etc.), so the type code is extracted by
  searching anywhere in the string for the pattern
  `<type>-<sequence>/<year>` (type optionally followed by a
  parenthesized sub-number), rather than anchoring at the start. This
  rule was tested against all 7,405 rows and matched 100% of them.
- **Choropleth metric (builder's call):** color by raw factory count
  per province/district, not a normalized metric (e.g. per area or per
  capita). This mirrors the Thai PBS reference style and directly shows
  where factory counts are heaviest within the user's responsibility
  area, which is the stated goal.
- **Delivery:** published as a shareable artifact, and also saved as a
  local HTML file in the project folder.

## What's left to the builder

Exact choropleth color scale/breakpoints, exact table column layout,
and general UI polish — the builder's call, following reasonable
dashboard-design conventions.
