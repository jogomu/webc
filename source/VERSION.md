# Text version

The underlying text in this repository is **frozen** at the version described
below. Notes in this project refer to this version in particular. It will not
change unless we intentionally update it, in which case this file must be
updated and `books/` regenerated (`./render.sh`).

| | |
|---|---|
| Edition | `eng-web-c` — World English Bible, Catholic edition (eBible.org) |
| Upstream version | digitally signed by eBible.org **2026-07-24 09:47:28 UTC** |
| Pulled | **2026-07-26** |
| Source page | <https://ebible.org/find/show.php?id=eng-web-c> |

## Archives pulled

| File | SHA-256 |
|------|---------|
| [`eng-web-c_usfm.zip`](https://ebible.org/Scriptures/eng-web-c_usfm.zip) | `d4901f9f788d1ea1b15bf1477f44f3518b3d7e8a064d5a0e67c2297613f1a08e` |
| [`eng-web-c_usfx.zip`](https://ebible.org/Scriptures/eng-web-c_usfx.zip) | `07bfcf295149f93043a5d4479e1ad490e7bb828ed4139ef833f828edbedc2f1b` |

`source/usfm/` is the verbatim contents of the USFM archive; `source/metadata/`
holds `eng-web-cmetadata.xml` and `BookNames.xml` from the USFX archive.

## Verification (performed at pull time, 2026-07-26)

- Every hosted file in `source/usfm/` matches the SHA-256 checksums inside
  eBible.org's signed manifest [`source/usfm/signature.txt.asc`](usfm/signature.txt.asc)
  (75 files checked, all OK).
- The manifest's PGP signature verifies as a good signature from
  “World English Bible editors \<editors@eBible.org\>”,
  DSA key `54D714D76956DA6673DC1EEA5F62009D93505F26`
  ([`source/usfm/keys.asc`](usfm/keys.asc)).

To re-verify at any time, from the repo root:

```sh
./run_bash.sh
cd source/usfm
grep -E "^[0-9a-f]{64}  " signature.txt.asc | sha256sum -c
gpg --import keys.asc && gpg --verify signature.txt.asc
```
