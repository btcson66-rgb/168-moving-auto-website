"""Package local simulation and rendered-review evidence without claiming real users."""
import html
import json
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).parent
D=ROOT/'dist'
OUT=D/'reports/usability-1031'
OUT.mkdir(exist_ok=True)
for name in ['run.json','interviews.json','profiles.json','pilot-seed.md','prompts.jsonl','pages.json','run.py']:
 shutil.copyfile(ROOT/'research/mirofish-review-1031'/name,OUT/name)
for name in ['qa.json','discovery-qa.json','midnight-motion-qa.json','taste-review-lint.txt']:
 shutil.copyfile(ROOT/'research'/name,OUT/name)
shutil.copyfile(ROOT/'MIROFISH_TASTE_REVIEW_20261031.md',OUT/'review.md')
for name in ['owner-home','owner-plan','owner-home-final','owner-plan-final']:
 target=OUT/name;target.mkdir(exist_ok=True)
 for file in (ROOT/'.taste-skill'/name).glob('*'):
  if file.suffix in ['.json','.jpg']:shutil.copyfile(file,target/file.name)
run=json.loads((OUT/'run.json').read_text(encoding='utf8'))
assert run['status']=='completed' and run['interviews']==8
interviews=json.loads((OUT/'interviews.json').read_text(encoding='utf8'))
h=html.escape
responses=''.join(f'<details><summary>第{x["round"]}輪 · {h(x["role"])}</summary><p>{h(x["response"])}</p></details>' for x in interviews)
page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>168｜MiroFish與taste檢查報告</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#0b0405;color:#fff;font:16px/1.9 Arial,'Microsoft JhengHei',sans-serif}}main{{max-width:1100px;padding:36px 24px 80px;margin:auto}}a{{color:#fff;text-underline-offset:5px}}h1{{font-size:40px;line-height:1.3}}h2{{font-size:28px;margin-top:48px}}p{{max-width:76ch;color:#d8cdd3}}.note,details{{padding:22px;background:#150e0f;border:1px solid #382e30;border-radius:4px;margin:16px 0}}summary{{cursor:pointer}}img{{max-width:100%;display:block;border:1px solid #382e30}}.shots{{display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:start}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:16px;border-bottom:1px solid #382e30;vertical-align:top}}li{{margin:12px 0}}@media(max-width:650px){{h1{{font-size:30px}}.shots{{display:block}}.shots img{{margin:20px 0}}td,th{{padding:10px}}}}</style></head><body><main><a href="/zh-hant/?v=audit-1031">← 最新首頁</a> · <a href="/zh-hant/plan/?v=audit-1031">搬遷規劃</a> · <a href="/owner-review.html">上一輪修改報告</a><h1>有測試，也核對模擬是否說錯。</h1><p>2026-10-31 · MiroFish / OASIS 本機受控訪談與 taste skill 兩輪畫面複查。</p><div class="note"><strong>8次模擬訪談已完成，並修正7項細節。</strong><p>4個人工情境、同一本機模型、2輪受控訪談；不是8位真人。模型只讀文字節錄，沒有看過截圖或點擊網站。第二輪受第一輪意見引導，結果不能當成市場統計或轉換預測。</p></div><h2>已修正</h2><ul><li>詢價說明改成由客戶確認後寄出，消除與Gmail功能的矛盾。</li><li>提高小字與部分正文可讀性，收窄長段落。</li><li>移除規劃頁重複品牌與裝飾編號，改為真實有序清單；加強標題層級，縮短手機Hero留白。</li><li>Email改為選填；沒有填Email時停用副本。仍可準備或下載詢價。</li><li>補上報價有效期限確認，以及照片需在Gmail另行加入附件。</li></ul><h2>MiroFish提出的問題，有哪些成立？</h2><table><tr><th>回饋</th><th>核對與處理</th></tr><tr><td>報價細節不清楚</td><td>既有指南已列因素；補強有效期限，不填假費率。</td></tr><tr><td>想知道倉儲政策與費用</td><td>已提供詢問清單；實際政策仍需業主確認。</td></tr><tr><td>「規劃頁有路線圖」</td><td>模型混淆：地圖在首頁，此回饋排除。</td></tr><tr><td>英文角色引用中文頁面</td><td>角色限制失效，不能據此推論英文版問題。</td></tr></table><h2>taste結果</h2><p>保留你指定的Andercore等寬技術字、線框與細線。首頁明確允許這些品牌例外後為<strong>0 FAIL / 4 WARN</strong>。規劃頁仍有<strong>3 FAIL / 2 WARN</strong>，分別是圖片不足、主視覺焦點與動態數量不足，沒有宣稱全數通過。完整主觀截圖評分與未修項見完整報告。</p><p>規劃頁目前以閱讀與詢價為主，未為達成照片及動畫門檻而塞入無關素材。實際美感仍待你觀看確認。</p><div class="shots"><img src="/reports/usability-1031/owner-plan-final/desktop-fold.jpg" alt="複查後桌面規劃頁"><img src="/reports/usability-1031/owner-plan-final/mobile-fold.jpg" alt="複查後手機規劃頁"></div><h2>模擬原始回應</h2><p>下列為未修飾的模型意見，其中包括上面已指出的錯誤。它們不是實際客戶證詞。</p>{responses}<h2>瀏覽器結果與可下載證據</h2><p>30組代表頁、12組規劃頁尺寸、Gmail預填與資料下載、Email選填及內鏈回歸通過；三語首頁與規劃頁axe自動違規0。沒有實際寄信、收件或正式部署證據。</p><p><a href="/reports/usability-1031/review.md">完整修改、評分與限制</a> · <a href="/reports/usability-1031/run.json">MiroFish執行紀錄</a> · <a href="/reports/usability-1031/interviews.json">8次訪談JSON</a> · <a href="/reports/usability-1031/pilot-seed.md">模型實際讀取的節錄</a> · <a href="/reports/usability-1031/discovery-qa.json">流程QA</a> · <a href="/reports/usability-1031/qa.json">頁面QA</a></p><p><a href="/reports/usability-1031/owner-home/report.json">首頁修改前taste</a> · <a href="/reports/usability-1031/owner-home-final/report.json">首頁修改後taste（含品牌例外）</a> · <a href="/reports/usability-1031/owner-plan-final/report.json">規劃頁修改後taste</a></p></main></body></html>'''
(D/'audit-review.html').write_text(page,encoding='utf8')
for name in ['report.html','ui-review.html','midnight-review.html','owner-review.html']:
 p=D/name;s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser');old=s.select_one('#usability-update')
 if old:old.decompose()
 a=s.new_tag('a',href='/audit-review.html',id='usability-update',attrs={'style':'display:block;padding:18px 24px;background:#150e0f;color:white;border-bottom:2px solid #e32735'});a.string='2026-10-31 最新：MiroFish／taste檢查、修正與未通過項目 →';target=s.body or s.select_one('main') or s;target.insert(0,a);p.write_text(str(s),encoding='utf8')
print('Packaged completed simulation and taste evidence')
