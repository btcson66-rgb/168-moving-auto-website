"""Andercore-inspired presentation, applied after the retained layout and before image optimization."""
from bs4 import BeautifulSoup

TEXT={
 'zh-hant':{'title':'跨州的距離，<br>交給 168。','intro':'美國跨州運車、長途搬家與倉儲。一個窗口，把車輛與生活一起安排到下一站。','kicker':'168 / 美國跨州運輸','fleet':'車與家，都在路上。','fleetNote':'運送動態示意，非即時車隊位置。','pause':'暫停動畫','play':'播放動畫','route':'路線運行示意','mapNote':'箭頭表示運送方向，非即時定位或到貨承諾。','status':'路線示意 / LOS ANGELES → NEW YORK'},
 'zh-hans':{'title':'跨州的距离，<br>交给 168。','intro':'美国跨州运车、长途搬家与仓储。一个窗口，把车辆与生活一起安排到下一站。','kicker':'168 / 美国跨州运输','fleet':'车与家，都在路上。','fleetNote':'运输动态示意，非实时车队位置。','pause':'暂停动画','play':'播放动画','route':'路线运行示意','mapNote':'箭头表示运输方向，非实时定位或到货承诺。','status':'路线示意 / LOS ANGELES → NEW YORK'},
 'en':{'title':'Across states.<br>Alongside you.','intro':'Auto transport, interstate moving and storage. One team to coordinate your car, your belongings and your next address.','kicker':'168 / Interstate transport','fleet':'Your whole move, in motion.','fleetNote':'Transport illustration. Not live fleet tracking.','pause':'Pause animation','play':'Play animation','route':'Route movement preview','mapNote':'Arrows show direction only, not live positions or guaranteed arrival times.','status':'Illustrative route / LOS ANGELES → NEW YORK'}
}

def truck_svg():
 return '''<svg class="fleet-scene" viewBox="0 0 1200 210" role="img" aria-label="Schematic freight trucks moving along a highway" data-animated-svg="fleet">
 <defs><linearGradient id="trailer-metal" x2="0" y2="1"><stop stop-color="#f1eeed"/><stop offset="1" stop-color="#bdb8b7"/></linearGradient><symbol id="freight-truck" viewBox="0 0 480 150">
 <path d="M17 20H324V112H17Z" fill="url(#trailer-metal)" stroke="#fff" stroke-width="1"/><path d="M25 28H315M25 102H315" stroke="#9a9493"/><path d="M28 34V96M36 34V96M306 34V96M314 34V96" stroke="#c3bdbc"/><path d="M18 114H386V123H18Z" fill="#615b5c"/><path d="M334 44H385L409 62 424 105H446V122H326V76Z" fill="#f4f1f0"/><path d="M344 53H379L398 71H343Z" fill="#272324"/><path d="M401 77H414L421 103H400Z" fill="#aaa3a2"/><path d="M350 83H389V115H343V83Z" fill="#d4cecd" stroke="#8c8483"/><path d="M351 89H361M411 109H436M411 114H436" stroke="#4e4645" stroke-width="3"/><path d="M376 24H382V44M432 101H444V107H432" stroke="#ddd6d5" stroke-width="5"/><path d="M18 109H323" stroke="#e32735" stroke-width="4"/>
 <g fill="#141011" stroke="#837b7a" stroke-width="4"><circle cx="58" cy="126" r="17"/><circle cx="99" cy="126" r="17"/><circle cx="319" cy="126" r="17"/><circle cx="356" cy="126" r="17"/><circle cx="414" cy="126" r="17"/></g><g fill="#b6b0ae"><circle cx="58" cy="126" r="7"/><circle cx="99" cy="126" r="7"/><circle cx="319" cy="126" r="7"/><circle cx="356" cy="126" r="7"/><circle cx="414" cy="126" r="7"/></g>
 <text x="55" y="78" font-family="Archivo,Arial,sans-serif" font-weight="500" font-size="52" fill="#171112">168</text><text x="166" y="62" font-family="Archivo,Arial,sans-serif" font-size="15" fill="#302829">Moving &amp; Auto</text><text x="166" y="82" font-family="Arial,sans-serif" font-size="9" fill="#625a59">INTERSTATE TRANSPORT</text></symbol></defs>
 <path class="highway-edge" d="M0 120H1200M0 175H1200M0 200H1200" stroke="#382e30"/><path class="road-dashes" d="M0 188H1200" stroke="#787170" stroke-width="2" stroke-dasharray="35 45"/>
 <g class="freight-unit freight-far"><use href="#freight-truck" x="0" y="25" width="310" height="100"/></g><g class="freight-unit freight-near"><use href="#freight-truck" x="0" y="32" width="480" height="150"/></g></svg>'''

def apply_midnight(s,lang):
 t=TEXT[lang]
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
 # This technical diagram is intentionally distinct from the original site's photographs.
 band=s.new_tag('section',attrs={'class':'fleet-band wrap','id':'fleet','aria-label':t['fleet']})
 primary=copy.select_one('[data-quote]')
 actions=s.new_tag('div',attrs={'class':'hero-actions'});primary.wrap(actions)
 link=s.new_tag('a',href='#fleet',attrs={'class':'button ghost'})
 link.string='See transport in motion' if lang=='en' else '查看运输动态' if lang=='zh-hans' else '查看運送動態'
 actions.append(link)
 bar=s.new_tag('div',attrs={'class':'fleet-bar'});title=s.new_tag('h2');title.string=t['fleet'];bar.append(title)
 control=s.new_tag('button',attrs={'class':'motion-control','type':'button','data-motion-toggle':'','data-pause-label':t['pause'],'data-play-label':t['play']});control.string=t['pause'];bar.append(control);band.append(bar)
 band.append(BeautifulSoup(truck_svg(),'html.parser'))
 note=s.new_tag('p',attrs={'class':'motion-note'});note.string=t['fleetNote'];band.append(note)
 s.select_one('.hero').insert_after(band)
 route_svg=s.select_one('.route-map>svg');route_svg['class']=['route-diagram'];route_svg['data-animated-svg']='routes';route_svg['aria-label']=t['route']
 paths=route_svg.select('g[fill="none"]>path')
 for i,path in enumerate(paths):
  path['class']=['route-path', 'is-current' if i==0 else ''];path['data-route-index']=str(i)
  group=s.new_tag('g',attrs={'class':'route-arrow','data-route-index':str(i),'aria-hidden':'true'})
  arrow=s.new_tag('path',attrs={'d':'M-9-6 3 0-9 6-5 0Z','fill':'#ffffff'})
  group.append(arrow)
  group.append(s.new_tag('animateMotion',attrs={'dur':f'{7+i*2}s','repeatCount':'indefinite','rotate':'auto','path':path['d']}))
  route_svg.append(group)
 for node in route_svg.select('circle'):node['class']=['route-city']
 for path in paths:path.parent['stroke']='#8d8584'
 for group in route_svg.select('g[fill="#d4ef78"]'):group['fill']='#ffffff'
 for text in route_svg.select('text'):text['fill']='#e8e2e1'
 for option in s.select('[data-route]'):
  option['data-route-label']=option.get_text(' ',strip=True)
 mapbox=s.select_one('.route-map');status=s.new_tag('p',attrs={'class':'route-status','aria-live':'polite'});status.string=t['status'];mapbox.insert(0,status)
 note=s.new_tag('p',attrs={'class':'motion-note'});note.string=t['mapNote'];mapbox.append(note)
 # The separate map control is synchronized with the hero control.
 ctl=s.new_tag('button',attrs={'class':'motion-control map-motion-control','type':'button','data-motion-toggle':'','data-pause-label':t['pause'],'data-play-label':t['play']});ctl.string=t['pause'];mapbox.append(ctl)
