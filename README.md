# Roygbviz wiki

This repo holds the source for the Roygbviz wiki: everything I know about making research figures with [Roygbviz](https://github.com/KhaiShea/roygbviz), my plotnine theme and palette.

## Read the wiki

**[khaishea.github.io/roygbviz-kb](https://khaishea.github.io/roygbviz-kb/)**

That's the best way to read it, with search, a menu, light and dark mode, and figures you can enlarge. The pages here are plain Markdown, so they also read fine on GitHub if you'd rather. Start with [Start here](start-here.md).

## Looking for the code?

The library itself lives in its own repo: **[KhaiShea/roygbviz](https://github.com/KhaiShea/roygbviz)**. That's where to install it from, read the source, or report a bug in Roygbviz.

This repo is only the wiki. If something on a wiki page is wrong or unclear, [open an issue here](https://github.com/KhaiShea/roygbviz-kb/issues).

<details>
<summary><strong>Working on the wiki</strong></summary>

Every figure has the script that made it in [`scripts/`](scripts/), and all example data is synthetic. The site uses a small layout of my own in the style of [GitHub Docs](https://docs.github.com/en), built on GitHub's [Primer](https://primer.style/) CSS. The menu, breadcrumbs and home page cards all come from [`_data/nav.yml`](_data/nav.yml).

To preview the site with the same Jekyll setup GitHub Pages uses:

```bash
bundle install
bundle exec jekyll serve   # then open http://localhost:4000/roygbviz-kb/
```

No Ruby? Docker works too. This runs in the background, so it works from any terminal:

```bash
docker run -d --rm --name rv-kb -p 4000:4000 -p 35729:35729 -v "$PWD":/site -w /site \
  -e HOME=/tmp -e BUNDLE_PATH=/site/vendor/bundle --user "$(id -u):$(id -g)" ruby:3.3 \
  bash -c "bundle install && bundle exec jekyll serve --host 0.0.0.0 --livereload"
docker logs -f rv-kb   # watch it start; Ctrl+C stops watching, not the server
docker stop rv-kb      # when you're done
```

In fish, write `(id -u):(id -g)` instead of `"$(id -u):$(id -g)"`.

After adding a new page, restart the preview (`docker restart rv-kb`). The link plugin remembers which pages exist from when the server started, so links to a brand-new page stay as `.md` until then. GitHub Pages always builds from scratch, so the live site isn't affected.

</details>
