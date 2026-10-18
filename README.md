# Press Start: How Video Games Grew Up

A data story about 35 years of video games (1980–2015): the console eras, genres, publishers and markets that shaped the industry, and where Australia fits in today.

FIT3179 Data Visualisation 2 · Monash University · Semester 2, 2026 · Abdullah Javed

**Live page:** https://abdullahjaved2003.github.io/3179_S2_2026_08/
**Sketch:** [sketch/sketch.pdf](sketch/sketch.pdf)

## What's in the repo

| Path | Contents |
|---|---|
| `index.html`, `css/`, `js/` | The web page. `js/main.js` embeds each chart; `js/theme.json` is the shared chart style. |
| `specs/` | One readable JSON specification per chart: Vega-Lite (`.vl.json`) or Vega (`.vg.json`). |
| `data/` | Small summary files the charts load (about 300 KB in total). |
| `data/raw/` | Source files before processing. |
| `scripts/prepare_data.py` | Builds everything in `data/` from `data/raw/`. Run `python3 scripts/prepare_data.py` (needs pandas). |

## Charts

| # | Chart | Idiom | Spec |
|---|---|---|---|
| 1 | Copies sold by platform maker, 1980–2015 | Streamgraph | `makers_stream.vl.json` |
| 2 | Each platform's selling life | Timeline (Gantt), faceted | `platform_timeline.vl.json` |
| 3 | Genre share of each year's sales | Heatmap | `genre_heatmap.vl.json` |
| 4 | Genres split by publisher | Treemap (Vega) | `genre_treemap.vg.json` |
| 5 | Top ten games per era | Bar chart + era radio buttons | `top_games.vl.json` |
| 6 | Publisher rank by era | Bump chart | `publisher_bump.vl.json` |
| 7 | Publisher headquarters | Proportional symbol map (3 panels) | `publisher_hq_map.vl.json` |
| 8 | Where each region's publishers sell | Flow map (polar azimuthal projection) | `export_flows.vl.json` |
| 9 | Genre share by sales region | Choropleth map + genre menu | `genre_world_map.vl.json` |
| 10 | Where each era's copies were sold | 100% stacked bar | `region_eras.vl.json` |
| 11 | Ages of Australian players | Waffle chart (pictogram) | `au_players_waffle.vl.json` |
| 12 | Game development by Australian state | Choropleth map + measure toggle | `au_states_map.vl.json` |
| 13 | Studios vs employees by state | Dumbbell chart | `au_dumbbell.vl.json` |
| 14 | Australian studio revenue and staff | Bar + line (concatenated) | `au_industry.vl.json` |

## Data sources

- **Video game sales**: Gregory Smith, ["Video Game Sales"](https://www.kaggle.com/datasets/gregorut/videogamesales), Kaggle (2016), scraped from [VGChartz](https://www.vgchartz.com/). It covers games that sold more than 100,000 copies; 2016 and later are excluded because they were incomplete when scraped.
- **Australian game development**: IGEA & Bond University, [Australian Game Development Survey FY2024 report](https://igea.net/wp-content/uploads/2024/12/AGDS-2024-Report-Final.pdf) and [FY2025 snapshot](https://igea.net/wp-content/uploads/2026/03/AGD-2025-Standalone-Infographic.pdf).
- **Australian players**: IGEA & Bond University, *Australia Plays 2025* ([media release](https://igea.net/2025/09/australian-parents-embrace-the-power-of-play/)).
- **Maps**: [Natural Earth](https://www.naturalearthdata.com/) via [vega-datasets](https://github.com/vega/vega-datasets); [rowanhogan/australian-states](https://github.com/rowanhogan/australian-states); [ISO-3166 Countries with Regional Codes](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes).

Generative AI (Claude by Anthropic) helped write code, process data and edit text; all content was reviewed by the author.
