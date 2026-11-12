#!/usr/bin/env python3
"""Build the Tanren website from src/<lang>/ (standard library only).

    python3 tools/build.py            # check every language, then write the pages
    python3 tools/build.py --check    # only check (structure of each translation against English)
    python3 tools/build.py --check tr # only check one language
    python3 tools/build.py en         # check and build only these languages (for a quick preview)

English pages go to the repository root, every other language to /<lang>/. Each language has
src/<lang>/strings.json (titles, navigation, footer) and one HTML fragment per page (the content of <main>).
Fragments use {{root}} for the path to the site root ("" or "../").
"""

from __future__ import annotations

import html
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BASE_URL = "https://lkmcelik.github.io/tanren/"
BASE_PATH = "/tanren/"
COPYRIGHT = "© 2026 Lokman Çelik"

# (code, endonym, direction, og:locale)
LANGS = [
    ("en", "English", "ltr", "en_US"),
    ("tr", "Türkçe", "ltr", "tr_TR"),
    ("de", "Deutsch", "ltr", "de_DE"),
    ("fr", "Français", "ltr", "fr_FR"),
    ("es", "Español", "ltr", "es_ES"),
    ("pt-BR", "Português (Brasil)", "ltr", "pt_BR"),
    ("ru", "Русский", "ltr", "ru_RU"),
    ("ar", "العربية", "rtl", "ar_AR"),
    ("ja", "日本語", "ltr", "ja_JP"),
    ("zh-Hans", "简体中文", "ltr", "zh_CN"),
]

# (page id, file name, title key, description key)
PAGES = [
    ("index", "index.html", "title_index", "desc_index"),
    ("support", "support.html", "title_support", "desc_support"),
    ("privacy", "privacy.html", "title_privacy", "desc_privacy"),
    ("terms", "terms.html", "title_terms", "desc_terms"),
    ("delete-account", "delete-account.html", "title_delete", "desc_delete"),
]

# Attributes whose values are translated; every other attribute must match English exactly.
TRANSLATED_ATTRIBUTES = {"alt", "title", "aria-label"}

GLOBE = (
    '<svg class="globe" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
    '<path d="M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>'
)


def prefix(lang: str) -> str:
    return "" if lang == "en" else f"{lang}/"


def rel_root(lang: str) -> str:
    return "" if lang == "en" else "../"


def page_href(from_lang: str, to_lang: str, file: str) -> str:
    """Relative link from a page in `from_lang` to `file` in `to_lang`."""
    base = rel_root(from_lang) + prefix(to_lang)
    if file == "index.html":
        return base or "./"
    return base + file


def canonical(lang: str, file: str) -> str:
    return BASE_URL + prefix(lang) + ("" if file == "index.html" else file)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


# ---------------------------------------------------------------------------------------------------------------
# Checks


class Shape(HTMLParser):
    """Collects the tag structure of a fragment: tags with their untranslated attributes, plus {{root}} tokens."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[str] = []

    def handle_starttag(self, tag, attrs):
        kept = sorted((k, v or "") for k, v in attrs if k not in TRANSLATED_ATTRIBUTES)
        self.items.append(f"<{tag} {kept}>")

    def handle_endtag(self, tag):
        self.items.append(f"</{tag}>")


def shape(text: str) -> list[str]:
    parser = Shape()
    parser.feed(text)
    parser.close()
    return parser.items


def check(langs: list[str]) -> list[str]:
    errors: list[str] = []
    en_strings = json.loads((SRC / "en" / "strings.json").read_text(encoding="utf-8"))
    for lang in langs:
        folder = SRC / lang
        if not folder.is_dir():
            errors.append(f"{lang}: missing folder src/{lang}")
            continue
        try:
            strings = json.loads((folder / "strings.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{lang}: strings.json: {error}")
            continue
        for key in en_strings:
            if not str(strings.get(key, "")).strip():
                errors.append(f"{lang}: strings.json is missing '{key}'")
        for key in strings:
            if key not in en_strings:
                errors.append(f"{lang}: strings.json has an unknown key '{key}'")
        for _, file, _, _ in PAGES:
            path = folder / file
            if not path.is_file():
                errors.append(f"{lang}: missing src/{lang}/{file}")
                continue
            text = path.read_text(encoding="utf-8")
            en_text = (SRC / "en" / file).read_text(encoding="utf-8")
            if text.count("{{root}}") != en_text.count("{{root}}"):
                errors.append(f"{lang}/{file}: the number of {{{{root}}}} tokens differs from English")
            if lang != "en":
                theirs, ours = shape(text), shape(en_text)
                if theirs != ours:
                    for index, (a, b) in enumerate(zip(theirs, ours)):
                        if a != b:
                            errors.append(f"{lang}/{file}: structure differs from English at tag {index + 1}: {a} vs {b}")
                            break
                    else:
                        errors.append(f"{lang}/{file}: {len(theirs)} tags, English has {len(ours)}")
    return errors


# ---------------------------------------------------------------------------------------------------------------
# Pages


def head(lang: str, direction: str, og_locale: str, page: str, file: str, title: str, desc: str) -> str:
    root = rel_root(lang)
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{canonical(code, file)}">' for code, *_ in LANGS
    )
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{canonical("en", file)}">'
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F6F3EF" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#110D0B" media="(prefers-color-scheme: dark)">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical(lang, file)}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tanren">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical(lang, file)}">
<meta property="og:image" content="{BASE_URL}assets/icon-512.png">
<meta property="og:locale" content="{og_locale}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{root}assets/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{root}style.css">
<script defer src="{root}script.js"></script>
</head>
<body class="page-{page}">
"""


def language_links(lang: str, file: str) -> str:
    items = []
    for code, endonym, *_ in LANGS:
        current = ' aria-current="true"' if code == lang else ""
        items.append(
            f'<li><a href="{page_href(lang, code, file)}" hreflang="{code}" lang="{code}"{current}>{esc(endonym)}</a></li>'
        )
    return "\n".join(items)


def header(lang: str, page: str, file: str, s: dict) -> str:
    root = rel_root(lang)
    endonym = next(name for code, name, *_ in LANGS if code == lang)

    def nav_item(target_page: str, target_file: str, label: str) -> str:
        current = ' aria-current="page"' if target_page == page else ""
        return f'<li><a href="{page_href(lang, lang, target_file)}"{current}>{esc(label)}</a></li>'

    return f"""<a class="skip-link" href="#main">{esc(s["skip_link"])}</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="{page_href(lang, lang, "index.html")}"><img src="{root}assets/icon.svg" alt="" width="32" height="32"><span>Tanren</span></a>
    <nav class="site-nav" aria-label="{esc(s["nav_label"])}">
      <ul>
        {nav_item("support", "support.html", s["nav_support"])}
        {nav_item("privacy", "privacy.html", s["nav_privacy"])}
        {nav_item("terms", "terms.html", s["nav_terms"])}
      </ul>
    </nav>
    <details class="lang-menu">
      <summary>{GLOBE}<span class="visually-hidden">{esc(s["language_label"])}: </span><span>{esc(endonym)}</span></summary>
      <ul class="lang-list">
{language_links(lang, file)}
      </ul>
    </details>
  </div>
</header>
"""


def footer(lang: str, page: str, file: str, s: dict) -> str:
    def item(target_page: str, target_file: str, label: str) -> str:
        current = ' aria-current="page"' if target_page == page else ""
        return f'<li><a href="{page_href(lang, lang, target_file)}"{current}>{esc(label)}</a></li>'

    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <p class="footer-brand">Tanren</p>
        <p class="footer-tagline">{esc(s["footer_tagline"])}</p>
      </div>
      <nav aria-label="{esc(s["footer_links_label"])}">
        <ul class="footer-links">
          {item("index", "index.html", s["nav_home"])}
          {item("support", "support.html", s["nav_support"])}
          {item("privacy", "privacy.html", s["nav_privacy"])}
          {item("terms", "terms.html", s["nav_terms"])}
          {item("delete-account", "delete-account.html", s["nav_delete"])}
        </ul>
      </nav>
    </div>
    <nav class="footer-langs" aria-label="{esc(s["footer_languages_label"])}">
      <ul>
{language_links(lang, file)}
      </ul>
    </nav>
    <p class="copyright">{COPYRIGHT}</p>
  </div>
</footer>
</body>
</html>
"""


def build_page(lang: str, direction: str, og_locale: str, page: str, file: str, title_key: str, desc_key: str) -> str:
    s = json.loads((SRC / lang / "strings.json").read_text(encoding="utf-8"))
    fragment = (SRC / lang / file).read_text(encoding="utf-8").replace("{{root}}", rel_root(lang)).strip()
    title = s[title_key] if page == "index" else f"{s[title_key]} · Tanren"
    if page == "index":
        main = f'<main id="main" tabindex="-1">\n{fragment}\n</main>\n'
    else:
        main = f'<main id="main" tabindex="-1" class="doc">\n<div class="container narrow">\n{fragment}\n</div>\n</main>\n'
    return (
        head(lang, direction, og_locale, page, file, title, s[desc_key])
        + header(lang, page, file, s)
        + main
        + footer(lang, page, file, s)
    )


def build_404() -> str:
    """GitHub Pages serves /404.html for every missing path, so it uses absolute paths and lists every language."""
    links = "\n".join(
        f'<li><a href="{BASE_PATH}{prefix(code)}" hreflang="{code}" lang="{code}">{esc(name)}</a></li>'
        for code, name, *_ in LANGS
    )
    return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="noindex">
<title>Page not found · Tanren</title>
<link rel="icon" href="{BASE_PATH}assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE_PATH}style.css">
</head>
<body class="page-404">
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="{BASE_PATH}"><img src="{BASE_PATH}assets/icon.svg" alt="" width="32" height="32"><span>Tanren</span></a>
  </div>
</header>
<main id="main" class="doc">
  <div class="container narrow">
    <h1>Page not found</h1>
    <p>This page doesn't exist. Choose your language to go back to the Tanren home page.</p>
    <ul class="lang-grid">
{links}
    </ul>
  </div>
</main>
<footer class="site-footer">
  <div class="container">
    <p class="copyright">{COPYRIGHT}</p>
  </div>
</footer>
</body>
</html>
"""


def build_sitemap() -> str:
    urls = []
    for code, *_ in LANGS:
        for _, file, _, _ in PAGES:
            alternates = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{other}" href="{canonical(other, file)}"/>'
                for other, *_ in LANGS
            )
            urls.append(f"  <url>\n    <loc>{canonical(code, file)}</loc>{alternates}\n  </url>")
    body = "\n".join(urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{body}\n</urlset>\n"
    )


def main(argv: list[str]) -> int:
    only_check = "--check" in argv
    selected = [a for a in argv if not a.startswith("--")]
    langs = selected or [code for code, *_ in LANGS]
    errors = check(langs)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"check passed: {', '.join(langs)}")
    if only_check:
        return 0
    for code, _, direction, og_locale in LANGS:
        if code not in langs:
            continue
        out_dir = ROOT / prefix(code)
        out_dir.mkdir(parents=True, exist_ok=True)
        for page, file, title_key, desc_key in PAGES:
            (out_dir / file).write_text(
                build_page(code, direction, og_locale, page, file, title_key, desc_key), encoding="utf-8"
            )
    (ROOT / "404.html").write_text(build_404(), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    print(f"built {len(langs) * len(PAGES)} pages ({', '.join(langs)}), 404.html and sitemap.xml")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
