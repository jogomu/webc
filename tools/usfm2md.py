#!/usr/bin/env python3
"""Render the USFM sources in source/usfm/ to GitHub-flavored Markdown in books/.

The Markdown output is a *reading view*: it deliberately drops machine-oriented
data (Strong's numbers, words-of-Jesus spans, toc entries) that is preserved in
the canonical source/usfm/ files. Do not hand-edit books/ — rerun this script.

Corrections from notes/corrections.json are folded in as strikethrough plus
replacement (~~original~~ corrected) with a "Correction (this project)"
footnote, so the source wording always stays visible. Each correction must
match exactly one place or rendering fails.

Usage: python3 tools/usfm2md.py [--src source/usfm] [--out books] [--notes notes]
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Paragraph-level markers (line-initial). Everything else is inline.
PARA_MARKERS = {
    "id", "ide", "h", "toc1", "toc2", "toc3", "mt1", "mt2", "mt3",
    "cl", "c", "ms1", "s1", "is1", "ip", "p", "m", "nb", "pc",
    "pi1", "mi", "q1", "q2", "q3", "b", "d", "sp", "li1",
}

POETRY = {"q1": "", "q2": "&emsp;", "q3": "&emsp;&emsp;"}
PROSE = {"p", "m", "nb", "pc", "pi1", "mi", "ip"}


def parse_blocks(text):
    """Split a USFM file into (marker, text) blocks at paragraph level."""
    blocks = []
    for line in text.splitlines():
        line = line.rstrip()
        m = re.match(r"\\([a-z0-9]+)( |$)", line)
        marker = m.group(1) if m else None
        if marker in PARA_MARKERS:
            blocks.append([marker, line[m.end():].strip()])
        elif blocks:
            # \v lines and continuation lines belong to the open block
            blocks[-1][1] = (blocks[-1][1] + " " + line.strip()).strip()
        # else: stray text before any marker; the WEB sources have none
    return blocks


class Renderer:
    def __init__(self):
        self.notes = []  # collected footnote/crossref bodies, in order

    def take_notes(self, text):
        """Replace \\f ...\\f* and \\x ...\\x* with GFM footnote references."""

        def sub_f(m):
            self.notes.append(self.format_footnote(m.group(1)))
            return f"[^{len(self.notes)}]"

        def sub_x(m):
            self.notes.append(self.format_crossref(m.group(1)))
            return f"[^{len(self.notes)}]"

        text = re.sub(r"\\f\s+\+?\s*(.*?)\\f\*", sub_f, text)
        text = re.sub(r"\\x\s+\+?\s*(.*?)\\x\*", sub_x, text)
        return text

    @staticmethod
    def strip_words(text):
        """Drop \\w / \\+w markup, keeping the word; keep \\+wh Hebrew text."""
        text = re.sub(r"\\\+?w\s(.*?)\|[^\\]*?\\\+?w\*", r"\1", text)
        text = re.sub(r"\\\+?w\s(.*?)\\\+?w\*", r"\1", text)
        text = re.sub(r"\\\+wh\s(.*?)\\\+wh\*", r"\1", text)
        return text

    def inline(self, text):
        """Convert inline character markup to Markdown (body text)."""
        text = self.take_notes(text)
        text = self.strip_words(text)
        text = re.sub(r"\\wj\s(.*?)\\wj\*", r"\1", text)  # red-letter: view drops it
        text = re.sub(r"\\\+?bk\s(.*?)\\\+?bk\*", r"*\1*", text)
        text = re.sub(r"\\qs\s(.*?)\\qs\*", r"*\1*", text)
        text = re.sub(r"\\v\s(\d[0-9a-b\-]*)\s*", r"<sup>\1</sup> ", text)
        return re.sub(r"  +", " ", text).strip()

    def format_footnote(self, body):
        body = self.strip_words(body)
        body = re.sub(r"\\\+?bk\s(.*?)\\\+?bk\*", r"*\1*", body)
        out = []
        # Footnote-internal markers style runs of text until the next marker.
        for m in re.finditer(r"\\(fr|ft|fl|fq|fqa|fp)\s(.*?)(?=\\f|\Z)", body):
            marker, chunk = m.group(1), m.group(2).strip()
            if not chunk:
                continue
            if marker == "fr":
                out.append(f"**{chunk}**")
            elif marker in ("fq", "fqa", "fl"):
                out.append(f"*{chunk}*")
            else:  # ft, fp
                out.append(chunk)
        return re.sub(r"  +", " ", " ".join(out)).strip()

    def format_crossref(self, body):
        body = self.strip_words(body)
        origin = re.search(r"\\xo\s(.*?)(?=\\|\Z)", body)
        target = re.search(r"\\xt\s(.*?)(?=\\|\Z)", body)
        out = "Cross reference:"
        if origin:
            out = f"**{origin.group(1).strip()}** {out}"
        if target:
            out += f" {target.group(1).strip()}"
        return out


# Each fold-in class renders the replacement with a distinct visual treatment
# so readers can tell what kind of change they are looking at (and, later,
# the source of a variant). GitHub's HTML sanitizer strips CSS colors, so
# classes must map to allowed tags: mark (highlight), ins (underline),
# kbd (bordered box), strong, em, code. The footnote label is the
# authoritative class indicator; the tag is the visual hint.
NOTE_TYPES = {
    "typo": {"tag": "mark", "label": "Typo correction (this project)", "ref": "c"},
    # "badge" is a superscript source tag appended to the reading itself, so
    # the source is visible even when "replace" is empty (deletion-only).
    "nova-vulgata": {"tag": "ins", "label": "Nova Vulgata reading", "ref": "c",
                     "badge": "NV"},
    # Footnote-only by policy: only Nova Vulgata-based English renderings
    # replace text in place; other sources' readings live in the notes.
    "lxx": {"label": "Septuagint reading", "ref": "x"},
    # No "tag" = pure-footnote class: the anchor text ("find") is left
    # untouched and the entry's "note" appears only in the footnote.
    "editor": {"label": "Editor’s note", "ref": "e"},
}


def note_type(corr):
    t = corr.get("type", "typo")
    if t not in NOTE_TYPES:
        raise ValueError(f"correction {corr['book']} {corr['where']}:"
                         f" unknown type {t!r}; known: {sorted(NOTE_TYPES)}")
    nt = NOTE_TYPES[t]
    if "tag" in nt:
        if ("replace" in corr) == ("insert" in corr):
            raise ValueError(f"correction {corr['book']} {corr['where']}:"
                             f" type {t!r} requires exactly one of"
                             " 'replace' (substitution/deletion) or"
                             " 'insert' (addition after the anchor)")
    elif "note" not in corr:
        raise ValueError(f"correction {corr['book']} {corr['where']}:"
                         f" type {t!r} requires a 'note' field")
    return nt


def strike(corr):
    t = note_type(corr)
    if "tag" not in t:
        return corr["find"]
    if "insert" in corr:
        # Addition: the anchor stays unstruck; the added text follows it.
        out = f"{corr['find']} <{t['tag']}>{corr['insert']}</{t['tag']}>"
    else:
        out = f"~~{corr['find']}~~"
        if corr["replace"]:
            out += f" <{t['tag']}>{corr['replace']}</{t['tag']}>"
    if "badge" in t:
        out += f"<sup>{t['badge']}</sup>"
    return out


def note_body(corr, source_phrase="the source reads"):
    t = note_type(corr)
    if "tag" not in t:
        return f"{t['label']}: {corr['note']}"
    if "insert" in corr:
        body = f"{t['label']}: the underlined text is an addition;" \
               " the source lacks it."
    else:
        body = f"{t['label']}: {source_phrase} “{corr['find']}”"
        body += "" if corr["find"].endswith((".", "!", "?", "”")) else "."
        if not corr["replace"]:
            body += " The text is struck with no replacement."
    if corr.get("reason"):
        body += f" {corr['reason']}"
    return body


def apply_correction(body, chap_label, corr, ref):
    """Fold one chapter:verse correction into rendered markdown, or die."""
    where = f"{corr['book']} {corr['where']} ({corr['find']!r})"
    chapter, verse = corr["where"].split(":")
    sec = re.search(
        rf"(?ms)^## {re.escape(chap_label)} {chapter}$(.*?)(?=^## |\Z)", body
    )
    if not sec:
        raise ValueError(f"correction {where}: chapter not found")
    # A verse span ends at the next verse-number sup; sups inserted by
    # earlier fold-ins in the same verse (badges, markers) don't end it.
    span = re.search(rf"(?s)<sup>{verse}</sup>.*?(?=<sup>\d|\Z)", sec.group(0))
    if not span:
        raise ValueError(f"correction {where}: verse not found")
    text, find = span.group(0), corr["find"]
    occurrence = corr.get("occurrence", 1)
    hits = text.count(find)
    if hits == 0 or occurrence > hits:
        raise ValueError(f"correction {where}: text not found in verse")
    if hits > 1 and "occurrence" not in corr:
        raise ValueError(f"correction {where}: ambiguous, {hits} matches"
                         " — set \"occurrence\" or widen \"find\"")
    idx = -1
    for _ in range(occurrence):
        idx = text.index(find, idx + 1)
    pos = sec.start() + span.start() + idx
    marker = f'<sup><a name="ref-{ref}"></a>[{ref}](#{ref})</sup>'
    return body[:pos] + strike(corr) + marker + body[pos + len(find):]


def version_line(src):
    """Version stamp from the signed manifest and VERSION.md, if present."""
    signed = pulled = None
    sig = src / "signature.txt.asc"
    if sig.exists():
        m = re.search(r"# Digitally signed (\d{4}-\d{2}-\d{2})", sig.read_text())
        signed = m and m.group(1)
    ver = src.parent / "VERSION.md"
    if ver.exists():
        m = re.search(r"\| Pulled \| \*\*(.*?)\*\*", ver.read_text())
        pulled = m and m.group(1)
    parts = ["Text version:"]
    if signed:
        parts.append(f"signed by eBible.org {signed}")
    if pulled:
        parts.append(f"(pulled {pulled})" if signed else f"pulled {pulled}")
    return " ".join(parts) if len(parts) > 1 else None


def render_book(text, version=None, corrections=()):
    blocks = parse_blocks(text)
    r = Renderer()
    header = {k: v for k, v in blocks if k in ("id", "h", "cl", "toc1")}
    code = header.get("id", "???")[:3]
    title = header.get("toc1") or header.get("h", code)
    chap_label = header.get("cl") or header.get("h", code)

    title_corrs = [c for c in corrections if c["where"] == "title"]
    for c in title_corrs:
        if title.count(c["find"]) != 1:
            raise ValueError(f"correction {code} title ({c['find']!r}):"
                             " must match exactly once")
        title = title.replace(c["find"], strike(c))

    out = [f"# {title}", ""]
    if version:
        out.append(f"*[World English Bible (Catholic)](README.md) — {version}.*")
        out.append("")
    for c in title_corrs:
        out.append(f"*{note_body(c, 'the source title reads')}*")
        out.append("")
    stanza = []   # open poetry stanza lines
    listing = []  # open list items

    def flush():
        if stanza:
            out.append("  \n".join(stanza))
            out.append("")
            stanza.clear()
        if listing:
            out.extend(f"- {li}" for li in listing)
            out.append("")
            listing.clear()

    for marker, raw in blocks:
        if marker in ("id", "ide", "h", "cl", "toc1", "toc2", "toc3",
                      "mt1", "mt2", "mt3"):
            continue
        if marker == "c":
            flush()
            out.append(f"## {chap_label} {raw}")
            out.append("")
        elif marker == "ms1":
            flush()
            out.append(f"**{r.inline(raw)}**")
            out.append("")
        elif marker in ("s1", "is1"):
            flush()
            out.append(f"### {r.inline(raw)}")
            out.append("")
        elif marker == "d":
            flush()
            out.append(f"*{r.inline(raw)}*")
            out.append("")
        elif marker == "sp":
            flush()
            out.append(f"**{r.inline(raw)}**")
            out.append("")
        elif marker == "b":
            flush()
        elif marker in POETRY:
            if listing:
                flush()
            line = r.inline(raw)
            if line:
                stanza.append(POETRY[marker] + line)
        elif marker == "li1":
            if stanza:
                flush()
            line = r.inline(raw)
            if line:
                listing.append(line)
        elif marker in PROSE:
            flush()
            para = r.inline(raw)
            if para:
                out.append(para)
                out.append("")
        else:
            raise ValueError(f"{code}: unhandled marker \\{marker}")

    flush()
    body = "\n".join(out)

    # Markers (c1…, e1…) are assigned here at render time, in document
    # order — never stored in the notes data, so adding an entry never
    # requires renumbering others.
    corr_notes = []
    counters = {}
    # Pure-footnote entries apply before replacements in the same verse:
    # their markers anchor to the original wording, which a replacement
    # entry may strike.
    verse_corrs = sorted(
        (c for c in corrections if c["where"] != "title"),
        key=lambda c: tuple(int(n) for n in c["where"].split(":"))
        + (0 if "note" in c else 1, c.get("occurrence", 1)),
    )
    for c in verse_corrs:
        prefix = note_type(c)["ref"]
        counters[prefix] = counters.get(prefix, 0) + 1
        ref = f"{prefix}{counters[prefix]}"
        body = apply_correction(body, chap_label, c, ref)
        corr_notes.append((ref, f"**{c['where']}** {note_body(c)}"))

    tail = []
    if corr_notes:
        # Project notes keep their own class-prefixed cadence (c1…, e1…) in
        # their own section; the WEB's translator footnotes below use GFM
        # footnotes, which GitHub numbers and lists separately.
        tail += ["", "## Notes (this project)", ""]
        tail.extend(
            f'- <a name="{ref}"></a>**{ref}** {note} [↩](#ref-{ref})'
            for ref, note in corr_notes
        )
    if r.notes:
        tail.append("")
        tail.extend(f"[^{i}]: {note}" for i, note in enumerate(r.notes, 1))
    return title, (body + "\n".join(tail)).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="source/usfm")
    ap.add_argument("--out", default="books")
    ap.add_argument("--notes", default="notes")
    args = ap.parse_args()

    src, out_dir = Path(args.src), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    corr_by_book = {}
    corr_file = Path(args.notes) / "corrections.json"
    if corr_file.exists():
        for c in json.loads(corr_file.read_text(encoding="utf-8"))["corrections"]:
            # In-text renderings from a badged source must let the reader
            # check the underlying Latin (deletions have none to quote).
            nt = NOTE_TYPES.get(c.get("type", "typo"), {})
            if ("badge" in nt and (c.get("replace") or c.get("insert"))
                    and "“" not in c.get("reason", "")):
                raise ValueError(
                    f"correction {c['book']} {c['where']}: in-text"
                    f" {c['type']} renderings must quote the underlying"
                    " Latin in 'reason'")
            corr_by_book.setdefault(c["book"], []).append(c)

    version = version_line(src)
    index = []
    for usfm in sorted(src.glob("*.usfm")):
        stem = re.sub(r"eng-web-c$", "", usfm.stem)  # 02-GENeng-web-c -> 02-GEN
        code = stem[3:]
        name, md = render_book(
            usfm.read_text(encoding="utf-8-sig"),
            version,
            corr_by_book.pop(code, ()),
        )
        (out_dir / f"{stem}.md").write_text(md, encoding="utf-8")
        index.append((stem, name))
        print(f"{usfm.name} -> {stem}.md")
    if corr_by_book:
        raise ValueError(f"corrections for unknown books: {sorted(corr_by_book)}")

    lines = [
        "# World English Bible (Catholic) — reading view",
        "",
        "Generated from [`source/usfm/`](../source/usfm/) by"
        " [`tools/usfm2md.py`](../tools/usfm2md.py). Do not edit by hand.",
        "",
    ]
    if version:
        lines[2:2] = [
            f"**{version}** — frozen; see"
            " [`source/VERSION.md`](../source/VERSION.md).",
            "",
        ]
    lines.extend(f"1. [{name}]({stem}.md)" for stem, name in index)
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(index)} books -> {out_dir}/")


if __name__ == "__main__":
    sys.exit(main())
