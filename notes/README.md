# Project notes layer

Everything in this directory is authored by this project, **not** by eBible.org.
It is folded into the generated reading view (`books/`) by `./render.sh`; the
`source/` tree stays verbatim.

Project notes keep a marker cadence entirely separate from the translation's
own footnotes: the WEB's translator footnotes remain ordinary numbered
footnotes, while project notes carry class-prefixed markers (`c1`, `c2`, …
for text corrections; `e1`, `e2`, … for editor notes) that link to a
**Notes (this project)** section on each book page. Markers are assigned at
render time in document order — they are never stored in the notes data, so
adding an entry never requires renumbering others.

## corrections.json

Entries come in two shapes. **Replacement classes** render as strikethrough
of the original wording followed by a class-styled replacement
(`~~original~~ <mark>corrected</mark>`), so the source text always stays
visible and the exact replacement span is unambiguous. **Pure-footnote
classes** leave the text completely untouched: the marker is attached after
the anchor phrase and the content lives only in the note. Fields:

| Field | Meaning |
|-------|---------|
| `book` | USFM book code (`GEN`, `EXO`, … `REV`) |
| `where` | `"title"` for the book title, or `"chapter:verse"` (e.g. `"3:14"`) |
| `type` | Class — see the table below (defaults to `typo`) |
| `find` | Exact target text as it appears in the rendered view (for pure-footnote classes: the anchor phrase the marker follows) |
| `replace` | Replacement wording (replacement classes); may be `""` for a deletion-only reading — the original is struck with nothing in its place |
| `insert` | Added wording (replacement classes, instead of `replace`): the anchor `find` stays unstruck and the addition follows it — for text the source has but WEBC lacks |
| `note` | The note content (pure-footnote classes only) |
| `occurrence` | Optional: which match within the verse (1-based) if `find` appears more than once |
| `reason` | Optional: appended to the generated note (replacement classes) |

`where` always uses **this repository's (WEBC) numbering** — renumbering
WEBC is out of scope. Source numbering can differ, especially in the
deuterocanon (e.g. WEBC Esther (Greek) 4:31 corresponds to Nova Vulgata
Esther 4:17q). Whenever that is the case, the `reason` must cite the
source's own location, so the note the reader sees says where the alternate
reading lives in that source.

## Classes

Each class has a distinct visual treatment, so a reader can tell at a glance
what kind of editorial bit they are looking at; the note label is the
authoritative indicator. Classes are registered in `NOTE_TYPES` in
[`tools/usfm2md.py`](../tools/usfm2md.py); an entry with an unregistered
`type` fails the render.

| `type` | Shape | Rendering | Note label |
|--------|-------|-----------|------------|
| `typo` | replacement | ~~original~~ <mark>replacement</mark><sup>c#</sup> | Typo correction (this project) |
| `nova-vulgata` | replacement | ~~original~~ <ins>replacement</ins><sup>NV</sup><sup>c#</sup> | Nova Vulgata reading |
| `lxx` | pure footnote | anchor text<sup>x#</sup> — text unchanged | Septuagint reading |
| `editor` | pure footnote | anchor text<sup>e#</sup> — text unchanged | Editor’s note |

Policy: only Nova Vulgata-based English renderings replace text in place
(strikethrough / underline / badge), and an in-text nova-vulgata reading
must itself be a rendering of the Latin. Only when the Latin is doubtful —
genuinely admitting multiple senses — does the English rendering follow the
liturgical tradition (e.g. the Grail Psalter); if that liturgical rendering
already matches WEBC's text, no alternate reading is entered. Readings from other sources, such as
the Septuagint, are footnote alternates only — the marker sits on the
anchor phrase and the alternate wording lives in the note, on its own
cadence (`x1`, `x2`, …).

`typo` marks an outright error being corrected; `nova-vulgata` presents an
alternate reading following the Nova Vulgata, with the WEB wording left
visible in the strikethrough; `editor` carries the (unnamed) editor's
thought without touching the text.

The reading view therefore supports **two coherent paths** through a
verse: follow the struck-through words (ignoring the underlined readings)
and you are reading pure WEBC; follow the underlined,
<sup>NV</sup>-badged readings (skipping the struck text) and you are
reading an NV-compatible text. For this reason an NV alternate is entered
even where a WEBC translator footnote already mentions the same reading —
the footnote is a remark, while the entry is a selectable reading in the
text. It is also why every replacement must remain grammatical within its
verse along both paths.

The superscript <sup>NV</sup> **badge** is part of the reading itself and
appears whether or not the replacement is empty. That matters for verses
thought to be inauthentic, where the Nova Vulgata reading is a deletion:
`"replace": ""` renders as ~~original~~<sup>NV</sup> — struck text, no
underlined segment — and the badge is the visual cue that the omission
follows the Nova Vulgata.

The mirror case is an **insertion** — text the source has but WEBC lacks.
An entry with `insert` instead of `replace` renders as
anchor text <ins>added text</ins><sup>NV</sup> — nothing struck, the
underline plus badge marking exactly what was added and on whose authority
(e.g. 2 Samuel 13:27: "…go with him. <ins>Absalom made a feast like a
king’s feast.</ins><sup>NV</sup>"). Future variant classes will likewise use
their visual treatment to indicate the **source** of the variant. Note that
GitHub's HTML sanitizer strips CSS colors, so class styling must come from
its allowed tags — `<mark>` (highlight), `<ins>` (underline), `<kbd>`
(bordered box), `<strong>`, `<em>`, `` `code` `` — rather than from
arbitrary colors.

## Examples

**`typo`** — live in the [Exodus](../books/03-EXO.md) and
[Leviticus](../books/04-LEV.md) titles:

> The Second Book of ~~Mosis~~ <mark>Moses</mark>, Commonly Called Exodus

**`editor`** — live at [Jude](../books/95-JUD.md) 1:11:

> <sup>11</sup> Woe to them! For they went in the way of Cain, and ran
> riotously in the error of Balaam for hire, and perished in Korah’s
> rebellion<sup>e1</sup>.

with, in the **Notes (this project)** section at the bottom of the page:

> **e1** **1:11** Editor’s note: Korah’s rebellion (Numbers 16) was against
> ordained authority; hence the Church retains an ordained hierarchy. ↩

**`nova-vulgata`** — live examples include [Genesis](../books/02-GEN.md)
49:24 ("~~But his bow remained strong.~~ <ins>And their bow was
broken,</ins><sup>NV</sup>") and [Hebrews](../books/88-HEB.md) 11:1. A
further illustrative (not yet adopted) showcase is the Prayer of Esther,
which differs substantially between
the WEB's Greek Esther (following the Septuagint) and the Nova Vulgata
(whose Esther additions follow the Old Latin tradition). Adopting the Nova
Vulgata's opening invocation at [Esther (Greek)](../books/43-ESG.md) 4:31
would be entered as:

```json
{
  "book": "ESG",
  "where": "4:31",
  "type": "nova-vulgata",
  "find": "O my Lord, you alone are our king.",
  "replace": "God of Abraham, God of Isaac, and God of Jacob, you are blessed.",
  "reason": "Nova Vulgata, Esther 4:17q: “Deus Abraham et Deus Isaac et Deus Iacob, benedictus es.”"
}
```

and would render in the chapter as:

> <sup>31</sup> She implored the Lord God of Israel, and said, “~~O my Lord,
> you alone are our king.~~ <ins>God of Abraham, God of Isaac, and God of
> Jacob, you are blessed.</ins><sup>NV</sup><sup>c1</sup> Help me. I am
> destitute, and have no helper but you, <sup>32</sup> for my danger is
> near at hand.

with, in the **Notes (this project)** section:

> **c1** **4:31** Nova Vulgata reading: the source reads “O my Lord, you
> alone are our king.” Nova Vulgata, Esther 4:17q: “Deus Abraham et Deus
> Isaac et Deus Iacob, benedictus es.” ↩

**`nova-vulgata`, deletion-only** — likewise illustrative. Matthew 17:21
stands in the WEB (whose base text follows the Majority Text) but is
omitted by the Nova Vulgata (which follows the critical Greek text; the
WEB's own translator footnote already observes "NU omits verse 21."):

```json
{
  "book": "MAT",
  "where": "17:21",
  "type": "nova-vulgata",
  "find": "But this kind doesn’t go out except by prayer and fasting.",
  "replace": "",
  "reason": "The Nova Vulgata, following the critical Greek text, omits this verse."
}
```

would render as:

> <sup>21</sup> ~~But this kind doesn’t go out except by prayer and
> fasting.~~<sup>NV</sup><sup>c1</sup>”

with, in the **Notes (this project)** section:

> **c1** **17:21** Nova Vulgata reading: the source reads “But this kind
> doesn’t go out except by prayer and fasting.” The text is struck with no
> replacement. The Nova Vulgata, following the critical Greek text, omits
> this verse. ↩

Rendering **fails** if an entry does not match its target exactly once
(or exactly at the given `occurrence`), so project notes cannot silently
drift if the frozen text is ever intentionally updated (see
`source/VERSION.md`).

## Reference material

Nova Vulgata reference material is not distributed as part of this
repository. Do not add a source corpus or large excerpts here; individual
notes may contain only the brief quotations needed to document their
readings. See [`AGENTS.md`](../AGENTS.md) for the user-supplied
reference-material workflow.

## Open research items

- Decide whether recurring, non-verse-anchored differences — “father of”
  vs “begot” (which may skip generations), “repent” vs “do penance”,
  “truly” vs “Amen”, and “steadfast love” vs “mercy” — need a mechanism
  for corpus-wide patterns.
- Exodus 40:26: investigate the Nova Vulgata's use of “propitiatory”; this
  is an observation to investigate, not currently an alternate reading.
- Sirach: review the Nova Vulgata's many additions using the same approach
  previously applied to Genesis.
