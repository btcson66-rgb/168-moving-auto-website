"""Andercore-inspired presentation, applied after the retained layout and before image optimization."""
from bs4 import BeautifulSoup

TEXT={
 'zh-hant':{'title':'跨州的距離，<br>交給 168。','intro':'美國跨州運車、長途搬家與倉儲。一個窗口，把車輛與生活一起安排到下一站。','kicker':'168 / 美國跨州運輸','fleet':'車與家，都在路上。','fleetNote':'運送動態示意，非即時車隊位置。','pause':'暫停動畫','play':'播放動畫','route':'路線運行示意','mapNote':'箭頭表示運送方向，非即時定位或到貨承諾。','status':'路線示意 / LOS ANGELES → NEW YORK'},
 'zh-hans':{'title':'跨州的距离，<br>交给 168。','intro':'美国跨州运车、长途搬家与仓储。一个窗口，把车辆与生活一起安排到下一站。','kicker':'168 / 美国跨州运输','fleet':'车与家，都在路上。','fleetNote':'运输动态示意，非实时车队位置。','pause':'暂停动画','play':'播放动画','route':'路线运行示意','mapNote':'箭头表示运输方向，非实时定位或到货承诺。','status':'路线示意 / LOS ANGELES → NEW YORK'},
 'en':{'title':'Across states.<br>Alongside you.','intro':'Auto transport, interstate moving and storage. One team to coordinate your car, your belongings and your next address.','kicker':'168 / Interstate transport','fleet':'Your whole move, in motion.','fleetNote':'Transport illustration. Not live fleet tracking.','pause':'Pause animation','play':'Play animation','route':'Route movement preview','mapNote':'Arrows show direction only, not live positions or guaranteed arrival times.','status':'Illustrative route / LOS ANGELES → NEW YORK'}
}

def apply_midnight(s,lang):
 t=TEXT[lang]
 from inquiry import apply_inquiry
 apply_inquiry(s,lang)
 from discovery import enhance
 enhance(s,lang)
 s.head.append(s.new_tag('link',rel='stylesheet',href='/midnight.css'))
 s.select_one('meta[name="theme-color"]')['content']='#0b0405'
 s.select_one('link[rel="icon"]')['href']='/assets/favicon-midnight.svg'
 s.body['class']=s.body.get('class',[])+['midnight-edition']
 if not s.select_one('.hero'):return
 script=s.new_tag('script',src='/motion.js',defer='');s.body.append(script)
 s.select_one('.hero h1').clear()
 for node in list(BeautifulSoup(t['title'],'html.parser').contents):s.select_one('.hero h1').append(node)
 s.select_one('.hero-intro').string=t['intro']
 copy=s.select_one('.hero-copy');badge=s.new_tag('p',attrs={'class':'industrial-label'});badge.string=t['kicker'];copy.insert(0,badge)
 # Integrate trust points into the services section.
 strip=s.select_one('.trust-strip');strip['class']=['service-benefits']
 strip.select_one('.wrap')['class']=['benefit-list']
 s.select_one('#services .section-top').insert_after(strip)
 s.select_one('#services h2').string={'zh-hant':'你的搬遷，一次安排。','zh-hans':'你的搬迁，一次安排。','en':'Your whole move. One place.'}[lang]
 for answer in s.select('.faq-layout details'):answer.attrs.pop('open',None)
 route_svg=s.select_one('.route-map>svg');route_svg['class']=['route-diagram'];route_svg['data-animated-svg']='routes';route_svg['aria-label']=t['route']
 paths=route_svg.select('g[fill="none"]>path')
 for i,path in enumerate(paths):
  path['class']=['route-path', 'is-current' if i==0 else ''];path['data-route-index']=str(i)
  group=s.new_tag('g',attrs={'class':'route-arrow','data-route-index':str(i),'aria-hidden':'true'})
  arrow=s.new_tag('path',attrs={'d':'M-9-6 3 0-9 6-5 0Z','fill':'#ffffff'})
  group.append(arrow)
  group.append(s.new_tag('animateMotion',attrs={'dur':'4s','repeatCount':'1','fill':'freeze','rotate':'auto','path':path['d']}))
  route_svg.append(group)
 for node in route_svg.select('circle'):node['class']=['route-city']
 for path in paths:path.parent['stroke']='#8d8584'
 for group in route_svg.select('g[fill="#d4ef78"]'):group['fill']='#ffffff'
 for text in route_svg.select('text'):text['fill']='#e8e2e1'
 for option in s.select('[data-route]'):
  option['data-route-label']=option.get_text(' ',strip=True)
 mapbox=s.select_one('.route-map');status=s.new_tag('p',attrs={'class':'route-status','aria-live':'polite'});status.string=t['status'];mapbox.insert(0,status)
 note=s.new_tag('p',attrs={'class':'motion-note'});note.string=t['mapNote'];mapbox.append(note)
 # Map arrows remain decorative; no visible playback button.
