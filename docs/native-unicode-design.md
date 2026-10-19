# Native Unicode expansion — design draft

The expansion covers all 1,082 code points in the frozen
`source/native-unicode-targets.json` checklist, plus U+031B combining horn.
Gaussian Modern Math now has 2,078 encoded characters and 3,723 glyphs.
The comparison covers Latin Modern Math 1.959, not all Unicode mathematics.
The text faces and Type 1 fonts retain their previous coverage.

## Construction

`scripts/build_native_unicode.py` composes existing Gaussian Modern outlines
and draws new symbols using `native_geometry.py`. `native_alphabets.py` contains
original centreline drawings for sans-serif, monospaced, Fraktur and open-faced
letters and digits. Bold script uses the existing Gaussian script capitals;
bold upright Greek is constructed from the native Greek. Compositions reuse
native letters and marks. These are new constructions, not Latin Modern outlines.
The reference font supplies only the coverage checklist in the audit.

These additions are maintained in Python, JSON and UFO sources, alongside the
preserved historical METAFONT sources. They are not new METAFONT programs.
Per-glyph construction provenance is in `source/native-unicode.json`.

## Review and limitations

The [four-page proof](native-unicode-proof.pdf) shows representative mathematics,
alphabet families and Latin/Vietnamese combinations. Coverage and structural
validation do not establish professional typographic quality for every glyph.
The original alphabet designs need visual review before a release.

New wide accents have discrete variants up to 24,000 units, rather than unlimited
horizontal assemblies. Existing extensible constructions remain intact; several
new delimiters reuse their native assemblies. Lenticular brackets use finite sizes.
The font version remains 0.108 while this extension is unreleased.

## Rebuild

```sh
python -m pip install -r requirements.txt
python scripts/build_math_additions.py
python scripts/build_native_unicode.py
python source/build.py
python source/validate.py
python scripts/check_sources.py
```

The generators do not open external font files. The coverage audit separately
reads a reference cmap; see `docs/math-coverage.md` for its inputs and hashes.
