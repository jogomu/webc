# World English Bible Catholic Edition (WEBC) with additional notes

This repository hosts the **World English Bible, Catholic edition** (73-book canon)
as published by [eBible.org](https://ebible.org/find/show.php?id=eng-web-c), plus
notes added in this project. The translation text itself is unchanged.

> **Text version:** eBible.org `eng-web-c`, digitally signed upstream
> **2026-07-24**, pulled **2026-07-26**, integrity verified against eBible.org's
> GPG-signed manifest. The text is frozen at this version — our notes refer to it
> specifically. Full details and re-verification steps:
> [`source/VERSION.md`](source/VERSION.md).

**Start reading: [books/README.md](books/README.md)** — one Markdown file per book,
rendered directly by GitHub.

## Layout

| Path | What it is |
|------|------------|
| `source/VERSION.md` | Which upstream version the text is frozen at, and how it was verified |
| `source/usfm/` | The canonical USFM sources from eBible.org, hosted **verbatim** — never edited here |
| `source/metadata/` | Translation metadata and book names from eBible.org |
| `books/` | Generated reading view (Markdown) — regenerate with `./render.sh`, never hand-edit |
| `notes/` | This project's fold-in layer (e.g. corrections), applied at render time |
| `tools/` | The rendering code |

Two roles, two layers:

1. **`source/usfm/` is lossless.** USFM is eBible.org's master format; every other
   format they publish is generated from it. It carries editorial data invisible in
   any rendering: Strong's concordance numbers on nearly every word (~1.26 million
   `\w` markers), 3,300+ translator footnotes (some with embedded Hebrew),
   cross-references, words-of-Jesus markup, poetry indentation, psalm descriptors,
   speaker labels, and more. Hosting it verbatim means this repository never loses
   information relative to the upstream editorial work. The accompanying
   `signature.txt.asc` / `keys.asc` are eBible.org's GPG signature of the sources.
2. **`books/` is a readable view.** Generated Markdown, one file per book, with
   chapter headings, verse numbers, footnotes, cross-references, and poetry layout.
   It deliberately omits machine-oriented markup (e.g. Strong's numbers) for
   readability — the source layer keeps it.

## Corrections

Editorial fold-ins are applied to the reading view at render time and come in
**classes**, each with its own visual treatment and label: `typo` corrections
render as strikethrough plus a highlighted replacement ("The Second Book of
~~Mosis~~ <mark>Moses</mark>"), `nova-vulgata` alternate readings use an
underlined replacement plus a superscript <sup>NV</sup> badge (readings the
Nova Vulgata omits are struck with the badge alone), and `editor` notes leave
the text untouched and live only in the notes. The original wording always remains visible, and the
`source/` tree is never touched. Project notes keep their own class-prefixed
markers (c1…, e1…) in a "Notes (this project)" section on each book page — a
separate cadence from the translation's own numbered footnotes. Entries are
indexed by book and location in
[`notes/corrections.json`](notes/corrections.json) (format, classes, and
rendered examples in [`notes/README.md`](notes/README.md)); rendering fails if
an entry no longer matches its target exactly.

## Reproducible tooling

All project code runs inside a project-specific Docker image, not host tools:

```sh
./build.sh     # build the webc-tools image
./render.sh    # regenerate books/ from source/usfm/ (runs in the container)
./run_bash.sh  # interactive shell in the container, repo mounted at /work
```

## License and attribution

The World English Bible is in the **public domain**. It is brought to you courtesy
of [eBible.org](https://ebible.org). "World English Bible" is a trademark that may
only be used to refer to faithful copies of the text as distributed from eBible.org;
this project does not change the text. See
[`source/usfm/copr.htm`](source/usfm/copr.htm) for the full statement.

Notes added by this project are kept distinct from the translation's own footnotes,
so nothing here should be read as originating from eBible.org except the contents
of `source/` and the text rendered from it.
