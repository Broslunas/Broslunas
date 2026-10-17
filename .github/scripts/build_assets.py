"""Generates the README's SVG assets (hero, section headers and buttons).

The look mirrors the hero of broslunas.com: near-black background, Archivo Black
display type, JetBrains Mono tags and an orange accent. Fonts are embedded as
base64 so the SVGs render the same inside GitHub's <img> sandbox.

Run from the repository root:  python .github/scripts/build_assets.py
"""
import base64
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"

BG = "#0a0a0a"
FG = "#eaeaea"
DIM = "#8a8a8a"
LINE = "#2a2a2a"
ACCENT = "#ff5a1f"


def font_face(family, file, weight="400"):
    data = base64.b64encode((ASSETS / "fonts" / file).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
    )


DISPLAY = font_face("Archivo Black", "archivo-black-latin.woff2")
MONO = font_face("JetBrains Mono", "jetbrains-mono-latin.woff2", "100 800")

BASE_CSS = """
.mono{font-family:'JetBrains Mono',ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em}
.macro{font-family:'Archivo Black',Impact,sans-serif;text-transform:uppercase;letter-spacing:-.05em}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

GRAIN = """<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>
<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter>"""


def svg(width, height, body, css="", fonts=(DISPLAY, MONO), label=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{label}">\n'
        f"<style>{''.join(fonts)}{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )


def logo_mark(x, y, size):
    s = size / 64
    return (
        f'<g transform="translate({x} {y}) scale({s})">'
        f'<rect width="64" height="64" fill="{ACCENT}"/>'
        f'<circle cx="29" cy="35" r="20" fill="{BG}"/>'
        f'<circle cx="40" cy="26" r="17" fill="{ACCENT}"/>'
        f'<rect x="43" y="13" width="7" height="7" fill="{BG}"/></g>'
    )


def arrow(x, y, color, size=12, down=False):
    """Hand-drawn arrow: → and ↓ are not in the embedded font subset."""
    h = size / 2
    if down:
        return (f'<path d="M{x} {y - size}V{y}M{x - h * .8} {y - h * .8}L{x} {y}L{x + h * .8} {y - h * .8}" '
                f'stroke="{color}" stroke-width="2" fill="none"/>')
    return (f'<path d="M{x - size} {y}H{x}M{x - h * .8} {y - h * .8}L{x} {y}L{x - h * .8} {y + h * .8}" '
            f'stroke="{color}" stroke-width="2" fill="none"/>')


# --------------------------------------------------------------------------- hero

def hud(cx, cy):
    """The orbit HUD from the portfolio's hero video, rebuilt as animated vectors."""
    out = []
    R = 330
    # Outer dial with ticks, slowly rotating.
    ticks = []
    for i in range(72):
        a = math.radians(i * 5)
        l = 16 if i % 6 == 0 else 7
        x1, y1 = cx + R * math.cos(a), cy + R * math.sin(a)
        x2, y2 = cx + (R - l) * math.cos(a), cy + (R - l) * math.sin(a)
        ticks.append(f"M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}")
    out.append(
        f'<g class="spin-slow" style="transform-origin:{cx}px {cy}px">'
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#3a3a3a"/>'
        f'<path d="{"".join(ticks)}" stroke="#3a3a3a"/></g>'
    )
    # Corner crosshairs.
    for dx, dy in ((-300, -190), (300, -190), (-300, 130), (300, 130)):
        x, y = cx + dx, cy + dy
        out.append(f'<path d="M{x - 8} {y}H{x + 8}M{x} {y - 8}V{y + 8}" stroke="#4a4a4a"/>')
    # Axes through the core.
    ox, oy = cx - 150, cy - 30
    out.append(f'<path d="M{ox - 110} {oy}H{ox + 110}M{ox} {oy - 110}V{oy + 110}" stroke="#2e2e2e"/>')
    out.append(f'<circle cx="{ox}" cy="{oy}" r="74" fill="none" stroke="#3a3a3a"/>')
    out.append(f'<circle cx="{ox}" cy="{oy}" r="46" fill="none" stroke="#2e2e2e"/>')
    out.append(
        f'<circle class="spin-rev" style="transform-origin:{ox}px {oy}px" cx="{ox}" cy="{oy}" r="100" '
        f'fill="none" stroke="#3a3a3a" stroke-dasharray="2 6"/>'
    )
    # Orbiting satellites.
    out.append(
        f'<g class="orbit" style="transform-origin:{ox}px {oy}px">'
        f'<rect x="{ox - 5}" y="{oy - 79}" width="10" height="10" fill="{ACCENT}"/></g>'
    )
    out.append(
        f'<g class="orbit-slow" style="transform-origin:{ox}px {oy}px">'
        f'<rect x="{ox + 96}" y="{oy - 4}" width="8" height="8" fill="none" stroke="{FG}"/></g>'
    )
    out.append(logo_mark(ox - 26, oy - 26, 52))
    out.append(f'<text x="{ox}" y="{oy + 132}" text-anchor="middle" class="mono" font-size="11" fill="{DIM}">BROSLUNAS / LUNA CRECIENTE</text>')
    out.append(f'<text x="{ox - 130}" y="{oy - 140}" class="mono" font-size="11" fill="{DIM}"><tspan fill="{ACCENT}">01</tspan> / [ ÓRBITA ]</text>')

    # Moon phases strip.
    px, py = cx - 10, cy - 60
    out.append(f'<text x="{px}" y="{py - 40}" class="mono" font-size="11" fill="{ACCENT}">&lt; FASES &gt;</text>')
    out.append('<defs>')
    for k in range(8):
        out.append(f'<clipPath id="ph{k}"><circle cx="{px + 12 + k * 33}" cy="{py}" r="12"/></clipPath>')
    out.append('</defs>')
    for k in range(8):
        x = px + 12 + k * 33
        shadow = 26 * k / 7
        out.append(
            f'<circle cx="{x}" cy="{py}" r="12" fill="#5a2410"/>'
            f'<g clip-path="url(#ph{k})"><circle cx="{x - shadow}" cy="{py}" r="12" fill="{BG}"/></g>'
            f'<circle cx="{x}" cy="{py}" r="12" fill="none" stroke="#6a3018"/>'
        )
    out.append(f'<path d="M{px} {py + 27}H{px + 260}" stroke="#2e2e2e"/>')
    out.append(f'<rect class="phase-bar" x="{px}" y="{py + 26}" width="26" height="3" fill="{ACCENT}"/>')
    for k in range(8):
        ilum = round(100 * k / 7)
        out.append(
            f'<text class="phase-label" style="animation-delay:-{(8 - k) % 8}s" x="{px}" y="{py + 50}" font-size="11">'
            f'<tspan class="mono" fill="{FG}" font-weight="700">FASE 0{k + 1} / 08</tspan>'
            f'<tspan class="mono" fill="{DIM}" dx="14">ILUM. {ilum:03d}%</tspan></text>'
        )
    return "\n".join(out)


def hero():
    W, H, P = 1280, 720, 56
    css = """
.spin-slow{animation:spin 90s linear infinite}
.spin-rev{animation:spin 40s linear infinite reverse}
.orbit{animation:spin 8s linear infinite}
.orbit-slow{animation:spin 20s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
.phase-bar{animation:phase 8s steps(8,end) infinite}
@keyframes phase{to{transform:translateX(264px)}}
.phase-label{opacity:0;animation:show 8s steps(1,end) infinite}
@keyframes show{0%{opacity:1}12.5%{opacity:0}100%{opacity:0}}
.scan{animation:scan 6s ease-in-out infinite alternate}
@keyframes scan{from{transform:translateY(0)}to{transform:translateY(500px)}}
"""
    grid = "".join(f"M{x} 0V{H}" for x in range(0, W + 1, 80)) + "".join(f"M0 {y}H{W}" for y in range(0, H + 1, 80))
    body = f"""
<defs>{GRAIN}
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset=".45" stop-color="{BG}" stop-opacity=".2"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
<linearGradient id="scanline" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="1" stop-color="{ACCENT}" stop-opacity=".05"/></linearGradient>
<clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<g clip-path="url(#frame)">
  <path d="{grid}" stroke="#151515"/>
  <g opacity=".75">{hud(980, 250)}</g>
  <rect class="scan" x="560" y="-80" width="{W - 560}" height="60" fill="url(#scanline)"/>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
</g>

<g class="mono" font-size="13" fill="{DIM}">
  <circle class="blink" cx="{P + 5}" cy="59.5" r="5" fill="{ACCENT}"/>
  <text x="{P + 20}" y="64">DISPONIBLE PARA PROYECTOS</text>
  <text x="{W - P}" y="64" text-anchor="end" xml:space="preserve">UNIT / D-01   REV 1.0</text>
</g>

<g>
  <text x="{P - 6}" y="500" class="macro" font-size="166" fill="{FG}">BROSLUNAS<tspan fill="{ACCENT}">.</tspan></text>
</g>
<path d="M{P} 548H{W - P}" stroke="{LINE}"/>
<g>
  <text x="{P}" y="592" class="mono" font-size="20" font-weight="800" fill="{FG}">PABLO LUNA<tspan font-size="11" dy="-9" fill="{ACCENT}">®</tspan></text>
  <text x="{P}" y="622" class="mono" font-size="13" fill="{ACCENT}">&gt;&gt;&gt; DESARROLLADOR WEB FULL-STACK FREELANCE</text>
  <text x="472" y="622" class="mono" font-size="12" fill="{DIM}"><tspan fill="{ACCENT}">//</tspan> NEXT.JS · ASTRO · TYPESCRIPT · NODE.JS · FIGMA</text>
</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".05"/>
"""
    return svg(W, H, body, css, label="Broslunas — Pablo Luna, desarrollador web full-stack freelance")


# ------------------------------------------------------------- section headers

def section(n, label, title):
    W, H = 1280, 150
    body = f"""
<rect width="{W}" height="{H}" fill="{BG}"/>
<path d="M0 .5H{W}" stroke="{LINE}"/>
<text x="0" y="40" class="mono" font-size="15" fill="{DIM}"><tspan fill="{ACCENT}">{n}</tspan> / [ {label} ]</text>
<text x="-4" y="128" class="macro" font-size="72" fill="{FG}">{title}<tspan fill="{ACCENT}">.</tspan></text>
"""
    return svg(W, H, body, label=f"{n} / {label}")


# ------------------------------------------------------------------- buttons

def button(text, style, icon=None):
    char = 9.6  # JetBrains Mono advance at 13px with .08em tracking
    pad = 22
    tw = len(text) * char + (22 if icon else 0)
    W, H = int(tw + pad * 2), 46
    fill = {"solid": ACCENT, "outline": "none", "ghost": "none"}[style]
    stroke = {"solid": ACCENT, "outline": ACCENT, "ghost": "#3a3a3a"}[style]
    color = {"solid": BG, "outline": ACCENT, "ghost": FG}[style]
    ix = pad + len(text) * char + 16
    icons = {
        "arrow": arrow(ix + 4, H / 2, color),
        "down": arrow(ix - 2, H / 2 + 6, color, down=True),
        "clock": (f'<circle cx="{ix - 2}" cy="{H / 2}" r="6.5" fill="none" stroke="{color}" stroke-width="1.6"/>'
                  f'<path d="M{ix - 2} {H / 2 - 4}V{H / 2}H{ix + 1.5}" stroke="{color}" stroke-width="1.6" fill="none"/>'),
        "ext": (f'<path d="M{ix - 6} {H / 2 + 6}L{ix + 4} {H / 2 - 4}M{ix - 3} {H / 2 - 5}H{ix + 5}V{H / 2 + 3}" '
                f'stroke="{color}" stroke-width="2" fill="none"/>'),
    }
    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="{fill}" stroke="{stroke}"/>
<text x="{pad}" y="{H / 2 + 4.5}" class="mono" font-size="13" font-weight="700" fill="{color}" xml:space="preserve">{text}</text>
{icons[icon] if icon else ""}
"""
    return svg(W, H, body, fonts=(MONO,), label=text.strip("[] "))


def main():
    (ASSETS / "hero.svg").write_text(hero(), encoding="utf-8")

    sections = ASSETS / "sections"
    sections.mkdir(exist_ok=True)
    for slug, n, label, title in [
        ("work", "01", "TRABAJO", "Trabajo seleccionado"),
        ("stack", "02", "STACK", "Herramientas"),
        ("blog", "03", "BLOG", "Últimos posts"),
        ("certs", "04", "CERTIFICACIONES", "Formación"),
        ("activity", "05", "ACTIVIDAD", "En GitHub"),
        ("contact", "06", "CONTACTO", "Hablemos"),
    ]:
        (sections / f"{slug}.svg").write_text(section(n, label, title), encoding="utf-8")

    buttons = ASSETS / "buttons"
    buttons.mkdir(exist_ok=True)
    for slug, text, style, icon in [
        ("start", "[ EMPEZAR UN PROYECTO ]", "solid", "arrow"),
        ("cv", "[ DESCARGAR CV ]", "outline", "down"),
        ("call", "[ AGENDAR LLAMADA ]", "ghost", "clock"),
        ("web", "[ BROSLUNAS.COM ]", "solid", "ext"),
        ("instagram", "[ INSTAGRAM ]", "ghost", "ext"),
        ("paypal", "[ PAYPAL ]", "ghost", "ext"),
        ("projects", "[ VER TODOS LOS PROYECTOS ]", "outline", "arrow"),
        ("posts", "[ VER TODOS LOS POSTS ]", "outline", "arrow"),
    ]:
        (buttons / f"{slug}.svg").write_text(button(text, style, icon), encoding="utf-8")

    print("Assets generated.")


if __name__ == "__main__":
    main()
