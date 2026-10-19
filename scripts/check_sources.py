"""Check that every font has complete, synchronized JSON and UFO sources."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'source'))
from build import read_ufo_points

FAMILIES = ['GaussianModern-' + style for style in
            ('Regular', 'Italic', 'Semibold', 'SemiboldItalic')]
FAMILIES.append('GaussianModernMath-Regular')


def geometry(glyph):
    """Compare closed Bezier paths regardless of contour/start-point order."""
    contours = []
    for contour in glyph['contours']:
        segments = []
        first = current = None
        for operation, points in contour['commands']:
            points = [tuple(round(v, 5) for v in point) for point in points]
            if operation == 'moveTo':
                first = current = points[0]
            elif operation in ('lineTo', 'curveTo'):
                if operation != 'lineTo' or current != points[0]:
                    segments.append((operation, current, *points))
                current = points[-1]
            elif operation == 'closePath':
                if current != first:
                    segments.append(('lineTo', current, first))
            else:
                raise AssertionError(f'Unsupported outline command: {operation}')
        contours.append(tuple(sorted(segments)))
    return tuple(sorted(contours))


for family in FAMILIES:
    model = json.loads((ROOT / 'source/masters' / (family + '.json')).read_text())
    ufo, features = read_ufo_points(ROOT / 'source/ufo' / (family + '.ufo'))
    assert set(model) == set(ufo), f'{family}: JSON/UFO glyph sets differ'
    assert features == (ROOT / 'source/features' / (family + '.fea')).read_text(), family
    for name, glyph in model.items():
        other = ufo[name]
        assert abs(glyph['width'] - other['width']) < 1e-7, (family, name, 'width')
        assert glyph.get('unicode') == other.get('unicode'), (family, name, 'Unicode')
        assert geometry(glyph) == geometry(other), (family, name, 'outline')
    print(f'{family}: {len(model)} complete glyphs; JSON/UFO outlines, metrics and features agree')
