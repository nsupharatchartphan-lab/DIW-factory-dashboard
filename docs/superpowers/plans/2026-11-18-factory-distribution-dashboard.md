# Factory Distribution Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single self-contained HTML dashboard that shows the 7,405
northern-Thailand factories on a real map of Thailand (province → district
drill-down, colored by factory count), with a table-view toggle, a detail
view for any individual factory (click its name to see its full record),
and live filters for horsepower (both a min/max range and a greater-than/
less-than comparison mode) and factory type, all combinable at once.

**Architecture:** A Python data pipeline reads the source Excel and public
Thai administrative-boundary GeoJSON, cleans/joins them into plain JSON, and
a build script injects that JSON into a static HTML/Leaflet.js template to
produce one final `dashboard.html`. Everything runs and renders locally with
no backend.

**Tech Stack:** Python 3.11 (stdlib `unittest`, `openpyxl`, `requests` —
all already available), Leaflet.js 1.9.4 via CDN, vanilla JS/HTML/CSS.

**Spec:** `docs/design/2026-11-18-factory-distribution-dashboard-design.md`

## Global Constraints

- Source file: `list of factories north thailand.xlsx`, sheet `export1`,
  header row 1, 7,405 data rows (rows 2–7406). Column order (0-indexed):
  0 ลำดับ, 1 เลขทะเบียนเดิม, 2 ประเภทรอง, 3 FID, 4 ชื่อโรงงาน,
  5 ผู้ประกอบการ, 6 ประกอบกิจการ, 7 เลขที่, 8 หมู่, 9 ซอย, 10 ถนน,
  11 ตำบล, 12 อำเภอ, 13 จังหวัด, 14 ไปรษณีย์, 15 โทรศัพท์, 16 แรงม้า,
  17 แรงม้าตรวจพบ, 18 ทะเบียนพาณิชย์, 19 เลขผู้เสียภาษี.
- The 17 provinces in scope (exact Thai spelling, as they appear in the
  sheet): เชียงใหม่, นครสวรรค์, เชียงราย, กำแพงเพชร, ลำปาง, เพชรบูรณ์,
  ลำพูน, ตาก, พิษณุโลก, พิจิตร, สุโขทัย, แพร่, พะเยา, อุตรดิตถ์, น่าน,
  อุทัยธานี, แม่ฮ่องสอน.
- One known malformed row: the row whose `FID` is `10600271025699`
  (บริษัท ทีทีดี โซลาร์ 1 จำกัด) has its ตำบล/อำเภอ/จังหวัด/ไปรษณีย์/
  โทรศัพท์/แรงม้า/แรงม้าตรวจพบ columns misaligned at the source (the raw
  row reads: ตำบล slot holds `"ตากฟ้า"`, อำเภอ slot holds `"นครสวรรค์"`,
  จังหวัด slot holds the postal code `60190`, and the horsepower slots
  hold `112500000` / `12351`). Only จังหวัด (`นครสวรรค์`), อำเภอ
  (`ตากฟ้า`, a real district of that province) and ไปรษณีย์ (`60190`,
  a real postal code of that district) can be recovered with confidence
  — fix those three. ตำบล cannot be recovered and must be set to `null`,
  not guessed. For horsepower, use `12351` as the `hp_registered` value
  (the smaller of the two misplaced numbers — `112500000` hp is not
  physically plausible for a facility described as 5,185 kW) but treat
  it as best-effort, not verified-correct; this affects exactly one row
  out of 7,405 and is not worth deeper reconstruction.
- Type code parsing rule: search anywhere in `เลขทะเบียนเดิม` for the
  regex `(\d+(?:\([0-9]+\))?)-\d+/\d+` and take group 1. This matches all
  7,405 rows regardless of prefix style (`3-10(3)-2/22ชม`,
  `จ3-10(1)-1/39ชม`, `น.53(5)-1/2540-นนน.`, etc.).
- `type_main` (used for grouping in the filter UI) is the leading digit
  run of the parsed type code, e.g. `10(3)` → `"10"`, `105` → `"105"`.
- HP filter must support both แรงม้า (`hp_registered`) and แรงม้าตรวจพบ
  (`hp_inspected`), user-toggleable (confirmed with user). Type filter
  matches only the primary parsed type code — `ประเภทรอง` is not used
  (confirmed with user).
- Choropleth colors by raw factory count per region, not normalized
  (confirmed design decision).
- Boundary data source: `chingchai/OpenGISData-Thailand` (CC BY 4.0),
  raw files at
  `https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson`
  and `.../master/districts.geojson`. Province features key Thai name as
  `pro_th`; district features key district name as `amp_th` and province
  name as `pro_th`.
- Sub-district (ตำบล) is a table/list breakdown only, never a third map
  layer (confirmed design decision).
- Horsepower filter has two modes, user-selectable: **range** (min and
  max, inclusive) and **comparison** (greater-than OR less-than a single
  value, user picks which). Whichever HP mode is active combines with
  the type-code filter and the search text using AND logic — narrowing
  one never disables the others.
- Clicking a factory's name (in the map sidebar list or the table view)
  opens a detail view showing its full record: name, operator, business
  description, full address (เลขที่/หมู่/ซอย/ถนน/ตำบล/อำเภอ/จังหวัด/
  ไปรษณีย์), phone, old registration number, both horsepower values,
  type code, commercial registration number, and tax ID. This requires
  `factories.json` to carry those extra raw fields (see Task 1).
- Final deliverable is one file, `dist/dashboard.html`, openable directly
  from disk (`file://`) — so all data must be inlined as JS values, not
  fetched, since `file://` pages cannot `fetch()` sibling JSON files in
  most browsers.

## Review Focus

- **The malformed row.** If the fix in Task 1 doesn't land exactly as
  specified, this one factory will silently appear under the wrong
  province or with a nonsense horsepower value. Task 1 tests this
  explicitly by FID.
- **Registration numbers with no parenthesis and no sub-type**, e.g.
  `3-105-112/48ชม` → type code `105`. A parser that assumes every type
  has a `(n)` suffix will crash or mis-parse ~40% of rows. Task 1 tests
  this case directly.
- **Districts whose Thai name doesn't match cleanly between the Excel
  and the boundary file** (e.g. different spelling/spacing). If silently
  dropped, that district's factories would vanish from the map — Task 3
  tests that every excel (province, district) pair resolves to a
  boundary district or is explicitly listed as unmatched, never silently
  skipped.
- **Horsepower values of 0 or very large** (e.g. power-plant entries
  with แรงม้า in the millions are real, not errors). A range filter with
  a linear slider bound to the true max will be unusable (one factory
  drags the whole range). Task 5 tests that the HP filter's bounds and
  behavior remain sane with the real min/max present in `meta.json`.
- **A province/district with zero factories after filtering.** The map
  and table must show it as zero/empty, not disappear or throw — Task 4
  and Task 5 tests cover a filter combination that legitimately empties
  a region.
- **Filters combining, not overriding each other.** The user explicitly
  asked that a type-code filter and an HP filter apply together (AND),
  not that picking one clears or disables the other. Task 5 Step 3
  verifies this directly by narrowing with type first, then narrowing
  further with HP, and checking the count drops in two stages.

---

## File Structure

```
D:\DIW\6.LIST OF FACTORY\
  scripts/
    build_factories.py       # Task 1
    fetch_boundaries.py      # Task 2
    match_boundaries.py      # Task 3
    build_dashboard.py       # Task 6
  tests/
    test_build_factories.py  # Task 1
    test_fetch_boundaries.py # Task 2
    test_match_boundaries.py # Task 3
  data/
    processed/
      factories.json         # Task 1 output
      meta.json               # Task 1 output
    boundaries/
      provinces.geojson       # Task 2 output
      districts.geojson       # Task 2 output
      name_aliases.json        # Task 3 input (manual correction list)
      match_report.json        # Task 3 output
  dashboard/
    template.html             # Task 4 + Task 5 (the real UI/JS)
  dist/
    dashboard.html            # Task 6 output — the deliverable
```

---

### Task 1: Factory data pipeline

**Files:**
- Create: `scripts/build_factories.py`
- Create: `tests/test_build_factories.py`

**Interfaces:**
- Produces: `parse_type_code(old_reg_no: str) -> str` and
  `type_main(type_code: str) -> str`, both importable from
  `scripts/build_factories.py`.
- Produces: `data/processed/factories.json` — a JSON array of objects,
  one per factory, each with exactly these keys: `fid` (int), `old_reg_no`
  (str), `name` (str), `operator` (str), `business` (str), `address_no`
  (str or null), `moo` (str or null), `soi` (str or null), `road` (str or
  null), `tambon` (str or null — null only for the one malformed row in
  Global Constraints), `amphoe` (str), `province` (str), `postcode` (str
  or null), `phone` (str or null), `hp_registered` (number), `hp_inspected`
  (number or null), `type_code` (str), `type_main` (str), `commercial_reg`
  (str or null), `tax_id` (str or null). These extra fields (beyond what
  filtering/mapping needs) exist solely so the per-factory detail view
  (see Global Constraints) has the full record to show.
- Produces: `data/processed/meta.json` — a JSON object:
  `{"type_codes": [{"code": str, "count": int}, ...]  // sorted by count desc`,
  `"provinces": [{"name": str, "count": int}, ...]  // sorted by count desc`,
  `"hp_registered_max": number, "hp_inspected_max": number}`.

- [ ] **Step 1: Write failing tests for the pure parsing functions**

```python
import unittest
from scripts.build_factories import parse_type_code, type_main

class TestParseTypeCode(unittest.TestCase):
    def test_simple_prefix(self):
        self.assertEqual(parse_type_code("3-10(3)-2/22ชม"), "10(3)")

    def test_letter_digit_prefix(self):
        self.assertEqual(parse_type_code("จ3-10(1)-1/39ชม"), "10(1)")

    def test_letter_dot_prefix_no_dash_before_type(self):
        self.assertEqual(parse_type_code("น.53(5)-1/2540-นนน."), "53(5)")

    def test_no_sub_type(self):
        self.assertEqual(parse_type_code("3-105-112/48ชม"), "105")

class TestTypeMain(unittest.TestCase):
    def test_with_subtype(self):
        self.assertEqual(type_main("10(3)"), "10")

    def test_without_subtype(self):
        self.assertEqual(type_main("105"), "105")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_build_factories -v`
Expected: FAIL/ERROR — `parse_type_code` and `type_main` not defined.

- [ ] **Step 3: Implement `parse_type_code` and `type_main` in `scripts/build_factories.py`**

`parse_type_code` uses `re.search(r"(\d+(?:\([0-9]+\))?)-\d+/\d+", old_reg_no)`
and returns group 1 (raise `ValueError` with the offending string if no
match — this must never happen on real data per the Global Constraints,
so a raise here is a loud signal of bad input, not a case to swallow).
`type_main` uses `re.match(r"\d+", type_code)` and returns group 0.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_build_factories -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Write a failing test for the malformed-row fix, against the real workbook**

```python
class TestMalformedRowFix(unittest.TestCase):
    def test_ttd_solar_row_is_corrected(self):
        factories = {f["fid"]: f for f in load_factories_from_workbook(
            "list of factories north thailand.xlsx")}
        row = factories[10600271025699]
        self.assertEqual(row["province"], "นครสวรรค์")
        self.assertEqual(row["amphoe"], "ตากฟ้า")
        self.assertIsNone(row["tambon"])
        self.assertEqual(row["postcode"], "60190")
        self.assertEqual(row["hp_registered"], 12351)  # best-effort, see Global Constraints
```

(`load_factories_from_workbook` is the function Step 7 defines; this test
is written first per TDD even though it names a not-yet-written function,
per the plan's own sequencing — write it, confirm it fails for the right
reason i.e. `NameError`/`ImportError`, then implement.)

- [ ] **Step 6: Run the test to verify it fails**

Run: `python -m unittest tests.test_build_factories -v`
Expected: FAIL — `load_factories_from_workbook` not defined.

- [ ] **Step 7: Implement `load_factories_from_workbook(path: str) -> list[dict]` in `scripts/build_factories.py`**

Reads the sheet with `openpyxl` (`data_only=True`), skips the header row,
and for every row builds the dict described in Interfaces above — mapping
columns 7/8/9/10/15/18/19 (เลขที่/หมู่/ซอย/ถนน/โทรศัพท์/ทะเบียนพาณิชย์/
เลขผู้เสียภาษี) to `address_no`/`moo`/`soi`/`road`/`phone`/`commercial_reg`/
`tax_id` as strings (or `None` if the cell is empty/`"-"`), alongside
`parse_type_code`/`type_main` on column 1. Before general parsing, special-case
the row where column 3 (`FID`) equals `10600271025699` per the Global
Constraints note: set `tambon` to `None`, `amphoe` to `"ตากฟ้า"`,
`province` to `"นครสวรรค์"`, `postcode` to `"60190"`, and `hp_registered`
to `12351` (overriding whatever the raw columns 11–17 would otherwise
produce for this one row). Cast `postcode` to `str` if not null for all
other rows too (the sheet stores it as int/str inconsistently).

- [ ] **Step 8: Run all tests in this file to verify they pass**

Run: `python -m unittest tests.test_build_factories -v`
Expected: PASS (7 tests)

- [ ] **Step 9: Implement the `main()` CLI entry that writes both output files**

`main()` calls `load_factories_from_workbook`, writes
`data/processed/factories.json` (UTF-8, `ensure_ascii=False`), computes
and writes `data/processed/meta.json` per the Interfaces schema above
(provinces/type_codes sorted by count descending, hp maxima from the
loaded data). Guard with `if __name__ == "__main__": main()`.

- [ ] **Step 10: Run the script against the real workbook and spot-check the output**

Run: `python scripts/build_factories.py`
Expected: `data/processed/factories.json` has 7405 entries; `len(set(f["province"] for f in factories)) == 17`;
`data/processed/meta.json`'s `provinces` list's top entry is `{"name": "เชียงใหม่", "count": 1062}`.

- [ ] **Step 11: Commit**

```bash
git init -q 2>/dev/null; git add scripts/build_factories.py tests/test_build_factories.py data/processed/factories.json data/processed/meta.json
git commit -m "feat: factory data pipeline (clean + parse Excel to JSON)"
```

---

### Task 2: Boundary data pipeline

**Files:**
- Create: `scripts/fetch_boundaries.py`
- Create: `tests/test_fetch_boundaries.py`

**Interfaces:**
- Consumes: the 17-province list from Global Constraints.
- Produces: `filter_boundaries(geojson: dict, allowed_provinces: set[str], province_key: str) -> dict`,
  importable from `scripts/fetch_boundaries.py` — returns a new
  FeatureCollection containing only features whose `properties[province_key]`
  is in `allowed_provinces`.
- Produces: `round_coordinates(geojson: dict, ndigits: int) -> dict` —
  returns a new FeatureCollection with every coordinate pair rounded to
  `ndigits` decimal places (recursing through Polygon/MultiPolygon nesting).
- Produces: `data/boundaries/provinces.geojson` (17 features) and
  `data/boundaries/districts.geojson` (features for those 17 provinces
  only), both coordinate-rounded to 5 decimal places.

- [ ] **Step 1: Write failing tests for `filter_boundaries` and `round_coordinates`**

```python
import unittest
from scripts.fetch_boundaries import filter_boundaries, round_coordinates

SAMPLE = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"pro_th": "เชียงใหม่"},
     "geometry": {"type": "Polygon", "coordinates": [[[98.123456, 18.654321]]]}},
    {"type": "Feature", "properties": {"pro_th": "สงขลา"},
     "geometry": {"type": "Polygon", "coordinates": [[[100.1, 7.2]]]}},
]}

class TestFilterBoundaries(unittest.TestCase):
    def test_keeps_only_allowed_provinces(self):
        result = filter_boundaries(SAMPLE, {"เชียงใหม่"}, "pro_th")
        self.assertEqual(len(result["features"]), 1)
        self.assertEqual(result["features"][0]["properties"]["pro_th"], "เชียงใหม่")

class TestRoundCoordinates(unittest.TestCase):
    def test_rounds_nested_polygon_coords(self):
        result = round_coordinates(SAMPLE, 2)
        self.assertEqual(
            result["features"][0]["geometry"]["coordinates"],
            [[[98.12, 18.65]]])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_fetch_boundaries -v`
Expected: FAIL/ERROR — functions not defined.

- [ ] **Step 3: Implement `filter_boundaries` and `round_coordinates` in `scripts/fetch_boundaries.py`**

`filter_boundaries` is a dict/list-comprehension filter over `features`
copying the `type` key through. `round_coordinates` recursively walks
`geometry.coordinates` (which nests 2–4 levels deep depending on
Polygon vs MultiPolygon) rounding every leaf pair with Python's
`round()`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_fetch_boundaries -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Implement the `main()` CLI entry that downloads, filters, rounds and writes**

Using `requests.get` on the two raw URLs in Global Constraints (10s
timeout, raise on non-200), filter `provinces.geojson` on `pro_th` and
`districts.geojson` on `pro_th`, round both to 5 decimals, and write to
`data/boundaries/provinces.geojson` / `districts.geojson`
(UTF-8, `ensure_ascii=False`). Guard with `if __name__ == "__main__": main()`.

- [ ] **Step 6: Run the script and verify the outputs**

Run: `python scripts/fetch_boundaries.py`
Expected: `data/boundaries/provinces.geojson` has exactly 17 features;
every feature in `data/boundaries/districts.geojson` has
`properties["pro_th"]` in the 17-province set; combined file size of
both files is under 3MB.

- [ ] **Step 7: Commit**

```bash
git add scripts/fetch_boundaries.py tests/test_fetch_boundaries.py data/boundaries/provinces.geojson data/boundaries/districts.geojson
git commit -m "feat: boundary data pipeline (fetch + filter + simplify Thai admin boundaries)"
```

---

### Task 3: Name-matching between Excel districts and boundary districts

**Files:**
- Create: `scripts/match_boundaries.py`
- Create: `tests/test_match_boundaries.py`
- Create: `data/boundaries/name_aliases.json` (starts as `{}`)

**Interfaces:**
- Consumes: `data/processed/factories.json` (Task 1), `data/boundaries/districts.geojson` (Task 2).
- Produces: `build_excel_pairs(factories: list[dict]) -> set[tuple[str, str]]` —
  the set of distinct `(province, amphoe)` pairs appearing in the factory data.
- Produces: `build_boundary_pairs(districts_geojson: dict) -> set[tuple[str, str]]` —
  the set of distinct `(pro_th, amp_th)` pairs in the boundary file.
- Produces: `find_unmatched(excel_pairs: set, boundary_pairs: set, aliases: dict[tuple[str,str], tuple[str,str]]) -> set[tuple[str, str]]` —
  for each excel pair, applies `aliases.get(pair, pair)` before checking
  membership in `boundary_pairs`; returns the excel pairs (original, unaliased)
  still unmatched after aliasing.
- Produces: `data/boundaries/match_report.json` — `{"total_excel_pairs": int, "unmatched": [[province, amphoe], ...]}`.

- [ ] **Step 1: Write failing tests for the three pure functions**

```python
import unittest
from scripts.match_boundaries import build_excel_pairs, build_boundary_pairs, find_unmatched

class TestBuildExcelPairs(unittest.TestCase):
    def test_extracts_distinct_pairs(self):
        factories = [{"province": "เชียงใหม่", "amphoe": "เมืองเชียงใหม่"},
                     {"province": "เชียงใหม่", "amphoe": "เมืองเชียงใหม่"},
                     {"province": "ลำปาง", "amphoe": "เมืองลำปาง"}]
        self.assertEqual(build_excel_pairs(factories),
                          {("เชียงใหม่", "เมืองเชียงใหม่"), ("ลำปาง", "เมืองลำปาง")})

class TestBuildBoundaryPairs(unittest.TestCase):
    def test_extracts_distinct_pairs(self):
        geojson = {"features": [
            {"properties": {"pro_th": "เชียงใหม่", "amp_th": "เมืองเชียงใหม่"}}]}
        self.assertEqual(build_boundary_pairs(geojson), {("เชียงใหม่", "เมืองเชียงใหม่")})

class TestFindUnmatched(unittest.TestCase):
    def test_direct_match_is_not_unmatched(self):
        excel = {("เชียงใหม่", "เมืองเชียงใหม่")}
        boundary = {("เชียงใหม่", "เมืองเชียงใหม่")}
        self.assertEqual(find_unmatched(excel, boundary, {}), set())

    def test_aliased_match_is_not_unmatched(self):
        excel = {("เชียงใหม่", "เมืองฯ")}
        boundary = {("เชียงใหม่", "เมืองเชียงใหม่")}
        aliases = {("เชียงใหม่", "เมืองฯ"): ("เชียงใหม่", "เมืองเชียงใหม่")}
        self.assertEqual(find_unmatched(excel, boundary, aliases), set())

    def test_truly_unmatched_is_reported(self):
        excel = {("เชียงใหม่", "ไม่มีจริง")}
        boundary = {("เชียงใหม่", "เมืองเชียงใหม่")}
        self.assertEqual(find_unmatched(excel, boundary, {}), {("เชียงใหม่", "ไม่มีจริง")})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_match_boundaries -v`
Expected: FAIL/ERROR — functions not defined.

- [ ] **Step 3: Implement the three functions in `scripts/match_boundaries.py`**

Straightforward set comprehensions per the Interfaces descriptions above.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_match_boundaries -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Implement `main()` and run it against the real data**

`main()` loads `data/processed/factories.json` and
`data/boundaries/districts.geojson`, loads `data/boundaries/name_aliases.json`
(defaulting to `{}` if the file is empty), computes `find_unmatched`, and
writes `data/boundaries/match_report.json` per the Interfaces schema.
Print the unmatched list to stdout.

Run: `python scripts/match_boundaries.py`

- [ ] **Step 6: Resolve any real unmatched pairs by editing `name_aliases.json`**

For every pair Step 5 printed, find its correct counterpart in
`data/boundaries/districts.geojson` (grep the file for the province name
and inspect nearby `amp_th` values for a spelling/spacing variant) and add
`"[\"<province>\", \"<excel amphoe>\"]": ["<province>", "<boundary amphoe>"]`
to `data/boundaries/name_aliases.json`. Re-run Step 5's command until
`match_report.json`'s `unmatched` list is empty, or — if a district
genuinely has no boundary counterpart (e.g. a very new district) — leave
it listed and note it in this task's commit message; Task 4/5's table
view still shows that district's factories correctly regardless (only
its map shape would be missing).

- [ ] **Step 7: Commit**

```bash
git add scripts/match_boundaries.py tests/test_match_boundaries.py data/boundaries/name_aliases.json data/boundaries/match_report.json
git commit -m "feat: match Excel districts to boundary districts, with alias corrections"
```

---

### Task 4: Dashboard map — province/district drill-down with choropleth

**Files:**
- Create: `dashboard/template.html`

**Interfaces:**
- Consumes: `FACTORIES` (the array shape from Task 1's `factories.json`),
  `PROVINCES_GEOJSON`/`DISTRICTS_GEOJSON` (Task 2's output shape) — all
  three will be injected by Task 6 as `const FACTORIES = /*__FACTORIES__*/;`
  etc. For this task, write literal placeholder data at the top of the
  file so it's directly openable in a browser during development; Task 6
  replaces those placeholder lines by exact string match.
- Produces: a global `renderMap(factories)` function and a module-level
  `currentLevel` ('province'|'district') and `currentProvince` (string|null)
  state, which Task 5 will read/call when filters change.
- Produces: a global `showFactoryDetail(fid)` function that looks up the
  factory in `FACTORIES` by `fid` and renders all of its fields (per the
  Global Constraints detail-view list) in a modal/overlay with a close
  control. Task 5's table view calls this same function, so there is one
  detail view implementation, not two.

- [ ] **Step 1: Write `dashboard/template.html` with placeholder data and the static page shell**

```html
<!doctype html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<style>/* full-height #map, sidebar panel for drill-down list — builder's call on exact layout */</style>
</head><body>
<div id="map"></div>
<div id="sidebar"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script>
const FACTORIES = /*__FACTORIES__*/ [];
const PROVINCES_GEOJSON = /*__PROVINCES_GEOJSON__*/ {"type":"FeatureCollection","features":[]};
const DISTRICTS_GEOJSON = /*__DISTRICTS_GEOJSON__*/ {"type":"FeatureCollection","features":[]};
</script>
</body></html>
```

(For local manual testing before Task 6 exists, temporarily paste the
real contents of `data/processed/factories.json` and the two boundary
files in place of the empty placeholders, or open it after Task 6 runs
once — either is fine, this step itself has no automated test.)

- [ ] **Step 2: Implement province-level choropleth rendering**

Add a Leaflet map (`L.map('map')`), add `PROVINCES_GEOJSON` as an
`L.geoJSON` layer, style each feature by its factory count — computed by
counting `FACTORIES` where `f.province === feature.properties.pro_th` —
using a color scale (builder's call on exact breakpoints/palette; must
be visually distinguishable across the real range 60–1062). Clicking a
province feature zooms the map to its bounds and calls `renderMap`
again in `'district'` mode for that province.

- [ ] **Step 3: Implement district-level choropleth rendering**

When `currentLevel === 'district'`, render `DISTRICTS_GEOJSON` features
filtered to `feature.properties.pro_th === currentProvince`, styled by
count of `FACTORIES` matching that `(province, amphoe)` pair. Clicking a
district shows, in `#sidebar`, the list of matching factories (name,
business, tambon, hp_registered), grouped under ตำบล headers, with each
factory's name clickable to call `showFactoryDetail(f.fid)`. Add a
"back to province view" control.

- [ ] **Step 4: Implement `showFactoryDetail(fid)`**

Looks up the factory by `fid` in `FACTORIES`, builds a modal/overlay
(simple fixed-position `div` over the page, builder's call on exact
styling) listing every field named in the Global Constraints detail-view
bullet with a Thai label each, and a close button/click-outside-to-close
that removes the overlay.

- [ ] **Step 5: Manual verification in the browser**

Open `dashboard/template.html` (with real data pasted in per Step 1's
note) directly in a browser. Verify: all 17 provinces render with visibly
different colors; เชียงใหม่ is the most intensely colored (1,062); clicking
it shows its districts; clicking เมืองเชียงใหม่ shows a non-empty factory
list in the sidebar whose count matches `FACTORIES.filter(f => f.province
=== "เชียงใหม่" && f.amphoe === "เมืองเชียงใหม่").length` (check via the
browser console); clicking any factory's name in that list opens the
detail overlay showing its operator, business description, full address,
phone, both horsepower values, and the three registration/tax numbers.

- [ ] **Step 6: Commit**

```bash
git add dashboard/template.html
git commit -m "feat: dashboard map with province/district drill-down choropleth and factory detail view"
```

---

### Task 5: Dashboard filters + table-view toggle

**Files:**
- Modify: `dashboard/template.html`

**Interfaces:**
- Consumes: `renderMap(factories)`, `currentLevel`, `currentProvince`
  from Task 4 — filters call `renderMap(filteredFactories)` instead of
  the full `FACTORIES` array whenever a filter changes.
- Consumes: `showFactoryDetail(fid)` from Task 4 — the table view's
  factory-name links call this same function, not a second
  implementation.
- Consumes: `meta.json`'s shape (Task 1) for populating the type-code
  filter options and the HP range bounds — injected by Task 6 the same
  way as Task 4's data, as `const META = /*__META__*/ {};`.
- Produces: a module-level `getFilteredFactories() -> array` function,
  combining the current HP mode (range, or greater-than/less-than) +
  field (registered/inspected), the type-code multi-select, and the
  search text with AND logic — used by both the map and the table view
  so they never disagree.

- [ ] **Step 1: Add the filter controls and `getFilteredFactories()`**

Add to the page: an HP field toggle (แรงม้า / แรงม้าตรวจพบ radio); an HP
mode toggle ("range" / "greater than" / "less than"); for range mode, a
min/max input pair bounded by `META.hp_registered_max` /
`META.hp_inspected_max` depending on the field toggle; for
greater-than/less-than mode, a single value input, compared with `>` or
`<` against the selected field; a multi-select (or checkbox list) of
type codes from `META.type_codes`; and a text input for free-text search
over `name` + `business`. `getFilteredFactories()` reads all current
control values and returns the `FACTORIES` array filtered by every
active control ANDed together (an inactive control imposes no
constraint — e.g. leaving the type multi-select empty means "all
types", not "no factories"). Wire every control's change event to call
`getFilteredFactories()` then `renderMap(result)`.

- [ ] **Step 2: Add the table-view toggle**

Add a view-mode toggle button/tabs ("Map" / "Table"). In table mode,
hide `#map`/`#sidebar` and render a `<table>` with one row per
province+district (from `getFilteredFactories()`, grouped by
`(province, amphoe)`), columns: province, district, factory count — each
row clickable to expand a sub-district (`tambon`) breakdown inline
listing each factory's name (clickable, calling `showFactoryDetail(f.fid)`)
and hp_registered. The table must use `getFilteredFactories()`, never
`FACTORIES` directly, so it always matches the map's filtered state.

- [ ] **Step 3: Manual verification in the browser**

With real data: set the type-code filter to a single common code (e.g.
`9(1)`, 113 factories per the design doc's exploration) and confirm both
the map's colors and the table's counts drop to match; switch to table
view and confirm the same filtered total; while that type filter is
still active, additionally set an HP range that excludes the known large
power-plant entries (e.g. max 10,000) and confirm counts drop further
still — proving the two filters combine, not override each other; switch
the HP control to "greater than" mode with a high value (e.g. 100,000)
and confirm only the handful of power-plant/solar-farm entries remain;
click a factory name in the table and confirm the same detail overlay
from Task 4 opens with matching data; pick a filter combination with a
legitimate zero-count province/district and confirm it renders as
empty/zero rather than disappearing or erroring (open the browser
console and confirm no errors).

- [ ] **Step 4: Commit**

```bash
git add dashboard/template.html
git commit -m "feat: dashboard filters (horsepower, factory type, search) and table-view toggle"
```

---

### Task 6: Build script — assemble the final single-file dashboard

**Files:**
- Create: `scripts/build_dashboard.py`
- Create: `tests/test_build_dashboard.py`

**Interfaces:**
- Consumes: `dashboard/template.html` (Task 4/5), `data/processed/factories.json`
  and `meta.json` (Task 1), `data/boundaries/provinces.geojson` and
  `districts.geojson` (Task 2/3).
- Produces: `inject(template: str, factories: list, meta: dict, provinces_geojson: dict, districts_geojson: dict) -> str`,
  importable from `scripts/build_dashboard.py`.
- Produces: `dist/dashboard.html` — the final deliverable.

- [ ] **Step 1: Write a failing test for `inject`**

```python
import unittest
from scripts.build_dashboard import inject

class TestInject(unittest.TestCase):
    def test_replaces_all_four_placeholders(self):
        template = (
            "const FACTORIES = /*__FACTORIES__*/ [];\n"
            "const PROVINCES_GEOJSON = /*__PROVINCES_GEOJSON__*/ {};\n"
            "const DISTRICTS_GEOJSON = /*__DISTRICTS_GEOJSON__*/ {};\n"
            "const META = /*__META__*/ {};\n")
        result = inject(template, [{"name": "x"}], {"a": 1}, {"type": "FeatureCollection"}, {"type": "FeatureCollection"})
        self.assertNotIn("/*__FACTORIES__*/ []", result)
        self.assertIn('"name": "x"', result)
        self.assertIn('"a": 1', result)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_build_dashboard -v`
Expected: FAIL — `inject` not defined.

- [ ] **Step 3: Implement `inject` in `scripts/build_dashboard.py`**

Four `str.replace` calls, each replacing the exact placeholder comment
plus its trailing default value (e.g. `/*__FACTORIES__*/ []`) with
`json.dumps(factories, ensure_ascii=False)`, and likewise for the other
three.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest tests.test_build_dashboard -v`
Expected: PASS

- [ ] **Step 5: Implement `main()` and run it**

`main()` reads all five input files, calls `inject`, and writes the
result to `dist/dashboard.html` (creating `dist/` if needed).

Run: `python scripts/build_dashboard.py`

- [ ] **Step 6: Final end-to-end manual verification**

Open `dist/dashboard.html` directly from disk (double-click / `file://`)
in a real browser. Repeat the checks from Task 4 Step 5 and Task 5 Step 3
against this final file (not the template) to confirm the injected data
round-tripped correctly. Confirm the file opens with no network requests
other than the Leaflet CDN assets (check the browser's network tab).

- [ ] **Step 7: Commit**

```bash
git add scripts/build_dashboard.py tests/test_build_dashboard.py dist/dashboard.html
git commit -m "feat: build script producing the final single-file dashboard"
```
