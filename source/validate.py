"""Check the built fonts and emit a compact, machine-readable validation record."""
import json,hashlib
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

ROOT=Path(__file__).resolve().parent.parent
COMMON='…∣⋮⋯⋱⏞⏟⟸⟹≠≤≥≈≡∈∉∋∌∅∀∃∄∇∂∞↦→←↔⇒⇔⊂⊃⊆⊇∧∨¬∑∏∫∮√∝×÷±∓∴∵∶'

def validate():
    records=[]
    for path in sorted([*(ROOT/'fonts').glob('otf/*'), *(ROOT/'fonts').glob('ttf/*')]):
        f=TTFont(path,checkChecksums=2)
        for table in f.keys():f[table]
        glyphs=f.getGlyphSet();cmap=f.getBestCmap();empty=[]
        for name in f.getGlyphOrder():
            p=RecordingPen();glyphs[name].draw(p)
            if not p.value:empty.append(name)
        assert set(empty)<=set(['space','uni00A0']),(path.name,empty)
        assert all(c in cmap for c in range(32,127)),path.name
        math='Math' in path.name
        if math:
            assert all(ord(c) in cmap for c in COMMON)
            assert 0x1d706 in cmap and 0x1d6ec in cmap
            assert 'MATH' in f
            assert 'math' in [r.ScriptTag for r in f['GSUB'].table.ScriptList.ScriptRecord]
            spec=f['MATH'].table.MathVariants
            for c in spec.VertGlyphConstruction+spec.HorizGlyphConstruction:
                for v in c.MathGlyphVariantRecord:assert v.VariantGlyph in glyphs
                if c.GlyphAssembly:
                    for part in c.GlyphAssembly.PartRecords:
                        assert part.glyph in glyphs
                        assert 0<=part.StartConnectorLength<=part.FullAdvance
                        assert 0<=part.EndConnectorLength<=part.FullAdvance
        else:
            assert all(u in cmap for u in [0x300,0x301,0x302,0x303,0x304,0x306,0x307,0x308,0x30a,0x30b,0x30c,0x327,0x328])
            assert len({f['hmtx'][cmap[c]][0] for c in range(48,58)})==1
            features={r.FeatureTag for r in f['GSUB'].table.FeatureList.FeatureRecord}
            assert {'ccmp','liga'}<=features
            assert {'kern','mark'}<={r.FeatureTag for r in f['GPOS'].table.FeatureList.FeatureRecord}
        records.append({'file':str(path.relative_to(ROOT)), 'glyphs':len(glyphs),'unicode_mappings':len(cmap),
                        'math':math,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        print(path.name,len(glyphs),'glyphs;',len(cmap),'Unicode mappings; passed',flush=True)
    target=ROOT/'source/validation.json';target.write_text(json.dumps(records,indent=2)+'\n')
    return records

if __name__=='__main__':validate()
