import json, re, hashlib, html, csv, collections
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
from opencc import OpenCC
from content import (
    TW, EN, GUIDES_TW, GUIDES_EN,
    CONTENT_DATE, PHONE_E164, PHONE_DISPLAY, PHONE_SCHEMA, EMAIL,
)
from optimize_images import optimize as optimize_images

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
ORIGIN = "https://one68-moving-demo-20261030.aa920602.chatgpt.site"
GFONTS_URL = "https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&display=swap"
# Label keys app.js reads as `c.<key>` (c = data.labels), plus `quote`, which
# polish.py reads back from the embedded JSON. Keep in sync with dist/app.js:
# archiveFilters, close, copied, date, dateError, details, emptyDetails, from,
# menu, noResults, originalRead, quote, results, summary, summaryNote, to,
# types, zipError
SITE_DATA_KEYS = (
    "archiveFilters", "close", "copied", "date", "dateError", "details",
    "emptyDetails", "from", "menu", "noResults", "originalRead", "quote",
    "results", "summary", "summaryNote", "to", "types", "zipError",
)
PUBLIC_INDEXING = False  # Enable only for an approved, authoritative production domain.
cc = OpenCC("t2s")
h = html.escape


def simp(v):
    if isinstance(v, str):
        return cc.convert(v)
    if isinstance(v, list):
        return [simp(x) for x in v]
    if isinstance(v, dict):
        return {k: simp(x) for k, x in v.items()}
    return v


CN = simp(TW)
CN.update(lang="zh-Hans", name="简体中文")
LANGS = {"zh-hant": TW, "zh-hans": CN, "en": EN}
GUIDES = {"zh-hant": GUIDES_TW, "zh-hans": simp(GUIDES_TW), "en": GUIDES_EN}
source = json.loads((ROOT / "research/crawl.json").read_text(encoding="utf8"))
SOURCE_KEYS = {
    "services": "https://haobun.com/services/",
    "process": "https://www.carshipping168.com/sample-page/",
    "quote": "https://www.carshipping168.com/car-transportation-rate-quote/car-shipping-cost-calculate/",
    "payment": "https://www.carshipping168.com/carshipping-168-payment-instruction/",
    "open-enclosed": "https://www.carshipping168.com/articles/open-or-enclosed-car-shipping/",
    "luggage": "https://www.carshipping168.com/car-transportation-rate-quote/personalitems/",
}
for r in source:
    title = r.get("title", "")
    u = r["url"]
    if "haobun.com" in u and "时间与流程" in unquote(u):
        SOURCE_KEYS["moving-process"] = u
    if "carshipping168.com" in u and "買賣二手車服務" in unquote(u):
        SOURCE_KEYS["buy-sell"] = u
    if "carshipping168.com" in u and "留学生指南" in unquote(u):
        SOURCE_KEYS["student"] = u
SOURCE_KEYS.setdefault("moving-process", "https://haobun.com/services/")
SOURCE_KEYS.setdefault("student", "https://www.carshipping168.com/")
SOURCE_KEYS.setdefault("buy-sell", "https://www.carshipping168.com/")


def write(path, text):
    if str(path).endswith(".html") and path != "index.html":
        from polish import polish_document

        text = polish_document(text, path)
    p = DIST / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf8")


def icon(name):
    paths = {
        "arrow": '<path d="M4 12h16m-6-6 6 6-6 6"/>',
        "car": '<path d="m5 7 2-4h10l2 4 2 3v8H3v-8zM3 10h18M7 14h1m8 0h1M6 18v3m12-3v3"/>',
        "box": '<path d="m3 6 9-4 9 4v12l-9 4-9-4zM3 6l9 4 9-4m-9 4v12M7 4l10 4"/>',
        "pin": '<path d="M19 10c0 6-7 12-7 12S5 16 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="9" r="2"/>',
        "check": '<path d="m5 12 4 4L19 6"/>',
        "phone": '<path d="m5 3 4 1 1 5-3 2c2 4 3 5 7 7l2-3 5 1 1 4c-2 6-8 2-13-3S0 5 5 3Z"/>',
        "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
        "swap": '<path d="M4 8h16l-4-4M20 16H4l4 4"/>',
        "close": '<path d="m5 5 14 14M5 19 19 5"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
        "shield": '<path d="m12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6zM8 12l3 3 5-6"/>',
        "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
        "chat": '<path d="M21 11a9 9 0 0 1-9 9H4l-3 2 2-6a9 9 0 1 1 18-5ZM7 10h10m-10 4h6"/>',
    }
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths.get(name,paths["arrow"])}</svg>'


def head(lang, title, desc, path, schemas=None, archive=False, html_lang=None):
    c = LANGS[lang]
    robots = "index,follow" if PUBLIC_INDEXING and not archive else "noindex,follow"
    alternates = (
        ""
        if archive
        else "".join(
            f'<link rel="alternate" hreflang="{d["lang"]}" href="{ORIGIN}/{l}/{path}">'
            for l, d in LANGS.items()
        )
        + f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}/en/{path}">'
    )
    canonical = (
        f"{ORIGIN}/{path}"
        if path.startswith("original/")
        else f"{ORIGIN}/{lang}/{path}"
    )
    # Fonts moved here from CSS @import so they load in parallel with style.css.
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        # Non-blocking: font-display:swap already renders system text first, so
        # don't hold first paint for the ~140KB Google Fonts stylesheet.
        f'<link rel="stylesheet" href="{h(GFONTS_URL)}" media="print" onload="this.media=\'all\'">'
        f'<noscript><link rel="stylesheet" href="{h(GFONTS_URL)}"></noscript>'
        '<link rel="stylesheet" href="/fonts.css">'
        # Erode 500 is the heading weight, used for English pages only.
        + (
            '<link rel="preload" as="font" type="font/woff2" href="/assets/erode-500.woff2" crossorigin>'
            if lang == "en"
            else ""
        )
    )
    return f'''<!doctype html><html lang="{html_lang or c['lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><meta name="description" content="{h(desc)}"><meta name="robots" content="{robots}"><link rel="canonical" href="{canonical}">{alternates}<meta property="og:type" content="website"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/social.jpg"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#142e37"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">{fonts}<link rel="stylesheet" href="/style.css">{''.join('<script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('</','<\\/')+'</script>' for s in (schemas or []))}</head><body>'''


def header(lang, path=""):
    c = LANGS[lang]
    ids = ["services", "routes", "process", "guides", "about"]
    return f"""<a class="skip" href="#main">Skip to content</a><div class="topbar"><div class="wrap"><span>{h(c['demo'])}</span><a href="tel:{PHONE_E164}">{icon('phone')} {PHONE_DISPLAY}</a></div></div><header class="header"><div class="wrap nav"><a class="brand" href="/{lang}/" aria-label="168 Moving and Auto"><b>168<span>↗</span></b><div>MOVING & AUTO<small>EVERY MILE, MORE PERSONAL.</small></div></a><nav id="navlinks" aria-label="Main">{''.join(f'<a href="/{lang}/#{i}">{h(t)}</a>' for i,t in zip(ids,c['nav']))}</nav><div class="nav-actions"><div class="language">{icon('globe')}<select aria-label="Language" id="language">{''.join(f'<option value="{l}" {"selected" if lang==l else ""}>{d["name"]}</option>' for l,d in LANGS.items())}</select></div><button class="button dark nav-quote" data-quote>{h(c['quote'])}{icon('arrow')}</button><button class="menu-button" aria-label="{h(c['menu'])}" aria-controls="navlinks" aria-expanded="false">{icon('menu')}</button></div></div></header>"""


def footer(lang):
    c = LANGS[lang]
    return f"""<section class="contact" id="contact"><div class="wrap contact-grid"><div><p class="eyebrow">LET’S MAKE YOUR NEXT MOVE.</p><h2>{c['contactTitle']}</h2><p>{h(c['contactBody'])}</p><button class="button lime" data-quote>{h(c['quote'])}{icon('arrow')}</button></div><div class="contact-options"><a href="tel:{PHONE_E164}">{icon('phone')}<span>{h(c['phone'])}<strong>{PHONE_DISPLAY}</strong></span>{icon('arrow')}</a><a href="mailto:{EMAIL}">{icon('mail')}<span>{h(c['email'])}<strong>{EMAIL}</strong></span>{icon('arrow')}</a><button data-wechat>{icon('chat')}<span>{h(c['wechat'])}<strong>carshipping168</strong></span>{icon('arrow')}</button><a href="https://line.me/ti/p/@fsp2682p" target="_blank" rel="noopener">{icon('chat')}<span>{h(c['line'])}<strong>@fsp2682p</strong></span>{icon('arrow')}</a></div></div></section><footer><div class="wrap footer-grid"><div><a class="brand" href="/{lang}/"><b>168<span>↗</span></b><div>MOVING & AUTO</div></a><p>{h(c['footerText'])}</p></div><div><h3>{h(c['footerLinks'][0])}</h3><a href="/{lang}/#services">{h(c['nav'][0])}</a><a href="/{lang}/guides/">{h(c['nav'][3])}</a><a href="/{lang}/library/">{h(c['archive'])}</a></div><div><h3>{h(c['footerLinks'][2])}</h3><a href="https://haobun.com/" target="_blank" rel="noopener">haobun.com ↗</a><a href="https://www.carshipping168.com/" target="_blank" rel="noopener">carshipping168.com ↗</a><a href="/report.html">{h(c['report'])} ↗</a></div></div><div class="wrap footer-bottom"><span>© 2026 168 Moving & Auto · Concept demo</span><p>{h(c['footerNote'])}</p></div></footer><button class="floating-contact" data-quote aria-label="{h(c['quote'])}">{icon('chat')}</button>"""


def wizard(lang):
    c = LANGS[lang]
    return f"""<dialog id="quote-dialog"><button class="dialog-close" data-close aria-label="{h(c['close'])}">{icon('close')}</button><div id="wizard-form"><p class="eyebrow">YOUR MOVE, YOUR WAY.</p><h2>{h(c['wizardTitle'])}</h2><p>{h(c['wizardIntro'])}</p><form id="inquiry-form"><label>{h(c['types'][0]+' / '+c['types'][1])}<select name="service">{''.join(f'<option value="{i}">{h(t)}</option>' for i,t in enumerate(c['types']))}</select></label><div class="field-row"><label>{h(c['from'])}<input name="from" required pattern="[0-9]{{5}}" maxlength="5" inputmode="numeric" placeholder="90012"></label><label>{h(c['to'])}<input name="to" required pattern="[0-9]{{5}}" maxlength="5" inputmode="numeric" placeholder="10001"></label></div><label>{h(c['date'])}<input type="date" name="date"></label><label>{h(c['details'])}<textarea name="details" rows="3" maxlength="2000" placeholder="{h(c['detailsPlaceholder'])}"></textarea></label><p role="alert" class="error" id="form-error"></p><button class="button dark" type="submit">{h(c['review'])}{icon('arrow')}</button></form></div><div id="wizard-summary" hidden><p class="eyebrow">READY FOR THE NEXT STEP.</p><h2>{h(c['summary'])}</h2><p>{h(c['summaryNote'])}</p><dl id="summary-fields"></dl><button class="button dark" id="download-summary">{h(c['download'])}{icon('arrow')}</button><button class="text-button" id="edit-summary">{h(c['edit'])}</button><p class="fine">{h(c['success'])}</p></div></dialog><dialog id="wechat-dialog"><button class="dialog-close" data-close aria-label="{h(c['close'])}">{icon('close')}</button><h2>WeChat</h2><img class="qr" src="/assets/wechat.png" alt="168 WeChat QR code"><p>carshipping168</p><button class="button dark" id="copy-wechat">{h(c['copy'])}</button></dialog><div id="toast" role="status"></div>"""


def end(lang, path=""):
    return (
        wizard(lang)
        + f'<script id="site-data" type="application/json">{json.dumps({"lang":lang,"path":path,"labels":{k:LANGS[lang][k] for k in SITE_DATA_KEYS}},ensure_ascii=False).replace("</","<\\/")}</script><script src="/app.js" defer></script></body></html>'
    )


def guide_cards(lang, all=False):
    c = LANGS[lang]
    gs = GUIDES[lang] if all else [GUIDES[lang][0], GUIDES[lang][1], GUIDES[lang][4]]
    ims = ["transport.jpg", "moving.jpg", "road.jpg"]
    return (
        '<div class="guide-grid">'
        + "".join(
            f"""<a class="guide-card" href="/{lang}/guides/{g[0]}/"><div class="guide-image"><img src="/assets/{ims[i%3]}" alt="" loading="lazy"><span>0{i+1} / {h(c['guideLabel'])}</span></div><div><h3>{h(g[1])}</h3><p>{h(g[2])}</p><span class="read-link">{h(c['read'])}{icon('arrow')}</span></div></a>"""
            for i, g in enumerate(gs)
        )
        + "</div>"
    )


def home(lang):
    c = LANGS[lang]
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "168 Moving & Auto",
            "url": ORIGIN + "/" + lang + "/",
            "telephone": PHONE_SCHEMA,
            "email": EMAIL,
            "sameAs": ["https://haobun.com/", "https://www.carshipping168.com/"],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "inLanguage": c["lang"],
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in c["faqs"]
            ],
        },
    ]
    s = head(lang, c["title"], c["description"], "", schemas) + header(lang)
    s += f"""<main id="main"><section class="hero"><img class="hero-bg" src="/assets/road.jpg" alt="" fetchpriority="high"><div class="hero-shade"></div><div class="wrap hero-inner"><div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span>{h(c['eyebrow'])}</p><h1>{c['hero']}</h1><p class="hero-intro">{h(c['intro'])}</p><a class="button lime" href="#services">{h(c['explore'])}{icon('arrow')}</a><div class="hero-meta"><span>01 / 168 MOVING & AUTO</span><span>{h(c['heroTag'])}</span></div></div><div class="hero-visual"><img src="/assets/transport.jpg" alt="{h(c['photoNote'])}"><div class="photo-label">{icon('pin')} CALIFORNIA → YOUR NEXT CHAPTER</div><span class="visual-caption">{h(c['photoNote'])}</span></div></div><div class="wrap quote-wrap"><div class="quick-quote"><div class="quote-heading"><p class="eyebrow">LET’S GET MOVING</p><h2>{h(c['formTitle'])}</h2><p>{h(c['formSub'])}</p></div><form id="quick-form"><div class="service-tabs" role="group" aria-label="Service">{''.join(f'<button type="button" class="service-tab {"active" if i==0 else ""}" data-service="{i}" aria-pressed="{str(i==0).lower()}">{icon("car" if i==0 else "box" if i==1 else "check")}{h(t)}</button>' for i,t in enumerate(c['types']))}</div><div class="quick-fields"><label>{h(c['from'])}<input name="from" inputmode="numeric" required pattern="[0-9]{{5}}" maxlength="5" placeholder="90012"></label><button type="button" id="swap-zips" aria-label="{h(c['swap'])}">{icon('swap')}</button><label>{h(c['to'])}<input name="to" inputmode="numeric" required pattern="[0-9]{{5}}" maxlength="5" placeholder="10001"></label><button class="button dark" type="submit">{h(c['next'])}{icon('arrow')}</button></div><small>{h(c['note'])}</small></form></div></div></section><div class="trust-strip"><div class="wrap">{''.join(f'<span>{icon("check")}{h(t)}</span>' for t in c['trust'])}</div></div>
 <section class="section wrap" id="services"><div class="section-top"><div><p class="eyebrow">{c['servicesEye']}</p><h2>{c['servicesTitle']}</h2></div><p class="section-intro">{h(c['servicesIntro'])}</p></div><div class="service-grid">"""
    for i, v in enumerate(c["services"]):
        slug, title, tag, desc, features, img = v
        s += f'<a class="service-card" href="/{lang}/guides/{slug}/"><div class="service-img"><img src="/assets/{img}" alt="{h(title)}" loading="lazy"><span>0{i+1}</span></div><div class="service-content"><p class="service-kicker">{h(features)}</p><h3>{h(title)}{icon("arrow")}</h3><h4>{h(tag)}</h4><p>{h(desc)}</p></div></a>'
    s += f"""</div></section><section class="route-section" id="routes"><div class="wrap route-layout"><div class="route-copy"><p class="eyebrow">{c['routesEye']}</p><h2>{c['routesTitle']}</h2><p>{h(c['routesIntro'])}</p><div class="route-options">{''.join(f'<button data-route="{a},{b}" class="route-option"><span>{icon("pin")}{h(t)}</span>{icon("arrow")}</button>' for t,(a,b) in zip(c['routeNames'],[('90012','10001'),('94103','98101'),('90012','75201'),('60601','33101')]))}</div><small>{h(c['routeHint'])}</small></div><div class="route-map" aria-label="Illustrative U.S. service route map"><div class="map-grid"></div><svg viewBox="0 0 640 400" role="img" aria-label="Coast to coast route illustration"><defs><pattern id="dots" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.4" fill="#789098" opacity=".5"/></pattern></defs><path d="M80 57 130 72 189 77 233 82 278 79 326 84 349 76 374 87 397 69 416 76 427 98 451 91 475 83 484 109 515 97 538 63 553 50 564 74 557 104 532 124 522 145 499 157 496 186 473 204 455 208 441 236 465 256 486 271 491 302 506 334 494 345 478 328 461 301 435 282 411 271 377 272 351 265 331 283 303 267 291 242 271 235 248 245 226 231 206 224 180 218 160 208 139 207 120 189 110 164 94 144 90 118 78 96Z" fill="url(#dots)" stroke="#627c86" stroke-width="1"/><g fill="none" stroke="#d4ef78" stroke-width="2"><path d="M120 185Q320 24 511 141"/><path d="M110 127Q99 69 144 84"/><path d="M120 185Q244 122 303 241"/><path d="M360 140Q442 197 486 311"/></g><g fill="#d4ef78"><circle cx="120" cy="185" r="6"/><circle cx="511" cy="141" r="6"/><circle cx="110" cy="127" r="4"/><circle cx="144" cy="84" r="4"/><circle cx="303" cy="241" r="4"/><circle cx="360" cy="140" r="4"/><circle cx="486" cy="311" r="4"/></g><g fill="#e8efed" font-family="Arial,sans-serif" font-size="12"><text x="63" y="210">LOS ANGELES</text><text x="502" y="126">NEW YORK</text><text x="116" y="65">SEATTLE</text><text x="271" y="264">DALLAS</text><text x="340" y="123">CHICAGO</text><text x="483" y="331">MIAMI</text></g></svg><div class="map-caption"><span>{h(c['west'])}</span><span class="map-line"></span><span>{h(c['east'])}</span></div><div class="map-note">ONE TEAM.<br><strong>EVERY MILE.</strong></div></div></div></section>
 <section class="section wrap" id="process"><div class="section-top"><div><p class="eyebrow">{c['processEye']}</p><h2>{c['processTitle']}</h2></div><a class="text-link" href="/{lang}/guides/auto/">{h(c['read'])}{icon('arrow')}</a></div><div class="process-grid">{''.join(f'<div class="step"><span>0{i+1}</span><h3>{h(t)}</h3><p>{h(b)}</p></div>' for i,(t,b) in enumerate(c['steps']))}</div></section>
 <section class="guides-section" id="guides"><div class="wrap"><div class="section-top"><div><p class="eyebrow">{c['guidesEye']}</p><h2>{h(c['guidesTitle'])}</h2><p>{h(c['guidesIntro'])}</p></div><a class="text-link" href="/{lang}/guides/">{h(c['allGuides'])}{icon('arrow')}</a></div>{guide_cards(lang)}</div></section>
 <section class="section wrap about-section" id="about"><div class="about-photo"><img src="/assets/moving.jpg" alt="{h(c['services'][1][1])}" loading="lazy"><span class="photo-stamp">168<br><small>HANDLED WITH CARE.</small></span></div><div><p class="eyebrow">{c['aboutEye']}</p><h2>{c['aboutTitle']}</h2><p>{h(c['aboutBody'])}</p><ul class="check-list">{''.join(f'<li>{icon("check")}{h(x)}</li>' for x in c['aboutList'])}</ul></div></section><section class="faq-section"><div class="wrap faq-layout"><div><p class="eyebrow">GOOD QUESTIONS. CLEAR ANSWERS.</p><h2>{h(c['faqTitle'])}</h2><p>{h(c['faqIntro'])}</p><a class="text-link" href="#contact">{h(c['faqMore'])}{icon('arrow')}</a></div><div>{''.join(f'<details {"open" if i==0 else ""}><summary><span>0{i+1}</span>{h(q)}<b>+</b></summary><p>{h(a)}</p></details>' for i,(q,a) in enumerate(c['faqs']))}</div></div></section></main>"""
    return s + footer(lang) + end(lang)


def guides_page(lang):
    c = LANGS[lang]
    return (
        head(lang, c["nav"][3] + " | 168 Moving & Auto", c["guidesIntro"], "guides/")
        + header(lang, "guides/")
        + f'<main id="main"><section class="page-hero wrap"><p class="eyebrow">{c["guidesEye"]}</p><h1>{h(c["guidesTitle"])}</h1><p>{h(c["guidesIntro"])}</p><a class="text-link" href="/{lang}/library/">{h(c["archive"])}{icon("arrow")}</a></section><section class="wrap section compact">{guide_cards(lang,True)}</section></main>'
        + footer(lang)
        + end(lang, "guides/")
    )


def guide_page(lang, g):
    c = LANGS[lang]
    slug, title, answer, sections, keys = g
    path = "guides/" + slug + "/"
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": answer,
        "inLanguage": c["lang"],
        "dateModified": CONTENT_DATE,
        "author": {"@type": "Organization", "name": "168 website demo editorial team"},
        "publisher": {"@type": "Organization", "name": "168 Moving & Auto"},
        "mainEntityOfPage": ORIGIN + "/" + lang + "/" + path,
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "168 Moving & Auto",
                "item": ORIGIN + "/" + lang + "/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": c["nav"][3],
                "item": ORIGIN + "/" + lang + "/guides/",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": title,
                "item": ORIGIN + "/" + lang + "/" + path,
            },
        ],
    }
    return (
        head(lang, title + " | 168 Moving & Auto", answer, path, [schema, crumbs])
        + header(lang, path)
        + f"""<main id="main"><div class="wrap article-top"><a href="/{lang}/guides/">← {h(c['nav'][3])}</a><p class="eyebrow">{h(c['guideLabel'])} · {h(c['updated'])}</p><h1>{h(title)}</h1><p class="answer-first">{h(answer)}</p></div><div class="wrap article-layout"><article>{''.join(f'<section id="section-{i}"><h2>{h(t)}</h2><p>{h(p)}</p></section>' for i,(t,p) in enumerate(sections))}<aside class="editor-note">{icon('shield')}<p>{h(c['guideDisclaimer'])}</p></aside><div class="article-sources"><h2>{h(c['source'])}</h2>{''.join(f'<a href="{h(SOURCE_KEYS[k])}" target="_blank" rel="noopener">{h(unquote(SOURCE_KEYS[k]))} ↗</a>' for k in keys if k in SOURCE_KEYS)}<a href="/report.html">{h(c['report'])} ↗</a></div></article><aside class="article-aside"><p class="eyebrow">LET’S GET MOVING</p><h2>{h(c['formTitle'])}</h2><p>{h(c['formSub'])}</p><button class="button dark" data-quote>{h(c['quote'])}{icon('arrow')}</button><nav>{''.join(f'<a href="#section-{i}">{h(t)}</a>' for i,(t,p) in enumerate(sections))}</nav></aside></div></main>"""
        + footer(lang)
        + end(lang, path)
    )


s2t = OpenCC("s2t")


def archive_lang(title, text):
    """zh-Hans when title + first 500 chars of body change noticeably under s2t, else zh-Hant."""
    sample = (title + "\n" + text)[:520]
    han = [ch for ch in sample if "\u4e00" <= ch <= "\u9fff"]
    if not han:
        return "zh-Hant"
    changed = sum(a != b for a, b in zip(sample, s2t.convert(sample)))
    return "zh-Hans" if changed / len(han) > 0.03 else "zh-Hant"


def build_archive():
    records = []
    seen = set()
    changes = []
    for r in source:
        u = r["url"]
        key = hashlib.sha1(u.encode()).hexdigest()
        f = ROOT / "research" / (key + ".html")
        row = {
            "source_url": u,
            "http_status": r.get("status", "error"),
            "source_title": r.get("title", ""),
            "action": "inventory-only",
            "new_url": "",
            "body_sha256": "",
            "notes": "Navigation, archive listing, duplicate or inaccessible page; no body rewrite.",
        }
        if r.get("status") != 200 or not f.exists():
            changes.append(row)
            continue
        soup = BeautifulSoup(f.read_text(encoding="utf8"), "html.parser")
        article = soup.select_one("article.et_pb_post")
        entry = soup.select_one(".entry-content")
        # A single WordPress post/page body; archive/listing pages are not treated as articles.
        if (
            not entry
            or soup.body is None
            or any(
                x in soup.body.get("class", []) for x in ["archive", "search", "blog"]
            )
        ):
            changes.append(row)
            continue
        for el in entry.select(
            "script,style,nav,form,.et_social_inline,.sharedaddy,.et_post_meta_wrapper,.yarpp-related,.related-posts"
        ):
            el.decompose()
        body = entry.get_text("\n", strip=True)
        if len(body) < 120:
            changes.append(row)
            continue
        digest = hashlib.sha256(body.encode()).hexdigest()
        if digest in seen:
            row["action"] = "duplicate-body"
            row["body_sha256"] = digest
            changes.append(row)
            continue
        seen.add(digest)
        titleNode = soup.select_one("h1.entry-title") or soup.select_one("h1")
        title = (
            titleNode.get_text(" ", strip=True)
            if titleNode
            else r.get("title", "").split("|")[0].strip()
        )
        # Service/landing pages stay in the inventory; preserve article bodies in the original library.
        is_post = "single-post" in soup.body.get("class", []) or bool(
            article and article.select_one("p.post-meta")
        )
        if not is_post:
            row["action"] = "service-reference"
            row["body_sha256"] = digest
            row["notes"] = (
                "Used as service reference; new trilingual guides are separately authored and sourced."
            )
            changes.append(row)
            continue
        aid = key[:12]
        category = "moving" if "haobun.com" in u else "auto"
        dateNode = soup.select_one("time") or soup.select_one(".published")
        date = dateNode.get_text(" ", strip=True) if dateNode else ""
        records.append(
            {
                "id": aid,
                "title": title,
                "source": u,
                "category": category,
                "date": date,
                "text": body,
                "sha256": digest,
                "url": "/original/" + aid + "/",
            }
        )
        row.update(
            action="original-body-preserved",
            new_url="/original/" + aid + "/",
            body_sha256=digest,
            notes="Body text retained verbatim after removing non-content UI; no factual correction or full English translation. noindex archive.",
        )
        changes.append(row)
    (ROOT / "research/changes.json").write_text(
        json.dumps(changes, ensure_ascii=False, indent=2), encoding="utf8"
    )
    with (ROOT / "research/content-changes.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        w = csv.DictWriter(f, fieldnames=list(changes[0]))
        w.writeheader()
        w.writerows(changes)
    public = [
        {k: v for k, v in r.items() if k not in ["text", "sha256"]} for r in records
    ]
    write("library-data.json", json.dumps(public, ensure_ascii=False))
    for r in records:
        body = "".join(
            "<p>" + h(x) + "</p>" for x in r["text"].splitlines() if x.strip()
        )
        c = TW
        alang = archive_lang(r["title"], r["text"])
        s = head(
            "zh-hant",
            r["title"] + " | 168 原文封存",
            "原站文章正文封存，歷史內容未經事實核實。",
            "original/" + r["id"] + "/",
            archive=True,
            html_lang=alang,
        ) + header("zh-hant")
        s += f'<main id="main" class="original-article wrap"><a href="/zh-hant/library/">← 繁體中文</a> · <a href="/zh-hans/library/">简体中文</a> · <a href="/en/library/">English</a><p class="eyebrow">ORIGINAL-LANGUAGE ARCHIVE · 原文封存</p><h1>{h(r["title"])}</h1><aside class="editor-note"><p>本頁正文保留原站語言與敘述，未全文翻譯、未背書其時效或正確性。歷史費用不是現行報價。<br>Original-language text, not a current offer or an independently verified account.</p></aside><p>{h(r["date"])}</p><p><a href="{h(r["source"])}" target="_blank" rel="noopener">查看原站 / View source ↗</a></p><article class="original-body" lang="{alang}">{body}</article></main>'
        write(
            "original/" + r["id"] + "/index.html",
            s + footer("zh-hant") + end("zh-hant", "library/"),
        )
    return records, changes


def library_page(lang, count):
    c = LANGS[lang]
    return (
        head(
            lang,
            c["archive"] + " | 168 Moving & Auto",
            c["archiveIntro"],
            "library/",
            archive=True,
        )
        + header(lang, "library/")
        + f"""<main id="main"><section class="page-hero wrap"><p class="eyebrow">THE ORIGINAL LIBRARY · {count}</p><h1>{h(c['archive'])}</h1><p>{h(c['archiveIntro'])}</p><p class="library-notice">{h(c['originalNotice'])}</p><div class="library-toolbar"><input type="search" id="library-search" placeholder="{h(c['articleSearch'])}" aria-label="{h(c['articleSearch'])}"><select id="library-category" aria-label="Category">{''.join(f'<option value="{v}">{h(t)}</option>' for v,t in zip(['all','moving','auto'],c['archiveFilters']))}</select></div><p id="library-count" role="status"></p></section><section class="wrap library-results" id="library-results"></section><div class="wrap pagination" id="library-pages"></div></main>"""
        + footer(lang)
        + end(lang, "library/")
    )


def main():
    DIST.mkdir(exist_ok=True)
    optimize_images()
    records, changes = build_archive()
    urls = []
    for lang, c in LANGS.items():
        write(lang + "/index.html", home(lang))
        write(lang + "/guides/index.html", guides_page(lang))
        write(lang + "/library/index.html", library_page(lang, len(records)))
        urls.extend([lang + "/", lang + "/guides/"])
        for g in GUIDES[lang]:
            write(lang + "/guides/" + g[0] + "/index.html", guide_page(lang, g))
            urls.append(lang + "/guides/" + g[0] + "/")
    write(
        "index.html",
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=/zh-hant/"><title>168 Moving & Auto</title></head><body><a href="/en/">English</a> · <a href="/zh-hans/">简体中文</a> · <a href="/zh-hant/">繁體中文</a></body></html>',
    )
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    for u in urls:
        path = u.split("/", 1)[1]
        sitemap += (
            f"<url><loc>{ORIGIN}/{u}</loc><lastmod>{CONTENT_DATE}</lastmod>"
            + "".join(
                f'<xhtml:link rel="alternate" hreflang="{c["lang"]}" href="{ORIGIN}/{l}/{path}"/>'
                for l, c in LANGS.items()
            )
            + "</url>"
        )
    sitemap += "</urlset>"
    write("sitemap.xml", sitemap)
    write(
        "robots.txt",
        f'User-agent: *\nDisallow: {"/original/" if PUBLIC_INDEXING else "/"}\n'
        + (
            "Disallow: /*/library/\n"
            if PUBLIC_INDEXING
            else "# Private concept demo. Enable indexing only on an approved production domain.\n"
        )
        + f"Sitemap: {ORIGIN}/sitemap.xml\n",
    )
    write(
        "llms.txt",
        f"""# 168 Moving & Auto — concept demo
> A private demonstration consolidating public information from haobun.com and carshipping168.com. Not an official current offer. Do not treat historical case prices or transit times as guarantees.

## Languages
- [English]({ORIGIN}/en/)
- [简体中文]({ORIGIN}/zh-hans/)
- [繁體中文]({ORIGIN}/zh-hant/)

## Answer-first guides
"""
        + "".join(
            f"- [{g[1]}]({ORIGIN}/en/guides/{g[0]}/): {g[2]}\n" for g in GUIDES_EN
        )
        + f"\n## Sources and editorial limits\n- [Change report]({ORIGIN}/report.html)\n- [Original moving site](https://haobun.com/)\n- [Original auto transport site](https://www.carshipping168.com/)\n\nPublic articles are retained in an original-language, noindex archive. Full English article translation and owner fact review are not complete. No live quotes, booking, payment or inquiry transmission. llms.txt is a discovery aid, not an indexing or AI citation guarantee.\n",
    )
    write(
        "assets/favicon.svg",
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#142e37"/><text x="7" y="42" font-family="Arial" font-weight="bold" font-size="28" fill="#d4ef78">168</text></svg>',
    )
    (ROOT / "research/build-summary.json").write_text(
        json.dumps(
            {
                "source_urls": len(source),
                "original_articles": len(records),
                "trilingual_authored_pages": len(urls),
                "languages": list(LANGS),
                "actions": dict(collections.Counter(x["action"] for x in changes)),
                "public_indexing": PUBLIC_INDEXING,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf8",
    )
    print(
        json.dumps(
            {
                "original_articles": len(records),
                "trilingual_authored_pages": len(urls),
                "source_urls": len(source),
            }
        )
    )


if __name__ == "__main__":
    main()
