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
Each result is labelled with its site. Above the results, a row of buttons ("All sites", then each site in alphabetical order,
with result counts) narrows the results to one site; it replaces Pagefind's filter panel.
The docs sites count the other sites' results at a tenth of their own, so their own pages come first for most queries.
valkey.io counts every site the same.

- **valkey.io** gains Pagefind search. Zola has no built-in search UI, so the proposal uses Pagefind's default UI as a placeholder.
  `build/pagefind-step.sh` downloads a pinned Pagefind binary, checks it against the release checksum, and indexes the built site.
  `pagefind.yml` limits the index to page content, and `build/check-search-index.sh` fails the build if a page is missing from the index.
- **The three Starlight sites** keep Starlight's built-in Pagefind search.
  Each adds the merge script, a site label for results, and the shared ranking settings in `astro.config.mjs`.
- **Every site** gets the same `pagefind-federation.sh`. Pagefind can only merge an index built with the same minor version,
  so each deploy also publishes copies of the site's index for the other Pagefind versions in use.
  The script also runs a version-change check: a change that would leave another site out of this site's search fails the build.

The patches change nothing else. Each site keeps the Pagefind version it runs today:

| Site | Pagefind | Pinned commit |
|---|---|---|
| valkey.io | 1.5.2 (new) | `edd43e6` on `main` |
| GLIDE docs | 1.3.0 | `19b5eca` on `public`, the branch its deploy workflow publishes |
| Valkey Admin docs | 1.5.2 | `cb34ef5e` on `main` |
| Spring Data Valkey docs | 1.4.0 | `01cf031` on `main` |

### valkey.io search box design

The search box design is a separate decision from the search backend, so it lives in its own patch, on top of the valkey.io patch.

- [`patches/valkey-io.github.io-search-ui.diff`](patches/valkey-io.github.io-search-ui.diff), which the demo applies, makes valkey.io's
  search work and look like the Starlight sites': a Search button in the header opens a modal, Ctrl+K (⌘K) toggles it, and the results use
  Starlight's layout, in Starlight's light colours with valkey.io's accent. On mobile the button is the first item of the menu, and the
  modal fills the screen. The modal script and styles are ported from Starlight's search component.
- [`patches/valkey-io.github.io-search-ui-dropdown.diff`](patches/valkey-io.github.io-search-ui-dropdown.diff), by
  [@vic-tsang](https://github.com/vic-tsang), is an alternative the demo doesn't apply: a search box in the header styled to match it,
  results as a dropdown of cards, and more results loading as the dropdown scrolls.

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

## Known limitations

- **One site at a time.** Pagefind's default UI, which Starlight also uses, combines filter values with AND
  ([Pagefind #594](https://github.com/Pagefind/pagefind/issues/594)), and each page belongs to one site, so the site buttons pick one site
  at a time. Picking several sites together would need a custom search UI.
- **Searches for a site's own name.** Pagefind scores each index on its own, so a word on nearly every page of one site, like
  "spring" on Spring Data Valkey, counts for little in that site's index. A query like `spring data` can rank other sites' pages first.

## What the demo doesn't show

- **Cross-origin requests.** All four sites share one origin here, while in production each site has its own hostname.
  GitHub Pages sends `Access-Control-Allow-Origin: *` on every file, which is what cross-site merging needs.
- **API reference pages.** The GLIDE API docs and the Spring Data Valkey Javadoc aren't built. They aren't indexed today either.
- **Independent deploys.** The four sites deploy together here. Each version script still reads the other sites from the previous demo deploy,
  the way it would read the live sites. So the first deploy, and the first after a Pagefind version change, needs a second run
  before every site publishes the copies the others need.

## Updating

To move a site to a newer upstream commit, check out the commit in its submodule, apply its patch, resolve any conflicts,
and regenerate the patch with `git diff --binary`.
