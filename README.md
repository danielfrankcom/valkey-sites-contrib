# Cross-site search for the Valkey sites: prototype and demo

This repository holds a prototype of cross-site search for four Valkey documentation sites, and builds a live demo of it.
It isn't an official Valkey project, and nothing here is upstream.

**Demo:** <https://danielfrankcom.github.io/valkey-sites-contrib/>

| Site | Upstream repository | Proposed changes |
|---|---|---|
| [valkey.io](https://danielfrankcom.github.io/valkey-sites-contrib/valkey-io/) | [`valkey-io/valkey-io.github.io`](https://github.com/valkey-io/valkey-io.github.io) | [`patches/valkey-io.github.io.diff`](patches/valkey-io.github.io.diff) |
| [GLIDE docs](https://danielfrankcom.github.io/valkey-sites-contrib/glide/) | [`valkey-io/valkey-glide-docs`](https://github.com/valkey-io/valkey-glide-docs) | [`patches/valkey-glide-docs.diff`](patches/valkey-glide-docs.diff) |
| [Valkey Admin docs](https://danielfrankcom.github.io/valkey-sites-contrib/valkey-admin/) | [`valkey-io/valkey-admin`](https://github.com/valkey-io/valkey-admin) | [`patches/valkey-admin.diff`](patches/valkey-admin.diff) |
| [Spring Data Valkey docs](https://danielfrankcom.github.io/valkey-sites-contrib/spring/) | [`valkey-io/spring-data-valkey`](https://github.com/valkey-io/spring-data-valkey) | [`patches/spring-data-valkey.diff`](patches/spring-data-valkey.diff) |

## What the patches change

Each site keeps its own [Pagefind](https://pagefind.app/) index, built in its own deploy workflow.
A small script on each site merges the other sites' indexes into its search box,
and skips any site whose index is missing, slow, or built with an incompatible Pagefind version.

- **valkey.io** gains Pagefind search. Zola has no built-in search UI, so the search box is Pagefind's default UI, as a placeholder.
  `build/pagefind-step.sh` downloads a pinned Pagefind binary, checks it against the release checksum, and indexes the built site.
  `pagefind.yml` limits the index to page content, and `build/check-search-index.sh` fails the build if a page is missing from the index.
- **The three Starlight sites** keep Starlight's built-in Pagefind search.
  Each adds the merge script, a site label for results, and the shared ranking settings in `astro.config.mjs`.
- **Every site** gets the same `pagefind-federation.sh`. Pagefind can only merge an index built with the same minor version,
  so each deploy also publishes copies of the site's index for the other Pagefind versions in use.
  The script also runs a version-change check: a change that would leave another site out of this site's search fails the build.

## How the demo is built

`sites/` pins each upstream repository as a submodule.
[`.github/workflows/pages.yml`](.github/workflows/pages.yml) builds each site the way its own deploy workflow does, with its patch applied,
and publishes all four on this repository's GitHub Pages site.

Two demo-only steps let the sites run under paths on one GitHub Pages site instead of their own hostnames.
Neither is part of the proposal.

- [`demo/adapt.sh`](demo/adapt.sh) runs before the build. It points each site's URLs at its demo path,
  sets Astro's `base` and Zola's `base_url`, and turns off GLIDE's link validator, which rejects root-relative links once a `base` is set.
- [`demo/rebase.py`](demo/rebase.py) runs after the build. It adds the demo path to root-relative links,
  and removes the analytics tags (Google Tag Manager, the consent manager, and a tracking pixel) so the demo doesn't report page views.

The sites' content is pinned too: valkey.io's build reads `valkey-doc`, `valkey`, and the module repositories at the commits in the workflow.

## What the demo doesn't show

- **Cross-origin requests.** All four sites share one origin here, while in production each site has its own hostname.
  GitHub Pages sends `Access-Control-Allow-Origin: *` on every file, which is what cross-site merging needs.
- **Mixed Pagefind versions.** All four sites run Pagefind 1.5.2, so no site needs another's version copy.
- **API reference pages.** The GLIDE API docs and the Spring Data Valkey Javadoc aren't built. They aren't indexed today either.
- **Independent deploys.** The four sites deploy together here. Each version script still reads the other sites from the previous demo deploy,
  the way it would read the live sites, so after a Pagefind version change the workflow needs to run twice.

## Updating

To move a site to a newer upstream commit, check out the commit in its submodule, apply its patch, resolve any conflicts,
and regenerate the patch with `git diff --binary`.
