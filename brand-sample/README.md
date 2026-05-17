# brand-sample

A small Paragon brand package that recolors Open edX with an autumn-inspired palette, demonstrating how to use the [design tokens](https://github.com/openedx/paragon) interface to theme platform MFEs.

| Before | After |
|---|---|
| ![Authn MFE without theme](./docs/images/authn-without-theme.png) | ![Authn MFE with theme](./docs/images/authn-with-theme.png) |

> [!IMPORTANT]
> Requires an Open edX environment with design-token support: Paragon >= 23 and the "Teak" release or later.

## How to use it

See the root [README](../README.md) for setup. The short version:

- **With Tutor** — [`tutor-contrib-sample`](../tutor-contrib-sample/) configures the brand override from jsDelivr automatically.
- **Without Tutor** — point your MFE at the published CSS via `env.config.js[x]` (see [Consuming the published brand](#consuming-the-published-brand) below).
- **Hacking on the brand locally with Tutor** — see [Local brand development with Tutor](#local-brand-development-with-tutor) below.
- **Hacking on the brand locally without Tutor** — these docs are coming soon.

## How it works

The brand source is a small set of Paragon [design tokens](./tokens/src/themes/light/global/color.json). The npm `build` script (see [`package.json`](./package.json)) invokes Paragon's `build-tokens` and `build-scss` to compile `dist/light.min.css`, which consumer MFEs load as a Paragon `brandOverride` on top of the default light theme.

## Consuming the published brand

For an MFE configured via `env.config.js[x]`:

```js
const config = {
  PARAGON_THEME_URLS: {
    variants: {
      light: {
        urls: {
          default: 'https://cdn.jsdelivr.net/npm/@openedx/paragon@$paragonVersion/dist/light.min.css',
          brandOverride: 'https://cdn.jsdelivr.net/gh/openedx/sample-plugin@main/brand-sample/dist/light.min.css',
        },
      },
    },
  },
};

export default config;
```

For a frontend-base site, set the equivalent in `site.config.tsx`:

```tsx
const siteConfig: SiteConfig = {
  // ...
  theme: {
    variants: {
      light: {
        url: 'https://cdn.jsdelivr.net/gh/openedx/sample-plugin@main/brand-sample/dist/light.min.css',
      },
    },
  },
};
```

## Local brand development with Tutor

Use [tutor-contrib-paragon](https://github.com/openedx/openedx-tutor-plugins/tree/main/plugins/tutor-contrib-paragon) to recompile and serve the brand from your local checkout instead of jsDelivr.

First, install the plugin and build its image:

```bash
tutor plugins install https://github.com/openedx/openedx-tutor-plugins/tree/main/plugins/tutor-contrib-paragon
tutor plugins enable paragon
tutor images build paragon-builder
tutor dev start -d lms cms mfe
```

After each edit to the theme sources, copy them into the Tutor root and rebuild. From the root of this repo:

```bash
tutor_root="$(tutor config printroot)"
[ -n "$tutor_root" ] \
  && rm -rf "$tutor_root/env/plugins/paragon/theme-sources/themes" \
  && cp -r brand-sample/tokens/src/themes "$tutor_root/env/plugins/paragon/theme-sources" \
  && tutor dev do paragon-build-tokens \
  && echo 'Your design tokens are ready to be built :)' \
  || echo 'Could not copy design token sources into tutor environment :('
```

If the build fails, check that `"$(tutor config printroot)/env/plugins/paragon"` looks like:

```
└── theme-sources
    └── themes
        └── light
            └── global
                └── color.json
```