import json, html, csv, re, hashlib, shutil, collections
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from content import GUIDES_TW, GUIDES_EN

ROOT = Path(__file__).parent
D = ROOT / "dist"
R = ROOT / "research"
h = html.escape
summary = json.loads((R / "build-summary.json").read_text(encoding="utf8"))
crawl = json.loads((R / "crawl.json").read_text(encoding="utf8"))
changes = json.loads((R / "changes.json").read_text(encoding="utf8"))
qa = json.loads((R / "qa.json").read_text(encoding="utf8"))
index = {x["url"]: x for x in crawl}
out = D / "reports"
out.mkdir(exist_ok=True)
rules = [
    (
        "地址版本不同",
        "15526 Benfield|14337 Pioneer",
        "高：確認目前辦公、交車與郵寄地址；新版未列實體地址。",
    ),
    (
        "評論數字／評分需更新",
        "170篇|447|4.9",
        "高：動態資料，未在新版展示或加入 AggregateRating。",
    ),
    ("州數錯誤疑點", "51州", "高：原站稱全美51州；新版未沿用，服務範圍待業主確認。"),
    (
        "地名疑點",
        "康州雪城|康州.*Syracuse",
        "高：Syracuse 與州名的對應疑點；封存原文未改，正式重刊前需依訂單與作者核實。",
    ),
    (
        "歷史價格",
        "\$\s*\d|美金|美元|\d+美",
        "中：僅原案例，不能當成現行價格；新版指南不引用固定金額。",
    ),
    (
        "到貨／取件保證",
        "保证|保證|一定|最短|保证准时|保證準時",
        "中：不可直接擴大成服務承諾；新版改為個案協調。",
    ),
    (
        "行李重量與免費條件",
        "100\s*(lbs|Lbs|磅)|免费|免費",
        "中：重量、費用及行李保險依車隊與訂單確認。",
    ),
    (
        "保險或牌照敘述",
        "保险|保險|执照|執照|牌照",
        "高：保單、承運人身分、牌照狀態尚未向主管機關核實；新版不列保額或牌照宣稱。",
    ),
    (
        "付款資訊",
        "318889802|322271627|ZELLE ACCOUNT|SWIFT",
        "高：僅原站歷史資訊，新版指南不重刊銀行帳號；實際付款須核對。",
    ),
]
riskrows = []
for row in changes:
    r = index.get(row["source_url"], {})
    f = R / (hashlib.sha1(row["source_url"].encode()).hexdigest() + ".html")
    body = ""
    if f.exists():
        s = BeautifulSoup(f.read_text(encoding="utf8"), "html.parser")
        node = s.select_one(".entry-content")
        body = node.get_text(" ", strip=True) if node else ""
    found = []
    for label, pattern, note in rules:
        m = re.search(pattern, body, re.I)
        if m:
            snippet = body[max(0, m.start() - 45) : min(len(body), m.end() + 90)]
            riskrows.append(
                {
                    "source_url": row["source_url"],
                    "title": row["source_title"],
                    "issue": label,
                    "evidence_excerpt": snippet,
                    "handling": note,
                    "status": "需業主／作者核對；自動規則篩選，未逐篇人工背書",
                }
            )
            found.append(label)
    row["risk_flags"] = "; ".join(found)
    row["review_status"] = (
        "原文未逐篇事實核實；非全篇英譯"
        if row["action"] == "original-body-preserved"
        else "參見處理方式與風險清單"
    )
    t = unquote(row["source_url"]) + " " + row["source_title"]
    guide = "auto"
    if "haobun.com" in t:
        guide = "moving"
    if re.search("封闭|封閉|open-or-enclosed", t):
        guide = "open-enclosed"
    elif re.search("行李|personalitems", t):
        guide = "luggage"
    elif re.search("仓储|倉儲|存放|寄放", t):
        guide = "storage"
    elif re.search("买卖|買賣|buy-car", t):
        guide = "buy-sell"
    elif re.search("价|價|付款|payment|cost|rate", t):
        guide = "pricing"
    elif re.search("留学|留學|毕业|畢業", t):
        guide = "student"
    row["suggested_topic_guide"] = "/zh-hant/guides/" + guide + "/"
    row["migration_note"] = "僅主題建議，不是已核准301對應；內容不等價時不能直接重導。"


def csvwrite(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


csvwrite(out / "content-changes.csv", changes)
csvwrite(out / "content-risks.csv", riskrows)
shutil.copy(R / "qa.json", out / "qa.json")
shutil.copy(R / "build-summary.json", out / "build-summary.json")
cross = []
from build import SOURCE_KEYS

for tw, en in zip(GUIDES_TW, GUIDES_EN):
    for key in tw[4]:
        u = SOURCE_KEYS.get(key, "")
        r = index.get(u, {})
        f = R / (hashlib.sha1(u.encode()).hexdigest() + ".html")
        text = ""
        if f.exists():
            soup = BeautifulSoup(f.read_text(encoding="utf8"), "html.parser")
            e = soup.select_one(".entry-content")
            text = e.get_text(" ", strip=True) if e else ""
        cross.append(
            {
                "source_url": u,
                "new_guide": "/zh-hant/guides/" + tw[0] + "/",
                "new_title": tw[1],
                "original_excerpt": text[:450],
                "new_summary_zh_hant": tw[2],
                "new_summary_en": en[2],
                "change_reason": "兩站主題整合、縮短重複介紹、答覆前置、移除固定價／固定時程與未核實宣稱；內容是新編摘要，不是原文章逐字翻譯。",
                "review_status": "英文人工編寫、簡體字形轉換；業務事實與全文翻譯仍須業主審校。",
            }
        )
csvwrite(out / "guide-rewrite-comparison.csv", cross)
counts = collections.Counter(x["action"] for x in changes)
viol = sum(len(x["violations"]) for x in qa["accessibility"])
errors = len(qa["errors"])
overflow = sum(x["overflow"] for x in qa["pages"])
stats = f"""<div class="stats"><div><b>{summary['source_urls']}</b><span>檢查網址（含變體／列表）</span></div><div><b>{summary['original_articles']}</b><span>去重後封存文章正文</span></div><div><b>3</b><span>語言：EN／简／繁</span></div><div><b>24</b><span>新編指南頁（8主題 × 3語）</span></div></div>"""
issues = [
    [
        "地址不一致",
        "首頁評論區顯示 14337 Pioneer Blvd Unit 63，聯絡頁與付款頁出現 15526 Benfield Ave。",
        "新版暫不列街道地址，保留兩站一致的主要電話、Email、WeChat 與 LINE。",
        "確認目前辦公、收件、交車與付款郵寄地址。",
    ],
    [
        "州數與地名疑點",
        "品牌頁稱「全美51州」；部分文章將 Syracuse 稱作「康州雪城」。",
        "新版不沿用錯誤州數；原文封存保留，不擅自改寫故事路線。",
        "以原始訂單、作者與服務範圍資料核實；有疑點不代表整篇判錯。",
    ],
    [
        "評論資料版本不同",
        "兩站出現 4.9、170 篇及 447 reviews 等不同版本。",
        "未顯示評分數字、未使用 AggregateRating、未編造見證。",
        "正式站若使用，需查當日 Google Business Profile 並記錄來源。",
    ],
    [
        "歷史價格與運送天數",
        "過往案例包含美元價格、3天／7天等個案時程。",
        "新版指南改成影響因素與詢價步驟，不承諾固定價格或送達日期。",
        "確認真實報價邏輯、有效期、費用項目與可承諾時程。",
    ],
    [
        "行李與保險",
        "文章中的100 lbs、免費寄放、可放行李等條件可能只適用個案；保險頁正文薄弱。",
        "FAQ要求預先確認承運條件與行李承保；不寫保額、全額保障或牌照有效狀態。",
        "取得目前承運保單、除外條款、理賠步驟與有效牌照。",
    ],
    [
        "付款與敏感交易資訊",
        "原付款頁刊登支票、Zelle與銀行帳號，不同服務付款節點不同。",
        "新編指南只介紹確認流程，不重刊帳號；歷史文章如原本包含資訊，封存仍可能保留。",
        "正式上線前核對收款窗口、帳號與付款規則。",
    ],
    [
        "英文翻譯範圍",
        "原站主要為中文且繁簡混用。",
        "首頁、指南列表與8篇新編指南有完整三語；205篇原文區保留原語言，未冒稱全篇英譯。",
        "如要完整三語文章站，205篇仍需逐篇翻譯、術語與事實審核。",
    ],
    [
        "爬取範圍與資產",
        "870個網址涵蓋sitemap、內部連結、分頁、分類、日期列表及重複變體。",
        "保存HTML快照與狀態；未繞過登入；原圖部分404，使用可讀取實景與標記來源的示意背景。",
        "非公開頁面、未連出的孤立頁、外站社群與影片逐字內容未納入完整性承諾。",
    ],
]
table = (
    lambda rows: '<div class="scroll"><table><thead><tr><th>檢查項目</th><th>原站觀察</th><th>新版處理</th><th>尚待確認</th></tr></thead><tbody>'
    + "".join(
        "<tr>" + "".join("<td>" + h(x) + "</td>" for x in row) + "</tr>" for row in rows
    )
    + "</tbody></table></div>"
)
report = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>168 整站整合與內容修改報告</title><style>*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,'Microsoft JhengHei',sans-serif;color:#18353e;background:#f5f6f1;line-height:1.85}}main{{max-width:1140px;margin:auto;padding:45px 28px 90px}}a{{color:#3d6546;overflow-wrap:anywhere}}h1{{font-size:36px;line-height:1.5;letter-spacing:-1px}}h2{{font-size:25px;margin:52px 0 18px}}h3{{font-size:18px;margin:25px 0 12px}}p,li{{font-size:14px}}.eyebrow{{letter-spacing:3px;font-size:11px;color:#5b7242}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:30px 0}}.stats>div{{padding:24px;background:#18353e;color:white;border-radius:8px}}.stats b{{display:block;color:#d4ef78;font-size:38px;line-height:1.5}}.stats span{{font-size:11px}}.notice{{padding:22px 25px;border-left:4px solid #8fa94e;background:#eaf0dd;border-radius:5px}}.downloads{{display:flex;flex-wrap:wrap;gap:10px}}.downloads a{{display:inline-block;background:#18353e;color:white;padding:10px 18px;border-radius:4px;font-size:12px;text-decoration:none}}table{{border-collapse:collapse;width:100%;background:white;font-size:12px}}th,td{{text-align:left;vertical-align:top;border:1px solid #d6dfd5;padding:16px}}th{{background:#e8eddf}}.scroll{{overflow:auto}}pre{{white-space:pre-wrap;background:#fff;padding:20px;border:1px solid #dbe2d5;font-size:12px;overflow-wrap:anywhere}}.muted{{color:#657571}}.comparison{{background:white;padding:25px;border-radius:6px;margin:20px 0}}.comparison small{{color:#6a7f60}}code{{background:#e2e9d9;padding:2px 5px}}@media(max-width:650px){{main{{padding:25px 18px 60px}}h1{{font-size:28px}}.stats{{grid-template-columns:1fr 1fr}}.stats>div{{padding:18px}}table{{min-width:800px}}}}</style></head><body><main><a href="/zh-hant/">← 繁體中文 Demo</a> · <a href="/zh-hans/">简体中文 Demo</a> · <a href="/en/">English demo</a><p class="eyebrow">168 WEBSITE CONSOLIDATION · EDITORIAL CHANGE REPORT</p><h1>兩個網站，一個整合入口。<br>內容改了什麼、依據是什麼、還有哪些風險。</h1><p class="muted">2026-10-30 · 來源：haobun.com、carshipping168.com · 本報告描述目前 Demo，不代表原站已改版。</p>{stats}<div class="notice"><strong>目前結論：</strong>可供瀏覽與操作的三語概念 Demo 已完成；原站未修改。8篇新編指南採完整三語，原文文章區則保留原語言。公開網站整合、逐篇全文英譯、官方業務事實核對與SEO成效驗證尚未完成。不能保證零錯誤；本報告與CSV把已發現疑點、改寫範圍和未驗證項目列出，供逐項審查。</div>
<h2>下載逐頁與逐項報告</h2><div class="downloads"><a href="/reports/content-changes.csv" download>870筆網址處理清單 CSV</a><a href="/reports/content-risks.csv" download>疑點與原文證據 CSV</a><a href="/reports/guide-rewrite-comparison.csv" download>指南原文／改寫對照 CSV</a><a href="/reports/qa.json" download>瀏覽器QA資料 JSON</a></div><p>CSV以UTF-8 BOM儲存，方便Excel開啟。自動疑點標記可能包含誤報；標記不等於已判定文章錯誤。研究HTML快照與完整爬取JSON保存在本機 <code>D:\\Christina\\168-unified-demo\\research</code>。</p>
<h2>1. 爬取範圍與實際數量</h2><p>由兩個首頁、公開sitemap和內部連結遞迴發現，共檢查870個URL，867筆回應200，2筆404，1筆401；發現佇列剩餘0。這是本輪可發現公開網址的覆蓋，不是870篇文章，也不等於涵蓋所有可能存在的孤立網址。URL百分比編碼、不同路徑與列表頁會增加數量。</p><ul><li>文章正文封存：{counts['original-body-preserved']}筆，移除非正文UI後保留原文。</li><li>同正文雜湊去重：{counts['duplicate-body']}筆；不是相似語意文章的自動合併。</li><li>服務參考頁：{counts['service-reference']}筆，做為新編指南來源。</li><li>清單／分類／分頁／錯誤等僅盤點：{counts['inventory-only']}筆。</li><li>未爬取管理目錄、不繞過登入；不送出原站表單。發現robots中運車站10秒間隔後，後續改為單線序列延遲並完成剩餘發現頁。</li></ul><p>2筆404為舊搬家服務連結與舊優勢頁；401是wp-login.php登入入口。原站失效圖片另記於本機資產下載記錄。沒有將不存在的頁面補成假文章。</p>
<h2>2. 新網站架構與三語範圍</h2><ul><li>3個語言獨立路徑：<code>/en/</code>、<code>/zh-hans/</code>、<code>/zh-hant/</code>。</li><li>每語包含：首頁、指南列表、8篇新編指南，共30個有完整三語內容的主頁／指南頁。</li><li>原文資料庫有3語操作介面、標題搜尋、服務分類與分頁；文章正文仍保留原語言，每篇明確標記未全文英譯。</li><li>功能：服務切換、ZIP路線帶入、起終點交換、三語切換保留詢價資料、日期與ZIP驗證、本機摘要與文字檔下載、微信與LINE聯絡。</li><li>沒有訂單、付款、真實報價或表單傳送後端。詢價僅儲存在該瀏覽器分頁的sessionStorage，沒有傳到原公司。</li></ul>
<h2>3. 文章與頁面具體怎麼改</h2><h3>原文封存</h3><p>保留正文的文字、歷史日期與來源連結；HTML快照另存本機。新版封存頁把正文以純文字段落重排，去掉導航、側欄、表單與部分分享元件。原圖、影片、原連結位置及全部格式不會完整重現，因此這是正文文字封存，不是像素級鏡像。每篇記錄正文SHA-256，可核對文字來源。未做逐篇事實更正、未將個案價錢轉成現行報價。</p><h3>新編指南</h3><p>以問題為入口，開頭先給簡短答案，再列準備資料、流程、限制與確認事項。兩站重複主題整合為8篇，而非把所有舊文章一口氣改寫成行銷文。英文重新編寫對應語意；簡體以OpenCC字形轉換為基礎，不能視為已由當地專業編輯全面校對。原案例姓名、故事、金額與到貨天數沒有任意翻寫為新見證。</p>
{''.join(f'<div class="comparison"><small>主題 {i+1:02d} · <a href="/zh-hant/guides/{g[0]}/">繁體版</a> · <a href="/zh-hans/guides/{g[0]}/">简体版</a> · <a href="/en/guides/{g[0]}/">English</a></small><h3>{h(g[1])}</h3><p><strong>新版摘要：</strong>{h(g[2])}</p><p><strong>調整方式：</strong>問答式標題、答案前置、依準備／確認／交付拆段、附原站來源；移除不適合通用的固定價格和保證。</p></div>' for i,g in enumerate(GUIDES_TW))}
<h2>4. 錯誤風險與原站疑點</h2>{table(issues)}<p>新版沒有杜撰客戶評論、送達績效、倉庫數量、牌照號碼或保險金額。未核實的公司細節不能靠文章間互相轉述就當成已證實。CSV另提供逐URL疑點與原文片段。</p>
<h2>5. SEO／AEO 已實作與限制</h2><ul><li>靜態HTML輸出：首頁和指南的主要內容不依賴JavaScript抓取。</li><li>每頁title、description、單一H1、語意標題、canonical、OG與社群預覽圖。</li><li>完整翻譯頁使用zh-Hant、zh-Hans、en及x-default互指；語言切換保持對應頁面。</li><li>首頁Organization與可見FAQ對應的FAQPage；指南Article與BreadcrumbList。沒有虛構Review／AggregateRating／價格Offer。</li><li>30頁sitemap與語言對應；原文封存不列入可索引主內容清單。封存與資料庫保留noindex。</li><li>AEO以可讀的短答、具體步驟、來源與限制為核心；llms.txt僅是導覽輔助。</li><li>Demo保留robots Disallow與noindex，私人預覽不以索引為目的。真正上線時需改正式網域與canonical、確認來源權利與資訊，並開放核准頁面索引。</li></ul><div class="notice">Google最新文件指出：AI搜尋仍使用SEO基礎，不需要特殊AI檔案或特殊schema。2026年FAQ搜尋複合結果已停止顯示；llms.txt不會正向或負向改變Google排名。因此本案的FAQ標記僅提供語意結構，不宣稱能產生FAQ搜尋版位或AI引用。</div><p>依據：<a href="https://developers.google.com/search/docs/specialty/international/localized-versions">Google多語頁面文件</a>、<a href="https://developers.google.com/search/docs/appearance/ai-features">AI features and your website</a>、<a href="https://developers.google.com/search/updates">Google官方更新（2026年5–6月FAQ與llms.txt說明）</a>。</p>
<h2>6. 原站SEO權重怎麼保留</h2><p>本次沒有對原站做任何重導或DNS變更。870筆CSV中的主題指南連結僅是分類建議，不是可直接上線的301規則。正式遷移需先選定主網域，保留高價值文章獨立URL與對應內容，逐URL決定保留／合併／移除；不能把所有文章一起301到首頁。需在原站設定可核對的301，測試www與非www及編碼變體，更新內部連結、sitemap、canonical與Search Console。沒有Search Console／流量／反向連結資料，因此未評估歷史權重，也不能預測排名變化。</p>
<h2>7. QA結果與尚未驗證項目</h2><p>本輪瀏覽器檢查：{len(qa['pages'])}組代表頁面（3語 × 桌機／390px手機 × 首頁／指南列表／指南正文／原文列表）；非200或橫向溢出：{overflow}；JavaScript頁面錯誤：{errors}。三語首頁axe自動檢查的違規項目數：{viol}。這不是完整WCAG認證，也不是所有文章的人工作品審查。</p><ul>{''.join('<li>'+h(t)+'</li>' for t in qa['interactions'])}</ul><p>沒有完成：真實後端送單、正式付款、跨瀏覽器實機、所有205篇逐篇人工校稿、正式網域Core Web Vitals、Google索引／Rich Results工具驗證、Search Console成效或AI平台引用實測。原文庫的搜尋靠JavaScript；原文頁本身是靜態HTML。</p>
<h2>8. 素材與交付</h2><p>運車、貨車與打包照片取自原站，來源列在本機research/assets.json與原站HTML；道路背景取自Unsplash，作為示意場景，不宣稱為168拍攝或真實運送路線。hero.jpg未使用於首頁。正式公開商業站需確認原站素材與第三方授權，替換未確認素材。</p><p>主目錄：<code>D:\\Christina\\168-unified-demo</code>。<code>content.py</code>為三語文案；<code>build.py</code>產生頁面；<code>report.py</code>產生報告；<code>dist</code>為可部署成果；<code>research</code>保存爬取證據與QA。修改文案後需重建、重新執行相關QA並更新報告。本版未變更兩個原站任何檔案。</p><p class="muted">本報告最後一筆事實核對日期：2026-10-30。網站可讀不等於事實已審核；技術通過也不等於視覺與內容已獲業主接受。</p></main></body></html>"""
report = report.replace(
    "<h2>8. 素材與交付</h2>",
    "<h2>部署與本機預覽狀態</h2><p>雲端Sites後續查詢回覆Sites project not found，未完成發布；以本機Demo與ZIP交付。保留原專案ID，未重複建立，也未更動兩個原網站。</p><h2>8. 素材與交付</h2>",
)
(D / "report.html").write_text(report, encoding="utf8")
(ROOT / "修改報告.html").write_text(report, encoding="utf8")
print(
    json.dumps(
        {
            "report": "dist/report.html",
            "risk_rows": len(riskrows),
            "url_rows": len(changes),
            "guide_comparisons": len(cross),
            "axe_violations": viol,
        }
    )
)
