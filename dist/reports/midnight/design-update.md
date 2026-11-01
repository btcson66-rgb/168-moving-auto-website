# Midnight transport design — 2026-10-31

## Baseline

Fetched GitHub twice at the user's request and fast-forwarded the clean local checkout to `61de28ad97881ecf821eabd2a7bc78f15b8905c0` (`main`, merged font-loading optimization PR #2). This edition builds on that state, including the optimized WebP imagery, original archive language metadata, portable QA and non-blocking Google Fonts loading.

## Visual direction

The user supplied an Andercore style reference: carbon `#0b0405`, graphite `#150e0f`, steel borders `#382e30`, white navigation and type, signal-red `#e32735` primary actions and 4px corners. That explicit reference supersedes the previous taste-skill house rules concerning outlines, monospaced instrument labels and the old blue/green palette. This edition does not claim to pass those incompatible aesthetic rules.

- A full-width source photograph with a dark scrim replaces the paper-card hero.
- Archivo 400/500 is self-hosted for Latin text; Noto Sans TC remains the CJK face. Space Mono is limited to technical labels.
- Text remains readable at 16px for long passages. Secondary colors are brighter than the reference's `#858182` where needed for contrast.
- The white navigation, red actions, 4px corners and dark panels extend to guides, the original archive, the inquiry sheet and contact sections.
- A direct “See transport in motion” action leads to the animated freight band.

## Motion and behavior

- A custom, schematic SVG freight convoy advances across two highway lanes. It is an original diagram, not camera footage or an actual vehicle location.
- Four arrowheads travel along the existing map's curved routes. The selected route updates the status label while the existing inquiry opens with the correct ZIP codes.
- Fleet and map buttons share pause/play state. SVG timelines and CSS truck motion pause together.
- `prefers-reduced-motion` disables truck motion and pauses SVG timelines; the control does not override the system preference.
- Offscreen SVG timelines and hidden-tab SVG playback pause to avoid needless work.
- All movement is labeled illustrative. No tracking feed, speed, ETA, quote, order or payment backend has been added.

## Scope preserved

English, Simplified Chinese and Traditional Chinese routes remain. Service facts, the original article body text, source inventory and SEO/AEO information are retained. The 205 original articles remain original-language archives, not newly translated or fact-checked accounts. No new business statistics, guarantees or customer reviews were introduced.

## Verification

Run `npm run build`, `npm run check` and `npm run qa`. With the preview server running, run `npm run qa:motion` to verify actual truck/arrow movement, pause synchronization, selected-route ZIPs, three-language responsive layout and reduced-motion behavior.

Revision-specific test results and screenshots are published under `dist/reports/midnight/` and summarized at `/midnight-review.html`. Previous UI review pages describe their original dated revisions and are not evidence for this design.

## Files

- `midnight.py`: presentation and SVG scene generation, called by the retained `polish.py` pipeline.
- `dist/midnight.css`: user-reference colors, layout and responsive motion styles.
- `dist/motion.js`: local animation controls and route state, separate from inquiry logic.
- `motion-qa.cjs`: browser-level motion checks.

Font sources: Google Fonts Archivo and Space Mono. Their OFL texts accompany the font files in `dist/assets/`. Existing original-site photographs are retained; no new stock photography or paid asset was introduced. Original-site media permissions still need confirmation before a public commercial launch.
