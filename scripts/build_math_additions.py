"""Build mathematics additions from Gaussian Modern's own glyphs.

    python scripts/build_math_additions.py

Every new outline is assembled from glyphs already in the mathematics master,
so the additions share the font's drawing and need no outside material:

  U+2026 …  three math periods (mi.period) set solid
  U+22EF ⋯  three centred dots (am.centerdot) set solid, on the maths axis
  U+22EE ⋮  the same three dots stacked at the same pitch, centred on the axis
  U+22F1 ⋱  the same dots on the diagonal, at the same pitch
  U+20DB    combining three dots above, using the diaeresis dot and pitch
  U+20DC    combining four dots above, using the same dot and pitch
  U+2033 ″  double prime, made from the existing single prime
  U+2034 ‴  triple prime, at the same pitch as unicode-math's repeated primes
  U+2057 ⁗  quadruple prime
  U+2223 ∣  a copy of the vertical bar (sy.bar), with the bar's assembly
  U+27F9 ⟹  the double arrow (sy.arrowdblright) with its rules lengthened by
  U+27F8 ⟸  the width of = less a 3mu \\joinrel, as TeX builds \\Longrightarrow;
            horizontal assemblies are cut from the same outlines
  U+23DE ⏞  the curly braces { and } (all five sizes and the assembly
  U+23DF ⏟  parts) turned through 90 degrees; set on the wide accents' 600-unit
            line and its mirror below the baseline

The script is idempotent: it replaces any glyphs and MATH records it made
before, then rewrites the JSON master, the MATH data and the UFO master.
Rebuild the fonts afterwards with `python source/build.py`.
"""
import json
import math
import plistlib
import sys
from pathlib import Path
from types import SimpleNamespace
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.ufoLib import UFOWriter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'source'))
from font_model import bounds, contour, replay

MASTER = ROOT / 'source/masters/GaussianModernMath-Regular.json'
MATH = ROOT / 'source/masters/GaussianModernMath-MATH.json'
UFO = ROOT / 'source/ufo/GaussianModernMath-Regular.ufo'

OVER_BOTTOM = 600      # ink bottom of the wide hats and tildes (wide.*)
JOINREL = 1000 * 3 / 18  # TeX's \joinrel, -3mu
ARROW_PIECE = 300      # rule length of the arrow extender and tail pieces
ARROW_LAP = 100        # rule kept in front of the arrowhead piece


def r(v):
    return round(v, 4)


def mapped(c, f):
    return {'ink': c['ink'],
            'commands': [(op, [list(map(r, f(*p))) for p in args]) for op, args in c['commands']]}


def glyph(width, contours, unicode=None):
    g = {'width': r(width), 'contours': [contour(c['commands'], c['ink']) for c in contours], 'ic': 0.0}
    if unicode is not None:
        g['unicode'] = unicode
    return g


def rect(x0, y0, x1, y1):
    return {'ink': True, 'commands': [('moveTo', [[x0, y0]]), ('lineTo', [[x1, y0]]), ('lineTo', [[x1, y1]]),
                                   ('lineTo', [[x0, y1]]), ('closePath', [])]}


def points(g):
    return [p for c in g['contours'] for _, args in c['commands'] for p in args]


def main():
    model = json.loads(MASTER.read_text())
    spec = json.loads(MATH.read_text())
    previous = set(json.loads((ROOT / 'source/math-additions.json').read_text())
                   if (ROOT / 'source/math-additions.json').exists() else [])
    out = {}

    # Dots: Gaussian Modern's square period and centred dot.
    period, cdot = model['mi.period'], model['am.centerdot']
    pp, cp = period['width'], cdot['width']
    shift = lambda c, dx, dy: mapped(c, lambda x, y: (x + dx, y + dy))
    out['sy.ellipsis'] = glyph(3 * pp, [shift(c, k * pp, 0) for k in range(3) for c in period['contours']], 0x2026)
    out['sy.ellipsismidline'] = glyph(3 * cp, [shift(c, k * cp, 0) for k in range(3) for c in cdot['contours']], 0x22EF)
    out['sy.ellipsisvertical'] = glyph(cp, [shift(c, 0, (k - 1) * cp) for k in range(3) for c in cdot['contours']], 0x22EE)
    d = cp / math.sqrt(2)
    out['sy.ellipsisdownright'] = glyph(cp + 2 * d, [shift(c, k * d, (1 - k) * d) for k in range(3)
                                                     for c in cdot['contours']], 0x22F1)

    # Multiple-dot accents: extend the existing diaeresis. Keep its dot size,
    # pitch and vertical position; centre the complete accent at x=0, with
    # zero advance and an explicit MATH top-accent attachment, like uni0308.
    dots = sorted(model['uni0308']['contours'], key=lambda c: bounds({'contours': [c]})[0])
    assert len(dots) == 2
    boxes = [bounds({'contours': [c]}) for c in dots]
    centres = [(b[0] + b[2]) / 2 for b in boxes]
    pitch = centres[1] - centres[0]
    for count, code in [(3, 0x20DB), (4, 0x20DC)]:
        out[f'uni{code:04X}'] = glyph(0, [
            shift(dots[0], (k - (count - 1) / 2) * pitch - centres[0], 0)
            for k in range(count)
        ], code)

    # unicode-math composes absent multiple primes with a -1.5mu kern.
    # Keep that spacing when providing the dedicated Unicode glyphs.
    prime = model['sy.prime']
    prime_pitch = prime['width'] - 1000 * 1.5 / 18
    for count, code in [(2, 0x2033), (3, 0x2034), (4, 0x2057)]:
        out[f'uni{code:04X}'] = glyph(prime['width'] + (count - 1) * prime_pitch,
            [shift(c, k * prime_pitch, 0) for k in range(count) for c in prime['contours']], code)

    # Divides: the vertical bar itself.
    out['sy.divides'] = glyph(model['sy.bar']['width'], model['sy.bar']['contours'], 0x2223)

    # Long double arrows: lengthen the rules of => and <=.
    grow = model['equal']['width'] - JOINREL
    arrows = {}
    for side, src, uni in [('right', 'sy.arrowdblright', 0x27F9), ('left', 'sy.arrowdblleft', 0x27F8)]:
        g = model[src]; w = g['width']; xs = [p[0] for p in points(g)]
        tail = min(xs) if side == 'right' else max(xs)
        at_tail = lambda x: abs(x - tail) < 0.01
        rules = sorted({p[1] for p in points(g) if at_tail(p[0])})
        assert len(rules) == 4, (src, rules)
        neck = (min(x for x in xs if not at_tail(x)) if side == 'right'
                else max(x for x in xs if not at_tail(x)))
        if side == 'right':
            out['sy.arrowdblrightlong'] = glyph(w + grow, [mapped(c, lambda x, y: (x if at_tail(x) else x + grow, y))
                                                           for c in g['contours']], uni)
            cut = neck - ARROW_LAP
            head = glyph(w - cut, [mapped(c, lambda x, y: ((cut if at_tail(x) else x) - cut, y)) for c in g['contours']])
            tail_piece = glyph(tail + ARROW_PIECE, [rect(tail, rules[0], tail + ARROW_PIECE, rules[1]),
                                                    rect(tail, rules[2], tail + ARROW_PIECE, rules[3])])
        else:
            out['sy.arrowdblleftlong'] = glyph(w + grow, [mapped(c, lambda x, y: (x + grow if at_tail(x) else x, y))
                                                          for c in g['contours']], uni)
            cut = neck + ARROW_LAP
            head = glyph(cut, [mapped(c, lambda x, y: (cut if at_tail(x) else x, y)) for c in g['contours']])
            rsb = w - tail
            tail_piece = glyph(ARROW_PIECE + rsb, [rect(0, rules[0], ARROW_PIECE, rules[1]),
                                                   rect(0, rules[2], ARROW_PIECE, rules[3])])
        out[f'part.arrowdbl{side}.head'] = head
        out[f'part.arrowdbl{side}.tail'] = tail_piece
        arrows[side] = rules
    assert arrows['left'] == arrows['right']
    rules = arrows['right']
    out['part.arrowdblhoriz.ex'] = glyph(ARROW_PIECE, [rect(0, rules[0], ARROW_PIECE, rules[1]),
                                                       rect(0, rules[2], ARROW_PIECE, rules[3])])
    horiz_variants = {
        'sy.arrowdblrightlong': [['sy.arrowdblrightlong', round(out['sy.arrowdblrightlong']['width'])]],
        'sy.arrowdblleftlong': [['sy.arrowdblleftlong', round(out['sy.arrowdblleftlong']['width'])]],
    }
    rt, rh, lt, lh = (out[n]['width'] for n in ['part.arrowdblright.tail', 'part.arrowdblright.head',
                                                 'part.arrowdblleft.tail', 'part.arrowdblleft.head'])
    horiz_assembly = {
        'sy.arrowdblrightlong': [[['part.arrowdblright.tail', 0, 0, ARROW_PIECE, round(rt)],
                                  ['part.arrowdblhoriz.ex', 1, ARROW_PIECE, ARROW_PIECE, ARROW_PIECE],
                                  ['part.arrowdblright.head', 0, ARROW_LAP, 0, round(rh)]], 0],
        'sy.arrowdblleftlong': [[['part.arrowdblleft.head', 0, 0, ARROW_LAP, round(lh)],
                                 ['part.arrowdblhoriz.ex', 1, ARROW_PIECE, ARROW_PIECE, ARROW_PIECE],
                                 ['part.arrowdblleft.tail', 0, ARROW_PIECE, 0, round(lt)]], 0],
    }

    # Horizontal braces: { and } turned clockwise, (x, y) -> (y, -x).
    turn = lambda c, dx, dy: mapped(c, lambda x, y: (y + dx, -x + dy))
    for kind, src in [('over', 'sy.braceleft'), ('under', 'sy.braceright')]:
        sizes = ['', 'big', 'Big', 'bigg', 'Bigg']
        names = [g for g, _ in spec['vertGlyphVariants'][src]]
        assert len(names) == len(sizes), names
        variants = []
        for size, name in zip(sizes, names):
            x0, y0, x1, y1 = bounds(model[name])
            dy = OVER_BOTTOM + x1 if kind == 'over' else (spec['constants']['AccentBaseHeight'] - OVER_BOTTOM) + x0
            new = f'sy.brace{kind}' if not size else f'ex.brace{kind}{size}'
            out[new] = glyph(y1 - y0, [turn(c, -y0, dy) for c in model[name]['contours']],
                             0x23DE if kind == 'over' and not size else 0x23DF if not size else None)
            variants.append([new, round(y1 - y0)])
        parts, ic = spec['vertGlyphAssembly'][src]
        # one shared frame for all parts, so their rules line up when assembled
        frame = [bounds(model[p[0]]) for p in parts]
        dy = (OVER_BOTTOM + max(b[2] for b in frame) if kind == 'over'
              else (spec['constants']['AccentBaseHeight'] - OVER_BOTTOM) + min(b[0] for b in frame))
        role = {0: 'lft', len(parts) - 1: 'rt'}
        assembly = []
        for i, (name, flags, start, end, full) in enumerate(parts):
            new = f'part.brace{kind}' + ('ex' if flags else role.get(i, 'mid'))
            out[new] = glyph(full, [turn(c, 0, dy) for c in model[name]['contours']])
            assembly.append([new, flags, start, end, full])
        horiz_variants[f'sy.brace{kind}'] = variants
        horiz_assembly[f'sy.brace{kind}'] = [assembly, ic]

    # Remove what an earlier run made, then add the new set.
    for name in previous:
        model.pop(name, None)
    for table in ['italicsCorrections', 'topAccentAttachments']:
        spec[table] = {k: v for k, v in spec[table].items() if k not in previous}
    spec['extendedShapes'] = sorted(set(spec['extendedShapes']) - previous - {'sy.divides'})
    for table in ['vertGlyphVariants', 'horizGlyphVariants', 'vertGlyphAssembly', 'horizGlyphAssembly']:
        spec[table] = {k: v for k, v in spec.get(table, {}).items() if k not in previous}
    clash = {n for n in out if n in model} | {g['unicode'] for g in out.values() if 'unicode' in g} & \
            {g.get('unicode') for g in model.values()}
    assert not clash, clash
    model.update(out)
    spec['vertGlyphAssembly']['sy.divides'] = spec['vertGlyphAssembly']['sy.bar']
    if 'sy.bar' in spec['extendedShapes']:
        spec['extendedShapes'] = sorted(set(spec['extendedShapes']) | {'sy.divides'})
    spec['horizGlyphVariants'].update(horiz_variants)
    spec['horizGlyphAssembly'] = {**spec.get('horizGlyphAssembly', {}), **horiz_assembly}
    spec['topAccentAttachments'].update({'uni20DB': 0, 'uni20DC': 0})
    for code in [0x2033, 0x2034, 0x2057]:
        name = f'uni{code:04X}'
        spec['topAccentAttachments'][name] = round(out[name]['width'] / 2)

    MASTER.write_text(json.dumps(model, separators=(',', ':')))
    MATH.write_text(json.dumps(spec, indent=2))
    (ROOT / 'source/math-additions.json').write_text(json.dumps(sorted(out), indent=2) + '\n')

    writer = UFOWriter(UFO, formatVersion=3)
    gs = writer.getGlyphSet()
    for name in previous - set(out):
        if name in gs:
            gs.deleteGlyph(name)
    for name, g in out.items():
        obj = SimpleNamespace(width=g['width'], unicodes=[g['unicode']] if 'unicode' in g else [])
        def draw(pointpen, g=g):
            pen = SegmentToPointPen(pointpen)
            for c in g['contours']:
                replay(c['commands'], pen)
        gs.writeGlyph(name, obj, drawPointsFunc=draw)
    gs.writeContents()
    lib = plistlib.loads((UFO / 'lib.plist').read_bytes())
    lib['public.glyphOrder'] = sorted((set(lib['public.glyphOrder']) - previous) | set(out))
    writer.writeLib(lib)
    writer.close()
    print(f'{len(out)} glyphs built from Gaussian Modern outlines; {len(previous - set(out))} earlier glyphs removed.')


if __name__ == '__main__':
    main()
