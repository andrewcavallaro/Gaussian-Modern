"""Check the committed Type 1 fonts and TeX files against the OpenType fonts.

Pure Python (FontTools only), so CI can run it without FontForge or TeX.
"""
import re, struct
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
T1 = ROOT / 'fonts' / 'type1'
TEXMF = ROOT / 'texmf'
STYLES = ['Regular', 'Italic', 'Semibold', 'SemiboldItalic']


def pfb_segments(data):
    """Yield (type, bytes) for each PFB segment; type 1 = ASCII, 2 = binary."""
    i = 0
    while i < len(data):
        assert data[i] == 0x80, 'not a PFB segment marker'
        kind = data[i + 1]
        if kind == 3: return
        n = struct.unpack('<I', data[i + 2:i + 6])[0]
        yield kind, data[i + 6:i + 6 + n]
        i += 6 + n
    raise AssertionError('PFB has no end marker')


for st in STYLES:
    ps = f'GaussianModern-{st}'
    otf = TTFont(ROOT / 'fonts' / 'otf' / f'{ps}.otf')
    hmtx = otf['hmtx']

    segs = list(pfb_segments((T1 / f'{ps}.pfb').read_bytes()))
    head = segs[0][1].decode('latin-1')
    assert [k for k, _ in segs] == [1, 2, 1], ps
    assert f'/FontName /{ps} def' in head, ps
    assert 'Andrew Cavallaro' in head and 'Knuth' in head, ps

    afm = (T1 / f'{ps}.afm').read_text()
    assert f'FontName {ps}' in afm, ps
    widths = {n: int(w) for w, n in re.findall(r'WX (\d+) ; N (\S+) ;', afm)}
    assert len(widths) == len(otf.getGlyphOrder()) - 1, (ps, len(widths))   # all but .notdef
    # FontForge files U+2044 under its Adobe Standard Encoding name
    rename = {'fraction': 'fractionsolidus'}
    bad = [n for n, w in widths.items() if abs(hmtx[rename.get(n, n)][0] - w) > 1]
    assert not bad, (ps, bad[:5])
    assert len(re.findall(r'^KPX ', afm, re.M)) > 2000, ps
    assert re.search(r'N f ;.* L i fi ;', afm), ps

    pfm = (T1 / f'{ps}.pfm').read_bytes()
    assert struct.unpack('<H', pfm[0:2])[0] == 0x100 and struct.unpack('<I', pfm[2:6])[0] == len(pfm), ps

    low = st.lower()
    for rel in [f'fonts/tfm/public/gaussianmodern/gmd-{low}-t1.tfm',
                f'fonts/tfm/public/gaussianmodern/gmd-{low}-t1--base.tfm',
                f'fonts/vf/public/gaussianmodern/gmd-{low}-t1.vf',
                f'fonts/type1/public/gaussianmodern/{ps}.pfb',
                f'fonts/afm/public/gaussianmodern/{ps}.afm']:
        assert (TEXMF / rel).is_file(), rel
    assert (TEXMF / f'fonts/type1/public/gaussianmodern/{ps}.pfb').read_bytes() == (T1 / f'{ps}.pfb').read_bytes(), ps
    print(ps, f'Type 1: {len(widths)} glyphs, widths match OpenType; AFM, PFM, TeX files present')

mapfile = (TEXMF / 'fonts/map/dvips/gaussianmodern/gaussianmodern.map').read_text()
for st in STYLES:
    line = next(l for l in mapfile.splitlines() if l.startswith(f'gmd-{st.lower()}-t1--base '))
    enc = re.search(r'<\[(\S+)', line).group(1)
    assert (TEXMF / 'fonts/enc/dvips/gaussianmodern' / enc).is_file(), enc
    assert line.endswith(f'<GaussianModern-{st}.pfb'), line
for f in ['tex/latex/gaussianmodern/gaussianmodern.sty', 'tex/latex/gaussianmodern/t1gmd.fd']:
    assert (TEXMF / f).is_file(), f
print('TeX map, encoding and LaTeX files consistent')
