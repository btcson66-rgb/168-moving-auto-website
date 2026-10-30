# 168 Moving & Auto — trilingual concept demo

Buildless static site combining public information from haobun.com and carshipping168.com. Original websites are unchanged.

- `dist/`: deployable HTML, CSS, JS, article archive and report.
- `content.py`: authored Traditional Chinese and English content. Simplified Chinese uses OpenCC conversion.
- `build.py`: produces trilingual pages, archive, sitemap and llms.txt.
- `report.py`: produces source/change/risk CSVs and the human-readable report.
- `research/`: original public HTML snapshots, crawl inventory, QA and hashes, included to reproduce the content build. Temporary browser files and logs are excluded.

Local preview: `npm run preview`, then open `http://127.0.0.1:4173/zh-hant/`.

Rebuild and verify: `npm run verify` runs `build`, `check` and `qa` in order. `qa.cjs` starts its own static server for `dist/` on `127.0.0.1:4173` when nothing is already listening there. It uses Playwright's bundled Chromium; set `CHROME_PATH` to use another Chrome executable, for example `CHROME_PATH='C:/Program Files/Google/Chrome/Application/chrome.exe'`.

After a content change, run `npm run verify`, then `npm run report` to refresh the reports.

The UI revision is applied by `polish.py` during the build; it preserves original article body text. Re-run the taste inspectors before `python ui_review.py` to refresh the visual review. The revision's screenshots, limitations and results are available at `/ui-review.html`.
Python requirements: requests, beautifulsoup4, opencc-python-reimplemented, pillow.
Browser QA requirements: playwright, @axe-core/playwright; uses Playwright Chromium, or set `CHROME_PATH` to another Chrome binary.

The demo has no inquiry submission, booking or payment backend. Local inquiry state uses sessionStorage. Original-language archive articles are not fully translated into English. Authoritative service terms and article facts need owner review.

SEO templates exist but indexing remains disabled for this private demo. Before production, replace the origin in `build.py`, verify business facts and image permissions, review URL-level migration mappings, enable approved indexing and rerun checks. Do not redirect every old article to the homepage or treat suggested topic grouping as an approved 301 map.

## GitHub handoff

This private repository contains the prebuilt demo, editable source, public-source HTML evidence, content change CSVs, UI comparisons and verification reports. The old failed Sites registration is excluded. Production hosting is not configured.

Install Python 3.12+ and Node.js 22+, then run:

```sh
python -m pip install -r requirements.txt
npm install
npm run preview
```

Open `http://127.0.0.1:4173/zh-hant/`. Other language pages: `/en/`, `/zh-hans/`. Reports: `/report.html` and `/ui-review.html`. On Windows, `start-demo.cmd` is also available.

The prebuilt `dist/` can be served without Node dependencies. The original-language archive is not fully translated. Browser QA runs on Windows, macOS and Linux (set `CHROME_PATH` to use a specific Chrome). Taste scripts belong to the installed local skill and are not vendored; their result JSON and screenshots are retained in `.taste-skill/` and `dist/reports/ui/`.
