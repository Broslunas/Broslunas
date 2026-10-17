"""Fills the projects, blog and certificates blocks of README.md from broslunas.com.

- Blog:          /feed.xml (RSS)
- Projects:      /sitemap.xml + each project page's Open Graph tags
- Certificates:  the cards on /es/certificates

Cards mirror the site's look: 3-column grid and a mono meta line. GitHub strips
inline styles, so only plain HTML attributes are used.
"""
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

SITE = "https://www.broslunas.com"
LANG = "es"
UA = {"User-Agent": "Mozilla/5.0 (broslunas README bot)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8")


def truncate(text, n=140):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def fmt_date(dt):
    return dt.strftime("%d.%m.%Y")


def grid(cells, cols=3):
    if not cells:
        return ""
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    return "<table>\n" + "\n".join("<tr>\n" + "\n".join(r) + "\n</tr>" for r in rows) + "\n</table>"


# ------------------------------------------------------------------- blog

def blog_html(limit=4):
    root = ET.fromstring(fetch(f"{SITE}/feed.xml?lang={LANG}"))
    rows = []
    for item in root.findall(".//item")[:limit]:
        title = html.escape(item.findtext("title", "").strip())
        url = item.findtext("link", "").strip()
        desc = html.escape(truncate(item.findtext("description", "")))
        try:
            date = fmt_date(parsedate_to_datetime(item.findtext("pubDate", "")))
        except (TypeError, ValueError):
            date = ""
        rows.append(
            f'<tr>\n<td width="18%" valign="top"><sub><code>{date}</code></sub></td>\n'
            f'<td valign="top"><b><a href="{url}" target="_blank" rel="noopener">{title}</a></b><br/><sub>{desc}</sub></td>\n</tr>'
        )
    return "<table>\n" + "\n".join(rows) + "\n</table>" if rows else ""


# --------------------------------------------------------------- projects

def og(page, prop):
    m = re.search(rf'<meta property="og:{prop}" content="([^"]*)"', page)
    return html.unescape(m.group(1)) if m else ""


def projects_html(limit=3):
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(fetch(f"{SITE}/sitemap.xml"))
    entries = []
    for u in root.findall("s:url", ns):
        loc = u.findtext("s:loc", "", ns)
        if re.search(rf"/{LANG}/projects/[^/]+$", loc):
            entries.append((loc, u.findtext("s:lastmod", "", ns)))
    cells = []
    for i, (loc, lastmod) in enumerate(entries[:limit]):
        page = fetch(loc)
        title = html.escape(og(page, "title"))
        desc = html.escape(truncate(og(page, "description")))
        image = html.escape(og(page, "image"))
        date = fmt_date(datetime.fromisoformat(lastmod.replace("Z", "+00:00"))) if lastmod else ""
        meta = " · ".join(x for x in (f"{i + 1:02d}", date) if x)
        cells.append(
            f'<td width="33%" valign="top">\n<a href="{loc}" target="_blank" rel="noopener"><img src="{image}" width="100%" alt="{title}"/></a>\n'
            f"<br/><sub><code>{meta}</code></sub>\n<br/><b><a href=\"{loc}\" target=\"_blank\" rel=\"noopener\">{title}</a></b>\n<br/><sub>{desc}</sub>\n</td>"
        )
    return grid(cells)


# ----------------------------------------------------------- certificates

def certs_html(limit=6):
    page = fetch(f"{SITE}/{LANG}/certificates")
    cells = []
    for art in re.findall(r"<article.*?</article>", page, re.S)[:limit]:
        img = re.search(r'<img src="([^"]+)"', art)
        link = re.search(r'<h3[^>]*><a href="([^"]+)"[^>]*>(.*?)</a>', art, re.S)
        when = re.search(r'<time dateTime="([^"]+)"', art)
        issuer = re.search(r'<p class="tag text-accent">(.*?)</p>', art)
        if not (img and link):
            continue
        src = html.unescape(img.group(1))
        src = src if src.startswith("http") else SITE + src
        title = link.group(2).strip()
        date = fmt_date(datetime.fromisoformat(when.group(1))) if when else ""
        meta = " · ".join(x for x in (issuer.group(1).strip() if issuer else "", date) if x)
        cells.append(
            f'<td width="33%" valign="top">\n<a href="{link.group(1)}" target="_blank" rel="noopener"><img src="{html.escape(src)}" width="100%" alt="{title}"/></a>\n'
            f"<br/><b><sub>{title}</sub></b>\n<br/><sub><code>{meta}</code></sub>\n</td>"
        )
    return grid(cells)


# ------------------------------------------------------------------ main

def replace_section(text, name, content):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = re.compile(re.escape(start) + ".*?" + re.escape(end), re.S)
    return pattern.sub(lambda _: f"{start}\n{content}\n{end}", text)


def main():
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    for name, build in (("projects", projects_html), ("blog", blog_html), ("certs", certs_html)):
        try:
            content = build()
        except Exception as e:  # keep the previous block if the site is unreachable
            print(f"Skipping {name}: {e}")
            continue
        if content:
            readme = replace_section(readme, name, content)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated successfully.")


if __name__ == "__main__":
    main()
