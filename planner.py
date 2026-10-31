"""Detailed planning hub. Instructions are preparation guidance, not service guarantees."""
TW={
 'title':'把搬遷細節，先安排清楚。',
 'intro':'從整理物品、選擇運送方式，到兩地交接與詢價。依照自己的需求逐步準備，再把資料交給專員確認。',
 'start':'填寫詢價資料', 'route':'你的路線', 'browse':'依照需求，了解下一步',
 'steps':[
  ('確認路線與日期','先準備出發地與目的地的五位數 ZIP Code、可取件日期區間，以及預計入住時間。取件與送達日期需要專員與承運方確認；不要直接把歷史案例的天數當成承諾。',['auto','moving']),
  ('分開列出車輛與搬家物品','車輛請提供年份、品牌、型號、是否能正常行駛、尺寸與改裝情況。搬家物品請記錄紙箱數量與尺寸、家具照片，以及易碎、大型或需拆裝的物品。車與家具可能分開運送。',['auto','moving','luggage']),
  ('確認兩地搬運條件','說明樓層、樓梯、電梯預約、門禁、裝卸區、停車限制與可搬運時段。若大車無法靠近，或需要額外搬運、拆裝及包裝，請先詢問是否提供與如何計費。',['moving','pricing']),
  ('釐清運送與倉儲選項','運車時可詢問開放式或封閉式方案的適用條件。入住前需要暫存時，請告知物品類型、預計時間與取回需求，再確認倉儲地點、進出方式、保管與費用。',['open-enclosed','storage']),
  ('看懂報價，再確認安排','請專員列明服務範圍、包含與不包含的項目、附加費、付款節點、報價有效期限、取消條件，以及保險與異常處理流程。網站詢價單只是需求整理，不是預訂成立或正式報價。',['pricing','buy-sell']),
  ('交接前後保留紀錄','取件前拍照並留存物品或車況清單，確認聯絡窗口及交接方式。送達時對照紀錄檢查，如有異常，立即向司機與客服反映並保留證據，依合約程序處理。',['auto','moving','student']),
 ],
 'checkTitle':'詢價前，檢查這份清單',
 'check':['兩地 ZIP Code 與可配合日期區間','車型與車況，或物品清單與照片','兩地樓層、電梯、停車及門禁條件','是否需要打包、裝卸、拆裝或暫存','聯絡姓名、電子郵件與特殊需求'],
 'sendTitle':'把需求交給專員，保留自己的副本',
 'send':'填寫資料後會先看到詢價摘要。你可以開啟 Gmail，預填寄給 help@carshipping168.com 的郵件，確認後自行按寄送；物品或車況照片請在 Gmail 另行加入附件。也能下載文字詢價單，或透過電話、LINE 與微信聯絡。網站不會自動寄信，也不代表已完成預訂。',
 'archiveTitle':'想看過去的經驗？',
 'archive':'指南整理準備方法，原文庫則保留兩站過去的文章。原文中的費用、地址、時效與個案敘述可能已過期，請以專員確認為準；原文尚未完整翻譯或逐篇事實核實。',
 'library':'瀏覽原文文章庫','guides':'查看全部搬遷指南'
}
EN={
 'title':'Plan the details before your next move.',
 'intro':'Prepare your inventory, transport options, pickup details and inquiry in one place. Work through the steps that fit your move, then confirm arrangements with the team.',
 'start':'Prepare my inquiry','route':'Your route','browse':'Find your next step',
 'steps':[
  ('Define your route and date window','Gather both five-digit ZIP codes, your available pickup window and expected move-in date. Pickup and delivery dates need confirmation from the team and carrier. Historical transit times are not promises.',['auto','moving']),
  ('List vehicles and household goods separately','For a vehicle, note its year, make, model, running condition, dimensions and modifications. For household goods, list box counts and sizes, furniture photos, and fragile, oversized or disassembly needs. Vehicles and furniture may travel separately.',['auto','moving','luggage']),
  ('Describe access at both locations','Include floors, stairs, elevator reservations, building access, loading zones, parking restrictions and permitted moving hours. Ask whether extra carrying, disassembly or packing is available and how it is charged.',['moving','pricing']),
  ('Discuss transport and storage options','Ask whether open or enclosed vehicle transport fits your needs. If you need storage before moving in, describe the goods, estimated duration and retrieval needs; confirm location, access, care and fees.',['open-enclosed','storage']),
  ('Review the quote before confirming','Request written scope, inclusions and exclusions, additional fees, payment stages, quote validity, cancellation terms, insurance and issue-handling procedures. An inquiry summary is preparation, not a booking or a binding quote.',['pricing','buy-sell']),
  ('Keep records at pickup and delivery','Take photos, retain a condition or inventory list, and confirm contacts and handover procedures. Compare the delivered items with your records. Report discrepancies promptly to the driver and team, preserve evidence and follow your contract.',['auto','moving','student']),
 ],
 'checkTitle':'Your inquiry checklist',
 'check':['Both ZIP codes and available date window','Vehicle details or an inventory with photos','Floors, elevators, parking and access at both ends','Packing, loading, disassembly or storage needs','Contact name, email and special requirements'],
 'sendTitle':'Send your needs and keep a copy',
 'send':'Review your summary, then open Gmail with a draft addressed to help@carshipping168.com. Add any inventory or vehicle photos as attachments in Gmail, check the details and press Send yourself. You can also download a text copy or contact the team by phone, LINE or WeChat. The website does not send email automatically or confirm a booking.',
 'archiveTitle':'Looking for past experiences?',
 'archive':'Guides explain preparation; the original library preserves articles from both sites. Historical prices, addresses, timing and individual experiences may be outdated. Confirm current terms with the team. Original articles are not fully translated or independently fact-checked.',
 'library':'Browse original articles','guides':'Explore all moving guides'
}

def render(b,lang):
 c=EN if lang=='en' else b.simp(TW) if lang=='zh-hans' else TW
 guides={g[0]:g[1] for g in b.GUIDES[lang]}
 link=lambda slug:f'<a href="/{lang}/guides/{slug}/">{b.h(guides[slug])} →</a>'
 schema={'@context':'https://schema.org','@type':'WebPage','name':c['title'],'description':c['intro'],'inLanguage':b.LANGS[lang]['lang'],'url':b.ORIGIN+'/'+lang+'/plan/'}
 crumbs={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'168 Moving & Auto','item':b.ORIGIN+'/'+lang+'/'},{'@type':'ListItem','position':2,'name':c['title'],'item':b.ORIGIN+'/'+lang+'/plan/'}]}
 sections=''.join(f'<li id="plan-step-{i}" class="plan-step"><div><h2>{b.h(t)}</h2><p>{b.h(body)}</p><div class="reading-links">{"".join(link(k) for k in related)}</div></div></li>' for i,(t,body,related) in enumerate(c['steps'],1))
 return b.head(lang,c['title']+' | 168',c['intro'],'plan/',[schema,crumbs])+b.header(lang,'plan/')+f'''<main id="main"><section class="page-hero wrap planner-hero"><h1>{c['title']}</h1><p>{c['intro']}</p><p id="plan-route-summary" role="status"></p><button class="button dark" data-quote>{c['start']}{b.icon('arrow')}</button><a class="text-link" href="#plan-checklist">{c['checkTitle']} ↓</a></section><nav class="wrap plan-jump" aria-label="{c['browse']}">{''.join(f'<a href="#plan-step-{i}">{b.h(t)}</a>' for i,(t,_,__) in enumerate(c['steps'],1))}</nav><div class="wrap plan-layout"><article><ol class="plan-steps">{sections}</ol></article><aside id="plan-checklist" class="plan-checklist"><h2>{c['checkTitle']}</h2><ul>{''.join(f'<li>{b.h(x)}</li>' for x in c['check'])}</ul><button class="button dark" data-quote>{c['start']}{b.icon('arrow')}</button><a href="/{lang}/guides/">{c['guides']} →</a><a href="/{lang}/library/">{c['library']} →</a></aside></div><section class="wrap plan-send"><h2>{c['sendTitle']}</h2><p>{c['send']}</p><button class="button dark" data-quote>{c['start']}{b.icon('arrow')}</button></section><section class="wrap plan-history"><h2>{c['archiveTitle']}</h2><p>{c['archive']}</p><div class="reading-links"><a href="/{lang}/guides/">{c['guides']} →</a><a href="/{lang}/library/">{c['library']} →</a></div></section></main>'''+b.footer(lang)+b.end(lang,'plan/')
