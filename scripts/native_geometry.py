"""Cubic drawing tools for original Gaussian Modern extensions.

All coordinates are in the font's 1000-unit design space. No donor fonts are read.
"""
import math
import sys
from pathlib import Path
import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.areaPen import AreaPen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'source'))
from font_model import bounds, contour, replay


def glyph(width, contours=()):
    return {'width': round(width, 4), 'ic': 0.0, 'contours': list(contours)}


def transform(g, xx=1, xy=0, yx=0, yy=1, dx=0, dy=0, width=None):
    cs = []
    for c in g['contours']:
        commands = [(op, [[round(xx*x+yx*y+dx,4), round(xy*x+yy*y+dy,4)] for x,y in pts])
                    for op,pts in c['commands']]
        cs.append(contour(commands, c['ink']))
    return glyph(g['width']*abs(xx) if width is None else width, cs)


def combine(*gs, width=None):
    return glyph(max((g['width'] for g in gs), default=0) if width is None else width,
                 [c for g in gs for c in g['contours']])


def path(g):
    p=pathops.Path()
    pen=p.getPen()
    for c in g['contours']: replay(c['commands'],pen)
    return p


def from_path(p, width):
    p.convertConicsToQuads(0.03)
    rec=RecordingPen(); p.draw(Qu2CuPen(rec,max_err=0.03,all_cubic=True))
    cs=[]; commands=[]
    for op,pts in rec.value:
        commands.append((op,[[round(x,4),round(y,4)] for x,y in pts]))
        if op=='closePath':
            a=AreaPen(); replay(commands,a)
            if abs(a.value)>0.01: cs.append(contour(commands,a.value>=0))
            commands=[]
    assert not commands
    return glyph(width,cs)


def boolean(a,b,kind='union'):
    operators={'union':pathops.PathOp.UNION,'difference':pathops.PathOp.DIFFERENCE,
               'intersection':pathops.PathOp.INTERSECTION}
    return from_path(pathops.op(path(a),path(b),operators[kind]),a['width'])


def clean(g):
    return from_path(pathops.simplify(path(g)),g['width']) if g['contours'] else g


def polygon(points, width=0):
    return glyph(width,[contour([('moveTo',[points[0]]),
           *[('lineTo',[p]) for p in points[1:]],('closePath',[])])])


def rect(x0,y0,x1,y1,width=0):
    return polygon([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],width)


def ellipse(cx,cy,rx,ry=None,width=0):
    ry=rx if ry is None else ry; k=0.5522847498
    return glyph(width,[contour([
        ('moveTo',[(cx+rx,cy)]),
        ('curveTo',[(cx+rx,cy+k*ry),(cx+k*rx,cy+ry),(cx,cy+ry)]),
        ('curveTo',[(cx-k*rx,cy+ry),(cx-rx,cy+k*ry),(cx-rx,cy)]),
        ('curveTo',[(cx-rx,cy-k*ry),(cx-k*rx,cy-ry),(cx,cy-ry)]),
        ('curveTo',[(cx+k*rx,cy-ry),(cx+rx,cy-k*ry),(cx+rx,cy)]),('closePath',[])])])


def stroke(commands, thickness=48, width=0, round_caps=False):
    p=pathops.Path(); pen=p.getPen()
    for op,pts in commands:
        getattr(pen,op)(*[tuple(v) for v in pts])
    p.stroke(thickness,pathops.LineCap.ROUND_CAP if round_caps else pathops.LineCap.BUTT_CAP,
             pathops.LineJoin.ROUND_JOIN,4)
    p.convertConicsToQuads(0.03)
    return from_path(pathops.simplify(p),width)


def line(points, thickness=48, width=0, closed=False):
    return stroke([('moveTo',[points[0]]),*[('lineTo',[p]) for p in points[1:]],
                  ('closePath',[]) if closed else ('endPath',[])],thickness,width)


def embolden(g, amount=15):
    p=path(g); p.stroke(2*amount,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4)
    p.convertConicsToQuads(0.03)
    return from_path(pathops.op(path(g),p,pathops.PathOp.UNION),g['width'])


def fit(g, x0,y0,x1,y1,width=None):
    a,b,c,d=bounds(g)
    sx=(x1-x0)/(c-a);sy=(y1-y0)/(d-b)
    return transform(g,xx=sx,yy=sy,dx=x0-a*sx,dy=y0-b*sy,width=x1+50 if width is None else width)


def centered(g,width=700,cy=281):
    x0,y0,x1,y1=bounds(g)
    return transform(g,dx=width/2-(x0+x1)/2,dy=cy-(y0+y1)/2,width=width)


def reflect(g, horizontal=True):
    x0,y0,x1,y1=bounds(g)
    return transform(g,xx=-1 if horizontal else 1,yy=1 if horizontal else -1,
                     dx=x0+x1 if horizontal else 0,dy=0 if horizontal else y0+y1,width=g['width'])


def rotate(g,angle,width=None,cy=281):
    t=math.radians(angle);c=math.cos(t);s=math.sin(t)
    h=transform(g,xx=c,xy=s,yx=-s,yy=c,width=g['width'])
    box=bounds(h)
    return centered(h,width if width is not None else box[2]-box[0]+100,cy)


def lengthen(g,extra):
    midpoint=g['width']/2
    return glyph(g['width']+extra,[contour([(op,[[round(x+(extra if x>midpoint else 0),4),y]
           for x,y in pts]) for op,pts in c['commands']],c['ink']) for c in g['contours']])
