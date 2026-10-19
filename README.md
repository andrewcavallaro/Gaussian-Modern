# Gaussian Modern

A serif text family with an OpenType mathematics companion based on the beautiful typesetting found in Gauss's Werke https://archive.org/details/werkecarlf03gausrich

Glyphs were averaged from the original text but liberty was taken to optimize for viewing on digital screens.

**Development release 0.108 · with an unreleased native Unicode expansion**

The math companion now covers the full 1,082-character expansion checklist.
See [design notes](docs/native-unicode-design.md) and the
[four-page preview](docs/native-unicode-proof.pdf). This is a design draft for review.


Gaussian Modern takes its upright proportions, serifs and terminals in part from
the roman type of C. F. Gauss, *Werke*, Band III (Göttingen, 2nd printing 1876).
Those Gauss-modelled shapes were produced with METAFONT programs built on Donald
Knuth's Computer Modern, included under `source/metafont/`.

## License

Original font work, sources, project code, and documentation are released under
[MIT](LICENSE). Inherited Computer Modern material retains Knuth's notices and the
requirement to rename modified files/packages. See [LICENSE.md](LICENSE.md) and
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) for the precise scope.

## Fonts

| Family | Styles | Unicode mappings per style |
| --- | --- | ---: |
| Gaussian Modern | Regular, Italic, Semibold, Semibold Italic | 303 |
| Gaussian Modern Math | Regular | 2,078 |

Both OTF and TTF are included. Install **one format**, using the five files in
`fonts/otf/` or `fonts/ttf/`; installing both can create duplicate menu entries.
The mathematical companion has 3,723 glyphs, including unencoded size variants
and assembly parts.

For older software and classic TeX, the four text styles also come as hinted
**Type 1** fonts (`fonts/type1/`: PFB outlines with AFM and PFM metrics) and as a
ready-to-install TeX tree (`texmf/`) for pdfLaTeX, dvips and plain TeX. The
mathematics companion is OpenType only.

**How to use the fonts** in applications, on the web, and in XeLaTeX, LuaLaTeX,
pdfLaTeX, plain TeX and PostScript: see [USAGE.md](USAGE.md).

The current design keeps a distinctive A, rounded Q tails, smooth J hooks,
refined E/F front serifs, and a slightly stronger regular lowercase l. Text
features include kerning, common f-ligatures, tabular lining digits, and basic
combining-mark attachment.

## Preview

- [Reading and mathematics specimen](specimens/GaussianModern-Specimen.pdf)

## Build

Requires Python 3.10 or later. From this repository's root:

```sh
python -m pip install -r requirements.txt
python source/build.py
python source/validate.py
python scripts/check_identity.py
```

To build from the editable UFO masters instead:

```sh
python source/build.py --from-ufo
```

Create a release archive with `python scripts/package.py`; the result is placed
in `dist/`.

Both routes write five OTF and five TTF files into `fonts/otf/` and `fonts/ttf/`. They use only the
included masters and FontTools; a METAFONT installation is not needed. Changes are not
synchronized automatically between JSON and UFO. See [CONTRIBUTING.md](CONTRIBUTING.md).

The Type 1 fonts and TeX files are generated from the OTF files:

```sh
python scripts/build_type1.py   # needs FontForge, LCDF Typetools and TeX Live
python scripts/check_type1.py   # FontTools only
```

The METAFONT programs under `source/metafont/` build with TeX Live
(`mf '\mode=ljfour; input gwr10'`). They are kept as the origin of the
Gauss-modelled shapes; the JSON and UFO masters are authoritative for the fonts.

## Quick start in LaTeX

XeLaTeX or LuaLaTeX, with the OpenType text and maths fonts:

```tex
\usepackage{fontspec}
\usepackage{unicode-math}
\setmainfont{GaussianModern-Regular.otf}[
  Path=fonts/otf/,
  ItalicFont=GaussianModern-Italic.otf,
  BoldFont=GaussianModern-Semibold.otf,
  BoldItalicFont=GaussianModern-SemiboldItalic.otf]
\setmathfont{GaussianModernMath-Regular.otf}[Path=fonts/otf/]
```

pdfLaTeX, with the Type 1 text fonts (install `texmf/` first, see USAGE.md):

```tex
\usepackage{gaussianmodern}
```

To regenerate the specimen, run `xelatex GaussianModern-Specimen.tex` from
`specimens/`, with fontspec, unicode-math, and the document's other packages
installed. The supplied specimen has been checked in XeTeX; other math layout
engines have not yet been qualified.

## Repository contents

| Path | Contents |
| --- | --- |
| `fonts/otf/`, `fonts/ttf/` | Ten installable OpenType files |
| `fonts/type1/` | Type 1 text fonts: PFB, AFM, PFM |
| `texmf/` | TeX tree: TFM, VF, encoding, map, `gaussianmodern.sty` |
| `source/masters/` | Cubic JSON masters and MATH layout data |
| `source/ufo/` | Editable UFO 3 masters |
| `source/features/` | OpenType feature definitions |
| `source/metafont/` | METAFONT programs for the Gauss-modelled roman (Computer Modern based) |
| `specimens/` | Specimen PDF, its TeX source, and the preview image |
| `scripts/` | Type 1 build, maths additions builder, checks, and release packaging |
| `tests/` | pdfLaTeX test for the Type 1 fonts; XeLaTeX/LuaLaTeX proof of the 0.108 changes |
| `.github/workflows/build.yml` | Build and validation checks, including Type 1 |

See [USAGE.md](USAGE.md) for using the fonts, [GITHUB.md](GITHUB.md) for repository setup, [CHANGES.md](CHANGES.md) for
revision history, and [VALIDATION.md](VALIDATION.md) for checks and limitations.

## Development limits

This is a working design release. Dedicated screen hinting, optical sizes,
small capitals, broader language proofing, and cross-engine math qualification
remain future work. The OpenType files are unhinted; the Type 1 files carry
FontForge autohints. Combining-mark support handles basic single accents, not
arbitrary stacked accents. Some source math variants remain unencoded, listed
in `source/math-unencoded.txt`. No controlled reading or learning study has
validated the design.
