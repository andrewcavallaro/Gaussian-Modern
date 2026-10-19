"""Check the built fonts and emit a compact, machine-readable validation record."""
import json,hashlib,unicodedata
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
        allowed_empty={'space','uni00A0'}|{name for code,name in cmap.items()
                        if unicodedata.category(chr(code)) in {'Zs','Cf'}}
        assert set(empty)<=allowed_empty,(path.name,empty)
        assert all(c in cmap for c in range(32,127)),path.name
        math='Math' in path.name
        if math:
            targets=json.loads((ROOT/'source/native-unicode-targets.json').read_text())
            assert all(row['codepoint'] in cmap for row in targets),path.name
            mono=list(range(0x1D670,0x1D6A4))+list(range(0x1D7F6,0x1D800))
            assert len({f['hmtx'][cmap[c]][0] for c in mono})==1,(path.name,'monospace widths')
            assert all(ord(c) in cmap for c in COMMON)
            accents=f['MATH'].table.MathGlyphInfo.MathTopAccentAttachment
            attachments=dict(zip(accents.TopAccentCoverage.glyphs,
                                 (v.Value for v in accents.TopAccentAttachment)))
            for code in [0x20DB,0x20DC]:
                name=cmap[code]
                assert f['hmtx'][name][0]==0,(path.name,name,'accent advance')
                assert attachments[name]==0,(path.name,name,'accent attachment')
            prime_widths=[f['hmtx'][cmap[code]][0] for code in [0x2032,0x2033,0x2034,0x2057]]
            assert all(a<b for a,b in zip(prime_widths,prime_widths[1:])),(path.name,'prime widths')
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
