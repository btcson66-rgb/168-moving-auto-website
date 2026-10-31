"""Topic-specific photos from the source sites; provenance is retained separately."""
GUIDE_PHOTOS = {
 'auto': ('guide-auto', '車輛固定在開放式拖車上', 'Vehicles secured on an open transport trailer'),
 'moving': ('guide-moving', '搬家前已包裝的家具與紙箱', 'Wrapped furniture and boxes prepared for a move'),
 'storage': ('guide-storage', '貨櫃內已包裝的家具與物品', 'Wrapped furniture and belongings inside a container'),
 'buy-sell': ('guide-buy-sell', '原站文章中的車輛外觀照片', 'Vehicle exterior photograph from a source article'),
 'open-enclosed': ('guide-open-enclosed', '開放式車架上的多輛汽車', 'Cars on an open transport carrier'),
 'pricing': ('guide-pricing', '木箱包裝的大型物品', 'A large item protected by a wooden crate'),
 'luggage': ('guide-luggage', '整理後的紙箱與收納箱', 'Organized cardboard boxes and storage bins'),
 'student': ('guide-student', '搬遷前車旁的行李箱與紙箱', 'Suitcases and boxes beside vehicles before a move'),
}

def alt(slug,lang):
 text=GUIDE_PHOTOS[slug][2 if lang=='en' else 1]
 if lang=='zh-hans':
  from opencc import OpenCC
  text=OpenCC('t2s').convert(text)
 return text

def add_photo_context(s,lang):
 """Credit source imagery, without implying current fleet or facility ownership."""
 import json
 from urllib.parse import urlsplit
 data=json.loads(s.select_one('#site-data').string);path=data['path']
 if s.select_one('.hero'):
  replacements={'moving':'service-moving','storage':'service-storage','buy-sell':'guide-buy-sell'}
  for slug,stem in replacements.items():
   image=s.select_one(f'.service-card[href$="/guides/{slug}/"] img')
   if image:
    image['src']='/assets/'+stem+'.jpg'
    image['alt']={'moving':('家具裝入貨車的歷史照片','Furniture being loaded into a moving truck'),'storage':('原站歷史文章中的倉庫室內照片','Warehouse interior from a historical source article'),'buy-sell':('原站文章中的車輛外觀照片','Vehicle exterior from a source article')}[slug][lang=='en']
    if lang=='zh-hans':
     from opencc import OpenCC
     image['alt']=OpenCC('t2s').convert(image['alt'])
 if path.startswith('guides/') and path!='guides/':
  slug=path.split('/')[1]
  if slug in GUIDE_PHOTOS:
   figure=s.new_tag('figure',attrs={'class':'guide-lead-photo'})
   image=s.new_tag('img',src='/assets/'+GUIDE_PHOTOS[slug][0]+'.jpg',alt=alt(slug,lang),loading='lazy');figure.append(image)
   caption=s.new_tag('figcaption');caption.string={'zh-hant':'原站歷史文章照片，作主題參考；不代表本次訂單、現有車隊或倉儲設施。','zh-hans':'原站历史文章照片，作主题参考；不代表本次订单、现有车队或仓储设施。','en':'Historical source photograph for context; not a representation of your shipment, current fleet or facilities.'}[lang];figure.append(caption)
   s.select_one('.article-top').append(figure)
 for f in s.select('.photo-credit'):
  f.clear();link=s.new_tag('a',href='/photo-review.html');link.string={'zh-hant':'照片來源與更換說明','zh-hans':'照片来源与更换说明','en':'Photo sources and replacement notes'}[lang];f.append(link)
