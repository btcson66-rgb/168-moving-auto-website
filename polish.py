"""Presentation-only refinements. Source articles and service facts remain unchanged."""

from bs4 import BeautifulSoup
from functools import lru_cache
from pathlib import Path
import json
from PIL import Image
from content import CONTENT_DATE
from optimize_images import variants

ASSETS = Path(__file__).parent / "dist" / "assets"
# srcset `sizes` per image container (layout widths from style.css breakpoints).
IMG_SIZES = [
    (".service-img", "(max-width:860px) 100vw, 34vw"),
    (".guide-image", "(max-width:860px) 100vw, 34vw"),
    (".hero-visual", "(max-width:860px) 100vw, 50vw"),
    (".about-photo", "(max-width:860px) 100vw, 50vw"),
]


@lru_cache(None)
def image_size(name):
    with Image.open(ASSETS / name) as im:
        return im.size


def picturize(s):
    """Add real width/height to every local <img>; wrap JPEGs that have WebP variants in <picture>."""
    for img in s.select("img"):
        src = img.get("src", "")
        if not src.startswith("/assets/") or not (ASSETS / src[8:]).exists():
            continue
        name = src[8:]
        w, h = image_size(name)
        img["width"], img["height"] = str(w), str(h)
        if name == "wechat.png":
            img["loading"] = "lazy"
        if not name.endswith(".jpg") or img.parent.name == "picture":
            continue
        vs = variants(name[:-4])
        if not vs:
            continue
        sizes = "100vw"
        for sel, val in IMG_SIZES:
            if img.find_parent(class_=sel[1:]):
                sizes = val
                break
        pic = s.new_tag("picture")
        pic.append(
            s.new_tag(
                "source",
                attrs={
                    "type": "image/webp",
                    "srcset": ", ".join(f"/assets/{f} {vw}w" for vw, f in vs),
                    "sizes": sizes,
                },
            )
        )
        img.wrap(pic)

COPY = {
    "zh-hant": {
        "hero": "車與家，<br>一起出發。",
        "intro": "美國跨州運車與搬家，一個窗口安排。告訴我們路線、日期，以及你要帶走的生活。",
        "services": "你的搬遷，<br>一次安排。",
        "routes": "從這座城市，<br>到你的下一站。",
        "process": "搬遷流程，<br>每一步都清楚。",
        "guides": "出發前，先了解。",
        "about": "用熟悉的語言，<br>安排新的生活。",
        "faq": "你想知道的，<br>先說清楚。",
        "contact": "準備好下一站了嗎？",
        "slip": "車輛與物品，一張需求單。",
        "form": "從路線開始",
        "formSub": "選擇服務，填入兩地郵遞區號。",
        "note": "這是 Demo：可下載需求摘要，尚未送出。",
        "credit": "實景照片取自 168 原站；道路照片為示意。",
        "first": "先了解服務",
        "ui": "UI／UX 優化報告",
        "steps": ["先告訴我們需求", "一起確認方案", "準備交付出發", "到貨檢查簽收"],
    },
    "zh-hans": {
        "hero": "车与家，<br>一起出发。",
        "intro": "美国跨州运车与搬家，一个窗口安排。告诉我们路线、日期，以及你要带走的生活。",
        "services": "你的搬迁，<br>一次安排。",
        "routes": "从这座城市，<br>到你的下一站。",
        "process": "搬迁流程，<br>每一步都清楚。",
        "guides": "出发前，先了解。",
        "about": "用熟悉的语言，<br>安排新的生活。",
        "faq": "你想知道的，<br>先说清楚。",
        "contact": "准备好下一站了吗？",
        "slip": "车辆与物品，一张需求单。",
        "form": "从路线开始",
        "formSub": "选择服务，填写两地邮政编码。",
        "note": "这是 Demo：可下载需求摘要，尚未发送。",
        "credit": "实景照片取自 168 原站；道路照片为示意。",
        "first": "先了解服务",
        "ui": "UI／UX 优化报告",
        "steps": ["先告诉我们需求", "一起确认方案", "准备交付出发", "到货检查签收"],
    },
    "en": {
        "hero": "Car + home.<br>One move.",
        "intro": "Auto transport and interstate moving, planned together. One team to help coordinate your vehicle, belongings and next address.",
        "services": "Your whole move.<br>One place.",
        "routes": "Where are you<br>heading next?",
        "process": "A clear plan,<br>from door to door.",
        "guides": "Before you go.",
        "about": "A familiar voice.<br>A fresh start.",
        "faq": "Good questions.<br>Clear answers.",
        "contact": "Let’s plan your next move.",
        "slip": "One inquiry. Your car and your home.",
        "form": "Start with your route",
        "formSub": "Choose a service and enter both ZIP codes.",
        "note": "Demo: download your inquiry draft. Nothing is sent.",
        "credit": "Work photos from the original 168 sites; road photo is illustrative.",
        "first": "Explore the services",
        "ui": "UI / UX review",
        "steps": [
            "Tell us your plans",
            "Confirm your options",
            "Prepare for pickup",
            "Inspect on arrival",
        ],
    },
}


def set_html(node, value):
    node.clear()
    for item in list(BeautifulSoup(value, "html.parser").contents):
        node.append(item)


def polish_document(text, path):
    s = BeautifulSoup(text, "html.parser")
    lang = path.split("/")[0]
    lang = lang if lang in COPY else "zh-hant"
    c = COPY[lang]
    if not s.body:
        return text
    is_home = bool(s.select_one(".hero"))
    s.body["class"] = ["home" if is_home else "inner-page"]
    # Remove ornament from the markup, rather than hide it from visual checks.
    for n in s.select(
        ".eyebrow,.hero-meta,.photo-label,.photo-stamp,.map-note,.map-grid,.guide-image>span,.service-img>span"
    ):
        if n.find_parent(class_="article-top") and "2026" in n.get_text():
            n["class"] = ["article-meta"]
            n.string = (
                "Updated October 30, 2026" if lang == "en" else f"整理日期：{CONTENT_DATE}"
            )
        else:
            n.decompose()
    for n in s.select(".brand small"):
        n.decompose()
    for n in s.select(".brand>div"):
        n.string = "Moving & Auto"
    for n in s.select(".brand>b>span"):
        n.decompose()
    for n in s.select(".floating-contact"):
        n.decompose()
    nav = s.select_one("#navlinks")
    if nav:
        action = s.new_tag(
            "button",
            attrs={
                "class": "button dark mobile-nav-quote",
                "data-quote": "",
                "type": "button",
            },
        )
        action.string = (
            "Get a free quote"
            if lang == "en"
            else "免费咨询报价" if lang == "zh-hans" else "免費諮詢報價"
        )
        nav.append(action)
    for n in s.select(".service-kicker"):
        n.decompose()
    for n in s.select(".service-content h4"):
        n.decompose()  # The descriptive paragraph already conveys the service.
    for n in s.select(".step>span, summary>span"):
        n.decompose()
    for n in s.select(".hero-shade"):
        n.decompose()
    for n in s.select(".hero-bg"):
        n.decompose()
    # Preserve photograph identity and use one consistent crop.
    if is_home:
        visual = s.select_one(".hero-visual")
        visual.name = "figure"
        image = visual.select_one("img")
        image["src"] = "/assets/auto-detail.jpg"
        image["fetchpriority"] = "high"
        cap = visual.select_one(".visual-caption")
        if cap:
            cap.decompose()  # Source credit lives with the other image credits in the footer.
        set_html(s.select_one(".hero h1"), c["hero"])
        s.select_one(".hero-intro").string = c["intro"]
        action = s.select_one(".hero-copy>.button")
        action.name = "button"
        action.attrs.pop("href", None)
        action["type"] = "button"
        action["data-quote"] = ""
        label = json.loads(s.select_one("#site-data").string)["labels"]["quote"]
        action.contents[0].replace_with(label)
        s.select_one(".quote-heading h2").string = c["form"]
        s.select_one(".quote-heading p").string = c["formSub"]
        s.select_one("#quick-form>small").string = c["note"]
        for ident, key in [
            ("services", "services"),
            ("routes", "routes"),
            ("process", "process"),
            ("guides", "guides"),
            ("about", "about"),
        ]:
            set_html(s.select_one("#" + ident + " h2"), c[key])
        set_html(s.select_one(".faq-layout h2"), c["faq"])
        steps = s.select_one(".process-grid")
        steps.name = "ol"
        for i, n in enumerate(steps.select(".step")):
            n.name = "li"
            n.select_one("h3").string = c["steps"][i]
        # Editorial row replaces a second grid of repeated cards.
        grid = s.select_one(".guides-section .guide-grid")
        grid["class"] = ["guide-grid", "editorial-guides"]
        for card in grid.select(".guide-card"):
            card.select_one("p").decompose()
        if lang == "en":
            for card, title in zip(
                grid.select(".guide-card"),
                [
                    "Car shipping, step by step",
                    "Planning an interstate move",
                    "Open or enclosed transport",
                ],
            ):
                card.select_one("h3").string = title
        s.select_one(".about-photo img")["src"] = "/assets/auto-detail.jpg"
        s.select_one(".about-photo img")["alt"] = (
            "168 原站車輛運送照片"
            if lang != "en"
            else "Vehicle transport photograph from the original 168 website"
        )
        for a in s.select(".route-map svg text"):
            a["font-size"] = "15"
        for line in s.select('.route-map svg path[stroke-width="1"]'):
            line.attrs.pop("stroke", None)
        # The final column is a contact slip; no mock founder quotation or new claims.
    for h2 in s.select(".contact h2"):
        set_html(h2, c["contact"])
    for title in s.select("#quote-dialog h2"):
        if lang == "en" and len(title.get_text()) > 30:
            title.string = "Your moving plan"
    for img in s.select("img"):
        if not img.has_attr("decoding"):
            img["decoding"] = "async"
    picturize(s)
    footer = s.select_one("footer .footer-bottom")
    if footer:
        credit = s.new_tag("p", attrs={"class": "photo-credit"})
        credit.string = c["credit"]
        footer.append(credit)
        ui = s.new_tag("a", href="/ui-review.html")
        ui.string = c["ui"]
        footer.append(ui)
    return str(s)
