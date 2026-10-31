# 168 網站：MiroFish / OASIS 與 taste 複查

日期：2026-10-31。基準：9cae508 加上尚未提交的使用者版面回饋、Gmail、規劃頁與內鏈修改。

## 實際執行的方法

- 使用本機 `D:/Claude/MiroFish-local` 的 MiroFish ProjectManager、LocalGraphStore、SimulationManager 與 OASIS ManualAction INTERVIEW / CREATE_POST。
- 模型 `espner-qwen25`，僅連 `http://127.0.0.1:11434/v1`，四個人工設定角色、兩輪、8次訪談全部完成。
- project `proj_4b834426ab45`；simulation `sim_9c67935baf15`。每次回應已記錄於訪談 JSON 與本機 OASIS SQLite。
- 這是人工種子圖譜與受控訪談，不是自動 ontology/config 全流程，不是自然社群擴散預測。第二輪先看第一輪意見，因此有引導與從眾偏差。
- 輸入來自 Playwright 擷取的七個頁面可見文字；模型實際使用其中四頁節錄。沒有給模型截圖、沒有讓模型操作瀏覽器，也沒有真人客戶或轉換率資料。
- taste skill 先跑實作來源 lint，再在 1440/768/390px 檢視首頁與規劃頁，保留修改前後 JSON 與截圖。首次 lint 誤把 `--help` 當路徑掃到研究封存；該結果排除，正式 lint 僅掃當前首頁、規劃頁與實作 CSS/JS。

## 模擬回饋核對

| 訪談疑點 | 核對結果 | 處理 |
|---|---|---|
| 不清楚影響報價的因素 | PARTIAL。原有 pricing 指南與規劃第五步已列服務範圍、附加費、付款及取消條件；不能判定全站缺漏 | 保留既有內容，不捏造價格表 |
| 想知道報價有效期限 | CONFIRMED。原規劃頁未明寫這項詢問 | 三語第五步補上「報價有效期限」，不承諾實際期限 |
| 想確認倉儲費用、進出方式 | OWNER CONFIRMATION。規劃第四步已有詢問清單，但沒有經營者已核准的固定政策 | 保留為詢價項，不虛構倉儲價格與保管條款 |
| 「規劃頁有示意路線圖」 | REJECTED。地圖在首頁，不在規劃頁 | 標示為模型混淆來源，不據此改版 |
| English-only 角色引用中文 pricing 頁 | INVALID PERSONA EVIDENCE。模型沒有穩定遵守角色限制 | 不推論英文版有導航缺陷；英文入口另外以真實瀏覽器測試 |
| 建議列出所有服務的固定費用 | REJECTED AS UNSUPPORTED。沒有目前核准費率 | 不填入假報價；由專員確認 |

## 已修正的實際問題

1. 頂部「資料不會送出」與 Gmail 手動寄送說明矛盾：改成「詢價由你確認後寄出」，三語一致。
2. 可讀文字小於13px：提高頂部、技術標籤、地圖說明、手機頁尾與表單標籤。相關正文提高至16px。
3. 規劃頁上方重複品牌與裝飾編號：移除重複標籤與01形式；步驟使用真正有序清單。
4. 規劃頁主標題層級偏弱、結尾段落太長：增大桌面標題、限制長段落行寬；手機Hero過多留白縮短。
5. Email原先必填，阻礙下載及電話/LINE使用者：改為選填；未填Email時停用寄送副本選項。
6. 補上「照片需在Gmail手動加入附件」，避免誤以為文字草稿會包含照片。
7. 補上報價有效期限的確認提醒。

## taste 結果與保留項

- 原始首頁5種 FAIL：品牌眉題、等寬字、細線、線框、小字。原始規劃頁包含重複標籤、編號、圖片不足、焦點、動態與小字等問題。
- 最後首頁：明確允許使用者指定 Andercore 的 `eyebrow,mono,hairline,outlined-box` 後 **0 FAIL / 4 WARN**。剩餘警告為重複卡片、字級數、部分正文尺寸與沒有影片，完整內容見JSON。這不是無例外通過。
- 最後規劃頁：只允許品牌細線與線框後，**3 FAIL / 2 WARN**。尚存 `few-pictures`、`focal-point`、`still-page`；沒有宣稱全部通過。規劃頁以可讀清單與詢價為主，目前沒有為湊照片/動態數量而加素材。
- 中性照片遮罩被來源lint視為gradient；依skill本身的neutral scrim例外保留。日期的padStart是日期格式，不是裝飾編號。
- 沒有重新抽設計方向。沿用使用者指定的Andercore配色與字體，避免抽籤覆蓋明確設計偏好；舊seed 974465387只屬更早的紙面風格，不代表本次設計。

## 截圖評分（主觀，不是客戶評分）

ROUND 1

Seen in one second: 首頁為白色標題與實際運車照片；規劃頁為文字與六個跳轉區。

Idea (one sentence): 將兩站分散的車輛與家居搬遷資訊整理成可帶入詢價的同一路徑。

Live thing: ZIP與服務帶入規劃、詢價摘要、Gmail草稿與本機下載。

Layout words by section: hero=photo / services=split / routes=map / guides=list / FAQ=grid / planner=ordered-reading。

Scores: design 7 · usability 7.5 · creativity 6.5 · content 7.5 → overall 7.1，依仍有FAIL上限6.0。

Caps applied: 嚴格house-style FAIL；技術字與線框；規劃頁無照片。

Top three problems:
1. owner-home/mobile-fold.jpg：小字與頂部矛盾文案；提高字級並修正文案。
2. owner-plan/mobile-fold.jpg：重複品牌與數字搶走重點；移除並改語意化清單。
3. owner-plan/desktop-page-01.jpg：結尾段落過寬、桌面標題弱；縮行寬並加強主標題。

ROUND 2

Seen in one second: 首頁照片仍主導；規劃頁標題更清楚，沒有重複品牌標籤。

Idea / live thing / layout: 同上，保留已驗證的操作與內容路徑。

Scores: 首頁 design 7.5 · usability 8 · creativity 6.5 · content 7.5 → 7.5，嚴格裝飾規則上限6.5；規劃頁 design 6.5 · usability 8 · creativity 6 · content 8 → 7.1，仍有FAIL上限6.0。

Caps applied: 指定品牌裝飾；規劃頁圖片不足、視覺焦點與動態數量。未把分數上修成全數通過。

Top three remaining:
1. 規劃頁長篇文字仍缺少可獨立說明搬運/交接的圖示或照片組。
2. 主標題已增大但沒有成為大比例的視覺主體，工具仍判焦點不足。
3. 規劃頁動態數低於skill門檻。保留可讀性，後續可用有資訊價值的互動清單處理。

## 瀏覽器驗證與界線

- 30組代表頁、12組規劃頁尺寸無溢出；三語首頁與規劃頁axe自動違規0；內鏈及JSON-LD檢查通過。
- Gmail預填、下載、微信、路線與語言切換回歸通過；新增Email選填與副本狀態測試通過。
- 沒有實際寄信、真人測試、Gmail收件驗證、正式部署或SEO排名證據。
- 原文正文未改寫。本次模型沒有直接更動程式，所有採用項都由實作與瀏覽器結果核對。
