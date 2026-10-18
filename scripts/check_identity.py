"""Verify family, version, and scoped license metadata in each built font."""
from pathlib import Path
from fontTools.ttLib import TTFont
ROOT = Path(__file__).resolve().parent.parent
fonts = sorted((ROOT / 'fonts').glob('*/*'))
assert len(fonts) == 10
for path in fonts:
    f = TTFont(path)
    names = f['name']
    family = 'Gaussian Modern Math' if 'Math' in path.name else 'Gaussian Modern'
    assert names.getDebugName(16) == family, path
    assert names.getDebugName(6).startswith(family.replace(' ', '') + '-'), path
    assert names.getDebugName(5) == 'Version 0.107', path
    assert 'MIT License' in names.getDebugName(13) and 'Knuth' in names.getDebugName(13), path
    assert 'Knuth' in names.getDebugName(0) and 'Andrew Cavallaro' in names.getDebugName(0), path
    assert names.getDebugName(9) == 'Andrew Cavallaro', path
    if 'CFF ' in f:
        assert f['CFF '].cff.topDictIndex[0].FamilyName == family
    print(path.name, 'identity and license scope passed')
