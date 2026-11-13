"""Parse the geography inputs used by the coordination-zone and protection-zone analysis.

Usage: python scripts/parse_geo.py <interim_dir> <raw_dir> <processed_dir>

interim_dir holds pdftotext -layout output of FCC DA 14-759 Attachments A2 and A3 (pea_ea.txt,
pea_county.txt). Writes:
  pea_ea.csv          PEA number, name, 2010 population, Economic Area (EA) number (DA 14-759 App. A)
  pea_counties.csv    PEA number, county FIPS, county name, state (DA 14-759 App. B)
  county_pop_2020.csv county FIPS, 2020 population, population-weighted centroid (Census CenPop2020)
  us88_zones.csv      the 27 federal earth station protection zones for 1695-1710 MHz AWS
                      (47 CFR 2.106 footnote US88, eCFR as of Nov. 1, 2026)
  ntia_sites.csv      the four NOAA DCS sites the FNPRM protects, with NTIA's coordination distances
                      (NTIA Report 24-01, Tables 3 and 9; FNPRM para. 101)
  ntia_table11.csv    NTIA's population impact for the top 25 PEAs, Alternative Distribution
                      Mechanism scenario (NTIA Report 24-01, Table 11) -- the reference case the zone
                      model must reproduce
"""
import csv
import re
import sys
from pathlib import Path

INTERIM, RAW, OUT = (Path(a) for a in sys.argv[1:4])
OUT.mkdir(parents=True, exist_ok=True)


def write(name, header, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


# DA 14-759 Appendix A: PEA -> EA
rows = []
pat = re.compile(r"^\s*(\d{1,3})\s+(.+?)\s+([\d,]+|-)\s+(\d{1,3})\s*$")
for line in open(INTERIM / "pea_ea.txt"):
    m = pat.match(line)
    if m:
        pop = 0 if m[3] == "-" else int(m[3].replace(",", ""))  # Gulf of Mexico has no population
        rows.append([int(m[1]), m[2].strip(), pop, int(m[4])])
seen = {}
for r in rows:
    seen.setdefault(r[0], r)
rows = [seen[k] for k in sorted(seen)]
assert len(rows) == 416, len(rows)
write("pea_ea.csv", ["pea", "pea_name", "population_2010", "ea"], rows)

# DA 14-759 Appendix B: county -> PEA
rows = []
pat = re.compile(r"^\s*(\d{1,3})\s+(\d{5})\s+(.+?)\s+([A-Z]{2})\s*$")
for line in open(INTERIM / "pea_county.txt"):
    m = pat.match(line)
    if m:
        rows.append([int(m[1]), m[2], m[3].strip(), m[4]])
assert len(rows) > 3200, len(rows)
write("pea_counties.csv", ["pea", "fips", "county", "state"], rows)

# Census 2020 county population centroids
rows = []
for r in csv.DictReader(open(RAW / "census" / "CenPop2020_Mean_CO.txt", encoding="utf-8-sig")):
    rows.append([r["STATEFP"] + r["COUNTYFP"], r["COUNAME"], r["STNAME"], int(r["POPULATION"]),
                 float(r["LATITUDE"]), float(r["LONGITUDE"])])
write("county_pop_2020.csv", ["fips", "county", "state", "population_2020", "lat", "lon"], rows)

# 47 CFR 2.106 US88 protection zones
xml = open(RAW / "ecfr" / "title47_section2.106_2026-11-01.xml", encoding="utf-8", errors="ignore").read()
text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
seg = text[text.index("US88 In the bands 1675-1695 MHz"):]
seg = seg[:seg.index("(89)")]


def dms(d, m, s):
    return int(d) + int(m) / 60 + int(s) / 3600


zpat = re.compile(r"([A-Z]{2}) ([A-Za-z .\-]+?) (\d+)°(\d+)′(\d+)″ (\d+)°(\d+)′(\d+)″ (\d+)")
rows = []
for table, part in (("1695-1710", seg[seg.index("Table 5"):seg.index("Table 6")]),
                    ("1675-1695", seg[seg.index("Table 6"):])):
    for m in zpat.finditer(part):
        st_, loc = m[1], m[2].strip()
        lat = dms(m[3], m[4], m[5])
        lon = dms(m[6], m[7], m[8])
        lon = lon if st_ == "GU" else -lon
        rows.append([st_, loc, round(lat, 6), round(lon, 6), int(m[9]), table])
assert len(rows) == 27, len(rows)
write("us88_zones.csv", ["state", "location", "lat", "lon", "radius_km", "us88_table_band"], rows)

# NTIA Report 24-01: the four sites the FNPRM protects, plus Hunt Valley (in NTIA's ADM scenario)
sites = [  # name, lat, lon (Table 3), DCS coordination distance km (Table 9), in FNPRM proposal
    ("Fairmont, WV", 39.4336, -80.1928, 459, "Y"),
    ("Sioux Falls, SD", 43.7351, -96.6255, 346, "Y"),
    ("Suitland, MD", 38.8522, -76.9367, 468, "Y"),
    ("Wallops, VA", 37.9465, -75.4621, 446, "Y"),
    ("Hunt Valley, MD", 39.4794, -76.6606, 388, "N"),
]
write("ntia_sites.csv", ["site", "lat", "lon", "ntia_dcs_coordination_km", "protected_in_fnprm"], sites)

# NTIA Report 24-01 Table 11 (ADM scenario): share of PEA population encumbered (non-overlapping +
# overlapping coordination zones) and unencumbered, top 25 PEAs.
t11 = [(1, 1.7, 92.4, 5.9), (2, 0, 0, 100), (3, 0, 0, 100), (4, 0, 0, 100), (5, 0, 100, 0),
       (6, 0, 100, 0), (7, 0, 0, 100), (8, 0, 0, 100), (9, 0, 0, 100), (10, 0, 0, 100), (11, 0, 0, 100),
       (12, 84.5, 0, 15.5), (13, 0, 0, 100), (14, 57.2, 42.8, 0), (15, 0, 0, 100), (16, 0, 0, 100),
       (17, 97.2, 0, 2.8), (18, 0, 0, 100), (19, 0, 0, 100), (20, 0, 0, 100), (21, 0, 0, 100),
       (22, 0, 0, 100), (23, 0, 100, 0), (24, 0, 0, 100), (25, 100, 0, 0)]
write("ntia_table11.csv", ["pea", "non_overlapping_pct", "overlapping_pct", "unencumbered_pct"], t11)
