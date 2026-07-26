# Agent guidance for this repository

This repository hosts the World English Bible (Catholic edition) from
eBible.org, frozen at the version recorded in `source/VERSION.md`, plus a
fold-in layer of project notes. Read `README.md` for the full layout.

## The source is immutable

- **Never edit anything under `source/`.** It is the verbatim, GPG-signed
  text from eBible.org; its integrity is verifiable against
  `source/usfm/signature.txt.asc` and must stay that way. An intentional
  upstream refresh is the only reason `source/` may change, and it requires
  updating `source/VERSION.md` and re-running the verification documented
  there.
- **Never hand-edit anything under `books/`.** It is generated output.
  Regenerate it with `./render.sh`.

## All changes are fold-ins at rendering time

Any change to the presented text — corrections, variant readings, editor
notes, future classes — must be expressed as data under `notes/` (see
`notes/README.md`) and folded in by `tools/usfm2md.py` when rendering.
Replacement classes keep the original wording visible (strikethrough plus a
class-styled replacement); insertion entries add class-styled text without
striking anything; pure-footnote classes leave the text untouched. The page
must stay readable along two paths — following the struck text yields pure
WEBC, following the badged readings yields a source-compatible text — so
replacements must remain grammatical in context, and an alternate reading
is still entered even if a WEBC translator footnote mentions the same
reading (the footnote is a remark, not a selectable reading).
Project notes use class-prefixed markers assigned at render time, on a
separate cadence from the translation's own footnotes — never embed markers
in the notes data. Whenever a Nova Vulgata alternate English rendering is
placed in the text (a replacement or insertion), its note must always quote
the underlying Latin in the `reason` field — the converter enforces this;
deletion-only readings are the exception, since the source has no text to
quote. Do not weaken the converter's guards: a fold-in that does
not match its target exactly, or that uses an unregistered class, must fail
the render.

## Nova Vulgata reference material

For work requiring the Nova Vulgata, use any local cache of the Latin and
accompanying English rendering that the user has supplied or identified.
Prefer that material to independently fetching, transcribing, or translating
the text. Treat the Latin as controlling and the supplied English as the
preferred working rendering; report any apparent conflict rather than
silently substituting another rendering.

If no such cache has been identified or is accessible, ask the user whether
one is available before beginning the source comparison.

External reference material must remain outside this repository. Never commit
a corpus or large excerpts; only brief quotations required by individual
notes belong here.

## Tooling

All project code runs inside the project Docker image, never host tools:
`./build.sh` builds the `webc-tools` image, `./render.sh` regenerates
`books/`, `./run_bash.sh` opens a shell with the repo mounted at `/work`.
