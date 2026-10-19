# Contributing

Original project contributions use the MIT license. Preserve inherited Computer
Modern notices and its naming condition. Add third-party font material only with
its license and attribution. See LICENSE.md and THIRD-PARTY-NOTICES.md.

Edit either the cubic JSON masters or the corresponding UFOs. Rebuild with
`python source/build.py` or `python source/build.py --from-ufo`, then run
`python source/validate.py` and `python scripts/check_identity.py`.
The maths additions (… ∣ ⋮ ⋯ ⋱ ⏞ ⏟ ⟸ ⟹) are generated from other glyphs;
after changing the period, centred dot, bar, double arrows or curly braces, run
`python scripts/build_math_additions.py` before rebuilding.
After changing a text font, rebuild the Type 1 fonts and TeX files with
`python scripts/build_type1.py` (needs FontForge, LCDF Typetools and TeX Live)
and run `python scripts/check_type1.py`.

The compiler does not synchronize changes between JSON and UFO sources. Update
both representations together before submitting a font change. Preserve glyph
names referenced by features and MATH records, check dependent accented forms
and ligatures, and include an enlarged proof and a reading-size specimen.

A, the rounded Q tails, smooth J hooks, E/F front serifs, and strengthened regular
l are deliberate current design decisions. Explain any change to them.
