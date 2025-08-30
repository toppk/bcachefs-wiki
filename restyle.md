# Restyle Plan — Transition to Documentation Design

Goals

- Establish a clean documentation-first layout and components as shown in the mock.
- Keep navigation simple and predictable across sections (Docs, Developers, Architecture, News).
- Improve readability (typography, measure, spacing) and mobile behavior.
- Minimize content moves up front; focus on presentation, then iterate on IA.

Summary Of Changes

- Layout: content column at ~72–80ch, optional right rail on home only; persistent left margin for breathing room on wide screens.
- Header: brand at left, primary nav centered/left-aligned, Patreon as a pill on the right; burger on mobile.
- Breadcrumbs: light background strip under header; show section and current page.
- Sidebar: “On this page” (auto ToC) and “In this section” lists; hide ToC on mobile.
- Typography: increase heading contrast and hierarchy; compact lists; improve code and pre overflow handling.
- News: card list with dates on the News landing; RSS link visible.
- Color system: light neutrals for surfaces, teal‑green links, and a reserved red accent.

Information Architecture (light-touch for now)

- Add a top-level `Documentation` section (`content/using/`) to match the mock’s primary tab.
- Keep existing sections: `developer/`, `architecture/`, `news/`.
- Create a minimal `content/using/_index.md` landing with intro and quick links. Migrate pages later as a separate pass.

Implementation Checklist (Hugo + CSS)

- [ ] Confirm color tokens (see “Color palette mapping” and questions).
- [ ] Update site title in `hugo.toml` from “bcachefs wiki” to “bcachefs” (or preferred) to match the less “wiki” tone.
- [ ] Add `content/using/_index.md` so the “Documentation” nav item resolves.
- [ ] Breadcrumbs: keep current partial but verify copy and separators match mock (`layouts/partials/breadcrumbs.html`).
- [ ] Header/nav: verify current base matches mock; adjust spacing if needed (`layouts/_default/baseof.html`).
- [ ] Sidebar: keep ToC + “In this section”; verify it hides on mobile (`layouts/partials/sidebar.html`).
- [ ] Section landing pages: list children in a simple list; News uses cards with dates (`layouts/_default/list.html`).
- [ ] Home page: add “News” rail on the right only for home. If desired, create a `layouts/index.html` with a `News` partial for the rail.
- [ ] Typography scale and spacing: verify heading sizes and line-height; tweak as needed in `assets/css/main.css`.
- [ ] Code blocks: keep horizontal scroll and prevent layout shift on mobile.
- [ ] Add callouts (optional): add shortcodes `shortcodes/callout.html` supporting info | warning | danger using the tokens below.

Files To Touch

- `hugo.toml`: site title; optional `[markup.tableOfContents]` config if we want different levels.
- `assets/css/main.css`: tokenize colors, spacing, and finalize link/hover, header/breadcrumb backgrounds, card borders.
- `layouts/_default/baseof.html`: header/nav structure; container behavior.
- `layouts/_default/single.html`: main article + sidebar container; leave wikilink transforms intact for legacy content.
- `layouts/_default/list.html`: News card layout and section listings.
- `layouts/partials/breadcrumbs.html`: visual separators and background.
- `layouts/partials/sidebar.html`: ToC and “In this section” behavior; mobile visibility.
- `layouts/index.html`: optional homepage composition with right-side News rail.

Color palette mapping (proposed)

Provided colors

- `#172E4E`, `#1F262E`, `#2E4769`, `#333333`, `#467265`, `#4F4F4F`, `#619E92`, `#DF362D`, `#F4F4F2`, `#FAFAF8`

Role tokens

- Body text: `--c-text: #1F262E`
- Muted text: `--c-muted: #4F4F4F`
- Link: `--c-link: #467265`
- Link hover: `--c-link-hover: #619E92`
- Header background: `--c-header-bg: #F4F4F2`
- Breadcrumb background: `--c-crumb-bg: #FAFAF8`
- Surface default (page bg): `--c-surface: #FAFAF8`
- Surface alt (cards, code): `--c-surface-alt: #F4F4F2`
- Border: `--c-border: rgba(31, 38, 46, 0.12)` (derived from `#1F262E`)
- Accent strong (danger): `--c-danger: #DF362D`
- Brand deep (optional headings/nav emphasis): `--c-brand-deep: #172E4E`
- Brand slate (optional subtle accents): `--c-brand-slate: #2E4769`

CSS variable stub (to implement in `assets/css/main.css`)

```css
:root {
  --c-text: #1F262E;
  --c-muted: #4F4F4F;
  --c-link: #467265;
  --c-link-hover: #619E92;
  --c-header-bg: #F4F4F2;
  --c-crumb-bg: #FAFAF8;
  --c-surface: #FAFAF8;
  --c-surface-alt: #F4F4F2;
  --c-border: rgba(31,38,46,.12);
  --c-danger: #DF362D;
  --c-brand-deep: #172E4E;
  --c-brand-slate: #2E4769;
}
```

Usage mapping (high level)

- Body/backgrounds use `--c-surface`; cards, code blocks, breadcrumb/header strips use `--c-surface-alt`/`--c-header-bg`.
- Links, nav items and interactive states use `--c-link` and `--c-link-hover`.
- Borders and dividers use `--c-border`.
- Danger/warnings use `--c-danger` (and keep the existing callout palettes for info/warn/danger).

Callout Tokens (used if we add shortcodes)

- Info: bg `#eef6ff`, text `#0b3a6f`
- Warning: bg `#fff8e6`, text `#5b3b00`
- Danger: bg `#ffebee`, text `#6f0b1a`

Typography & Spacing

- Base: system sans; 16px base; line-height 1.6.
- Headings: `h1` 28–32px; `h2` 22–24px; `h3` ~18–20px; bold for `h1/h2/h3`.
- Measure: article width ~80ch on wide screens.
- Lists: reduced indent; minimal spacing between items; paragraphs in list items have no extra margins.
- Code: `pre` scrolls horizontally; inline `code` does not break layout.

Accessibility

- Ensure 4.5:1 contrast for body text and link states on the chosen backgrounds.
- Maintain visible focus outlines on links and buttons (including Patreon pill).
- Burger control has `aria-label` and toggles expanded state (already present in markup; verify visually).

Nice-To-Haves (post restyle)

- Search: add client-side search (e.g., Pagefind/Lunr) surfaced in the header.
- Version switcher: if/when versioned docs are introduced.
- Dark mode: CSS variables make this easy later; defer for now.

Open Color Questions

1) Primary link color: confirm `#467265` with hover `#619E92` for accessibility and brand fit?
2) Header vs breadcrumb: OK with header `#F4F4F2` and breadcrumb `#FAFAF8` for subtle separation?
3) Borders: approve derived border `rgba(31,38,46,.12)` or prefer a solid from the palette?
4) Headings: stay `#1F262E` or use a subtle `#172E4E` tint for h1/h2?
5) Visited links: keep same as link, or slightly darken (e.g., `color-mix` 10% `#172E4E`)?

If you confirm these tokens, I’ll wire them into CSS variables and finalize the layout tweaks in the templates listed above.

Stage 1 Refresh — Complete

- Navbar: full‑bleed navy bar; brand in Light‑Green text; left‑aligned sections; Support/Getting Started/Patreon right‑aligned; normal‑case, unbold text; active = Royal, hover = Royal‑Blue with white strip; consistent height; earlier mobile collapse.
- Breadcrumbs: simplified separators to "/" and removed background/underline.
- Section layout: section intro header under breadcrumbs on all subpages; section landing auto‑redirects to first page.
- Sidebars: two‑column nav; left = section links in a light card; right = page ToC + optional "See also"; consistent weights; hover/active match navbar accents.
- Colors: centralized tokens; switched site to provided palette; added variables for Royal/Royal‑Blue/Navy/Light‑Green/Better‑White.
- Misc spacing: fixed top margin on first article heading, alignment, and jitter from hover underlines.

Stage 2 — TODOs / Open Work

- Root section: finalize homepage/header content, hero spacing, and any news rail or quick links.
- News section: confirm card design, metadata, and article styling; double‑check RSS placement and pagination spacing.
- ToC style: update right‑sidebar ToC visual (link sizes, bullets/indents, sticky behavior), plus See‑Also box treatment.
- Responsive: polish breakpoints for header and dual sidebars; decide mobile behavior (collapse left nav; ToC jump link; sticky header interactions); ensure no overflow or clipping.
- Site design page: add a reference page documenting the tokens, components, and layout rules with examples; link it from Developers.
- Accessibility: focus states on nav/sidebars, aria labels for burger/sidebars, color contrast re‑check after palette changes.
- Performance/cleanup: verify minified CSS via Hugo Pipes; remove legacy wiki styles once migration stabilizes.
