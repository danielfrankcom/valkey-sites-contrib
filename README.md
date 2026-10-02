# Cross-site search for the Valkey sites: prototype

Prototype of the cross-site search proposed in an issue on [`valkey-io/valkey-io.github.io`](https://github.com/valkey-io/valkey-io.github.io).
The issue has the design and the findings. This repository isn't an official Valkey project.

**Demo:** <https://danielfrankcom.github.io/valkey-sites-contrib/>

`sites/` pins each site's repository as a submodule, and `patches/` holds the proposed change for each:

- [`valkey-io.github.io.diff`](patches/valkey-io.github.io.diff), and the optional search box change
  [`valkey-io.github.io-search-ui.diff`](patches/valkey-io.github.io-search-ui.diff), which the demo applies on top
- [`valkey-glide-docs.diff`](patches/valkey-glide-docs.diff)
- [`valkey-admin.diff`](patches/valkey-admin.diff)
- [`spring-data-valkey.diff`](patches/spring-data-valkey.diff)

[`pages.yml`](.github/workflows/pages.yml) builds each site with its patch and publishes all four on GitHub Pages.
The files in `demo/` aren't part of the proposal: they host the sites under paths on one site and remove analytics.
