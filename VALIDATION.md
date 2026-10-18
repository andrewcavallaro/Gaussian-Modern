# Validation record

**Release 0.107 · 18 October 2026**

## Built files

| Face | Glyphs | Unicode mappings | Formats checked |
| --- | ---: | ---: | --- |
| Regular | 311 | 303 | OTF, TTF |
| Italic | 311 | 303 | OTF, TTF |
| Semibold | 311 | 303 | OTF, TTF |
| Semibold Italic | 311 | 303 | OTF, TTF |
| Math Regular | 2,403 | 981 | OTF, TTF |

The four text styles also exist as Type 1 fonts (310 glyphs each, Adobe Standard Encoding)
and as TeX metrics in the T1 (Cork) encoding.

The math count includes unencoded size variants, assembly components, and script-size alternates; it does not mean 2,403 independently encoded characters.

## Checks completed

- All ten font files opened with checksum checking enabled. All tables and glyph outlines were decoded successfully.
- Printable ASCII is present. Only space and nonbreaking space have empty outlines.
- Each text style has the 13 documented combining marks, equal-width lining digits, `liga` and `ccmp` substitutions, and `kern` and `mark` positioning.
- Shaping confirmed active kerning and ligatures in all four text styles. For example, regular `AV` closes by 99 units with kerning enabled, and `ffi` closes by 40 units with its ligature enabled.
- The mathematics font has an OpenType MATH table and a registered `math` script, 29 vertical variant constructions, 13 vertical assemblies, and two horizontal accent variant constructions. All referenced glyphs and connector-length bounds passed checks.
- Common arithmetic, relation, set, calculus, and arrow characters were checked for Unicode coverage, including not-equal, non-membership, partial derivative, mapping arrow, ratio colon, and mathematical lambda.
- All five UFO masters were read back. Their glyph sets, Unicode assignments, advances, feature text, and outline bounds match the JSON masters.
- Fonts built from the UFO masters match those built from the JSON masters in every metric, mapping, feature and MATH table. Outlines draw identical shapes; in three OTFs, a few glyphs store their contours in a different order.
- Name records were checked for family, PostScript name, version, copyright and license scope (`scripts/check_identity.py`).
- The three-page specimen compiled with XeTeX and `unicode-math`. PDF font inspection confirmed that only the five Gaussian Modern faces were embedded, with no fallback math font, and the pages were rendered and visually inspected.

## Type 1 and TeX checks

- Each PFB passed `t1lint` and has the standard three-segment structure; every AFM glyph width matches the OpenType advance exactly, and each AFM carries 2,700–3,500 kerning pairs and the f-ligatures.
- PFB and OTF rasters were compared for every encoded character at 120 px. They agree apart from hinting differences (median 2%), except four glyphs that FreeType cannot map to Unicode from their traditional names (`dotlessj`, `asteriskcentered`, `bardbl`, `interrobangdown`); their outlines are present and TeX addresses them by name.
- A test document with accents, ligatures, kerning, quotes, dashes and guillemets compiled with pdfLaTeX, and with `latex` + `dvips` + Ghostscript. Both PDFs embed the four Gaussian Modern Type 1 fonts and render identically.
- A plain TeX file, a PostScript program using the fonts by name (with Latin-1 reencoding), and Ghostscript's PDF output were checked.
- Rebuilding the Type 1 fonts and TeX files reproduces them byte for byte. `scripts/check_type1.py` rechecks them against the OpenType fonts.

`source/validate.py` reruns the structural font checks. `source/validation.json` records file hashes and counts. The archive also includes a SHA-256 manifest.

## Limits of these checks

These checks do not certify every kerning pair, every mathematical expression, all target applications, or every screen-rendering environment. They are not a specialist font-engine certification or a controlled readability study. The package remains a working design release, with manual contour finishing, broader language proofing, hinting, and cross-engine math validation still appropriate before a production release.
