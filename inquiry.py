"""Localised email inquiry UI shared by all generated pages."""
from bs4 import BeautifulSoup

COPY = {
 'zh-hant': ['聯絡姓名','聯絡電子郵件','用 Gmail 寄出詢價','使用其他郵件軟體','填寫資料後可開啟 Gmail 寄出詢價單，或下載保存。費用由專員確認。','確認內容後，開啟 Gmail 自行寄出；你也可以下載詢價單或使用其他方式聯絡。','完成後可用 Gmail 寄出詢價，或下載保存。','副本寄給我'],
 'zh-hans': ['联系姓名','联系电子邮箱','用 Gmail 发送询价','使用其他邮件软件','填写资料后可打开 Gmail 发送询价单，或下载保存。费用由专员确认。','确认内容后，打开 Gmail 自行发送；也可以下载询价单或使用其他方式联系。','完成后可用 Gmail 发送询价，或下载保存。','副本发给我'],
 'en': ['Contact name','Contact email','Send inquiry with Gmail','Use another email app','Open Gmail to send your inquiry or download a copy. Pricing requires team confirmation.','Review your inquiry, then open Gmail and send it yourself, download a copy, or contact us another way.','Send with Gmail or download your inquiry after review.','Email me a copy'],
}

def apply_inquiry(s, lang):
 c=COPY[lang];form=s.select_one('#inquiry-form')
 if not form:return
 fields=BeautifulSoup('<div class="field-row"><label></label><label></label></div>','html.parser')
 for label,text,name in zip(fields.select('label'),c[:2],['name','email']):
  label.string=text
  inp=s.new_tag('input',attrs={'name':name,'type':'email' if name=='email' else 'text','required':'','maxlength':'254' if name=='email' else '100','autocomplete':name})
  label.append(inp)
  if name=='email':
   inp.attrs.pop('required',None)
   label.contents[0].replace_with(text+(' (optional)' if lang=='en' else '（選填）' if lang=='zh-hant' else '（选填）'))
 form.insert(0,fields)
 s.select_one('#wizard-form>p:not(.eyebrow)').string=c[4]
 s.select_one('#wizard-summary>p:not(.eyebrow)').string=c[5]
 s.select_one('#wizard-summary .fine').string=c[4]
 quick=s.select_one('#quick-form>small')
 if quick:quick.string=c[6]
 top=s.select_one('.topbar .wrap>span')
 if top:top.string={'zh-hant':'概念展示網站 · 詢價由你確認後寄出','zh-hans':'概念展示网站 · 询价由你确认后发送','en':'Concept demo · Review and send your own inquiry'}[lang]
 download=s.select_one('#download-summary')
 actions=s.new_tag('div',attrs={'class':'email-actions'});download.insert_before(actions)
 for ident,label in [('send-inquiry',c[2]),('email-draft',c[3])]:
  b=s.new_tag('button',attrs={'id':ident,'class':'button dark' if ident=='send-inquiry' else 'text-button','type':'button'});b.string=label;actions.append(b)
 consent=s.new_tag('label',attrs={'class':'copy-consent'});check=s.new_tag('input',attrs={'type':'checkbox','id':'email-copy'});consent.append(check);consent.append(' '+c[7]);actions.insert_before(consent)
 status=s.new_tag('p',attrs={'id':'email-status','class':'email-status','role':'status'});actions.insert_after(status)
 contacts=s.new_tag('div',attrs={'class':'inquiry-contacts'})
 for label,href in [('+1 (626) 873-4458','tel:+16268734458'),('LINE @fsp2682p','https://line.me/ti/p/@fsp2682p')]:
  a=s.new_tag('a',href=href,attrs={'class':'text-link'});a.string=label
  if href.startswith('https:'):a['target']='_blank';a['rel']='noopener noreferrer'
  contacts.append(a)
 wechat=s.new_tag('button',attrs={'type':'button','class':'text-button','id':'inquiry-wechat'});wechat.string='WeChat: carshipping168';contacts.append(wechat);status.insert_after(contacts)
 s.body.append(s.new_tag('script',src='/inquiry.js',defer=''))
