#!/usr/bin/env bash
# Demo-only changes that let a patched site run under a GitHub Pages project path instead of its own hostname.
# Nothing here is part of the proposal: patches/ holds the proposed changes, and this script only adjusts
# where each site lives (https://valkey.io/ -> $DEMO_ORIGIN$DEMO_PATH/valkey-io/, and so on).
#
# Usage: demo/adapt.sh <site> <checkout>
#   <site> is valkey-io, glide, valkey-admin or spring. Run it after applying the site's patch and before building.
set -euo pipefail
site=$1
checkout=$2
origin=${DEMO_ORIGIN:-https://danielfrankcom.github.io}
path=${DEMO_PATH:-/valkey-sites-contrib}

case $site in
  valkey-io) project=. ;;
  glide) project=. ;;
  valkey-admin) project=docs-site ;;
  spring) project=docs ;;
  *) echo "unknown site $site" >&2; exit 2 ;;
esac
cd "$checkout/$project"
prefix="$path/$site"

# Each site's production URL and its demo URL.
rewrite_hosts=(
  -e "s#https://valkey\.io/#${origin}${path}/valkey-io/#g"
  -e "s#https://glide\.valkey\.io/#${origin}${path}/glide/#g"
  -e "s#https://valkey-admin\.valkey\.io/#${origin}${path}/valkey-admin/#g"
  -e "s#https://spring\.valkey\.io/#${origin}${path}/spring/#g"
)

if [ "$site" = valkey-io ]; then
  merge_script=static/pagefind-merge.js
  federation_script=build/pagefind-federation.sh
  # Zola builds every get_url() link from base_url.
  sed -i.bak -E "s#^base_url = .*#base_url = \"${origin}${prefix}\"#" config.toml
else
  merge_script=public/pagefind-merge.js
  federation_script=scripts/pagefind-federation.sh
  # Astro prefixes its own links and assets with `base`, and Starlight's search loads /<base>/pagefind/.
  perl -pi -e "s#^(\s*)site: *['\"][^'\"]*['\"],#\1site: '${origin}',\n\1base: '${prefix}',#" astro.config.mjs
  grep -q "base: '${prefix}'" astro.config.mjs || { echo "couldn't set base in astro.config.mjs" >&2; exit 1; }
  # GLIDE's link validator reports every root-relative link in its pages once there's a `base`, and fails the build.
  # The links work in the demo after demo/rebase.py, and the production build still validates them.
  if [ "$site" = glide ]; then
    perl -0pi -e 's/\n\s*starlightLinksValidator\(\{.*?\}\),//s' astro.config.mjs
    ! grep -q 'starlightLinksValidator(' astro.config.mjs || { echo "couldn't turn off the link validator" >&2; exit 1; }
  fi
fi

# The merge script names every site by URL, and loads this site's own index from /pagefind/.
sed -i.bak "${rewrite_hosts[@]}" -e "s#\"/pagefind/#\"${prefix}/pagefind/#g" "$merge_script"
# The version script expects each index at the root of its host; under a project path it sits deeper (and a local test server adds a port).
sed -i.bak -e 's#https://\[A-Za-z0-9.-\]+/pagefind/#https://[A-Za-z0-9.:/-]+/pagefind/#' "$federation_script"
grep -q 'A-Za-z0-9.:/-' "$federation_script" || { echo "couldn't adapt $federation_script" >&2; exit 1; }

find . -name '*.bak' -not -path '*/node_modules/*' -delete
echo "$site adapted for ${origin}${prefix}/"
