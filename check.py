from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
import json,xml.etree.ElementTree as ET
root=Path(__file__).parent/'dist';errors=[];schemas=0;links=0
for f in root.rglob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 for el,attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
  for n in s.select(f'{el}[{attr}]'):
   u=n[attr];p=urlsplit(u)
   if not u.startswith('/') or u.startswith('//'):continue
   target=root/unquote(p.path.lstrip('/'));links+=1
   if target.is_dir():target=target/'index.html'
   if not target.exists():errors.append(f'{f.relative_to(root)}: missing {u}')
   elif p.fragment and el=='a':
    content=BeautifulSoup(target.read_text(encoding='utf8'),'html.parser')
    if not content.find(id=p.fragment):errors.append(f'{f.relative_to(root)}: missing anchor {u}')
 for sc in s.select('script[type="application/ld+json"]'):
  try:json.loads(sc.string or sc.get_text());schemas+=1
  except Exception as e:errors.append(f'{f}: invalid JSON-LD {e}')
 if f.parts[-2] in ['en','zh-hant','zh-hans'] or '/guides/' in f.as_posix():
  if len(s.select('h1'))!=1:errors.append(f'{f}: H1 count')
ET.parse(root/'sitemap.xml')
out={'html_files':len(list(root.rglob('*.html'))),'internal_links_checked':links,'json_ld_valid':schemas,'errors':errors}
(root.parent/'research/static-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False))
if errors:raise SystemExit(1)
