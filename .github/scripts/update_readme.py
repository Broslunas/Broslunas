import urllib.request
import xml.etree.ElementTree as ET
import re

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
            
            res.append(html_format.format(url=link, title=title, image=image))
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

    projects_format = '<a href="{url}" target="_blank">\n  <img src="{image}" width="250" alt="{title}" style="border-radius:10px; margin: 10px;"/>\n</a>'
    blog_format = '- [{title}]({url})'
    certs_format = '<a href="{url}" target="_blank">\n  <img src="{image}" height="80" title="{title}" style="margin: 5px;"/>\n</a>'

    projects_html = extract_data(items, '/projects/', 3, projects_format)
    blog_html = extract_data(items, '/blog/', 5, blog_format)
    certs_html = extract_data(items, '/certificates/', 6, certs_format)

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
