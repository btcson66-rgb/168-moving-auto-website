"""Server-rendered, topic-based internal links outside preserved article bodies."""
import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlsplit
from opencc import OpenCC
from content import GUIDES_TW, GUIDES_EN

CC=OpenCC('t2s')
TERMS={
 'auto':['运车','托运','汽车','车辆','car','auto','shipping'],
 'moving':['搬家','搬迁','长途','moving','move'],
 'storage':['仓储','仓库','暂存','寄存','storage'],
 'buy-sell':['买车','卖车','买卖','二手','buy','sell'],
 'open-enclosed':['开放','封闭','敞篷','跑车','豪车','enclosed','open'],
 'pricing':['费用','价格','报价','多少钱','收费','运费','便宜','cost','price'],
 'luggage':['行李','车内','物品','箱','luggage'],
 'student':['留学','毕业','学生','入职','student','graduation'],
}
RELATED={'auto':['open-enclosed','luggage','pricing'],'moving':['storage','pricing','student'],'storage':['moving','pricing'],'buy-sell':['auto','pricing'],'open-enclosed':['auto','pricing','luggage'],'pricing':['auto','moving'],'luggage':['auto','moving'],'student':['moving','storage','auto']}
LABELS={
 'zh-hant':['搬遷規劃','搬遷指南','原文文章','延伸閱讀，繼續了解','相關歷史原文','原文保留原語言；個案價格與時效不代表現行條件。','查看全部原文','回到搬遷指南','規劃我的搬遷','相關搬遷指南','同類原文文章','依照需求閱讀','先看準備指南，再參考過去文章，最後整理你的詢價資料。'],
 'zh-hans':['搬迁规划','搬迁指南','原文文章','延伸阅读，继续了解','相关历史原文','原文保留原语言；个案价格与时效不代表现行条件。','查看全部原文','回到搬迁指南','规划我的搬迁','相关搬迁指南','同类原文文章','按需求阅读','先看准备指南，再参考过去文章，最后整理你的询价资料。'],
 'en':['Plan your move','Moving guides','Original articles','Keep exploring','Related historical articles','Original language retained. Historical prices and timing are not current offers.','All original articles','All moving guides','Plan my move','Related moving guides','More original articles','Find what you need','Start with a preparation guide, explore past articles, then prepare your inquiry.'],
}

@lru_cache(maxsize=1)
def records():
 return json.loads((Path(__file__).parent/'dist/library-data.json').read_text(encoding='utf8'))

def norm(text):return CC.convert(text).lower()
def score(text,slug):return sum(term in norm(text) for term in TERMS[slug])
def guides(lang):
 values=GUIDES_EN if lang=='en' else GUIDES_TW
 return {g[0]:g[1] if lang!='zh-hans' else CC.convert(g[1]) for g in values}

def fragment(s,title,links,cls='related-reading'):
 box=s.new_tag('section',attrs={'class':cls});h=s.new_tag('h2');h.string=title;box.append(h)
 ul=s.new_tag('ul')
 for label,url in links:
  li=s.new_tag('li');a=s.new_tag('a',href=url);a.string=label;li.append(a);ul.append(li)
 box.append(ul);return box

def enhance(s,lang):
 c=LABELS[lang];g=guides(lang)
 nav=s.select_one('#navlinks')
 if nav:
  for a in nav.select('a'):
   if a.get('href','').endswith('#process'):a['href']=f'/{lang}/plan/';a.string=c[0]
   elif a.get('href','').endswith('#guides'):a['href']=f'/{lang}/guides/';a.string=c[1]
   elif a.get('href','').endswith('#about'):a['href']=f'/{lang}/library/';a.string=c[2]
 footer=s.select_one('.footer-grid>div:nth-child(2)')
 if footer:
  a=s.new_tag('a',href=f'/{lang}/plan/');a.string=c[0];footer.append(a)
 data=json.loads(s.select_one('#site-data').string);path=data['path'];main=s.select_one('main')
 if s.select_one('.original-body'):
  canonical=s.select_one('link[rel=canonical]')['href'];current=next((r for r in records() if r['url']==urlsplit(canonical).path),None)
  if current:
   slugs=sorted(TERMS,key=lambda slug:score(current['title'],slug),reverse=True)
   base='moving' if current['category']=='moving' else 'auto'
   selected=list(dict.fromkeys([base]+[x for x in slugs if score(current['title'],x)>0]))[:3]
   main.append(fragment(s,c[9],[(g[k],f'/{lang}/guides/{k}/') for k in selected]+[(c[8],f'/{lang}/plan/')]))
   peers=[r for r in records() if r['category']==current['category'] and r['id']!=current['id']]
   peers.sort(key=lambda r:sum(score(r['title'],k) for k in selected[1:] or [base]),reverse=True)
   main.append(fragment(s,c[10],[(r['title'],r['url']) for r in peers[:3]]))
  return
 if path.startswith('guides/') and path!='guides/':
  slug=path.split('/')[1]
  if slug not in g:return
  article=s.select_one('.article-layout article')
  panel=fragment(s,c[3],[(g[k],f'/{lang}/guides/{k}/') for k in RELATED[slug]]+[(c[8],f'/{lang}/plan/'),(c[7],f'/{lang}/guides/')])
  article.append(panel)
  category='moving' if slug in ('moving','storage','student') else 'auto'
  candidates=[r for r in records() if r['category']==category or score(r['title'],slug)>0]
  candidates.sort(key=lambda r:score(r['title'],slug),reverse=True)
  originals=fragment(s,c[4],[(r['title'],r['url']) for r in candidates[:3]]+[(c[6],f'/{lang}/library/')])
  note=s.new_tag('p');note.string=c[5];originals.insert(1,note);article.append(originals)
  # Add contextual links next to the preparation content, not only in the footer.
  for section,key in zip(article.select('section[id^=section-]'),RELATED[slug]):
   a=s.new_tag('a',href=f'/{lang}/guides/{key}/',attrs={'class':'context-link'});a.string=g[key]+' →';section.append(a)
 if path in ('guides/','library/') or s.select_one('.hero'):
  start=s.select_one('.page-hero') if not s.select_one('.hero') else s.select_one('#guides .section-top')
  if start:
   box=fragment(s,c[11],[(g['auto'],f'/{lang}/guides/auto/'),(g['moving'],f'/{lang}/guides/moving/'),(g['pricing'],f'/{lang}/guides/pricing/'),(c[2],f'/{lang}/library/'),(c[8],f'/{lang}/plan/')],cls='reading-hub')
   p=s.new_tag('p');p.string=c[12];box.insert(1,p);start.insert_after(box)
 if path=='library/':
  # Every preserved article remains reachable without JavaScript or pagination.
  index=s.new_tag('section',attrs={'class':'wrap archive-index'})
  title=s.new_tag('h2');title.string={'zh-hant':'全部原文目錄','zh-hans':'全部原文目录','en':'Complete original article index'}[lang];index.append(title)
  for category,label in [('moving', 'Moving' if lang=='en' else '搬家'),('auto','Auto transport' if lang=='en' else '汽車運送' if lang=='zh-hant' else '汽车运输')]:
   details=s.new_tag('details');summary=s.new_tag('summary');summary.string=label;details.append(summary)
   listing=s.new_tag('ul')
   for r in records():
    if r['category']!=category:continue
    li=s.new_tag('li');a=s.new_tag('a',href=r['url']);a.string=r['title'];li.append(a);listing.append(li)
   details.append(listing);index.append(details)
  main.append(index)
 if s.select_one('.hero-copy'):
  action=s.select_one('.hero-copy [data-quote]');action.name='a';action.attrs.pop('data-quote',None);action.attrs.pop('type',None);action['href']=f'/{lang}/plan/'
  action.contents[0].replace_with(c[8])
