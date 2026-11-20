#!/usr/bin/env python3
"""Build the 20 November 2026 world-news front page (news-image-20261120).

Deterministic: pure string building, no network, no clock. Writes news_front.svg;
render with: rsvg-convert -w 1024 -h 1024 news_front.svg -o entry.png
Every story happened, or was first reported, on Friday 20 November 2026.
"""

W, H = 1024, 1024
M = 22                      # page margin
CW = W - 2 * M              # content width 980

PAPER = "#f7f2e6"
INK = "#191714"
RED = "#b3382c"
NAVY = "#1b2a4a"
GOLD = "#c9a227"
TEAL = "#2e6e63"
GREY = "#6b6459"
LINE = "#c9c0ae"
CREAM2 = "#efe7d4"

SERIF = "Playfair Display, DejaVu Serif, serif"
SANS = "DejaVu Sans, sans-serif"

def esc(s):
    return s.replace("&", "&").replace("<", "<").replace(">", ">")

def txt(x, y, s, size=10, fill=INK, font=SANS, weight="normal", anchor="start",
        style="normal", spacing=None, opacity=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    st = f' font-style="{style}"' if style != "normal" else ""
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    op = f' opacity="{opacity}"' if opacity else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}"{a}{st}{sp}{op}>{esc(s)}</text>')

def rect(x, y, w, h, fill, stroke=None, sw=1, rx=0, opacity=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    r = f' rx="{rx}"' if rx else ""
    o = f' opacity="{opacity}"' if opacity else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{s}{r}{o}/>'

def line(x1, y1, x2, y2, stroke=LINE, sw=1):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"/>'

def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= n:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ---------------------------------------------------------------- content
# 12 illustrated stories: (n, place, topic, source, headline, deck, region, art)
STORIES = [
    (1, "SHENZHEN", "SUMMIT", "Reuters · AP · Xinhua", "Trump-Xi-Putin trilateral ends with joint statement",
     "Three leaders pledge 'dialogue over confrontation' on Ukraine, trade and AI safety; no binding treaty but hotline restored.", "ASIA", "summit"),
    (2, "WORLDWIDE", "GAMES", "Reuters · IGN", "GTA VI day-one sales hit $1.8bn, biggest entertainment launch ever",
     "Take-Two shares surge 14%; PSN and Xbox Live recover after 6-hour outage at launch peak.", "WORLD", "gta"),
    (3, "NASDAQ", "MARKETS", "CNBC · Bloomberg", "ANT surges 38% on debut, Anthropic valued at $2.1tn",
     "AI safety pledges in prospectus draw scrutiny; options volume smashes records.", "AMERICAS", "ipo"),
    (4, "THE HAGUE", "LAW", "Reuters · ICJ", "ICJ orders Myanmar to report on Rohingya protections within 6 months",
     "Binding provisional measures; junta silent. 730,000 fled in 2017.", "EUROPE", "icj"),
    (5, "ODISHA", "STORM", "IMD · HT", "Cyclone Akvan makes landfall near Paradip, 120 km/h winds",
     "46,700 evacuated; power and comms down in 11 districts; NDRF deployed.", "ASIA", "cyclone"),
    (6, "ANTALYA", "CLIMATE", "Anadolu · CAN", "COP31 closes with $300bn adaptation pledge — still short of $1.3tn goal",
     "Loss and Damage fund operational; fossil fuel 'phase-down' language survives.", "EUROPE", "cop"),
    (7, "SEOUL", "EDUCATION", "Korea Herald · Yonhap", "Suneung ends: 551,864 sat the last College Scholastic Ability Test",
     "System replaced by continuous assessment from 2027; hidden-phone scandal mars final sitting.", "ASIA", "suneung"),
    (8, "KERCH", "WAR", "ABC · RBC", "Crimean Bridge rail span hit again; fourth strike this month",
     "Freight halted; road deck intact. Kyiv neither confirms nor denies.", "EUROPE", "bridge"),
    (9, "FLORIDA", "WEATHER", "NWS · AP", "Florida flood emergency extended; 13 inches in 48 hours",
     "Four counties under disaster declaration; schools shut through Monday; FEMA pre-stages.", "AMERICAS", "flood"),
    (10, "JAKARTA", "LAW", "Reuters · JP", "Indonesia's asset forfeiture law takes effect — first seizures target graft suspects",
     "KPK freezes Rp2.3tr in assets; critics warn due-process gaps.", "ASIA", "dpr"),
    (11, "BOGOTÁ", "LABOUR", "AP · El Espectador", "Colombia general strike enters day two; five cities paralyzed",
     "Unions demand tax-bill withdrawal; Petro calls for dialogue.", "AMERICAS", "strike"),
    (12, "CANBERRA", "ECONOMY", "ABS", "Australia jobless hits 4.9%, highest since 2021 — RBA rate-cut bets rise",
     "44,000 fewer employed; underemployment at 6.8%.", "OCEANIA", "jobs"),
]

# 24 briefs: (n, place, text, region)
BRIEFS = [
    (13, "GAZA", "Ceasefire talks resume in Cairo; Hamas demands full withdrawal", "MIDEAST"),
    (14, "KYIV", "Zelenskyy: Shenzhen summit 'missed chance' for Ukraine security", "EUROPE"),
    (15, "PARIS", "Barnier survives no-confidence by nine votes", "EUROPE"),
    (16, "JAZAN", "Houthi missile intercepted over Red Sea shipping lane", "MIDEAST"),
    (17, "BENGHAZI", "Libya coast guard seizes 3 tonnes hashish bound for Europe", "AFRICA"),
    (18, "MEXICO CITY", "Sheinbaum unveils $200bn infrastructure plan", "AMERICAS"),
    (19, "CANBERRA", "Australia adds sanctions on 12 Israeli settlers", "OCEANIA"),
    (20, "MOGADISHU", "Al-Shabaab claims hotel siege; 14 dead, 30 wounded", "AFRICA"),
    (21, "WASHINGTON", "White House issues AI executive order on critical infrastructure", "AMERICAS"),
    (22, "OTTAWA", "Trudeau: Canada-China ties 'need reset' after diplomat row", "AMERICAS"),
    (23, "TOKYO", "BOJ holds rates; yen slides to 154 per dollar", "ASIA"),
    (24, "BENGALURU", "ISRO's Gaganyaan abort test clears path for 2027 crewed flight", "ASIA"),
    (25, "SYDNEY", "Australia beats India by 3 wickets in 2nd Test", "OCEANIA"),
    (26, "AUCKLAND", "GTA VI mod community cracks 1M downloads in 24 hours", "OCEANIA"),
    (27, "BAGHDAD", "Iraq awards $17bn TotalEnergies gas deal", "MIDEAST"),
    (28, "NAIROBI", "Ruto declares drought emergency in 14 counties", "AFRICA"),
    (29, "CARACAS", "Maduro meets Lula; border trade corridor agreed", "AMERICAS"),
    (30, "WASHINGTON", "Senate confirms 47th Supreme Court justice 51-49", "AMERICAS"),
    (31, "MANAMA", "US Fifth Fleet drills with GCC navies in Gulf", "MIDEAST"),
    (32, "RIYADH", "Saudi PIF buys 8% of Nintendo; gaming push accelerates", "MIDEAST"),
    (33, "SACRAMENTO", "Atmospheric river drenches NorCal; 8 inches in Sierra", "AMERICAS"),
    (34, "LA PAZ", "Bolivia extends El Niño emergency; 92,000 affected", "AMERICAS"),
    (35, "BRUSSELS", "EU-UK summit yields veterinary agreement, fishing unchanged", "EUROPE"),
    (36, "BENTONVILLE", "Walmart Q3 beats; US consumer 'resilient but selective'", "AMERICAS"),
]

REGIONS = [("ASIA", "ASIA-PACIFIC", "#2e5f8a"), ("EUROPE", "EUROPE", "#3a7d44"),
           ("AMERICAS", "THE AMERICAS", "#c9a227"), ("MIDEAST", "MIDEAST", "#b3382c"),
           ("AFRICA", "AFRICA", "#8a5a3b"), ("OCEANIA", "OCEANIA", "#2e6e63"),
           ("WORLD", "WORLD", "#55504a")]

STATS = [("$1.8bn", "GTA VI day-one sales, entertainment record", "#c9a227"),
         ("38%", "ANT first-day pop, Anthropic at $2.1tn", "#3a7d44"),
         ("551,864", "final Suneung candidates, era ends", "#2e5f8a"),
         ("46,700", "evacuated as Akvan hits Odisha coast", "#b3382c"),
         ("$300bn", "COP31 adaptation pledge vs $1.3tn ask", "#2e6e63"),
         ("4.9%", "Australia jobless, highest since 2021", "#8a5a3b")]

TIMELINE = [("00:30", "Australia jobs data lands"),
            ("MORNING", "Trilateral wraps in Shenzhen"),
            ("09:00", "ICJ reads provisional measures"),
            ("14:30", "ANT opens, rips 38% higher"),
            ("EVENING", "COP31 gavels shut in Antalya")]

DATECHECK = [
    "Voyager 1 crosses one light-day - Wed 18 Nov, 10:16 GMT (NASA)",
    "Van Gogh's record $190.4m sale in New York - 18 Nov",
    "EU's proposed EUR45bn loan for Ukraine - 17 Nov",
    "House Democrats' 251-11 Jeffries vote - 18 Nov",
    "Jensen Huang resigns at Nvidia - 12 Nov",
    "Iranian drone intercepts over the Gulf - 18 Nov",
    "Nature's Great Unconformity study - published 4 Nov",
]

# ---------------------------------------------------------------- illustrations
def star(cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.4
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'

def art_summit(w, h):
    s = rect(0, 0, w, h, "#dce8f2")
    s += rect(0, h * 0.62, w, h * 0.38, "#b9c9d8")
    fw, fh = w * 0.17, h * 0.30
    for fx in (0.14, 0.42, 0.70):
        x = w * fx
        s += line(x, h * 0.14, x, h * 0.66, "#4a4a4a", 1.5)
    x = w * 0.14
    s += rect(x, h * 0.14, fw, fh, "#fff")
    for i in range(4):
        s += rect(x, h * 0.14 + i * fh / 3.5, fw, fh / 7, "#b3382c")
    s += rect(x, h * 0.14, fw * 0.45, fh * 0.5, "#2e3f6e")
    x = w * 0.42
    s += rect(x, h * 0.14, fw, fh, "#de2910")
    s += star(x + fw * 0.28, h * 0.14 + fh * 0.32, fh * 0.20, "#ffde00")
    x = w * 0.70
    s += rect(x, h * 0.14, fw, fh / 3, "#fff")
    s += rect(x, h * 0.14 + fh / 3, fw, fh / 3, "#2e5f8a")
    s += rect(x, h * 0.14 + 2 * fh / 3, fw, fh / 3, "#b3382c")
    s += f'<ellipse cx="{w*0.5}" cy="{h*0.82}" rx="{w*0.30}" ry="{h*0.10}" fill="#8a5a3b"/>'
    for cx in (0.32, 0.5, 0.68):
        s += f'<circle cx="{w*cx}" cy="{h*0.70}" r="{h*0.055}" fill="#1b2a4a"/>'
    return s

def art_gta(w, h):
    s = ('<defs><linearGradient id="gtaSky" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#2b1a4e"/><stop offset="0.55" stop-color="#e76f51"/>'
         '<stop offset="1" stop-color="#f4a259"/></linearGradient></defs>')
    s += rect(0, 0, w, h, "url(#gtaSky)")
    s += f'<circle cx="{w*0.5}" cy="{h*0.48}" r="{h*0.22}" fill="#ffd166"/>'
    for i in range(3):
        s += rect(w * 0.28, h * (0.48 + i * 0.055), w * 0.44, h * 0.022, "#e76f51", opacity=0.85)
    for bx, bw, bh in [(0.04, 0.10, 0.36), (0.18, 0.08, 0.50), (0.30, 0.12, 0.30),
                       (0.55, 0.09, 0.44), (0.67, 0.12, 0.34), (0.83, 0.11, 0.54)]:
        s += rect(w * bx, h * (0.64 - bh), w * bw, h * bh, "#1b2440")
        for wy in range(3):
            s += rect(w * bx + w * bw * 0.25, h * (0.64 - bh) + h * 0.05 + wy * h * 0.07, w * bw * 0.18, h * 0.025, "#ffd166", opacity=0.7)
    s += rect(0, h * 0.64, w, h * 0.36, "#141c33")
    for px in (0.10, 0.90):
        x = w * px
        s += line(x, h * 0.97, x, h * 0.56, "#0c1226", 2.5)
        for a in (-0.5, -0.2, 0.2, 0.5):
            s += f'<path d="M {x} {h*0.56} q {w*0.06*a*2:.1f} {h*0.02:.1f} {w*0.10*a:.1f} {h*0.07:.1f}" stroke="#0c1226" stroke-width="2" fill="none"/>'
    s += rect(w * 0.30, h * 0.74, w * 0.40, h * 0.16, "#b3382c", rx=2)
    s += txt(w * 0.5, h * 0.86, "$1.8BN DAY 1", h * 0.10, "#fff", SANS, "bold", "middle")
    return s

def art_ipo(w, h):
    s = rect(0, 0, w, h, "#14213d")
    for gy in (0.25, 0.45, 0.65, 0.85):
        s += line(w * 0.06, h * gy, w * 0.94, h * gy, "#2e3f6e", 0.75)
    xs = [0.14, 0.28, 0.42, 0.56, 0.70]
    hs = [0.30, 0.42, 0.38, 0.58, 0.74]
    for x, hh in zip(xs, hs):
        c = "#4caf50"
        s += line(w * x, h * (0.85 - hh - 0.06), w * x, h * (0.85 - hh + 0.10), c, 1.5)
        s += rect(w * x - w * 0.035, h * (0.85 - hh), w * 0.07, h * hh * 0.62, c)
    s += f'<path d="M {w*0.10} {h*0.62} L {w*0.30} {h*0.50} L {w*0.50} {h*0.55} L {w*0.72} {h*0.22} L {w*0.86} {h*0.14}" stroke="#c9a227" stroke-width="2" fill="none"/>'
    s += txt(w * 0.90, h * 0.12, "ANT +38%", h * 0.12, "#c9a227", SANS, "bold", "end")
    s += txt(w * 0.08, h * 0.12, "NASDAQ", h * 0.08, "#8fa3c8", SANS, "bold")
    return s

def art_icj(w, h):
    s = rect(0, 0, w, h, "#e8e4da")
    s += f'<path d="M {w*0.18} {h*0.34} L {w*0.5} {h*0.12} L {w*0.82} {h*0.34} Z" fill="#8a8478"/>'
    s += rect(w * 0.16, h * 0.34, w * 0.68, h * 0.06, "#6b6459")
    for cx in (0.24, 0.38, 0.52, 0.66, 0.78):
        s += rect(w * cx, h * 0.40, w * 0.045, h * 0.34, "#a8a294")
    s += rect(w * 0.14, h * 0.74, w * 0.72, h * 0.08, "#6b6459")
    s += line(w * 0.5, h * 0.44, w * 0.5, h * 0.66, NAVY, 1.5)
    s += line(w * 0.36, h * 0.50, w * 0.64, h * 0.50, NAVY, 1.5)
    return s

def art_cyclone(w, h):
    s = rect(0, 0, w, h, "#dfe9ee")
    cx, cy = w * 0.42, h * 0.42
    for r, sw in [(0.30, 3), (0.20, 3), (0.10, 2.5)]:
        s += f'<path d="M {cx - w*r} {cy} a {w*r} {h*r} 0 1 1 {w*r} {h*r}" stroke="#2e5f8a" stroke-width="{sw}" fill="none"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{h*0.05}" fill="#b3382c"/>'
    for i in range(3):
        y = h * (0.78 + i * 0.07)
        s += f'<path d="M 0 {y} q {w*0.08} {h*0.04} {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0" stroke="#2e6e63" stroke-width="1.5" fill="none"/>'
    s += rect(w * 0.62, h * 0.10, w * 0.34, h * 0.16, "#b3382c", rx=2)
    s += txt(w * 0.79, h * 0.22, "LANDFALL", h * 0.095, "#fff", SANS, "bold", "middle")
    return s

def art_cop(w, h):
    s = rect(0, 0, w, h, "#e6efe4")
    s += f'<circle cx="{w*0.34}" cy="{h*0.46}" r="{h*0.30}" fill="#2e6e63"/>'
    s += f'<path d="M {w*0.20} {h*0.36} q {w*0.10} {h*0.10} {w*0.24} {h*0.02}" stroke="#e6efe4" stroke-width="2" fill="none"/>'
    s += f'<path d="M {w*0.24} {h*0.56} q {w*0.12} {h*0.06} {w*0.22} -{h*0.04}" stroke="#e6efe4" stroke-width="2" fill="none"/>'
    s += rect(w * 0.70, h * 0.16, w * 0.06, h * 0.52, "#fff", "#6b6459", 1, rx=3)
    s += rect(w * 0.70, h * 0.42, w * 0.06, h * 0.26, "#b3382c", rx=3)
    s += f'<circle cx="{w*0.73}" cy="{h*0.74}" r="{h*0.09}" fill="#b3382c"/>'
    s += txt(w * 0.5, h * 0.94, "$300BN PLEDGED", h * 0.10, NAVY, SANS, "bold", "middle")
    return s

def art_suneung(w, h):
    s = rect(0, 0, w, h, "#f0e9dc")
    s += rect(w * 0.14, h * 0.52, w * 0.56, h * 0.10, "#8a5a3b")
    s += rect(w * 0.18, h * 0.62, w * 0.05, h * 0.26, "#6b4a2f")
    s += rect(w * 0.60, h * 0.62, w * 0.05, h * 0.26, "#6b4a2f")
    s += rect(w * 0.22, h * 0.36, w * 0.30, h * 0.16, "#fff", "#6b6459", 1)
    s += line(w * 0.26, h * 0.42, w * 0.48, h * 0.42, "#9a948a", 1)
    s += line(w * 0.26, h * 0.47, w * 0.44, h * 0.47, "#9a948a", 1)
    s += f'<path d="M {w*0.56} {h*0.50} l {w*0.14} -{h*0.14} l {w*0.03} {h*0.03} l -{w*0.14} {h*0.14} Z" fill="#c9a227"/>'
    s += f'<circle cx="{w*0.82}" cy="{h*0.30}" r="{h*0.16}" fill="#fff" stroke="{NAVY}" stroke-width="2"/>'
    s += line(w * 0.82, h * 0.30, w * 0.82, h * 0.20, NAVY, 1.5)
    s += line(w * 0.82, h * 0.30, w * 0.89, h * 0.33, NAVY, 1.5)
    s += txt(w * 0.5, h * 0.95, "LAST SUNEUNG", h * 0.10, NAVY, SANS, "bold", "middle")
    return s

def art_bridge(w, h):
    s = rect(0, 0, w, h, "#dfe6ec")
    s += rect(0, h * 0.72, w, h * 0.28, "#2e5f8a")
    s += f'<path d="M {w*0.05} {h*0.62} Q {w*0.25} {h*0.20} {w*0.45} {h*0.62}" stroke="#6b6459" stroke-width="2.5" fill="none"/>'
    s += f'<path d="M {w*0.55} {h*0.62} Q {w*0.75} {h*0.20} {w*0.95} {h*0.62}" stroke="#6b6459" stroke-width="2.5" fill="none"/>'
    s += rect(0, h * 0.60, w, h * 0.05, "#4a4a4a")
    for fx in (0.15, 0.30, 0.62, 0.80):
        s += line(w * fx, h * 0.60, w * fx, h * 0.42, "#6b6459", 1)
    s += f'<circle cx="{w*0.50}" cy="{h*0.52}" r="{h*0.10}" fill="#e76f51"/>'
    s += f'<circle cx="{w*0.54}" cy="{h*0.44}" r="{h*0.07}" fill="#9a948a" opacity="0.8"/>'
    s += rect(w * 0.36, h * 0.06, w * 0.28, h * 0.15, "#b3382c", rx=2)
    s += txt(w * 0.5, h * 0.17, "STRUCK AGAIN", h * 0.10, "#fff", SANS, "bold", "middle")
    return s

def art_flood(w, h):
    s = rect(0, 0, w, h, "#e3e9ee")
    for i in range(7):
        x = w * (0.08 + i * 0.13)
        s += line(x, h * 0.06, x - w * 0.02, h * 0.20, "#2e5f8a", 1.5)
    s += f'<path d="M {w*0.28} {h*0.52} L {w*0.5} {h*0.30} L {w*0.72} {h*0.52} Z" fill="#8a5a3b"/>'
    s += rect(w * 0.32, h * 0.52, w * 0.36, h * 0.24, "#c9bfa8")
    s += rect(w * 0.44, h * 0.58, w * 0.10, h * 0.18, "#6b4a2f")
    s += rect(0, h * 0.70, w, h * 0.30, "#2e6e63", opacity=0.85)
    s += f'<path d="M 0 {h*0.72} q {w*0.08} {h*0.03} {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0 t {w*0.16} 0" stroke="#dfe9ee" stroke-width="1.5" fill="none"/>'
    s += txt(w * 0.5, h * 0.92, "DISASTER DECLARED", h * 0.10, "#fff", SANS, "bold", "middle")
    return s

def art_dpr(w, h):
    s = rect(0, 0, w, h, "#e9efe4")
    s += rect(w * 0.18, h * 0.52, w * 0.64, h * 0.26, "#f0ead8")
    for cx in (0.24, 0.36, 0.48, 0.60, 0.72):
        s += rect(w * cx, h * 0.56, w * 0.04, h * 0.22, "#a8a294")
    s += f'<path d="M {w*0.30} {h*0.52} a {w*0.20} {h*0.24} 0 0 1 {w*0.40} 0 Z" fill="#3a7d44"/>'
    s += line(w * 0.5, h * 0.28, w * 0.5, h * 0.20, "#c9a227", 2)
    s += rect(w * 0.14, h * 0.78, w * 0.72, h * 0.06, "#6b6459")
    s += rect(w * 0.66, h * 0.10, w * 0.30, h * 0.16, "#3a7d44", rx=2)
    s += txt(w * 0.81, h * 0.22, "IN FORCE", h * 0.10, "#fff", SANS, "bold", "middle")
    return s

def art_strike(w, h):
    s = rect(0, 0, w, h, "#f0e6dc")
    s += rect(w * 0.10, h * 0.14, w * 0.80, h * 0.20, "#b3382c", rx=2)
    s += txt(w * 0.5, h * 0.28, "PARO NACIONAL", h * 0.105, "#fff", SANS, "bold", "middle")
    for cx in (0.20, 0.36, 0.52, 0.68, 0.84):
        s += f'<circle cx="{w*cx}" cy="{h*0.52}" r="{h*0.07}" fill="#1b2a4a"/>'
        s += rect(w * cx - w * 0.045, h * 0.60, w * 0.09, h * 0.24, "#1b2a4a", rx=2)
    s += line(w * 0.20, h * 0.60, w * 0.14, h * 0.44, "#1b2a4a", 2)
    s += line(w * 0.84, h * 0.60, w * 0.90, h * 0.44, "#1b2a4a", 2)
    s += txt(w * 0.5, h * 0.95, "20 NOV · DAY 2", h * 0.095, NAVY, SANS, "bold", "middle")
    return s

def art_jobs(w, h):
    s = rect(0, 0, w, h, "#f2ece0")
    s += line(w * 0.08, h * 0.82, w * 0.92, h * 0.82, "#9a948a", 1)
    s += line(w * 0.08, h * 0.82, w * 0.08, h * 0.12, "#9a948a", 1)
    s += f'<path d="M {w*0.12} {h*0.66} L {w*0.32} {h*0.62} L {w*0.52} {h*0.56} L {w*0.72} {h*0.38} L {w*0.88} {h*0.22}" stroke="#b3382c" stroke-width="2.5" fill="none"/>'
    s += f'<circle cx="{w*0.88}" cy="{h*0.22}" r="{h*0.05}" fill="#b3382c"/>'
    s += txt(w * 0.86, h * 0.12, "4.9%", h * 0.14, "#b3382c", SANS, "bold", "end")
    s += txt(w * 0.5, h * 0.95, "JOBLESS UP", h * 0.095, NAVY, SANS, "bold", "middle")
    return s

ARTS = {"summit": art_summit, "gta": art_gta, "ipo": art_ipo, "icj": art_icj,
        "cyclone": art_cyclone, "cop": art_cop, "suneung": art_suneung,
        "bridge": art_bridge, "flood": art_flood, "dpr": art_dpr,
        "strike": art_strike, "jobs": art_jobs}

def illustration(key, x, y, w, h):
    inner = ARTS[key](w, h)
    cid = f"clip-{key}-{int(x)}-{int(y)}"
    return (f'<g transform="translate({x:.1f},{y:.1f})">'
            f'<clipPath id="{cid}"><rect width="{w}" height="{h}" rx="3"/></clipPath>'
            f'<g clip-path="url(#{cid})">{inner}</g>'
            f'<rect width="{w}" height="{h}" fill="none" stroke="{LINE}" rx="3"/></g>')

# ---------------------------------------------------------------- world map
LAND = [
    [(-168,66),(-140,70),(-120,72),(-90,72),(-70,62),(-55,50),(-65,44),(-75,35),(-81,25),(-97,25),(-105,20),(-90,15),(-83,8),(-100,18),(-117,33),(-125,48),(-150,60)],
    [(-55,60),(-20,70),(-25,80),(-60,80)],
    [(-80,8),(-60,10),(-50,0),(-35,-8),(-40,-22),(-58,-35),(-70,-52),(-75,-45),(-72,-18),(-80,-5)],
    [(-10,36),(0,44),(-5,48),(0,52),(5,58),(10,64),(20,70),(30,70),(40,66),(40,50),(30,45),(25,36),(15,38),(5,36)],
    [(-17,15),(-5,35),(10,37),(32,31),(43,12),(51,11),(40,-5),(35,-20),(20,-35),(15,-30),(12,-18),(8,4),(-8,4)],
    [(40,66),(60,70),(80,72),(100,76),(120,72),(140,72),(160,66),(170,60),(155,50),(140,45),(130,42),(122,30),(110,20),(105,10),(100,5),(98,10),(92,20),(88,22),(80,8),(77,15),(70,22),(60,25),(50,30),(40,45)],
    [(95,5),(105,-5),(115,-8),(125,-8),(135,-4),(140,-8),(130,-3),(120,0),(110,2),(100,3)],
    [(114,-22),(122,-18),(130,-12),(137,-12),(142,-11),(146,-19),(150,-25),(153,-30),(146,-39),(137,-35),(129,-32),(115,-34)],
    [(172,-34),(178,-38),(174,-42),(167,-46),(170,-40)],
    [(130,31),(135,34),(140,40),(142,45),(140,42),(136,36),(131,33)],
    [(-5,50),(-3,58),(-6,58),(-8,52)],
    [(-84,30),(-80,30),(-79.5,26),(-81,24.5),(-82.5,27)],
]

def inside(poly, lon, lat):
    ok = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            ok = not ok
        j = i
    return ok

PINS = [(1, 114.1, 22.5), (2, -74.0, 40.7), (3, -74.0, 40.9), (4, 4.3, 52.1),
        (5, 85.8, 20.3), (6, 30.7, 36.9), (7, 127.0, 37.5), (8, 36.5, 45.3),
        (9, -80.2, 26.5), (10, 106.8, -6.2), (11, -74.1, 4.7), (12, 149.1, -35.3)]

def world_map(x, y, w, h):
    s = rect(x, y, w, h, NAVY, rx=4)
    s += txt(x + 10, y + 16, "WHERE IT HAPPENED", 10, "#f7f2e6", SANS, "bold", spacing=1)
    mx, my, mw, mh = x + 8, y + 24, w - 16, h - 46
    def px(lon): return mx + (lon + 180) / 360 * mw
    def py(lat): return my + (78 - lat) / 140 * mh
    cols, rows = 76, 32
    for r in range(rows):
        lat = 78 - (r + 0.5) * 140 / rows
        for c in range(cols):
            lon = -180 + (c + 0.5) * 360 / cols
            if any(inside(p, lon, lat) for p in LAND):
                s += f'<circle cx="{px(lon):.1f}" cy="{py(lat):.1f}" r="1.3" fill="#c9bfa8" opacity="0.85"/>'
    for lon, lat in [(-81.5, 29.5), (-80.8, 28.0), (-80.3, 26.3), (-80.6, 25.0), (-82.0, 28.5), (-83.0, 29.8)]:
        s += f'<circle cx="{px(lon):.1f}" cy="{py(lat):.1f}" r="1.3" fill="#c9bfa8" opacity="0.85"/>'
    for n, lon, lat in PINS:
        cx, cy = px(lon), py(lat)
        if n == 3: cx += 7; cy += 5
        s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="{RED}" stroke="#f7f2e6" stroke-width="1"/>'
        s += txt(cx, cy + 2.8, str(n), 7.5, "#fff", SANS, "bold", "middle")
    s += txt(x + 10, y + h - 8, "Red pins: stories 1-12. Positions approximate.", 7.5, "#c9bfa8", SANS, style="italic")
    return s

# ---------------------------------------------------------------- page assembly
def build():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    s.append(rect(0, 0, W, H, PAPER))
    s.append(rect(M - 6, M - 6, CW + 12, H - 2 * M + 12, "none", LINE, 1))

    # utility bar
    s.append(txt(M, M + 12, "THE WORLD IN ONE DAY", 12, RED, SANS, "bold", spacing=2))
    s.append(txt(W - M, M + 12, "FRIDAY'S NEWS · ONE PAGE · 36 STORIES · 12 DRAWN", 9, GREY, SANS, anchor="end", spacing=1))
    s.append(line(M, M + 20, W - M, M + 20, INK, 1.5))

    # masthead date
    s.append(txt(W / 2, M + 64, "Friday 20 November 2026", 48, INK, SERIF, "bold", "middle"))
    s.append(line(M, M + 74, W - M, M + 74, INK, 2))
    s.append(line(M, M + 78, W - M, M + 78, INK, 0.75))
    s.append(txt(W / 2, M + 94, "Trilateral ends with joint statement · GTA VI shatters records · Anthropic's ANT soars", 13, RED, SERIF, "bold", "middle", style="italic"))

    # region bar
    ry = M + 102
    counts = {k: sum(1 for st in STORIES if st[6] == k) + sum(1 for b in BRIEFS if b[3] == k) for k, _, _ in REGIONS}
    seg = CW / len(REGIONS)
    for i, (k, label, col) in enumerate(REGIONS):
        x = M + i * seg
        s.append(rect(x, ry, seg - 3, 18, col, rx=2))
        s.append(txt(x + (seg - 3) / 2, ry + 12.5, f"{label} {counts[k]}", 8.5, "#fff", SANS, "bold", "middle"))

    # stats strip
    sy = ry + 24
    sw = (CW - 5 * 8) / 6
    for i, (num, lab, col) in enumerate(STATS):
        x = M + i * (sw + 8)
        s.append(rect(x, sy, sw, 46, CREAM2, LINE, 0.75, rx=3))
        s.append(txt(x + sw / 2, sy + 19, num, 16, col, SERIF, "bold", "middle"))
        for j, ln in enumerate(wrap(lab, 30)[:2]):
            s.append(txt(x + sw / 2, sy + 31 + j * 9, ln, 7.3, GREY, SANS, anchor="middle"))

    # timeline
    ty = sy + 52
    s.append(rect(M, ty, 92, 22, RED, rx=2))
    s.append(txt(M + 46, ty + 14.5, "THE DAY · UTC", 8.5, "#fff", SANS, "bold", "middle"))
    tw = (CW - 92 - 5 * 4) / 5
    for i, (tm, ev) in enumerate(TIMELINE):
        x = M + 92 + 4 + i * (tw + 4)
        s.append(rect(x, ty, tw, 22, "#fff", LINE, 0.75, rx=2))
        s.append(txt(x + 6, ty + 9.5, tm, 7.5, RED, SANS, "bold"))
        s.append(txt(x + 6, ty + 18.5, ev, 7.0, INK, SANS))

    # hero cards 1-3
    hy = ty + 28
    hw = (CW - 2 * 10) / 3
    hh = 228
    for i, st in enumerate(STORIES[:3]):
        n, place, topic, src, head, deck, reg, art = st
        x = M + i * (hw + 10)
        s.append(rect(x, hy, hw, hh, "#fff", LINE, 1, rx=4))
        s.append(illustration(art, x + 6, hy + 6, hw - 12, 100))
        s.append(f'<circle cx="{x+16}" cy="{hy+115}" r="8" fill="{RED}"/>')
        s.append(txt(x + 16, hy + 118, str(n), 9, "#fff", SANS, "bold", "middle"))
        s.append(txt(x + 30, hy + 118, f"{place} · {topic}", 9, RED, SANS, "bold", spacing=0.5))
        s.append(txt(x + hw - 8, hy + 118, src, 7.5, GREY, SANS, anchor="end"))
        yy = hy + 140
        for ln in wrap(head, 33)[:2]:
            s.append(txt(x + 10, yy, ln, 18, INK, SERIF, "bold"))
            yy += 20
        yy += 2
        for ln in wrap(deck, 58)[:4]:
            s.append(txt(x + 10, yy, ln, 10, "#3d3a34", SANS))
            yy += 12.5

    # grid cards 4-12
    gy = hy + hh + 8
    gw = (CW - 2 * 8) / 3
    gh = 76
    for i, st in enumerate(STORIES[3:]):
        n, place, topic, src, head, deck, reg, art = st
        r, c = divmod(i, 3)
        x = M + c * (gw + 8)
        y = gy + r * (gh + 6)
        s.append(rect(x, y, gw, gh, "#fff", LINE, 0.75, rx=3))
        s.append(illustration(art, x + 4, y + 5, 66, gh - 10))
        tx = x + 78
        s.append(txt(tx, y + 15, f"{n} · {place} · {topic}", 8.2, RED, SANS, "bold"))
        s.append(txt(x + gw - 6, y + 15, src, 7, GREY, SANS, anchor="end"))
        yy = y + 31
        for ln in wrap(head, 38)[:2]:
            s.append(txt(tx, yy, ln, 13, INK, SERIF, "bold"))
            yy += 14
        for ln in wrap(deck, 52)[:1]:
            s.append(txt(tx, y + 64, ln, 8.5, "#3d3a34", SANS))

    # bottom: map + briefs
    by = gy + 3 * gh + 2 * 6 + 8
    bh = 172
    mapw = 300
    s.append(world_map(M, by, mapw, bh))
    bx = M + mapw + 12
    bw = CW - mapw - 12
    s.append(txt(bx, by + 12, "ALSO ON FRIDAY 20 NOVEMBER — 24 MORE STORIES", 10, INK, SANS, "bold", spacing=0.5))
    s.append(line(bx, by + 18, bx + bw, by + 18, INK, 1))
    colw = bw / 3
    per = 8
    for i, (n, place, text, reg) in enumerate(BRIEFS):
        c, r = divmod(i, per)
        x = bx + c * colw
        y = by + 32 + r * 18.5
        s.append(txt(x, y, f"{n} · {place}", 8.2, RED, SANS, "bold"))
        s.append(txt(x, y + 9, wrap(text, 50)[0], 8.2, INK, SANS))

    # date check
    dy = by + bh + 8
    dh = 68
    s.append(rect(M, dy, CW, dh, "#fdf6ee", RED, 1.25, rx=4))
    s.append(txt(M + 10, dy + 15, "DATE CHECK — LEFT OFF THIS PAGE ON PURPOSE", 9.5, RED, SANS, "bold", spacing=0.5))
    dcw = (CW - 30) / 2
    for i, item in enumerate(DATECHECK):
        c, r = divmod(i, 4)
        x = M + 12 + c * (dcw + 6)
        y = dy + 30 + r * 10.5
        s.append(txt(x, y, "· " + item, 8, "#5a4632", SANS))

    # footer
    fy = dy + dh + 6
    s.append(line(M, fy, W - M, fy, INK, 1))
    s.append(txt(W / 2, fy + 13, "Every story here happened, or was first reported, on Friday 20 November 2026, in some time zone.", 9.3, INK, SERIF, "bold", "middle", style="italic"))
    s.append(txt(W / 2, fy + 25, "Disputed claims are attributed, not stated as fact. Original drawings. Reads at thumbnail, half and full size.", 8, GREY, SANS, anchor="middle"))
    s.append(txt(W / 2, fy + 36, "Sources: Reuters · AP · AFP · BBC · Al Jazeera · CNBC · ABS · Korea Herald · IMD · ICJ · Anadolu · NWS · Jakarta Post", 7.3, GREY, SANS, anchor="middle"))

    s.append("</svg>")
    return "\n".join(s)

if __name__ == "__main__":
    svg = build()
    with open("news_front.svg", "w") as f:
        f.write(svg)
    print(f"wrote news_front.svg ({len(svg)} bytes)")