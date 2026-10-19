# Design and construction notes

## The intended voice

The family keeps a generous lowercase and open interior spaces, while reducing some of the decorative gestures that drew attention to individual letters. Warmth comes from the proportions and bracketed serifs. Restraint comes from restrained terminals and a more regular rhythm.

## Construction

| Area | Construction |
| --- | --- |
| Upright Latin letters and digits | Drawn outlines combined with Gauss-modelled outlines from the METAFONT programs in `source/metafont/`, with glyph-specific weighting |
| Serifs and terminal character | More of the compact Gauss-modelled treatment, particularly in `l`, `t`, and `Q` |
| Text italic styles | True italic forms with a slightly reduced slant, normalized to the shared proportions |
| Supporting Latin repertoire | Drawn outlines, recomposed with the upright bases where applicable |
| Upright text ligatures | Assembled from the base letters to preserve their geometry and spacing |
| Mathematics | Drawn math outlines mapped to Unicode and integrated with the text letters, metrics, and OpenType MATH layout data |

The upright core contains 52 basic Latin letters and 10 digits. The Gauss-modelled share of each upright outline is 34% by default, 43% for `a` and `g`, 64% for `l` and `t`, and 65% for `Q`. These are construction parameters, not measures of perceptual effect or research-derived optimal values.

The Gauss-modelled outlines were taken from the METAFONT programs evaluated with their drawing-nib values set to zero, so they are outline captures rather than exact exports of the bitmap font. Before combining, ink extents were aligned and contours were sampled at 1,500 pixels per em, matched by orientation and position, and rebuilt as cubic curves. Glyphs whose combined outlines showed uneven joins were redrawn as clean cubic paths at the same ink extents and advances.

The JSON and UFO masters contain the resulting curves. OTF uses cubic outlines. TTF converts those curves to quadratic outlines with a 0.65-unit approximation tolerance.

## Deliberate design decisions

- **A** has its own distinctive construction, shared by its accented forms.
- **Q** has a clean bowl and a shallow curved tail ending in a rounded cap.
- **J** joins its vertical and lower-left curve tangentially.
- **E** and **F** have slim, curved front serifs on their right-facing arms, with a compact middle fin; their rear serifs and the F foot are plain.
- **l** in the regular weight has a slightly heavier stem (about 87 units) than a plain fit would give, but stays lighter than the h/i stems (about 96–98 units) to balance its long vertical.
- **L** in the semibold has a 55-unit lower arm.

## Shared proportions

The design uses 1,000 units per em. Its target lowercase x-height is 515 units, capital height 710, figure height 680, ascender height 745, and descender depth 240. Curved forms include optical overshoots. The regular and semibold upright models share this framework; italic styles keep their own true italic structures.

Digits are tabular. Text word space is 280 units. Kerning was scaled to the final widths and screened for direct ink collisions at a large raster size. This is an engineering check, not a substitute for extended visual spacing review.

## Mathematics

The companion has its own `math` script registration and `ssty` substitutions. Script and scriptscript forms are 4% and 7.5% wider in their own em space; their displayed sizes are controlled by the MATH table. The table uses a 281-unit axis and a 47-unit fraction/radical rule thickness.

Large delimiter chains and assembly parts are carried into OpenType. The 0.108 additions are assembled from the font's own glyphs by `scripts/build_math_additions.py`: … ⋯ ⋮ ⋱ use the square math period and centred dot set solid at their own advance (vertical and diagonal dots keep the same pitch); ∣ is the vertical bar; ⟸ and ⟹ lengthen the rules of ⇐ and ⇒ by the width of = less a 3mu join, as TeX builds `\Longrightarrow`; ⏞ and ⏟ are the curly braces, all sizes and assembly parts, turned through 90° and set on the wide accents' 600-unit line and its mirror below the baseline. Hats and tildes have six width variants each. Common TeX overlay constructions such as not-equal and non-membership have been turned into encoded glyphs. Mathematical italic and bold italic are distinct from the text italic family.

The font does not supply complete sans, monospaced, fraktur, or every other mathematical alphabet. Some math variants remain unencoded (`source/math-unencoded.txt`). Applications needing absent ranges should use an explicit fallback for those ranges.

## Design judgments and research

The restrained terminals, generous counters, and distinguishable forms are design intentions. Their effect on perceived warmth, reading speed, fatigue, or learning has not been measured here. The right next comparison is actual text and equations at intended sizes, followed by reader testing if performance claims are desired.
