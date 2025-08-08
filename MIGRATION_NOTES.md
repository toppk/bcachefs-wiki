# Hugo Migration Notes

This document outlines the status of the migration from Ikiwiki to Hugo. The original goal was a *like-for-like* transition—keeping things as close as possible to the original site, with minimal changes to content.

---

## 🎯 Migration Goals

### Phase 1: Like-for-like Conversion (mostly complete)

* ✅ Set up basic Hugo site structure (`config`, layouts, content).
* ✅ Moved existing pages into Hugo under a section-based hierarchy.
* ✅ Converted key pages using idiomatic names, while keeping old URLs functional via `aliases`.
* ✅ Supported legacy `[[Page]]` wiki-style links temporarily (prefer `relref` going forward).
* 🔄 Page-by-page content verification is still in progress.

---

## 🗂 Content Organization

Content was moved into logical sections under `content/`, using lowercase filenames. The final URLs keep their CamelCase structure where needed (for familiarity and legacy support).

### Features

| Ikiwiki Filename     | Hugo Path                                      |
| -------------------- | ---------------------------------------------- |
| `Caching.mdwn`       | `content/features/caching_n_data_placement.md` |
| `Compression.mdwn`   | `content/features/compression.md`              |
| `Encryption.mdwn`    | `content/features/encryption.md`               |
| `ErasureCoding.mdwn` | `content/features/erasure_coding.md`           |
| `Snapshots.mdwn`     | `content/features/subvolumes_n_snapshots.md`   |

### Using

| Ikiwiki Filename      | Hugo Path                          |
| --------------------- | ---------------------------------- |
| `Fsck.mdwn`           | `content/using/fsck.md`            |
| `FAQ.mdwn`            | `content/using/faq.md`             |
| `GettingStarted.mdwn` | `content/using/getting_started.md` |

### Architecture

| Ikiwiki Filename        | Hugo Path                                   |
| ----------------------- | ------------------------------------------- |
| `Allocator.mdwn`        | `content/architecture/allocator.md`         |
| `Architecture.mdwn`     | `content/architecture/guide.md`             |
| `BtreeIterators.mdwn`   | `content/architecture/btree_iterators.md`   |
| `BtreeNodes.mdwn`       | `content/architecture/btree_nodes.md`       |
| `BtreePerformance.mdwn` | `content/architecture/btree_performance.md` |
| `BtreeWhiteouts.mdwn`   | `content/architecture/btree_whiteouts.md`   |
| `Transactions.mdwn`     | `content/architecture/transactions.md`      |
| `StablePages.mdwn`      | `content/architecture/stable_pages.md`      |

### Developer

| Ikiwiki Filename       | Hugo Path                                |
| ---------------------- | ---------------------------------------- |
| `Wishlist.mdwn`        | `content/developer/wishlist.md`          |
| `Debugging.mdwn`       | `content/developer/debugging.md`         |
| `Contributing.mdwn`    | `content/developer/contributing.md`      |
| `Irc.mdwn`             | `content/developer/irc.md`               |
| `Roadmap.mdwn`         | `content/developer/roadmap.md`           |
| `TestServerSetup.mdwn` | `content/developer/test_server_setup.md` |

### News

| Ikiwiki Filename       | Hugo Path                                 |
| ---------------------- | ----------------------------------------- |
| `news/members-v2.mdwn` | `content/news/members-v2.md`              |
| `News-full.mdwn`       | REMOVED |
| `index.mdwn`           | ⚠️ `content/_index.md` (needs work)       |

### Miscellaneous & Static

* PDF: `bcachefs-principles-of-operation.pdf` → `static/`
* Matrix server file: `.well-known/matrix/server` → `static/`
* CSS: `local.css` → `assets/css/main.css` (cleaned & minified)
* `sidebar.mdwn`: no longer used; replaced with a partial in Hugo

---

## 🌐 Deployment & Assets

* Hugo site builds and deploys via GitHub Actions.
* Published at: `https://bcachefs.bllue.org/`
* Custom domain & CNAME handled in CI.
* Static files like PDFs and `.well-known` data preserved under `static/`.

---

## ✅ Completed

* Initial migration to Hugo complete
* Section landing pages now include brief intros and optional footers
* Navigation includes sidebar, navbar, and breadcrumbs
* CSS simplified and cleaned up
* Home page partially ported

---

## 🔜 Next Steps

### 🧭 Navigation

* [ ] Make "bcachefs" logo in navbar link to homepage
* [ ] Add links in navbar: "Documentation", "Developer Docs", and "Patreon"
* [ ] Review sidebar: reduce redundancy, clean up old external links

### 🏠 Home Page

* [ ] Shrink homepage content significantly
* [ ] Move most content into proper sections
* [ ] Organize News section; display dates from frontmatter

### 🔗 Link Audit

* [ ] Find remaining Ikiwiki-style links:

  ```sh
  grep -RIn "\[\[[^]]\+\]" content
  ```

* [ ] Find root-absolute links:

  ```sh
  grep -RIn "/\(Features\|Developer\|Using\)/" content
  ```

* [ ] Convert internal links to `relref` (e.g. `{{< relref "features/compression.md" >}}`)
* [ ] Use `relURL` or absolute paths for static assets (e.g. PDFs)
* [ ] Add link checker (e.g. `lychee` or `htmltest`) to CI

### 🧱 Information Architecture

* [ ] Propose updated site structure
* [ ] Normalize to `content/<section>/<slug>/index.md`
* [ ] Improve internal linking using Hugo’s `ref`/`relref`

### ✏️ Content Improvements

* [ ] Identify missing or outdated pages
* [ ] Create outlines and seed missing docs
* [ ] Add diagrams, standardize tips, callouts, etc.

### 🎨 Visual Improvements

* [ ] Tune typography, colors, dark mode, and code blocks
* [ ] Improve accessibility
* [ ] Add or integrate site search

### 🔧 Tooling

* [ ] Add `hugo` builds and link checking to CI
* [ ] Enable preview deploys per PR

---

## 🧪 Handy Dev Command

Run local dev server:

```sh
hugo server --noHTTPCache --disableFastRender --bind 127.0.0.1 -p 31312
```
