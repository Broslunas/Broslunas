import urllib.request
import xml.etree.ElementTree as ET
import re

from email.utils import parsedate_to_datetime

def extract_data(items, category, max_items, html_format):
    res = []
    for item in items:
        link_elem = item.find('link')
        if link_elem is None or not link_elem.text:
            continue
        link = link_elem.text.strip()
        if category in link:
            title_elem = item.find('title')
            title = title_elem.text.strip() if title_elem is not None else ''
            
            img_elem = item.find('image')
            image = img_elem.text.strip() if img_elem is not None else ''
            
            pub_date_elem = item.find('pubDate')
            if pub_date_elem is not None and pub_date_elem.text:
                try:
                    dt = parsedate_to_datetime(pub_date_elem.text.strip())
                    date = dt.strftime("%d/%m/%Y")
                except:
                    date = pub_date_elem.text.strip()[:16]
            else:
                date = ''
                
            desc_elem = item.find('description')
            desc = desc_elem.text.strip() if desc_elem is not None else ''
            # Truncate description if too long
            if len(desc) > 150:
                desc = desc[:147] + '...'
            
            res.append(html_format.format(url=link, title=title, image=image, date=date, desc=desc))
            if len(res) >= max_items:
                break
    return '\n'.join(res)

def replace_section(readme_text, start_tag, end_tag, new_content):
    pattern = re.compile(f'({start_tag}).*?({end_tag})', re.DOTALL)
    # Put the new content exactly between the tags
    return pattern.sub(f'\\1\n{new_content}\n\\2', readme_text)

def main():
    url = "https://www.broslunas.com/rss.xml"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"Failed to fetch RSS: {e}")
        return

    root = ET.fromstring(xml_data)
    items = root.findall('.//item')

    project_card_format = """<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; margin-bottom: 20px; border: 1px solid #30363d; border-radius: 10px; overflow: hidden; background: #0d1117;">
  <tr>
    <td width="5" bgcolor="#bc52ee" style="padding: 0px;"></td>
    <td style="padding: 20px;">
      <table width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
          <td valign="top">
            <h3><a href="{url}" target="_blank" style="color: #bc52ee; text-decoration: none;">🚀 {title}</a></h3>
            <p style="color: #8b949e; font-size: 0.85em; margin: 5px 0;">📅 <strong>{date}</strong></p>
            <p style="color: #c9d1d9; font-size: 0.95em; line-height: 1.5; margin-top: 10px;">{desc}</p>
          </td>
          <td width="160" align="right" valign="middle" style="padding-left: 20px;">
            <a href="{url}" target="_blank">
              <img src="{image}" width="150" style="border-radius: 8px; object-fit: cover; aspect-ratio: 16/10; border: 1px solid #30363d;" alt="{title}"/>
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""

    blog_card_format = """<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; margin-bottom: 20px; border: 1px solid #30363d; border-radius: 10px; overflow: hidden; background: #0d1117;">
  <tr>
    <td width="5" bgcolor="#38bdf8" style="padding: 0px;"></td>
    <td style="padding: 20px;">
      <table width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
          <td valign="top">
            <h3><a href="{url}" target="_blank" style="color: #38bdf8; text-decoration: none;">📝 {title}</a></h3>
            <p style="color: #8b949e; font-size: 0.85em; margin: 5px 0;">📅 <strong>{date}</strong></p>
            <p style="color: #c9d1d9; font-size: 0.95em; line-height: 1.5; margin-top: 10px;">{desc}</p>
          </td>
          <td width="160" align="right" valign="middle" style="padding-left: 20px;">
            <a href="{url}" target="_blank">
              <img src="{image}" width="150" style="border-radius: 8px; object-fit: cover; aspect-ratio: 16/10; border: 1px solid #30363d;" alt="{title}"/>
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""

    projects_html = extract_data(items, '/projects/', 3, project_card_format)
    blog_html = extract_data(items, '/blog/', 3, blog_card_format) # limited to 3 to not fill the whole screen
    
    # Extract certs explicitly to make a grid (3 columns per row)
    certs_tds = extract_data(items, '/certificates/', 6, '<td align="center" valign="top" width="33%" style="padding: 10px;"><table width="100%" style="border-collapse: collapse; border: 1px solid #30363d; border-radius: 10px; background-color: #0d1117;"><tr><td align="center" style="padding: 20px 10px;"><a href="{url}" target="_blank"><img src="{image}" height="90" title="{title}" style="border-radius: 8px; border: 1px solid #30363d; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));"/></a><br/><br/><strong style="color: #adbac7; font-size: 0.9em; display: block; min-height: 40px; line-height: 1.3;">{title}</strong><br/><span style="color: #768390; font-size: 0.8em; display: block; margin-top: 5px;">📅 {date}</span></td></tr></table></td>')
    certs_list = certs_tds.split('\n')
    
    certs_html = '<table width="100%" border="0" cellpadding="0" cellspacing="0">'
    for i, td in enumerate(certs_list):
        if i % 3 == 0:
            if i > 0: certs_html += "</tr>"
            certs_html += "<tr>"
        certs_html += td
    if certs_list:
        certs_html += "</tr>"
    certs_html += "</table>"

    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

    readme = replace_section(readme, '<!-- projects:start -->', '<!-- projects:end -->', projects_html)
    readme = replace_section(readme, '<!-- blog:start -->', '<!-- blog:end -->', blog_html)
    readme = replace_section(readme, '<!-- certs:start -->', '<!-- certs:end -->', certs_html)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
        
    print("README.md updated successfully.")

if __name__ == '__main__':
    main()
