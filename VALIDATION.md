# Validation record

**Release 0.108 · 18 October 2026**

## Replacement PR verification · 19 October 2026

The replacement branch starts from the intact 0.107 main branch and retains every
tracked file. It applies the additions and modifications from PR #1 without its
file deletions, preserving the complete JSON, UFO and METAFONT sources and the
Type 1/pdfLaTeX distribution.

Checks rerun on this branch:

- `scripts/check_sources.py`: all five JSON/UFO glyph sets, outlines, metrics and
  feature sources agree; all referenced UFO glyph files exist.
- Both JSON and UFO builds complete; all ten fonts pass the structural and
  identity checks. Their cmap, advances, GSUB, GPOS and MATH tables agree.
- The math additions generator leaves its source outputs unchanged when rerun.
- All four supplied Type 1 fonts pass `t1lint` and `scripts/check_type1.py`.
- The math proof compiles with XeLaTeX without missing characters; the Type 1
  smoke test compiles with pdfLaTeX. The proof also exercises the reported
  “Outline” and “Ill-posed” words and Semibold Italic fi/ffi ligatures.

Local Type 1 regeneration could not be completed because the local FontForge
binary crashes. LuaLaTeX was not rerun locally for this replacement branch.
The added GitHub Actions workflow covers both builds, Type 1 regeneration,
pdfLaTeX, XeLaTeX, LuaLaTeX and release packaging in a clean Linux environment;
its result must be checked before merging. The release record below is retained
from PR #1 and includes checks beyond those rerun for this replacement.

## Built files

| Face | Glyphs | Unicode mappings | Formats checked |
| --- | ---: | ---: | --- |
| Regular | 311 | 303 | OTF, TTF |
| Italic | 311 | 303 | OTF, TTF |
| Semibold | 311 | 303 | OTF, TTF |
| Semibold Italic | 311 | 303 | OTF, TTF |
| Math Regular | 2,433 | 990 | OTF, TTF |

The four text styles also exist as Type 1 fonts (310 glyphs each, Adobe Standard Encoding)
and as TeX metrics in the T1 (Cork) encoding.

The math count includes unencoded size variants, assembly components, and script-size alternates; it does not mean 2,433 independently encoded characters.

## Checks completed

- All ten font files opened with checksum checking enabled. All tables and glyph outlines were decoded successfully.
- Printable ASCII is present. Only space and nonbreaking space have empty outlines.
- Each text style has the 13 documented combining marks, equal-width lining digits, `liga` and `ccmp` substitutions, and `kern` and `mark` positioning.
- Shaping confirmed active kerning and ligatures in all four text styles. For example, regular `AV` closes by 99 units with kerning enabled, and `ffi` closes by 40 units with its ligature enabled.
- The mathematics font has an OpenType MATH table and a registered `math` script, 32 vertical constructions with 14 assemblies, and 6 horizontal constructions (the two wide accents, the over- and underbrace, and the two long double arrows) with 4 assemblies. All referenced glyphs and connector-length bounds passed checks.
- Common arithmetic, relation, set, calculus, and arrow characters were checked for Unicode coverage, including not-equal, non-membership, partial derivative, mapping arrow, ratio colon, mathematical lambda, and the nine 0.108 additions.
- Fonts rebuilt from the JSON masters with FontTools 4.61.1 match the committed fonts byte for byte. Fonts built from the UFO masters match them in every table except the CFF outlines of three OTFs (Regular, Semibold, Math), where some contours start at a different point or in a different order; after normalising for that, every glyph draws the same outline. The five TTFs are identical.
- Name records were checked for family, PostScript name, version, copyright and license scope (`scripts/check_identity.py`).
- The three-page specimen compiled with XeTeX and `unicode-math`. PDF font inspection confirmed that only the five Gaussian Modern faces were embedded, with no fallback math font, and the pages were rendered and visually inspected. Every word sits where it did in 0.107; only the version in the footer changed.

## 0.108 changes

- **Semibold i:** the stem is straight and parallel (x = 89 to 225 from 120 to 521 units; the 0.107 right edge bowed out to a control point at x = 286) and measures 136 units, against 137 for n and h. The dot is symmetric, with no join kinked by more than about 3° (up to 26° before). The dotless i and í ì î ï contain the new outline, ij contains the new i, and fi and ffi contain it exactly at offsets of 352 and 704 units; the mark anchor is centred on it.
- **Semibold l:** ink 225 units wide (239 before, −5.9%), centred at x = 154.5 as before; height 730; advance 304. ĺ and ľ contain it exactly, and fl at a 352-unit offset. In ffl it sits within 1 unit, the same rounding offset as in 0.107. The mark anchors for l, ĺ and ľ moved down 15 units with it.
- **Semibold and Semibold Italic fi/ffi:** in both ligatures, the f before the i is unchanged below y = 590 and has its terminal moved left, by 30 units in Semibold and 20 in Semibold Italic, with the arm's curves eased between x = 254 and 330 (upright) or 380 and 440 (italic). Both x ranges are measured from the ligature's origin. The nearest distance from the f to the i dot is now 59 units in Semibold (was 30) and 61 in Semibold Italic (was 41); Regular has 47 and Italic 62. Advance widths, the i, and the AFM and TFM metrics are unchanged.
- **Math bold i/l:** `mb.i` and `mb.l` are identical to the Semibold outlines. Their `ssty1` and `ssty2` forms are horizontal expansions of the base forms (×1.04 and ×1.07, within 1 unit), the same transform as in 0.107. No other existing glyph in the math font changed.
- **Maths additions:** each of the nine new characters was checked in the built OTF against the glyphs it is made from. … is three `mi.period` outlines at a 322.7-unit pitch. ⋯, ⋮ and ⋱ are three `am.centerdot` outlines at a 248.8-unit pitch (horizontal, vertical and diagonal) and centred on the 281-unit axis. ∣ is identical to | and uses the same assembly. ⟸ and ⟹ match ⇐ and ⇒ except that the rules are 423 units longer (advance 1,270). Every ⏞ and ⏟ variant and assembly part is its { or } counterpart turned through 90° (within 2 units of rounding). The brace ink starts at 600, the line of the wide hats and tildes, and ⏟ mirrors it about half the x-height, ending at −85. Re-running `scripts/build_math_additions.py` reproduces the masters and fonts byte for byte. No Latin Modern or other outside outlines remain.
- `tests/math-additions.tex` compiled with XeLaTeX and LuaLaTeX with `\tracinglostchars=2`. Neither run reported a missing character, and both PDFs embed only Gaussian Modern faces. The rendered pages show the nine symbols in context; ∣ through `\bigm` … `\Biggm`, `\middle` and a twelve-row `\right` (the bar's assembly); over- and underbraces from one symbol to a full line (the five turned brace sizes, then the assembly); and, in LuaTeX, ⟸ and ⟹ stretched through their assemblies.

## Type 1 and TeX checks

- Each PFB passed `t1lint` and has the standard three-segment structure; every AFM glyph width matches the OpenType advance exactly, and each AFM carries 2,700–3,500 kerning pairs and the f-ligatures (`scripts/check_type1.py`).
- Rendered without hinting at 120 px, every encoded character of each PFB matches its OTF exactly. With hinting, the median difference is 2.1–2.6%, largest on the small accents. Four glyphs are excluded because FreeType cannot map them to Unicode from their traditional names (`dotlessj`, `asteriskcentered`, `bardbl`, `interrobangdown`); their outlines are present and TeX addresses them by name.
- The test document `tests/type1-pdflatex.tex` (accents, ligatures, kerning, quotes, dashes, guillemets) compiled with pdfLaTeX, and with `latex` + `dvips` + Ghostscript. Both PDFs embed the four Gaussian Modern Type 1 fonts and render identically apart from anti-aliasing.
- A plain TeX file and a PostScript program using the fonts by name (with Latin-1 reencoding), and Ghostscript's PDF output, were checked, including the Semibold i/l forms.
- Rebuilding the Type 1 fonts and TeX files reproduces them byte for byte. The same toolchain (FontForge 20230101, LCDF Typetools 2.110, TeX Live 2023) also reproduced the 0.107 files byte for byte from the 0.107 fonts. With the pinned alignment zones it produces identical charstrings for them; only the Private-dictionary layout and the AFM `Descender` differ.

`source/validate.py` reruns the structural font checks. `source/validation.json` records file hashes and counts. The archive also includes a SHA-256 manifest.

## Limits of these checks

These checks do not certify every kerning pair, every mathematical expression, all target applications, or every screen-rendering environment. They are not a specialist font-engine certification or a controlled readability study. The package remains a working design release, with manual contour finishing, broader language proofing, hinting, and cross-engine math validation still appropriate before a production release.

Points noted during the 0.108 proofs and left as they are:

- … uses the 117-unit square math period, so it is heavier than ⋯ (84-unit centred dots), as `x.y` and `x⋅y` already are.
- The smallest braces are the text-size { turned (890 units wide), so a brace over a single letter overhangs it. Above the Bigg size (2,658 units) braces switch to the heavy assembly (140-unit rule), as the vertical braces do.
- Tall ∣ and | come from the bar's assembly, whose extender is 70 units wide against 48 for the bar itself (unchanged from 0.107).
- The other long arrows (⟵ ⟶ ⟷ ⟺) are not included.
- At 730 units, with a 107-unit stem, the Semibold l is visibly shorter and lighter than b, d, h and k (745 units, about 137-unit stems). Its stem is 78% of n's, against 91% in Regular.
