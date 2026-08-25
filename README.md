# FCS Fans thumbnail kit

Everything the weekly "FCS targets" task needs to render YouTube covers in the FCS Fans style.

* `make_thumbnails.py` — the generator (1280x720 PNG per game).
* `teams.json` — every 2026 FCS program: background color, wordmark text, nickname, logo file, ESPN id.
  Edit a color or point a team at a different logo file here.
* `logos/` — transparent PNG logos, one per team, named like `montana_state.png` (see `teams.json` -> `logo`).
  Populate it once: run `python3 download_logos.py` on your computer and upload the `logos/` folder,
  or use the Actions tab -> "Fetch logos" -> Run workflow (no local Python needed).
  West Florida has no ESPN logo yet; add `logos/west_florida.png` by hand if you have one.
* `badge/badge.png` — the FCS Fans badge (2026). Replace with your own transparent PNG any time.

Teams without a logo file get a bold text wordmark instead, so a missing logo never blocks a render.

Manual use:
```
python3 make_thumbnails.py games.json --out out --badge-pos right --left away
```
`games.json`: `[{"away": "Montana State", "home": "Utah Tech", "date": "2026-08-29"}]`
