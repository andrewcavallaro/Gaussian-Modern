"""Shared cubic outline model and font compiler for Gaussian Modern."""
from pathlib import Path
import math, copy
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

VERSION='0.107'
COPYRIGHT=('Copyright (c) 2026 Andrew Cavallaro. '
           'Includes material derived from Computer Modern by Donald E. Knuth.')
LICENSE=('MIT License for original font work and project code. Inherited Computer Modern '
         'material retains Knuth terms, including renaming modified files. '
         'See LICENSE and THIRD-PARTY-NOTICES.md.')

def replay(commands, pen):
    for op,args in commands:
        getattr(pen,op)(*[tuple(p) for p in args])

def contour(commands, ink=1):
    a=AreaPen(); replay(commands,a)
    if (a.value<0)==bool(ink):
        p=RecordingPen(); replay(commands,ReverseContourPen(p)); commands=p.value
    return {'ink':ink,'commands':commands}

def bounds(g):
    p=BoundsPen(None)
    for c in g['contours']: replay(c['commands'],p)
    return p.bounds or (0,0,0,0)

def build_font(glyphs,path,family='Gaussian Modern',style='Regular',features='',weight=400,italic=False):
    glyphs=copy.deepcopy(glyphs)
    box=[('moveTo',[(80,0)]),('lineTo',[(80,700)]),('lineTo',[(520,700)]),('lineTo',[(520,0)]),('closePath',[])]
    glyphs['.notdef']={'width':600,'contours':[contour(box)]}
    for name,code in [('space',32),('uni00A0',160)]:
        glyphs.setdefault(name,{'width':300,'contours':[],'unicode':code})
    order=['.notdef']+sorted(n for n in glyphs if n!='.notdef')
    is_ttf=Path(path).suffix=='.ttf';fb=FontBuilder(1000,isTTF=is_ttf)
    fb.setupGlyphOrder(order)
    cmap={g['unicode']:n for n,g in glyphs.items() if g.get('unicode') is not None}
    fb.setupCharacterMap(cmap)
    metrics={};cs={};tt={}
    for n in order:
        g=glyphs[n];w=round(g['width'])
        if is_ttf:
            p=TTGlyphPen(None);cp=Cu2QuPen(p,max_err=0.65,reverse_direction=True)
            for c in g['contours']:replay(c['commands'],cp)
            tt[n]=p.glyph()
        else:
            p=T2CharStringPen(w,None)
            for c in g['contours']:replay(c['commands'],p)
            cs[n]=p.getCharString()
        metrics[n]=(w,math.floor(bounds(g)[0]))
    if is_ttf:fb.setupGlyf(tt)
    else:
        ps=(family+'-'+style).replace(' ','')
        fb.setupCFF(ps,{'FullName':family+' '+style,'FamilyName':family,'Weight':style},cs,{})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=980,descent=-280,lineGap=40)
    legacy_family=family+(' Semibold' if weight==600 else '')
    legacy_style='Italic' if italic else 'Regular'
    fb.setupNameTable({'familyName':legacy_family,'styleName':legacy_style,
      'uniqueFontIdentifier':family+' '+style+' '+VERSION,
      'fullName':family+' '+style,'psName':(family+'-'+style).replace(' ',''),
      'version':'Version '+VERSION,'typographicFamily':family,'typographicSubfamily':style,
      'licenseDescription':LICENSE,
      'copyright':COPYRIGHT,'designer':'Andrew Cavallaro'})
    fb.setupOS2(version=4,sTypoAscender=800,sTypoDescender=-240,sTypoLineGap=160,
      usWinAscent=1100,usWinDescent=340,usWeightClass=weight,
      sxHeight=515,sCapHeight=710,fsSelection=(1 if italic else 64)|128)
    fb.setupPost(italicAngle=-11 if italic else 0,underlinePosition=-100,underlineThickness=50)
    fb.setupMaxp()
    fb.font['head'].macStyle=(2 if italic else 0)
    fb.font['head'].created=fb.font['head'].modified=3875000000
    fb.font['head'].fontRevision=float(VERSION)
    if features:addOpenTypeFeaturesFromString(fb.font,features)
    if is_ttf:
        from fontTools.ttLib import newTable
        gasp=newTable('gasp');gasp.gaspRange={65535:15};fb.font['gasp']=gasp
    Path(path).parent.mkdir(parents=True,exist_ok=True);fb.save(path)
    return {'glyphs':len(order),'unicode':len(cmap)}
