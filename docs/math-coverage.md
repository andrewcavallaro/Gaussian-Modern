# Math coverage audit

This is an encoded-character comparison, not a claim that every reference character
is essential or that every absent character needs a new drawing. TeX may compose
some symbols, and Gaussian Modern contains unencoded glyphs and differently encoded
related forms. Font fallbacks can also conceal missing characters.

Reference: **Latin Modern Math, Version 1.959**.
Gaussian Modern Math: **2,078 Unicode mappings**, **3,723 glyphs**.
Reference: **2,045 Unicode mappings**; **2,045** are also in Gaussian Modern.

| Absent reference characters | Count |
| --- | ---: |
| Letters, mathematical alphabets and styled digits | 0 |
| Other unicode-math symbols | 0 |
| Additional reference characters | 0 |
| Total absent Unicode mappings | 0 |

The full list, including code points, Unicode names and LaTeX commands where
available, is in [missing-math-characters.csv](missing-math-characters.csv).

## Coverage result

All reference Unicode mappings are present.

The original expansion checklist is preserved in `source/native-unicode-targets.json`.
New glyphs use Gaussian Modern outlines and original constructions; the generators
do not read Latin Modern outlines. See [native design notes](native-unicode-design.md).

## Scope and reproducibility

The reference is Latin Modern Math, not all of Unicode. The unicode-math table
is used only to label and group missing reference characters; entries unsupported
by the reference font are outside this comparison. Unencoded glyphs, shaping
variants, MATH constructions, kerning and visual quality are outside a cmap audit.

Regenerate with:

```sh
python scripts/audit_math_coverage.py --reference /path/to/latinmodern-math.otf \
  --unicode-math-table /path/to/unicode-math-table.tex
```

Input SHA-256 hashes:

- Gaussian Modern Math OTF: `121abdd0cca6ecdd2422d4898c17df402f432c7f6a7cd869cb5269620159da60`
- Reference font: `6075562b771f8b82f0c179e363389684f2dd09de30038269e2628e504bd7be0f`
- unicode-math table: `3976ff8f39c84b61055b1cb6851a1b2cfdefa918a2a642c954e6ceafdca7277e`
