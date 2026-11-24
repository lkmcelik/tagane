# Tagane website (`tagane-site`)

Public website for [Tagane](https://lkmcelik.github.io/tagane/) (formerly Tanren), the calisthenics and workout app
for iPhone, iPad and Apple Watch: home page, privacy policy, terms of use, support, account deletion and the
open-source licenses, in the app's 11 languages.

Hosted on **GitHub Pages** from `lkmcelik/tagane` (branch `main`, folder `/`) at `https://lkmcelik.github.io/tagane/`.
The app was renamed from Tanren to Tagane (app repository ADR-0079), and this repo was renamed from `lkmcelik/tanren`
on 2026-11-24. The old `/tanren/` URLs keep working through `lkmcelik/tanren`, a separate repo that only holds
redirect pages (local copy `../tagane-redirect`). No custom domain yet: that waits for `tagane.app` (OQ-001).

## Layout

```
.
├── src/<lang>/              # SOURCE: strings.json + one HTML fragment per page (the content of <main>)
├── src/licenses.json        # SOURCE: the open-source notices of licenses.html (generated, see below)
├── tools/build.py           # builds every page from src/ (Python 3, standard library only)
├── index.html … *.html      # English pages (generated)
├── tr/ de/ fr/ es/ it/ pt-BR/ ru/ ar/ ja/ zh-Hans/   # the other languages (generated)
├── 404.html, sitemap.xml    # generated
├── style.css                # Ember & Iron palette (app repository ADR-0056), light and dark
├── script.js                # closes the language menu on Escape or an outside click
├── assets/                  # app icon (SVG, PNG), Barlow Condensed Bold (SIL OFL, see assets/fonts/OFL.txt)
└── .nojekyll
```

Languages: `en` (source, at the root), `tr`, `de`, `fr`, `es`, `it`, `pt-BR`, `ru`, `ar` (right to left), `ja`, `zh-Hans`.
Every page has a language menu, `hreflang` alternates and the same structure in every language.

No trackers, no cookies, no external fonts or scripts: everything is served from this repository.

## Editing

1. Change the English source in `src/en/` and the same place in every other language in `src/<lang>/`.
   Keep the tags, ids, classes and links identical across languages; only text, `alt`, `title` and `aria-label`
   are translated. Fragments use `{{root}}` for the path to the site root.
2. When a legal text changes, update its effective date in all 11 languages.
3. Build and check:

   ```sh
   python3 tools/build.py            # checks every language against English, then writes the pages
   python3 tools/build.py --check    # check only
   ```

4. Preview: `python3 -m http.server 8080`, then open http://localhost:8080/ (the 404 page uses `/tagane/` paths and
   only renders correctly on GitHub Pages).
5. Commit and push `main`; GitHub Pages republishes in about a minute.

The licenses page (`licenses.html`) lists every package in the app's `Package.resolved` with its license and
notices, in English as each package publishes them; only the frame around them is translated. `src/licenses.json` is
written from the app repository: `python3 -I Tools/Licenses/generate_licenses.py <SwiftPM checkouts or repository
cache> <this repo>` (app repository ADR-0067 amendment A7). Run it, then `tools/build.py`, whenever the app's
packages change, and publish the site with the app build that ships them. `--check <this repo>` tells whether the page is current.

In-app labels in the pages (Profile › Settings › …, Restore Purchases, Export my data, Delete account, …) must match
the app's String Catalogs in each language. The privacy policy must match what the app does: when the app starts
collecting something new, or a retention period is decided, change the policy first.

## How the app uses it

| Where | URL |
|---|---|
| Paywall and Settings, Privacy link (`TANREN_PRIVACY_POLICY_URL`) | https://lkmcelik.github.io/tagane/privacy.html |
| Paywall and Settings, Terms link | Apple's standard EULA (the terms page says it applies) |
| App Store Connect, Privacy Policy URL | https://lkmcelik.github.io/tagane/privacy.html |
| App Store Connect, Support URL | https://lkmcelik.github.io/tagane/support.html |
| App Store Connect, Marketing URL | https://lkmcelik.github.io/tagane/ |
| Google Cloud consent screen, home page and privacy policy | https://lkmcelik.github.io/tagane/ and …/privacy.html |
| Open-source licenses (moved out of the app's Settings, 2026-11-23); linked from the terms page and every footer | https://lkmcelik.github.io/tagane/licenses.html |

Localized pages live at `https://lkmcelik.github.io/tagane/<lang>/privacy.html` and so on.

When the app is live, replace the "Coming soon to the App Store" label in `src/<lang>/index.html` with a link to
`https://apps.apple.com/app/id6833955059`.

## Custom domain (later)

1. Add a `CNAME` file with the domain, set it under Settings › Pages and enforce HTTPS.
2. Change `BASE_URL` and `BASE_PATH` in `tools/build.py`, rebuild, and update the URLs in the app's configuration.
