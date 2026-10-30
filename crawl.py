import requests, json, time, re, hashlib, concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlunsplit, urldefrag
from urllib.robotparser import RobotFileParser
from pathlib import Path

ROOT = Path(__file__).parent / "research"
DOMAINS = {
    "haobun.com",
    "www.haobun.com",
    "carshipping168.com",
    "www.carshipping168.com",
}
session = requests.Session()
session.headers["User-Agent"] = "168WebsiteContentInventory/1.0 (public-page research)"


def norm(u):
    p = urlsplit(urldefrag(u)[0])
    return urlunsplit((p.scheme, p.netloc, p.path or "/", p.query, ""))


def eligible(u):
    p = urlsplit(u)
    return (
        p.scheme in ["http", "https"]
        and p.netloc in DOMAINS
        and not re.search(
            r"\.(jpg|png|webp|jpeg|gif|pdf|zip|mp4|xml|css|js|svg|ico)$", p.path, re.I
        )
        and not any(
            x in u for x in ["wp-json", "wp-admin", "?s=", "replytocom=", "/feed/"]
        )
    )


def fetch(u):
    try:
        r = session.get(u, timeout=35)
        r.encoding = (
            r.apparent_encoding
            if not r.encoding or r.encoding == "ISO-8859-1"
            else r.encoding
        )
        if "text/html" not in r.headers.get("content-type", ""):
            return {"url": u, "status": r.status_code, "non_html": True}, []
        s = BeautifulSoup(r.text, "html.parser")
        links = sorted(
            set(norm(urljoin(r.url, a["href"])) for a in s.select("a[href]"))
        )
        imgs = [
            {"url": urljoin(r.url, x.get("src", "")), "alt": x.get("alt", "")}
            for x in s.select("img[src]")
        ]
        for x in s.select("script,style,noscript,nav,header,footer"):
            x.decompose()
        d = {
            "url": u,
            "final_url": r.url,
            "status": r.status_code,
            "title": s.title.get_text(" ", strip=True) if s.title else "",
            "headings": [x.get_text(" ", strip=True) for x in s.select("h1,h2,h3,h4")],
            "text": s.get_text("\n", strip=True),
            "links": links,
            "images": imgs,
        }
        (ROOT / (hashlib.sha1(u.encode()).hexdigest() + ".html")).write_text(
            r.text, encoding="utf8"
        )
        return d, [x for x in links if eligible(x)]
    except Exception as e:
        return {"url": u, "error": str(e)}, []


queue = ["https://haobun.com/", "https://www.carshipping168.com/"]
seen = set()
records = []
if (ROOT / "crawl.json").exists():
    records = json.loads((ROOT / "crawl.json").read_text(encoding="utf8"))
    seen = {x["url"] for x in records}
    for x in records:
        queue += [u for u in x.get("links", []) if eligible(u) and u not in seen]
for origin in ([] if records else queue.copy()):
    for path in ["robots.txt", "sitemap_index.xml", "sitemap.xml", "wp-sitemap.xml"]:
        try:
            r = session.get(urljoin(origin, path), timeout=20)
            (
                ROOT / (urlsplit(origin).netloc + "-" + path.replace("/", "_"))
            ).write_text(r.text, encoding="utf8")
            if r.status_code == 200 and "xml" in r.headers.get("content-type", ""):
                locs = re.findall(r"<loc>(.*?)</loc>", r.text)
                for loc in locs:
                    if loc.endswith(".xml"):
                        z = session.get(loc, timeout=20)
                        (
                            ROOT / (hashlib.sha1(loc.encode()).hexdigest() + ".xml")
                        ).write_text(z.text, encoding="utf8")
                        queue += [
                            x
                            for x in re.findall(r"<loc>(.*?)</loc>", z.text)
                            if eligible(x)
                        ]
                    elif eligible(loc):
                        queue.append(loc)
        except Exception:
            pass
while queue and len(seen) < 1500:
    batch = list(dict.fromkeys(x for x in queue if x not in seen))[:1]
    queue = [x for x in queue if x not in batch]
    if not batch:
        break
    seen.update(batch)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for d, links in ex.map(fetch, batch):
            records.append(d)
            queue += [x for x in links if x not in seen]
    (ROOT / "crawl.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf8"
    )
    print(f"Fetched {len(records)}, pending {len(set(queue)-seen)}", flush=True)
    time.sleep(10.1 if "carshipping168.com" in batch[0] else 1)
(ROOT / "summary.json").write_text(
    json.dumps(
        {
            "pages": len(records),
            "remaining": len(set(queue) - seen),
            "successful": sum(x.get("status") == 200 for x in records),
            "errors": [x for x in records if x.get("status") != 200],
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf8",
)
print("DONE", flush=True)
