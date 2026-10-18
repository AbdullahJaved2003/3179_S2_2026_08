"""
Prepare the small, chart-ready data files used by the Vega-Lite / Vega specs.

Inputs (data/raw/):
  vgsales.csv          VGChartz sales of games selling > 100,000 copies (Gregory Smith scrape, 2016)
  iso.csv              ISO-3166 country codes with UN regions (lukes/ISO-3166-Countries-with-Regional-Codes)
  aus_states.geojson   Australian state & territory boundaries (rowanhogan/australian-states)

Australian industry figures are typed in (see australia() below) from IGEA publications:
  Australian Game Development Survey FY2024 report
    https://igea.net/wp-content/uploads/2024/12/AGDS-2024-Report-Final.pdf
  Australian Game Development Survey FY2025 infographic
    https://igea.net/wp-content/uploads/2026/03/AGD-2025-Standalone-Infographic.pdf
  Australia Plays 2025 media release
    https://igea.net/2025/09/australian-parents-embrace-the-power-of-play/

Run from the repository root:  python3 scripts/prepare_data.py
"""
import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

FIRST_YEAR, LAST_YEAR = 1980, 2015  # 2016 was only partially recorded when the data was scraped

ERAS = [
    (1, "Early consoles", 1980, 1985),
    (2, "8 & 16-bit", 1986, 1994),
    (3, "3D revolution", 1995, 2000),
    (4, "PS2 era", 2001, 2005),
    (5, "Motion & HD", 2006, 2012),
    (6, "Modern", 2013, 2015),
]

PLATFORMS = {
    # code: (full name, maker, type)
    "2600": ("Atari 2600", "Atari", "Home"),
    "NES": ("Nintendo Entertainment System", "Nintendo", "Home"),
    "SNES": ("Super Nintendo", "Nintendo", "Home"),
    "N64": ("Nintendo 64", "Nintendo", "Home"),
    "GC": ("GameCube", "Nintendo", "Home"),
    "Wii": ("Wii", "Nintendo", "Home"),
    "WiiU": ("Wii U", "Nintendo", "Home"),
    "GB": ("Game Boy", "Nintendo", "Handheld"),
    "GBA": ("Game Boy Advance", "Nintendo", "Handheld"),
    "DS": ("Nintendo DS", "Nintendo", "Handheld"),
    "3DS": ("Nintendo 3DS", "Nintendo", "Handheld"),
    "PS": ("PlayStation", "Sony", "Home"),
    "PS2": ("PlayStation 2", "Sony", "Home"),
    "PS3": ("PlayStation 3", "Sony", "Home"),
    "PS4": ("PlayStation 4", "Sony", "Home"),
    "PSP": ("PlayStation Portable", "Sony", "Handheld"),
    "PSV": ("PlayStation Vita", "Sony", "Handheld"),
    "XB": ("Xbox", "Microsoft", "Home"),
    "X360": ("Xbox 360", "Microsoft", "Home"),
    "XOne": ("Xbox One", "Microsoft", "Home"),
    "GEN": ("Sega Genesis / Mega Drive", "Sega", "Home"),
    "SCD": ("Sega CD", "Sega", "Home"),
    "SAT": ("Sega Saturn", "Sega", "Home"),
    "DC": ("Dreamcast", "Sega", "Home"),
    "GG": ("Game Gear", "Sega", "Handheld"),
    "PC": ("PC", "PC", "Home"),
    "NG": ("Neo Geo", "Other", "Home"),
    "WS": ("WonderSwan", "Other", "Handheld"),
    "TG16": ("TurboGrafx-16", "Other", "Home"),
    "PCFX": ("PC-FX", "Other", "Home"),
    "3DO": ("3DO", "Other", "Home"),
}

REGIONS = {"NA_Sales": "North America", "EU_Sales": "Europe", "JP_Sales": "Japan", "Other_Sales": "Rest of world"}

# Headquarters of the 30 biggest publishers (about 90% of all copies sold), grouped by metro area.
# Locations from each company's Wikipedia article; Sony Computer Entertainment was Tokyo-based until 2016,
# Atari refers to Atari Inc. (New York), the 2000s publisher that sold most "Atari" games in the data.
HQ = {
    "Nintendo": ("Kyoto", "Japan", "JP"),
    "Electronic Arts": ("San Francisco Bay Area", "USA", "NA"),
    "Activision": ("Los Angeles area", "USA", "NA"),
    "Sony Computer Entertainment": ("Tokyo area", "Japan", "JP"),
    "Ubisoft": ("Paris area", "France", "EU"),
    "Take-Two Interactive": ("New York area", "USA", "NA"),
    "THQ": ("Los Angeles area", "USA", "NA"),
    "Konami Digital Entertainment": ("Tokyo area", "Japan", "JP"),
    "Sega": ("Tokyo area", "Japan", "JP"),
    "Namco Bandai Games": ("Tokyo area", "Japan", "JP"),
    "Microsoft Game Studios": ("Seattle area", "USA", "NA"),
    "Capcom": ("Osaka", "Japan", "JP"),
    "Atari": ("New York area", "USA", "NA"),
    "Warner Bros. Interactive Entertainment": ("Los Angeles area", "USA", "NA"),
    "Square Enix": ("Tokyo area", "Japan", "JP"),
    "Disney Interactive Studios": ("Los Angeles area", "USA", "NA"),
    "Eidos Interactive": ("London", "UK", "EU"),
    "LucasArts": ("San Francisco Bay Area", "USA", "NA"),
    "Bethesda Softworks": ("Washington DC area", "USA", "NA"),
    "Midway Games": ("Chicago", "USA", "NA"),
    "Acclaim Entertainment": ("New York area", "USA", "NA"),
    "Vivendi Games": ("Los Angeles area", "USA", "NA"),
    "SquareSoft": ("Tokyo area", "Japan", "JP"),
    "505 Games": ("Milan", "Italy", "EU"),
    "Tecmo Koei": ("Tokyo area", "Japan", "JP"),
    "Codemasters": ("Southam (Warwickshire)", "UK", "EU"),
    "Virgin Interactive": ("London", "UK", "EU"),
    "Enix Corporation": ("Tokyo area", "Japan", "JP"),
    "Deep Silver": ("Munich area", "Germany", "EU"),
}
CITY_COORDS = {
    "Kyoto": (35.01, 135.77), "Osaka": (34.69, 135.50), "Tokyo area": (35.68, 139.69),
    "San Francisco Bay Area": (37.60, -122.30), "Los Angeles area": (34.05, -118.40),
    "Seattle area": (47.65, -122.20), "New York area": (40.75, -73.95), "Chicago": (41.88, -87.63),
    "Washington DC area": (39.00, -77.10), "Paris area": (48.85, 2.40), "London": (51.50, -0.13),
    "Southam (Warwickshire)": (52.25, -1.39), "Milan": (45.46, 9.19), "Munich area": (48.10, 11.45),
}
HOME_POINT = {"NA": (39.5, -98.5), "EU": (50.0, 10.0), "JP": (36.2, 138.3)}
HUB_NAME = {"NA": "North America", "EU": "Europe", "JP": "Japan"}
N_STEPS = 24  # points along each flow path


SHORT = {
    "Sony Computer Entertainment": "Sony", "Microsoft Game Studios": "Microsoft", "Take-Two Interactive": "Take-Two",
    "Konami Digital Entertainment": "Konami", "Namco Bandai Games": "Namco Bandai", "Electronic Arts": "EA",
    "Warner Bros. Interactive Entertainment": "Warner Bros.", "Disney Interactive Studios": "Disney",
    "Square Enix": "Square Enix", "Eidos Interactive": "Eidos",
}


def era_of(year):
    for order, name, y0, y1 in ERAS:
        if y0 <= year <= y1:
            return order, f"{y0}–{str(y1)[-2:] if y0 // 100 == y1 // 100 else y1}", name
    raise ValueError(year)


def load_sales():
    df = pd.read_csv(RAW / "vgsales.csv")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    df = df[(df.Year >= FIRST_YEAR) & (df.Year <= LAST_YEAR)]
    # One DS game is dated 1985, two decades before the DS existed: a data-entry error, so it is dropped.
    df = df[~((df.Platform == "DS") & (df.Year < 2004))]
    df["Maker"] = df.Platform.map(lambda p: PLATFORMS[p][1])
    eras = df.Year.map(era_of)
    df["EraOrder"] = eras.map(lambda e: e[0])
    df["EraYears"] = eras.map(lambda e: e[1])
    df["EraName"] = eras.map(lambda e: e[2])
    return df


def write_csv(frame, name):
    frame.to_csv(OUT / name, index=False, float_format="%.4g")
    print(f"  {name:28s} {len(frame):5d} rows")


def headline(df):
    stats = {
        "games": int(len(df)),
        "titles": int(df.Name.nunique()),
        "copies_millions": round(float(df.Global_Sales.sum()), 1),
        "first_year": FIRST_YEAR,
        "last_year": LAST_YEAR,
        "platforms": int(df.Platform.nunique()),
        "publishers": int(df.Publisher.nunique()),
    }
    (OUT / "headline.json").write_text(json.dumps(stats, indent=2))
    print("  headline.json", stats)


def maker_year(df):
    t = df.groupby(["Year", "Maker"]).Global_Sales.sum().unstack(fill_value=0).stack().rename("sales").reset_index()
    write_csv(t, "maker_year.csv")


def eras_table():
    rows = [{"order": o, "era": n, "start": y0, "end": y1 + 1, "mid": (y0 + y1 + 1) / 2} for o, n, y0, y1 in ERAS]
    write_csv(pd.DataFrame(rows), "eras.csv")


def platforms(df):
    rows = []
    for code, g in df.groupby("Platform"):
        total = g.Global_Sales.sum()
        if total < 5:  # platforms with under 5 million copies are too small to show
            continue
        by_year = g.groupby("Year").Global_Sales.sum()
        active = by_year[by_year >= 0.01 * total]  # years carrying at least 1% of the platform's sales
        name, maker, kind = PLATFORMS[code]
        rows.append({
            "code": code, "name": name, "maker": maker, "type": kind,
            "start": int(active.index.min()), "end": int(active.index.max()) + 1,
            "peak_year": int(by_year.idxmax()), "peak_sales": round(by_year.max(), 2),
            "total": round(total, 1), "games": int(len(g)),
            "top_game": g.sort_values("Global_Sales", ascending=False).Name.iloc[0],
        })
    write_csv(pd.DataFrame(rows).sort_values(["start", "total"], ascending=[True, False]), "platforms.csv")


def genre_year(df):
    t = df.groupby(["Year", "Genre"]).Global_Sales.sum().unstack(fill_value=0).stack().rename("sales").reset_index()
    t["share"] = t.sales / t.groupby("Year").sales.transform("sum")
    write_csv(t, "genre_year.csv")


def genre_tree(df):
    rows = [{"id": "root", "parent": "", "name": "All games", "genre": "", "sales": None}]
    for genre, g in df.groupby("Genre"):
        pubs = g.groupby("Publisher").Global_Sales.sum().sort_values(ascending=False)
        rows.append({"id": genre, "parent": "root", "name": genre, "genre": genre, "sales": None,
                     "genre_total": round(pubs.sum(), 1)})
        top, rest = pubs.head(4), pubs.iloc[4:].sum()
        for pub, s in top.items():
            rows.append({"id": f"{genre}|{pub}", "parent": genre, "name": SHORT.get(pub, pub), "genre": genre,
                         "sales": round(s, 2),
                         "genre_total": round(pubs.sum(), 1)})
        rows.append({"id": f"{genre}|other", "parent": genre, "name": "Other publishers", "genre": genre,
                     "sales": round(rest, 2), "genre_total": round(pubs.sum(), 1)})
    write_csv(pd.DataFrame(rows), "genre_tree.csv")


def top_games(df):
    g = df.groupby(["EraOrder", "EraYears", "EraName", "Name"]).agg(
        sales=("Global_Sales", "sum"), genre=("Genre", "first"), publisher=("Publisher", "first"),
        platforms=("Platform", lambda s: ", ".join(sorted(set(s)))),
    ).reset_index()
    g["rank"] = g.groupby("EraOrder").sales.rank(method="first", ascending=False).astype(int)
    write_csv(g[g["rank"] <= 10].sort_values(["EraOrder", "rank"]), "top_games_era.csv")


def publisher_ranks(df):
    t = df.groupby(["EraOrder", "EraYears", "EraName", "Publisher"]).Global_Sales.sum().rename("sales").reset_index()
    t["rank"] = t.groupby("EraOrder").sales.rank(method="first", ascending=False).astype(int)
    keep = set(t[t["rank"] <= 6].Publisher)  # publishers that reached the top 6 in at least one era
    t = t[t.Publisher.isin(keep)].copy()
    home = {name: hub for name, (_, _, hub) in HQ.items()}
    home.update({"Imagic": "NA", "Parker Bros.": "NA"})  # early-1980s US publishers outside the top 30
    t["hub_name"] = t.Publisher.map(lambda n: HUB_NAME[home[n]])
    write_csv(t.sort_values(["Publisher", "EraOrder"]), "publisher_rank_era.csv")


def publisher_hq(df):
    pub = df.groupby("Publisher").Global_Sales.sum()
    covered = pub[pub.index.isin(HQ)].sum() / pub.sum()
    rows = []
    for name, (city, country, hub) in HQ.items():
        rows.append({"publisher": name, "city": city, "country": country, "hub": hub, "sales": pub[name]})
    p = pd.DataFrame(rows)
    city = p.sort_values("sales", ascending=False).groupby(["city", "country", "hub"]).agg(
        sales=("sales", "sum"), n=("publisher", "size"), publishers=("publisher", lambda s: ", ".join(s)),
    ).reset_index()
    city["lat"] = city.city.map(lambda c: CITY_COORDS[c][0])
    city["lon"] = city.city.map(lambda c: CITY_COORDS[c][1])
    city["hub_name"] = city.hub.map(HUB_NAME)
    # Label anchor positions (some labels are moved off their circle so neighbouring cities stay readable)
    label_pos = {
        "Kyoto": (37.3, 134.6, "center", "Kyoto · Nintendo"), "Osaka": (32.9, 134.3, "center", "Osaka · Capcom"),
        "Tokyo area": (33.2, 139.6, "center", "Tokyo · 8 publishers"),
        "San Francisco Bay Area": (39.8, -119.0, "left", "SF Bay Area"), "Los Angeles area": (32.4, -116.0, "left", "Los Angeles"),
        "Seattle area": (47.65, -120.0, "left", "Seattle"), "New York area": (44.6, -76.0, "right", "New York"),
        "Chicago": (41.88, -88.6, "right", "Chicago"), "Washington DC area": (37.6, -78.5, "right", "Washington DC"),
        "Paris area": (48.85, 4.0, "left", "Paris"), "London": (51.5, 0.9, "left", "London"),
        "Southam (Warwickshire)": (53.2, -0.6, "left", "Southam"), "Milan": (45.46, 8.2, "right", "Milan"),
        "Munich area": (48.10, 10.6, "right", "Munich"),
    }
    city["label_lat"] = city.city.map(lambda c: label_pos[c][0])
    city["label_lon"] = city.city.map(lambda c: label_pos[c][1])
    city["label_align"] = city.city.map(lambda c: label_pos[c][2])
    city["label"] = city.city.map(lambda c: label_pos[c][3])
    write_csv(city.sort_values("sales", ascending=False), "publisher_hq.csv")
    print(f"    mapped publishers cover {covered:.1%} of copies sold")

    # Export flows: where do games from each home market's publishers get sold?
    sub = df[df.Publisher.isin(HQ)].copy()
    sub["hub"] = sub.Publisher.map(lambda n: HQ[n][2])
    reg = sub.groupby("hub")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum()
    paths, points = [], []
    dest_code = {"NA_Sales": "NA", "EU_Sales": "EU", "JP_Sales": "JP"}
    for origin, r in reg.iterrows():
        total = r.sum()
        for col, dest in dest_code.items():
            share = r[col] / total
            if dest == origin:
                points.append({"origin": HUB_NAME[origin], "sales": round(r[col], 1), "share": round(share, 4),
                               "lat": HOME_POINT[origin][0], "lon": HOME_POINT[origin][1],
                               "other": round(r["Other_Sales"], 1), "other_share": round(r["Other_Sales"] / total, 4),
                               "total": round(total, 1)})
                continue
            # A curved, tapering path along the great circle (shortest route over the globe), bent to the right of
            # travel so the A->B and B->A paths do not overlap; wide at the publisher's home, narrow at the market.
            for i, (lat, lon) in enumerate(_arc(HOME_POINT[origin], HOME_POINT[dest])):
                t = i / N_STEPS
                paths.append({"origin": HUB_NAME[origin], "dest": HUB_NAME[dest], "step": i,
                              "lat": round(lat, 2), "lon": round(lon, 2),
                              "sales": round(r[col], 1), "share": round(share, 4),
                              "width": round(r[col] * (1 - 0.7 * t), 1)})
    write_csv(pd.DataFrame(paths), "flow_paths.csv")


def _xyz(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return [math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)]


def _arc(a, b, bend=0.12):
    """Points along the great circle from a to b (lat, lon), pushed sideways by up to `bend` radians."""
    p, q = _xyz(*a), _xyz(*b)
    omega = math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(p, q)))))
    n = [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]]
    norm = math.sqrt(sum(x * x for x in n))
    n = [x / norm for x in n]
    out = []
    for i in range(N_STEPS + 1):
        t = i / N_STEPS
        w0, w1 = math.sin((1 - t) * omega) / math.sin(omega), math.sin(t * omega) / math.sin(omega)
        v = [w0 * x + w1 * y - bend * math.sin(math.pi * t) * z for x, y, z in zip(p, q, n)]
        length = math.sqrt(sum(x * x for x in v))
        v = [x / length for x in v]
        out.append((math.degrees(math.asin(v[2])), math.degrees(math.atan2(v[1], v[0]))))
    return out


def regions(df):
    iso = pd.read_csv(RAW / "iso.csv", keep_default_na=False)
    def region(row):
        code = int(row["country-code"])
        if code in (840, 124):
            return "North America"
        if code == 392:
            return "Japan"
        if row["region"] == "Europe":
            return "Europe"
        return "Rest of world"
    iso["region"] = iso.apply(region, axis=1)
    iso["id"] = iso["country-code"].astype(int)
    write_csv(iso[["id", "name", "region"]], "country_region.csv")

    long = df.groupby("Genre")[list(REGIONS)].sum().rename(columns=REGIONS)
    share = long / long.sum()  # genre's share of each region's sales
    wide = share.T.add_prefix("share_")
    wide = wide.join(long.T.add_prefix("sales_"))
    wide["total"] = long.sum()
    wide.index.name = "region"
    write_csv(wide.reset_index(), "region_genre_wide.csv")

    era = df.groupby(["EraOrder", "EraYears", "EraName"])[list(REGIONS)].sum().rename(columns=REGIONS)
    era = era.stack().rename("sales").reset_index().rename(columns={"level_3": "region"})
    era["share"] = era.sales / era.groupby("EraOrder").sales.transform("sum")
    write_csv(era, "region_era.csv")


# ---------- Australian state boundaries: simplify, fix winding ----------

def _rdp(points, eps):
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        x0, y0 = points[i]
        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return _rdp(points[: idx + 1], eps)[:-1] + _rdp(points[idx:], eps)
    return [points[0], points[-1]]


def _area(ring):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:])) / 2


def _ring(ring, eps, clockwise):
    pts = _rdp(ring[:-1], eps) if ring[0] == ring[-1] else _rdp(ring, eps)
    pts = [[round(x, 3), round(y, 3)] for x, y in pts]
    if len(pts) < 3:
        return None
    pts.append(pts[0])
    # d3-geo (used by Vega) expects exterior rings clockwise, holes anticlockwise
    if (_area(pts) < 0) != clockwise:
        pts.reverse()
    return pts


def aus_states():
    src = json.loads((RAW / "aus_states.geojson").read_text())
    abbrev = {"New South Wales": "NSW", "Victoria": "VIC", "Queensland": "QLD", "South Australia": "SA",
              "Western Australia": "WA", "Tasmania": "TAS", "Northern Territory": "NT",
              "Australian Capital Territory": "ACT"}
    features = []
    for f in src["features"]:
        name = f["properties"]["STATE_NAME"]
        if name not in abbrev:
            continue
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        out = []
        for poly in polys:
            ext = poly[0]
            if abs(_area(ext)) < 0.02 and name != "Australian Capital Territory":
                continue  # drop tiny islands
            ring = _ring(ext, 0.02, clockwise=True)
            if ring:
                out.append([ring])
        features.append({"type": "Feature", "properties": {"name": name, "abbrev": abbrev[name]},
                         "geometry": {"type": "MultiPolygon", "coordinates": out}})
    (OUT / "geo" / "aus_states.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"  geo/aus_states.geojson      {len(features):5d} states, "
          f"{(OUT / 'geo' / 'aus_states.geojson').stat().st_size // 1024} KB")


def australia():
    # IGEA Australian Game Development Survey. FY2025: infographic "Location, location" (studios / employees).
    # FY2024: report p.8 table "Studio location / Full time employees".
    states = pd.DataFrame([
        # abbrev, name, capital, lat, lon, FY2025 studios %, FY2025 employees %, FY2024 studios %, FY2024 employees %
        ("VIC", "Victoria", "Melbourne", -37.81, 144.96, 27, 30, 28, 36),
        ("QLD", "Queensland", "Brisbane", -27.47, 153.03, 17, 27, 25, 27),
        ("NSW", "New South Wales", "Sydney", -33.87, 151.21, 17, 23, 15, 18),
        ("SA", "South Australia", "Adelaide", -34.93, 138.60, 8, 11, 6, 11),
        ("WA", "Western Australia", "Perth", -31.95, 115.86, 14, 8, 15, 6),
        ("ACT", "Australian Capital Territory", "Canberra", -35.28, 149.13, 2, 1, 3, 1),
        ("NT", "Northern Territory", "Darwin", -12.46, 130.84, 4, 1, 2, 1),
        ("TAS", "Tasmania", "Hobart", -42.88, 147.33, 2, 1, 2, 1),
    ], columns=["abbrev", "name", "capital", "lat", "lon", "studios_2025", "employees_2025",
                "studios_2024", "employees_2024"])
    # label positions near the middle of each state (ACT/TAS labels nudged offshore so they stay readable)
    label = {"VIC": (-37.05, 144.3), "QLD": (-22.5, 144.5), "NSW": (-32.2, 146.5), "SA": (-29.5, 135.5),
             "WA": (-25.5, 121.5), "ACT": (-36.2, 153.6), "NT": (-19.0, 133.5), "TAS": (-42.3, 150.6)}
    states["label_lat"] = states.abbrev.map(lambda a: label[a][0])
    states["label_lon"] = states.abbrev.map(lambda a: label[a][1])
    write_csv(states, "au_states.csv")

    # IGEA report "Key figures" (FY2016–FY2024) and FY2025 infographic. No survey was published for FY2018.
    industry = pd.DataFrame([
        ("FY2016", 2016, 114.8, 842, 63, ""),
        ("FY2017", 2017, 118.5, 928, 114, ""),
        ("FY2019", 2019, 143.5, 1275, 143, ""),
        ("FY2020", 2020, 184.6, 1245, 97, ""),
        ("FY2021", 2021, 226.5, 1327, 187, ""),
        ("FY2022", 2022, 284.4, 2104, 102, ""),
        ("FY2023", 2023, 345.5, 2458, 111, ""),
        ("FY2024", 2024, 339.1, 2465, 137, ""),
        ("FY2025", 2025, 608.5, 2443, 141, "New method: adds Sensor Tower sales data, not directly comparable"),
    ], columns=["fy", "year", "revenue_m", "employees", "studios_surveyed", "note"])
    write_csv(industry, "au_industry.csv")

    # IGEA "Australia Plays 2025" (media release, 8 Sep 2025): ages of Australians who play video games.
    write_csv(pd.DataFrame([
        ("Children", 1, 19), ("Working age", 2, 71), ("Retirement age", 3, 10),
    ], columns=["group", "order", "pct"]), "au_players_age.csv")


def main():
    print("Preparing data ...")
    df = load_sales()
    headline(df)
    maker_year(df)
    eras_table()
    platforms(df)
    genre_year(df)
    genre_tree(df)
    top_games(df)
    publisher_ranks(df)
    publisher_hq(df)
    regions(df)
    aus_states()
    australia()


if __name__ == "__main__":
    main()
