#!/usr/bin/env python3
"""
FCS Fans thumbnail generator — reproduces Nick's "Team A vs Team B / date / FCS Fans" cover style.

Usage:
  python3 make_thumbnails.py games.json --out out/ [--kit .] [--badge-pos right|center] [--left away|home]

games.json: [{"away": "Montana State", "home": "Utah Tech", "date": "2026-08-29", "tier": "Must-do"}, ...]
Kit folder layout:
  teams.json        {"Team Name": {"color": "#RRGGBB", "logo": "file.png", "short": "MONTANA STATE", "nickname": "Bobcats"}}
  logos/<file>.png  transparent PNG logos (any size; fitted into a 400x400 box)
  badge/badge.png   the FCS Fans badge (transparent PNG). Missing -> a simple procedural badge is drawn.
  fonts/OpenSans-Regular.ttf, OpenSans-ExtraBold.ttf (fetched from GitHub if missing)
Teams missing from teams.json or without a logo file get a bold text wordmark on a color (gray if unknown).
"""
import argparse, json, os, re, sys, urllib.request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
SS = 2                                  # supersample factor for clean diagonal/rounded edges
DIAG_TOP_X, DIAG_BOT_X = 834, 466       # diagonal from (834,0) to (466,720), measured from Nick's samples
LOGO_BOX = 400                          # max logo side
LEFT_CENTER, RIGHT_CENTER = (310, 340), (990, 340)
VS_BOX = (549, 265, 730, 394)           # rounded rect, black @ 44% opacity
VS_RADIUS = 18
DATE_BASELINE_Y = 101
BADGE_POS = {"right": (973, 500), "center": (585, 492)}
FONT_URLS = {
    "OpenSans-Regular.ttf": "https://raw.githubusercontent.com/googlefonts/opensans/main/fonts/ttf/OpenSans-Regular.ttf",
    "OpenSans-ExtraBold.ttf": "https://raw.githubusercontent.com/googlefonts/opensans/main/fonts/ttf/OpenSans-ExtraBold.ttf",
}

def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def ensure_fonts(kit):
    fdir = os.path.join(kit, "fonts")
    os.makedirs(fdir, exist_ok=True)
    for name, url in FONT_URLS.items():
        p = os.path.join(fdir, name)
        if not os.path.exists(p):
            try:
                urllib.request.urlretrieve(url, p)
            except Exception as e:  # fall back to DejaVu below
                print(f"[warn] could not fetch {name}: {e}", file=sys.stderr)
    return fdir

def font(fdir, name, size):
    p = os.path.join(fdir, name)
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if "Bold" in name else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(fallback, size)

def load_teams(kit):
    p = os.path.join(kit, "teams.json")
    return json.load(open(p)) if os.path.exists(p) else {}

def find_logo(kit, team, info):
    cands = []
    if info and info.get("logo"):
        cands.append(info["logo"])
    cands += [slug(team) + ".png", slug(team) + ".PNG"]
    for c in cands:
        p = os.path.join(kit, "logos", c)
        if os.path.exists(p):
            return p
    return None

def fit(im, box):
    im = im.convert("RGBA")
    scale = min(box / im.width, box / im.height)
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)

def wordmark(team, info, fdir, box):
    """Fallback when no logo file exists: bold white team name (+ nickname) with a soft shadow."""
    name = (info or {}).get("short") or team.upper()
    nick = (info or {}).get("nickname", "")
    words = name.split()
    lines = [name]
    if len(name) > 12 and len(words) > 1:           # split long names into two balanced lines
        best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    size = 150
    while size > 30:
        f = font(fdir, "OpenSans-ExtraBold.ttf", size)
        widths = [f.getlength(l) for l in lines]
        if max(widths) <= box * 1.12:
            break
        size -= 4
    fn = font(fdir, "OpenSans-ExtraBold.ttf", max(32, int(size * 0.42))) if nick else None
    line_h = int(size * 1.15)
    total_h = line_h * len(lines) + (int(size * 0.75) if nick else 0)
    im = Image.new("RGBA", (int(box * 1.15), box), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = im.width
    y = (im.height - total_h) // 2
    for l in lines:
        for dx, dy in ((3, 3), (0, 0)):
            d.text((box / 2 + dx, y + dy), l, font=f, fill=(0, 0, 0, 140) if dx else "white", anchor="mt")
        y += line_h
    if nick:
        d.text((box / 2, y + 4), nick.upper(), font=fn, fill=(255, 255, 255, 230), anchor="mt")
    return im

def procedural_badge(fdir, year):
    """Simple stand-in for the FCS Fans badge if badge/badge.png isn't in the kit."""
    s = 4
    im = Image.new("RGBA", (289 * s, 221 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fb = font(fdir, "OpenSans-ExtraBold.ttf", 34 * s)
    d.text((145 * s, 8 * s), "F C S", font=fb, fill="black", anchor="mt")
    # ribbon with swallowtail ends
    d.polygon([(0, 112 * s), (289 * s, 112 * s), (289 * s, 160 * s), (0, 160 * s)], fill="black")
    d.polygon([(0, 112 * s), (14 * s, 136 * s), (0, 160 * s)], fill=(0, 0, 0, 0))
    d.polygon([(289 * s, 112 * s), (275 * s, 136 * s), (289 * s, 160 * s)], fill=(0, 0, 0, 0))
    fy = font(fdir, "OpenSans-ExtraBold.ttf", 21 * s)
    d.text((44 * s, 136 * s), str(year)[:2], font=fy, fill="white", anchor="mm")
    d.text((245 * s, 136 * s), str(year)[2:], font=fy, fill="white", anchor="mm")
    # football
    d.ellipse((56 * s, 62 * s, 234 * s, 162 * s), fill=(150, 75, 30), outline="black", width=5 * s)
    d.rectangle((88 * s, 62 * s, 100 * s, 162 * s), fill="white")
    d.rectangle((190 * s, 62 * s, 202 * s, 162 * s), fill="white")
    d.line((120 * s, 84 * s, 170 * s, 84 * s), fill="white", width=4 * s)
    for x in range(124, 168, 8):
        d.line((x * s, 76 * s, x * s, 92 * s), fill="white", width=3 * s)
    import math
    cx, cy, r = 145 * s, 118 * s, 18 * s
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill="black")
    d.polygon([(80 * s, 168 * s), (209 * s, 168 * s), (200 * s, 221 * s), (89 * s, 221 * s)], fill="black")
    d.text((145 * s, 194 * s), "FANS", font=font(fdir, "OpenSans-ExtraBold.ttf", 26 * s), fill="white", anchor="mm")
    return im.resize((289, 221), Image.LANCZOS)

def render(game, teams, kit, fdir, badge, badge_pos, left_side):
    away, home, date = game["away"], game["home"], game["date"]
    left, right = (away, home) if left_side == "away" else (home, away)
    li, ri = teams.get(left), teams.get(right)
    lc = hex_to_rgb((li or {}).get("color", "#3a3a3a"))
    rc = hex_to_rgb((ri or {}).get("color", "#5a5a5a"))
    if lc == rc:                                   # same-color matchup: darken the right side a bit
        rc = tuple(max(0, int(c * 0.6)) for c in rc)

    im = Image.new("RGB", (W * SS, H * SS), rc)
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(0, 0), (DIAG_TOP_X * SS, 0), (DIAG_BOT_X * SS, H * SS), (0, H * SS)], fill=lc)

    # date
    dt = datetime.strptime(date, "%Y-%m-%d")
    d.text((W / 2 * SS, DATE_BASELINE_Y * SS), dt.strftime("%m-%d-%y"), font=font(fdir, "OpenSans-Regular.ttf", 66 * SS), fill="white", anchor="ms")

    # logos / wordmarks
    for team, info, center in ((left, li, LEFT_CENTER), (right, ri, RIGHT_CENTER)):
        lp = find_logo(kit, team, info)
        art = fit(Image.open(lp), LOGO_BOX * SS) if lp else wordmark(team, info, fdir, LOGO_BOX * SS)
        im.paste(art, (center[0] * SS - art.width // 2, center[1] * SS - art.height // 2), art)

    # VS badge (translucent black rounded rect + text)
    x0, y0, x1, y1 = [v * SS for v in VS_BOX]
    d.rounded_rectangle((x0, y0, x1, y1), radius=VS_RADIUS * SS, fill=(0, 0, 0, 112))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 + 2 * SS), "VS", font=font(fdir, "OpenSans-Regular.ttf", 80 * SS), fill="white", anchor="mm")

    # FCS Fans badge
    if badge is not None:
        b = badge.resize((badge.width * SS, badge.height * SS), Image.LANCZOS)
        bx, by = BADGE_POS[badge_pos]
        im.paste(b, (bx * SS, by * SS), b)

    out = im.resize((W, H), Image.LANCZOS)
    fname = f"{slug(away)}_at_{slug(home)}_{dt.strftime('%m-%d-%y')}.png"
    return out, fname

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("--out", default="out")
    ap.add_argument("--kit", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--badge-pos", choices=["right", "center"], default="right")
    ap.add_argument("--left", choices=["away", "home"], default="away", help="which team goes on the left half")
    ap.add_argument("--year", type=int, default=None, help="season year for the procedural badge fallback")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    fdir = ensure_fonts(a.kit)
    teams = load_teams(a.kit)
    games = json.load(open(a.games))
    bp = os.path.join(a.kit, "badge", "badge.png")
    year = a.year or datetime.strptime(games[0]["date"], "%Y-%m-%d").year
    badge = Image.open(bp).convert("RGBA") if os.path.exists(bp) else procedural_badge(fdir, year)

    manifest = []
    for g in games:
        img, fname = render(g, teams, a.kit, fdir, badge, a.badge_pos, g.get("left", a.left))
        path = os.path.join(a.out, fname)
        img.save(path, optimize=True)
        missing = [t for t in (g["away"], g["home"]) if not find_logo(a.kit, t, teams.get(t))]
        manifest.append({"file": fname, "tier": g.get("tier", ""), "missing_logos": missing})
        print(f"{fname}  {'(wordmark fallback: ' + ', '.join(missing) + ')' if missing else ''}")
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
