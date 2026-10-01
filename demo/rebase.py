#!/usr/bin/env python3
"""Demo-only post-build step: moves a built site under its GitHub Pages project path, and removes analytics.

Usage: demo/rebase.py <site-dir> <prefix>      for example: demo/rebase.py public /valkey-sites-contrib/valkey-io

1. Links and assets written as root-relative paths ("/css/styles.css", "/pagefind/pagefind-ui.js") would point at
   the root of danielfrankcom.github.io, so they get the site's prefix. Astro already adds the prefix (its `base`
   setting) to what it generates, and those are left alone. The Pagefind index itself is untouched: Pagefind works
   out each index's URL from where it is loaded.
2. The production sites load Google Tag Manager, a consent manager, and a tracking pixel. The demo must not send
   page views to the Valkey project's analytics, so those tags are removed.
"""
import pathlib
import re
import sys

site_dir = pathlib.Path(sys.argv[1])
prefix = sys.argv[2].rstrip("/")

TRACKERS = re.compile(
    r"<script\b[^>]*>(?:(?!</script>).)*?googletagmanager\.com(?:(?!</script>).)*?</script>"
    r"|<script\b[^>]*\bsrc=\"https://cmp\.osano\.com/[^\"]*\"[^>]*>\s*</script>"
    r"|<noscript\b[^>]*>\s*<iframe\b[^>]*googletagmanager\.com[^>]*>\s*</iframe>\s*</noscript>"
    r"|<img\b[^>]*\bsrc=\"https://static\.scarf\.sh/[^\"]*\"[^>]*>",
    re.DOTALL,
)
# A root-relative URL: one leading slash, not two (protocol-relative), and not already under the prefix.
ROOT_RELATIVE = rf"/(?!/)(?!{re.escape(prefix.lstrip('/'))}/)"
ATTRIBUTE = re.compile(rf"(\b(?:href|src|action|poster|srcset|content)=)([\"'])({ROOT_RELATIVE})")
# srcset lists several URLs: "a.png 1x, /b.png 2x".
SRCSET_ITEM = re.compile(rf"(,\s*)({ROOT_RELATIVE})")
CSS_URL = re.compile(rf"(url\(\s*[\"']?)({ROOT_RELATIVE})")
REFRESH = re.compile(rf"(content=[\"']\d+;\s*url=)({ROOT_RELATIVE})", re.IGNORECASE)


def rebase_html(text):
    text = TRACKERS.sub("", text)
    text = REFRESH.sub(lambda m: m[1] + prefix + m[2], text)
    text = ATTRIBUTE.sub(lambda m: m[1] + m[2] + prefix + m[3], text)
    text = re.sub(r"srcset=\"[^\"]*\"", lambda m: SRCSET_ITEM.sub(lambda n: n[1] + prefix + n[2], m[0]), text)
    return CSS_URL.sub(lambda m: m[1] + prefix + m[2], text)


def rebase_css(text):
    return CSS_URL.sub(lambda m: m[1] + prefix + m[2], text)


changed = 0
for path in site_dir.rglob("*"):
    if not path.is_file() or "pagefind" in path.relative_to(site_dir).parts[:1]:
        continue
    if path.suffix == ".html":
        rebase = rebase_html
    elif path.suffix == ".css":
        rebase = rebase_css
    else:
        continue
    text = path.read_text(encoding="utf-8", errors="surrogateescape")
    new = rebase(text)
    if new != text:
        path.write_text(new, encoding="utf-8", errors="surrogateescape")
        changed += 1
print(f"{site_dir}: rebased {changed} files under {prefix}/")
