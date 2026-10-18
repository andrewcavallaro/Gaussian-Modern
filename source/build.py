"""Rebuild installable fonts from the included cubic JSON or editable UFO masters.

    python3 build.py
    python3 build.py --from-ufo

Requires Python 3.10+ and fonttools. Run from any directory.
"""
import argparse,json,sys
from pathlib import Path
from types import SimpleNamespace
from fontTools.ttLib import TTFont
from fontTools.otlLib.builder import buildMathTable
from fontTools.ufoLib import UFOReader
from fontTools.pens.recordingPen import RecordingPen
from font_model import build_font,contour

HERE=Path(__file__).resolve().parent

def read_ufo_points(path):
    from fontTools.pens.pointPen import PointToSegmentPen
    reader=UFOReader(path);glyphset=reader.getGlyphSet();model={}
    for name in glyphset.keys():
        obj=SimpleNamespace(width=0,unicodes=[]);pen=RecordingPen()
        glyphset.readGlyph(name,obj,PointToSegmentPen(pen))
        contours=[];current=[]
        from fontTools.pens.areaPen import AreaPen
        from font_model import replay
        for op,args in pen.value:
            if op=='addComponent':raise ValueError('Decompose UFO components before rebuilding: '+name)
            current.append((op,args))
            if op in ['closePath','endPath']:
                area=AreaPen();replay(current,area)
                contours.append(contour(current,int(area.value>=0)));current=[]
        model[name]={'width':obj.width,'unicode':obj.unicodes[0] if obj.unicodes else None,'contours':contours}
    return model,reader.readFeatures()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--from-ufo',action='store_true');args=ap.parse_args()
    for tag,weight,italic in [('Regular',400,False),('Italic',400,True),('Semibold',600,False),('SemiboldItalic',600,True),('Math-Regular',400,False)]:
        name='GaussianModernMath-Regular' if tag=='Math-Regular' else 'GaussianModern-'+tag
        ismath=tag=='Math-Regular'
        if args.from_ufo:model,fea=read_ufo_points(HERE/'ufo'/(name+'.ufo'))
        else:
            model=json.loads((HERE/'masters'/(name+'.json')).read_text())
            fea=(HERE/'features'/(name+'.fea')).read_text()
        for ext in ['otf','ttf']:
            target=HERE.parent/'fonts'/ext/(name+'.'+ext)
            result=build_font(model,target,family='Gaussian Modern Math' if ismath else 'Gaussian Modern',
                              style='Regular' if ismath else tag.replace('SemiboldItalic','Semibold Italic'),
                              weight=weight,italic=italic,features=fea)
            if ismath:
                spec=json.loads((HERE/'masters/GaussianModernMath-MATH.json').read_text())
                f=TTFont(target);buildMathTable(f,**spec)
                f['OS/2'].usWinAscent=max(1100,f['head'].yMax)
                f['OS/2'].usWinDescent=max(340,-f['head'].yMin)
                f.recalcTimestamp=False
                f.save(target)
            print(target.name,result)

if __name__=='__main__':main()
