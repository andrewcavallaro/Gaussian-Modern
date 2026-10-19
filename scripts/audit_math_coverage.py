"""Compare encoded math coverage with an installed reference font.

python scripts/audit_math_coverage.py --reference /path/to/latinmodern-math.otf \
    --unicode-math-table /path/to/unicode-math-table.tex

No reference outlines are copied. Reports distinguish unicode-math letters,
other math entries and additional reference-font characters. Missing cmap
entries do not establish that the font lacks a related unencoded outline.
"""
import argparse
import csv
import hashlib
import re
import unicodedata
from collections import Counter
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--unicode-math-table', type=Path, required=True)
    args = parser.parse_args()
    font_path = ROOT / 'fonts/otf/GaussianModernMath-Regular.otf'
    font, reference = TTFont(font_path), TTFont(args.reference)
    current, comparison = font.getBestCmap(), reference.getBestCmap()
    pattern = r'\\UnicodeMathSymbol\{"([0-9A-Fa-f]+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}'
    table = {int(u, 16): (command.strip(), kind) for u, command, kind, _ in
             re.findall(pattern, args.unicode_math_table.read_text())}
    rows = []
    for code in sorted(set(comparison) - set(current)):
        command, kind = table.get(code, ('', ''))
        category = ('Letters, mathematical alphabets and styled digits'
                    if kind == r'\mathalpha' or 0x1D400 <= code <= 0x1D7FF else
                    'Other unicode-math symbols' if kind else 'Additional reference characters')
        rows.append({'codepoint': f'U+{code:04X}', 'character': chr(code),
                     'unicode_name': unicodedata.name(chr(code), 'UNNAMED'),
                     'latex_command': command, 'math_class': kind,
                     'category': category, 'reference_glyph': comparison[code]})
    counts = Counter(row['category'] for row in rows)
    output = ROOT / 'docs'
    output.mkdir(exist_ok=True)
    with (output / 'missing-math-characters.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, lineterminator='\n', fieldnames=['codepoint', 'character', 'unicode_name',
            'latex_command', 'math_class', 'category', 'reference_glyph'])
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        '# Math coverage audit', '',
        'This is an encoded-character comparison, not a claim that every reference character',
        'is essential or that every absent character needs a new drawing. TeX may compose',
        'some symbols, and Gaussian Modern contains unencoded glyphs and differently encoded',
        'related forms. Font fallbacks can also conceal missing characters.', '',
        f"Reference: **{reference['name'].getDebugName(1)}, {reference['name'].getDebugName(5)}**.",
        f'Gaussian Modern Math: **{len(current):,} Unicode mappings**, '
        f'**{len(font.getGlyphOrder()):,} glyphs**.',
        f'Reference: **{len(comparison):,} Unicode mappings**; '
        f'**{len(set(current) & set(comparison)):,}** are also in Gaussian Modern.', '',
        '| Absent reference characters | Count |', '| --- | ---: |',
        *[f'| {label} | {counts[label]:,} |' for label in [
            'Letters, mathematical alphabets and styled digits', 'Other unicode-math symbols',
            'Additional reference characters']],
        f'| Total absent Unicode mappings | {len(rows):,} |', '',
        'The full list, including code points, Unicode names and LaTeX commands where',
        'available, is in [missing-math-characters.csv](missing-math-characters.csv).', '',
        '## Coverage result', '',
        ('All reference Unicode mappings are present.' if not rows else
         'The CSV lists the remaining reference Unicode mappings.'), '',
        'The original expansion checklist is preserved in `source/native-unicode-targets.json`.',
        'New glyphs use Gaussian Modern outlines and original constructions; the generators',
        'do not read Latin Modern outlines. See [native design notes](native-unicode-design.md).', '',
        '## Scope and reproducibility', '',
        'The reference is Latin Modern Math, not all of Unicode. The unicode-math table',
        'is used only to label and group missing reference characters; entries unsupported',
        'by the reference font are outside this comparison. Unencoded glyphs, shaping',
        'variants, MATH constructions, kerning and visual quality are outside a cmap audit.', '',
        'Regenerate with:', '', '```sh',
        'python scripts/audit_math_coverage.py --reference /path/to/latinmodern-math.otf \\',
        '  --unicode-math-table /path/to/unicode-math-table.tex', '```', '',
        'Input SHA-256 hashes:', '',
    ]
    for label, path in [('Gaussian Modern Math OTF', font_path),
                        ('Reference font', args.reference), ('unicode-math table', args.unicode_math_table)]:
        lines.append(f'- {label}: `{hashlib.sha256(path.read_bytes()).hexdigest()}`')
    (output / 'math-coverage.md').write_text('\n'.join(lines) + '\n')
    print(f'{len(rows)} absent reference mappings: {dict(counts)}')


if __name__ == '__main__':
    main()
