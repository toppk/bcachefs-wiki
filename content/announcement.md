---
title: Announcement

# Keep this file in the repo; the banner only shows if you set
# one of the activation fields below. By default, nothing renders.
#
# For full behavior and options, see inline docs in:
# layouts/partials/emergency-banner.html

# Content-only mode: set banner: true and write your notice below.
banner: true

# Optional configuration
# (Content-only) No frontmatter text/html is used; body below is rendered.
banner_scope: all   # all | home
banner_level: warning  # info | warning | danger
banner_id: demo-announce-6

# Prevent generating a public /announcement/ page while keeping the
# page available to templates (requires Hugo build options support)
build:
  render: false
  list: false
  publishResources: false
---

<!--
To activate the site-wide banner:
1) Set banner: true above
2) Put your notice in this body (Markdown allowed)

Dismissal persists per browser session only. To re-show for everyone,
change banner_id to a new unique value.
-->
Hi there, this not the real site, go to [bcachefs.org](https://bcachefs.org/) for the current site, or give us [feedback](https://github.com/toppk/bcachefs-wiki/issues) on this test site.
