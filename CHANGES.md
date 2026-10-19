# Changes

## Unreleased

- Document explicit unicode-math alphabet selection and exercise legacy math
  alphabet commands in the native proof to avoid unintended text-font fallback.

- Build all 1,082 previously missing reference Unicode characters from native
  Gaussian Modern outlines and original drawings, plus a combining horn needed
  for Vietnamese compositions. No Latin Modern outlines are imported.
- Add original alphabet families, symbols, accents, delimiter constructions and
  display operator variants. Math now has 2,078 mappings and 3,723 glyphs.
- Preserve the original checklist, add a four-page proof and reproducible native
  geometry sources, and extend validation and CI. This remains a design draft.

- Add combining three dots above (U+20DB) and four dots above (U+20DC) to
  Gaussian Modern Math, for `\dddot` and `\ddddot`. Both extend the existing
  double-dot accent with the same dot shape, spacing and height, zero advance,
  and a centred MATH attachment. JSON and UFO sources and OTF/TTF fonts agree.
- Add a TeX proof for one through four dots on lowercase, uppercase, Greek,
  bold and italic variables, including script and scriptscript sizes.
- Add double, triple and quadruple primes (U+2033, U+2034 and U+2057),
  composed from the existing single prime with unicode-math's default
  repeated-prime spacing. The proof covers Unicode input, apostrophes and
  script sizes. That intermediate build had 995 Unicode mappings and 2,438 glyphs.
- Add a reproducible Latin Modern Math coverage audit and a CSV of remaining
  missing Unicode mappings, separating alphabet entries from other symbols.

## 0.108 — 18 October 2026

Semibold i/l refinements and nine mathematics symbols.

- Upright Semibold i: straight, parallel stem (136 units, matching n and h)
  and a smoother, symmetric dot. The dotless i, í ì î ï, ij, fi and ffi carry
  the new shape.
- Upright Semibold l: ink narrowed 6% (239 to 225 units) and height lowered
  from 745 to 730 units; the advance width is unchanged. ĺ, ľ, fl, ffl and
  the mark anchors follow.
- The bold mathematical i and l (U+1D422, U+1D425) and their script-size
  forms take the same changes.
- Semibold and Semibold Italic fi and ffi: the arm of the f before the i is
  shorter (30 and 20 units), so its terminal clears the i dot by 59 and 61
  units instead of 30 and 41 (Regular 47, Italic 62) and no longer runs into
  it at text sizes. The terminal's shape, the i, and the ligature widths are
  unchanged.
- Gaussian Modern Math adds … ∣ ⋮ ⋯ ⋱ ⏞ ⏟ ⟸ ⟹ (U+2026, U+2223, U+22EE,
  U+22EF, U+22F1, U+23DE, U+23DF, U+27F8, U+27F9), built from the font's own
  glyphs by the new `scripts/build_math_additions.py`:
  - … is three square math periods set solid; ⋯, ⋮ and ⋱ are three centred
    dots at the same pitch, horizontal, vertical and diagonal, on the axis.
  - ∣ is the vertical bar, and stretches with the bar's assembly.
  - ⟸ and ⟹ are ⇐ and ⇒ with the rules lengthened by the width of = less a
    3mu join (1,270 units, as TeX builds `\Longrightarrow`), with horizontal
    assemblies cut from the same outlines.
  - ⏞ and ⏟ are the curly braces turned through 90°: the five sizes as
    variants, then the brace assembly parts, set on the wide accents'
    600-unit line and its mirror below the baseline.
  Now 990 Unicode mappings and 2,433 glyphs.
- Type 1 fonts and the TeX tree rebuilt. `build_type1.py` now pins the Type 1
  alignment zones per style: with the shorter Semibold l, FontForge's guessed
  ascender zone (730–757) was too tall for its BlueScale and failed `t1lint`.
  Hinting is otherwise unchanged. The AFM `Descender` of Regular and Semibold
  is now the depth of p (−228), as the AFM specification defines it.
- New proof `tests/math-additions.tex` for XeLaTeX and LuaLaTeX; specimen
  and preview rebuilt.

## 0.107 — 18 October 2026

First release of Gaussian Modern.

- Text family in Regular, Italic, Semibold and Semibold Italic, each with 303
  Unicode mappings, kerning, common f-ligatures, tabular lining digits, and basic
  combining-mark attachment.
- Gaussian Modern Math, an OpenType MATH companion with 981 Unicode mappings and
  2,403 glyphs, including size variants and assembly parts.
- OTF and TTF builds from cubic JSON masters or editable UFO 3 masters, with
  GitHub Actions validation.
- Type 1 versions of the four text styles (hinted PFB, AFM with kerning and
  ligatures, PFM) and a TeX tree for pdfLaTeX, dvips and plain TeX, with the
  `gaussianmodern` LaTeX package.
- Usage guide (`USAGE.md`) for applications, the web, XeLaTeX/LuaLaTeX,
  pdfLaTeX, plain TeX and PostScript.
- Underline position and thickness set in all fonts (−100 and 50 units).
- METAFONT sources for the Gauss-modelled roman, built on Computer Modern.
