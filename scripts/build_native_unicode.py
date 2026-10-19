"""Build native Unicode coverage without reading any outside font outlines.

Requires the pinned skia-pathops dependency. Targets are the frozen coverage
checklist in source/native-unicode-targets.json. Recipes use existing Gaussian
Modern outlines and original design-space drawings. Run before source/build.py.
"""
import copy
import json
import math
import plistlib
import unicodedata as ud
from pathlib import Path
from types import SimpleNamespace
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.ufoLib import UFOWriter
from native_geometry import *
from native_alphabets import sans, fraktur, double_struck, draw_skeleton

ROOT=Path(__file__).resolve().parent.parent
MASTER=ROOT/'source/masters/GaussianModernMath-Regular.json'
SPEC=ROOT/'source/masters/GaussianModernMath-MATH.json'
UFO=ROOT/'source/ufo/GaussianModernMath-Regular.ufo'
RECORD=ROOT/'source/native-unicode.json'
AXIS=281


class Builder:
    def __init__(self,model,spec,targets):
        self.model=model;self.spec=spec;self.targets=targets
        self.bycode={g['unicode']:n for n,g in model.items() if g.get('unicode') is not None}
        self.new={};self.notes={};self.busy=set();self.variants={};self.assemblies={}
        self.rules={};self.make_rules()

    def src(self,name):return copy.deepcopy(self.model[name])
    def g(self,code):
        if isinstance(code,str):return self.src(code)
        if code in self.bycode:return self.src(self.bycode[code])
        name=f'native.u{code:04X}'
        if name in self.new:return copy.deepcopy(self.new[name])
        if code in self.busy:raise ValueError(f'Circular recipe U+{code:04X}')
        self.busy.add(code)
        if code in self.rules:g,note=self.rules[code](), 'native symbol recipe'
        elif 0x1D400<=code<=0x1D7FF or code in self.letterlike():
            g=self.alphabet(code);note='original alphabet drawing or native letter construction'
        elif ud.decomposition(chr(code)) and not ud.decomposition(chr(code)).startswith('<'):
            g=self.composite(code);note='native letter and accent composition'
        else:raise KeyError(f'No recipe U+{code:04X} {ud.name(chr(code),"?")}')
        g=clean(g);g['unicode']=code
        self.new[name]=g;self.notes[name]=note;self.busy.remove(code)
        self.spec['topAccentAttachments'][name]=0 if ud.combining(chr(code)) else round(g['width']/2)
        if 0x1D400<=code<=0x1D7FF and ('ITALIC' in ud.name(chr(code))):
            self.spec['italicsCorrections'][name]=max(0,round(bounds(g)[2]-g['width']+20))
        return copy.deepcopy(g)

    @staticmethod
    def letterlike():return {0x2107,0x210C,0x2128,0x212D,0x213C,0x213D,0x213E,0x213F,0x2140,0x2145,0x2146,0x2147,0x2148,0x2149}

    def alphabet(self,code):
        name=ud.name(chr(code));base=ud.normalize('NFKD',chr(code))
        special={0x2107:'Ε',0x210C:'H',0x2128:'Z',0x212D:'C',0x213C:'π',0x213D:'γ',0x213E:'Γ',0x213F:'Π',
                 0x2145:'D',0x2146:'d',0x2147:'e',0x2148:'i',0x2149:'j'}
        base=special.get(code,base)
        if code==0x2140:return double_struck('Σ')
        if code==0x2107:return fit(self.g(0x3F5),70,0,620,710,width=690)
        if len(base)!=1:raise ValueError((code,name,base))
        if 'SANS-SERIF' in name:return self.align_letter(sans(base,'BOLD' in name,'ITALIC' in name),base)
        if 'MONOSPACE' in name:return self.align_letter(sans(base,mono=True),base)
        if 'FRAKTUR' in name or code in [0x210C,0x2128,0x212D]:
            if base in 'IR' and 'BOLD' in name:return embolden(self.src('sy.'+base+'fractur'),18)
            return fraktur(base,'BOLD' in name)
        if 'DOUBLE-STRUCK' in name:return double_struck(base,'ITALIC' in name)
        if 'SCRIPT' in name:
            return embolden(self.src('sy.cal'+base),18)
        b=self.g(ord(base))
        if 'BOLD ITALIC' in name:return transform(embolden(b,15),yx=.19,width=b['width'])
        if 'BOLD' in name:return embolden(b,15)
        if 'ITALIC' in name:return transform(b,yx=.19,width=b['width'])
        return b

    def align_letter(self,g,base):
        # Match the existing family's baseline, ascender and overshoot levels.
        if ord(base) in self.bycode:
            a,y0,c,y1=bounds(self.g(ord(base)));ga,gy0,gc,gy1=bounds(g)
            sy=(y1-y0)/(gy1-gy0)
            return transform(g,yy=sy,dy=y0-gy0*sy,width=g['width'])
        return g

    def composite(self,code):
        chars=[ord(c) for c in ud.normalize('NFD',chr(code))]
        if len(chars)==1:
            other=int(ud.decomposition(chr(code)).split()[0],16)
            return self.g(other)
        base=self.g(chars[0]);w=base['width'];top=bounds(base)[3];bottom=bounds(base)[1]
        if 0x031B in chars:
            horn_base={ord('O'):0x01A0,ord('o'):0x01A1,ord('U'):0x01AF,ord('u'):0x01B0}[chars[0]]
            base=self.g(horn_base);w=base['width'];top=bounds(base)[3]
            chars.remove(0x031B)
        # Dotless i before a top accent; this preserves a single accent layer.
        if chars[0]==ord('i') and any(ud.combining(chr(c))==230 for c in chars[1:]):
            base=self.g(0x131);top=bounds(base)[3]
        for c in chars[1:]:
            mark=self.g(c);a,b,d,e=bounds(mark)
            if ud.combining(chr(c)) in [202,220]:
                dy=min(-65,bottom-45)-e;bottom=b+dy
            else:
                dy=max(600,top+65)-b;top=e+dy
            base=combine(base,transform(mark,dx=w/2-(a+d)/2,dy=dy),width=w)
        return base

    def above(self,g,width=None,below=False):
        w=g['width'] if width is None else width;x0,y0,x1,y1=bounds(g)
        return transform(g,dx=-(x0+x1)/2,dy=(-110-y1 if below else 600-y0),width=0)

    def mark(self,g,code,below=False):return self.above(g,below=below)
    def small(self,g,scale=.7):return centered(transform(g,xx=scale,yy=scale),g['width']*scale,AXIS)
    def ring(self,cx=350,cy=281,r=240,t=48):
        return boolean(ellipse(cx,cy,r,width=2*cx),ellipse(cx,cy,r-t),'difference')
    def neg(self,code):
        g=self.g(code);w=g['width']
        slash=line([(w/2-140,-70),(w/2+140,650)],42)
        return combine(g,slash,width=w)
    def dot(self,cx,cy):return ellipse(cx,cy,42)
    def relstack(self,top,bottom,gap=95):
        w=max(top['width'],bottom['width']);a=bounds(top);b=bounds(bottom)
        lo=transform(bottom,dx=w/2-(b[0]+b[2])/2,dy=0)
        hi=transform(top,dx=w/2-(a[0]+a[2])/2,dy=b[3]+gap-a[1])
        return centered(combine(lo,hi,width=w),w)
    def juxtapose(self,a,b,gap=55):
        return combine(a,transform(b,dx=a['width']+gap),width=a['width']+gap+b['width'])
    def over_equal(self,g):return self.relstack(self.small(g,.55),self.g(0x3D),65)

    def multi_integral(self,count):
        base=self.src('op.integral');pitch=base['width']*.65
        result=combine(*[transform(base,dx=k*pitch) for k in range(count)],width=base['width']+(count-1)*pitch)
        return result

    def white_arrow(self,direction=0,double=False,solid=False):
        pts=[(50,185),(450,185),(450,50),(740,281),(450,512),(450,377),(50,377)]
        if double:pts=[(50,281),(300,50),(300,185),(500,185),(500,50),(750,281),(500,512),(500,377),(300,377),(300,512)]
        shape=polygon(pts,width=800)
        if not solid:shape=self.outline(shape,40)
        return rotate(shape,direction,800 if direction in [0,180] else 650)

    def outline(self,g,t=35):
        p=path(g);p.stroke(2*t,pathops.LineCap.ROUND_CAP,pathops.LineJoin.ROUND_JOIN,4)
        p.convertConicsToQuads(0.03)
        border=from_path(p,g['width'])
        return boolean(g,border,'intersection')

    def circle_arrow(self):
        commands=[];cx,cy,r=350,281,260
        for a,b in [(60,150),(150,240),(240,330),(330,390)]:
            a,b=math.radians(a),math.radians(b);k=4/3*math.tan((b-a)/4)
            p=(cx+r*math.cos(a),cy+r*math.sin(a));q=(cx+r*math.cos(b),cy+r*math.sin(b))
            if not commands:commands.append(('moveTo',[p]))
            commands.append(('curveTo',[(p[0]-k*r*math.sin(a),p[1]+k*r*math.cos(a)),
                                       (q[0]+k*r*math.sin(b),q[1]-k*r*math.cos(b)),q]))
        commands.append(('endPath',[]))
        tip=q;theta=math.radians(120);tx,ty=math.cos(theta),math.sin(theta)
        head=[(tip[0]-120*tx-75*ty,tip[1]-120*ty+75*tx),tip,
              (tip[0]-120*tx+75*ty,tip[1]-120*ty-75*tx)]
        return combine(stroke(commands,48,width=700),line(head,48),width=700)

    def make_rules(self):
        R=self.rules
        aliases={
            0x2010:'hyphen',0x203D:'interrobang',0x2215:'slash',0x2216:'bm.smallsetminus',0x2218:'sy.openbullet',0x2219:'am.centerdot',
            0x2225:'sy.bardbl',0x220E:'am.blacksquare',0x27C2:'sy.perpendicular',0x2305:'am.barwedge',0x2306:'am.doublebarwedge',
            0x25B7:'mi.triangleright',0x25C1:'mi.triangleleft',0x25BD:'sy.triangleinv',0x2A3F:'sy.coproduct',
            0x27EE:'parenleft',0x27EF:'parenright',0x2329:'sy.angbracketleft',0x232A:'sy.angbracketright',
            0x23D0:'part.vextendsingle',0x23B7:'part.radicalbt',0x2422:'visiblespace',
            0x0305:'uni0304',0x0338:'sy.negationslash',0x03F4:'gr.Theta',0x212A:'K',0x212B:'Aring',
        }
        for c,n in aliases.items():R[c]=lambda n=n:self.src(n)
        # Existing unencoded native components with standard standalone codes.
        parts=['parenlefttp','parenleftex','parenleftbt','parenrighttp','parenrightex','parenrightbt',
               'bracketlefttp','bracketleftex','bracketleftbt','bracketrighttp','bracketrightex','bracketrightbt',
               'bracelefttp','braceleftmid','braceleftbt','braceex','bracerighttp','bracerightmid','bracerightbt']
        for c,n in enumerate(parts,0x239B):R[c]=lambda n=n:self.src('part.'+n)
        # Canonical spaces and invisible operators legitimately have no ink.
        spaces={0x2000:500,0x2001:1000,0x2002:500,0x2003:1000,0x2004:1000/3,0x2005:250,0x2006:1000/6,
                0x2007:self.g(48)['width'],0x2008:self.g(46)['width'],0x2009:200,0x200A:100,0x202F:200,0x205F:1000*4/18}
        spaces.update({c:0 for c in [0x200B,0x200C,0x200D,0x2060,0x2061,0x2062,0x2063,0x2064,0xFEFF]})
        for c,w in spaces.items():R[c]=lambda w=w:glyph(w)
        # Additional accents, all anchored at zero with zero advance.
        for c,src in {0x0330:0x0303,0x0332:0x0304,0x0323:0x0307,0x032C:0x030C,0x032D:0x0302,0x032E:0x0306,0x0331:0x0304}.items():
            R[c]=lambda src=src:self.above(self.g(src),below=True)
        R[0x0311]=lambda:self.above(reflect(self.g(0x0306),False))
        R[0x032F]=lambda:self.above(reflect(self.g(0x0306),False),below=True)
        R[0x030F]=lambda:combine(transform(self.g(0x0300),dx=-90),transform(self.g(0x0300),dx=90),width=0)
        R[0x0333]=lambda:combine(self.g(0x0332),transform(self.g(0x0332),dy=-110),width=0)
        R[0x033F]=lambda:combine(self.g(0x0305),transform(self.g(0x0305),dy=110),width=0)
        R[0x0309]=lambda:self.above(stroke([('moveTo',[(0,0)]),('curveTo',[(100,55),(100,175),(-20,165)]),('endPath',[])],42))
        R[0x0326]=lambda:self.above(fit(self.g(44),-35,-180,35,-65,width=0),below=True)
        R[0x031B]=lambda:self.above(stroke([('moveTo',[(0,0)]),('curveTo',[(95,0),(115,65),(90,120)]),('endPath',[])],42))
        R[0x20E8]=lambda:self.above(self.g(0x20DB),below=True)
        for c,src,below in [(0x20D0,'am.upharpoonright',False),(0x20D1,'am.upharpoonleft',False),
                            (0x20D6,'sy.arrowleft',False),(0x20E1,'sy.arrowboth',False),
                            (0x034D,'sy.arrowboth',True),(0x20EE,'sy.arrowleft',True),(0x20EF,'sy.arrowright',True)]:
            R[c]=lambda src=src,below=below:self.above(fit(rotate(self.src(src),90 if src.endswith('right') else -90) if 'harpoon' in src else self.src(src),0,0,650,160,width=650),below=below)
        R[0x20EC]=lambda:self.above(reflect(self.g(0x20D1),False),below=True)
        R[0x20ED]=lambda:self.above(reflect(self.g(0x20D0),False),below=True)
        R[0x20D2]=lambda:rect(-24,-220,24,745)
        R[0x20D3]=lambda:rect(-24,0,24,515)
        R[0x20E6]=lambda:combine(transform(self.g(0x20D2),dx=-65),transform(self.g(0x20D2),dx=65),width=0)
        R[0x20E5]=lambda:reflect(self.g(0x0338))
        R[0x20EB]=lambda:combine(transform(self.g(0x0338),dx=-65),transform(self.g(0x0338),dx=65),width=0)
        R[0x20EA]=lambda:transform(centered(self.g(0x2190),650),dx=-325,width=0)
        R[0x20DD]=lambda:transform(self.ring(400,281,460,38),dx=-400,width=0)
        R[0x20D8]=lambda:transform(self.ring(270,281,250,38),dx=-270,width=0)
        R[0x20DE]=lambda:line([(-420,-180),(420,-180),(420,740),(-420,740)],38,closed=True)
        R[0x20DF]=lambda:line([(-500,281),(0,800),(500,281),(0,-240)],38,closed=True)
        R[0x20E4]=lambda:line([(-500,-160),(0,780),(500,-160)],38,closed=True)
        R[0x20E9]=lambda:self.above(line([(-350,0),(-350,110),(350,110),(350,0)],40))
        R[0x20F0]=lambda:self.above(self.small(self.src('sy.asteriskmath'),.65))
        # Dashes, operators and simple relations.
        R[0x2012]=lambda:rect(0,257,self.g(48)['width'],305,width=self.g(48)['width'])
        R[0x2015]=lambda:rect(0,257,1000,305,width=1000)
        R[0x2017]=lambda:combine(rect(0,-110,650,-65),rect(0,-220,650,-175),width=650)
        R[0x2206]=lambda:self.g(0x394)
        for c,src in [(0x220A,0x2208),(0x220D,0x220B)]:R[c]=lambda src=src:self.small(self.g(src),.75)
        R[0x221F]=lambda:line([(100,550),(100,30),(650,30)],48,width=750)
        for c,src in {0x2244:0x2243,0x2249:0x2248,0x2262:0x2261,0x226D:0x224D,0x2274:0x2272,0x2275:0x2273,
                      0x2278:0x2276,0x2279:0x2277,0x2284:0x2282,0x2285:0x2283,0x22E2:0x2291,0x22E3:0x2292}.items():
            R[c]=lambda src=src:self.neg(src)
        R[0x2245]=lambda:self.relstack(self.g(0x223C),self.g(0x3D),85)
        R[0x2246]=lambda:combine(self.g(0x2245),line([(300,-80),(460,235)],40),width=self.g(0x2245)['width'])
        R[0x224B]=lambda:self.relstack(self.g(0x223C),self.g(0x2248),95)
        R[0x224C]=lambda:reflect(self.g(0x2245))
        R[0x2263]=lambda:self.relstack(self.g(0x3D),self.g(0x3D),115)
        R[0x2250]=lambda:self.over_equal(self.dot(100,100))
        R[0x2254]=lambda:self.juxtapose(self.g(0x2236),self.g(0x3D),20)
        R[0x2255]=lambda:self.juxtapose(self.g(0x3D),self.g(0x2236),20)
        for c,src in {0x2258:'am.smallfrown',0x2259:'sy.logicaland',0x225A:'sy.logicalor',0x225B:'am.bigstar',
                      0x225D:'math.def',0x225E:'m',0x225F:'question'}.items():
            if src=='math.def':R[c]=lambda:self.over_equal(self.juxtapose(self.juxtapose(self.g(ord('d')),self.g(ord('e')),0),self.g(ord('f')),0))
            else:R[c]=lambda src=src:self.over_equal(self.src(src))
        R[0x2237]=lambda:self.juxtapose(self.g(0x2236),self.g(0x2236),20)
        R[0x2238]=lambda:self.relstack(self.dot(100,100),self.g(0x2212),95)
        R[0x2239]=lambda:self.juxtapose(self.g(0x2212),self.g(0x2236),20)
        R[0x223A]=lambda:self.juxtapose(self.juxtapose(self.g(0x2236),self.g(0x2212),20),self.g(0x2236),20)
        R[0x223B]=lambda:combine(self.g(0x223C),self.dot(self.g(0x223C)['width']/2,530),self.dot(self.g(0x223C)['width']/2,32),width=self.g(0x223C)['width'])
        R[0x223E]=lambda:centered(stroke([('moveTo',[(80,120)]),('curveTo',[(30,580),(350,530),(400,281)]),('curveTo',[(450,30),(710,-20),(660,440)]),('endPath',[])],48,width=740))
        R[0x223F]=lambda:centered(stroke([('moveTo',[(50,281)]),('curveTo',[(200,810),(500,-250),(650,281)]),('endPath',[])],48,width=700))
        R[0x228C]=lambda:combine(self.g(0x222A),fit(self.g(0x2190),250,350,550,480),width=self.g(0x222A)['width'])
        R[0x228D]=lambda:combine(self.g(0x222A),self.dot(self.g(0x222A)['width']/2,281),width=self.g(0x222A)['width'])
        R[0x229C]=lambda:combine(self.ring(),fit(self.g(0x3D),210,210,490,352),width=700)
        R[0x22A6]=lambda:line([(130,650),(130,-90),(130,281),(650,281)],48,width=750)
        R[0x22A7]=lambda:combine(line([(130,-90),(130,650)],48),rect(130,190,650,238),rect(130,324,650,372),width=750)
        R[0x22AB]=lambda:combine(self.g(0x22A7),line([(25,-90),(25,650)],48),width=750)
        R[0x22B6]=lambda:combine(self.ring(140,281,95,42),line([(235,281),(560,281)],48),ellipse(560,281,95),width=750)
        R[0x22B7]=lambda:reflect(self.g(0x22B6))
        R[0x22B9]=lambda:combine(line([(350,20),(350,221)],48),line([(350,341),(350,542)],48),line([(90,281),(290,281)],48),line([(410,281),(610,281)],48),width=700)
        R[0x22BD]=lambda:self.relstack(self.g(0x2212),self.g(0x2228),90)
        R[0x22BE]=lambda:combine(self.g(0x221F),stroke([('moveTo',[(100,300)]),('curveTo',[(260,300),(370,190),(370,30)]),('endPath',[])],40),width=750)
        R[0x22BF]=lambda:line([(100,530),(100,30),(650,30)],48,width=750,closed=True)
        R[0x22C8]=lambda:line([(70,70),(650,492),(650,70),(70,492)],48,width=720,closed=True)
        R[0x22D5]=lambda:combine(self.g(0x3D),line([(265,-80),(265,640)],44),line([(465,-80),(465,640)],44),width=self.g(0x3D)['width'])
        R[0x22DC]=lambda:self.relstack(self.g(0x3D),self.g(0x3C),80)
        R[0x22DD]=lambda:reflect(self.g(0x22DC))
        R[0x22E4]=lambda:combine(self.g(0x2291),line([(300,-100),(440,120)],40),width=self.g(0x2291)['width'])
        R[0x22E5]=lambda:reflect(self.g(0x22E4))
        R[0x22F0]=lambda:reflect(self.g(0x22F1),False)
        R[0x2300]=lambda:combine(self.ring(),line([(100,-20),(600,582)],42),width=700)
        R[0x2310]=lambda:reflect(self.g(0xAC))
        R[0x2319]=lambda:reflect(self.g(0x2310),False)
        for c,points in {0x231C:[(80,0),(80,710),(550,710)],0x231D:[(80,710),(550,710),(550,0)],
                         0x231E:[(80,710),(80,0),(550,0)],0x231F:[(80,0),(550,0),(550,710)]}.items():
            R[c]=lambda points=points:line(points,48,width=630)
        # Reversed primes use the same native prime spacing.
        for count,c in [(2,0x2036),(3,0x2037)]:
            R[c]=lambda count=count:combine(*[transform(self.src('am.backprime'),dx=k*(self.src('am.backprime')['width']-1000/12)) for k in range(count)],width=self.src('am.backprime')['width']+(count-1)*(self.src('am.backprime')['width']-1000/12))
        for c,count in [(0x222C,2),(0x222D,3),(0x2A0C,4)]:R[c]=lambda count=count:self.multi_integral(count)
        R[0x2A11]=lambda:combine(self.g(0x222B),fit(self.g(0x21BA),0,150,500,450),width=self.g(0x222B)['width'])
        R[0x2320]=lambda:boolean(self.src('ex.integraltext'),rect(-10000,0,10000,10000),'intersection')
        R[0x2321]=lambda:boolean(self.src('ex.integraltext'),rect(-10000,-10000,10000,0),'intersection')
        R[0x23B2]=lambda:boolean(self.src('op.summation'),rect(-10000,281,10000,10000),'intersection')
        R[0x23B3]=lambda:boolean(self.src('op.summation'),rect(-10000,-10000,10000,281),'intersection')
        # Directional combinations and native arrow heads.
        R[0x219F]=lambda:rotate(self.src('am.twoheadrightarrow'),90,600)
        R[0x21A1]=lambda:reflect(self.g(0x219F),False)
        R[0x21A4]=lambda:reflect(self.g(0x21A6))
        R[0x21A5]=lambda:rotate(self.g(0x21A6),90,600)
        R[0x21A7]=lambda:rotate(self.g(0x21A6),-90,600)
        R[0x21B2]=lambda:reflect(self.src('am.Lsh'),False)
        R[0x21B3]=lambda:reflect(self.src('am.Rsh'),False)
        R[0x21B4]=lambda:combine(line([(50,600),(600,600),(600,100)],48),line([(470,240),(600,100),(730,240)],48),width=800)
        R[0x21B5]=lambda:combine(line([(650,600),(650,150),(100,150)],48),line([(240,280),(100,150),(240,20)],48),width=800)
        R[0x21BA]=self.circle_arrow
        R[0x21BB]=lambda:reflect(self.g(0x21BA))
        R[0x20D4]=lambda:self.above(fit(self.g(0x21BA),0,0,550,200))
        R[0x20D5]=lambda:self.above(fit(self.g(0x21BB),0,0,550,200))
        R[0x21C5]=lambda:self.juxtapose(self.g(0x2191),self.g(0x2193),40)
        R[0x21F5]=lambda:reflect(self.g(0x21C5))
        for c,angle in [(0x21D6,135),(0x21D7,45),(0x21D8,-45),(0x21D9,-135)]:R[c]=lambda angle=angle:rotate(self.g(0x21D2),angle,800)
        R[0x21DC]=lambda:reflect(self.src('am.rightsquigarrow'))
        for c,angle in [(0x21E6,180),(0x21E7,90),(0x21E8,0),(0x21E9,-90)]:R[c]=lambda angle=angle:self.white_arrow(angle)
        R[0x21F3]=lambda:self.white_arrow(90,True)
        R[0x2B04]=lambda:self.white_arrow(0,True)
        for c,angle in [(0x27A1,0),(0x2B05,180),(0x2B06,90),(0x2B07,-90)]:R[c]=lambda angle=angle:self.white_arrow(angle,solid=True)
        R[0x2B0C]=lambda:self.white_arrow(0,True,True)
        R[0x2B0D]=lambda:self.white_arrow(90,True,True)
        R[0x21F6]=lambda:combine(*[transform(self.g(0x2192),dy=k*190) for k in [-1,0,1]],width=self.g(0x2192)['width'])
        R[0x2B31]=lambda:reflect(self.g(0x21F6))
        for c,src in [(0x27F5,0x2190),(0x27F6,0x2192),(0x27F7,0x2194),(0x27FA,0x21D4),
                      (0x27FB,0x21A4),(0x27FC,0x21A6),(0x27FF,0x21DD),(0x2B33,0x21DC)]:
            R[c]=lambda src=src:lengthen(self.g(src),500)
        R[0x2907]=lambda:combine(self.g(0x21D2),rect(20,100,68,462),width=self.g(0x21D2)['width'])
        R[0x2906]=lambda:reflect(self.g(0x2907))
        R[0x27FD]=lambda:lengthen(self.g(0x2906),500)
        R[0x27FE]=lambda:lengthen(self.g(0x2907),500)
        R[0x27F4]=lambda:combine(self.g(0x2192),self.ring(155,281,105,35),line([(95,281),(215,281)],32),line([(155,221),(155,341)],32),width=self.g(0x2192)['width'])
        # Brackets and horizontal delimiters.
        for c,src in [(0x27E6,0x5B),(0x27E7,0x5D),(0x27EA,0x27E8),(0x27EB,0x27E9)]:
            R[c]=lambda src=src,c=c:combine(self.g(src),transform(self.g(src),dx=230 if c in [0x27E6,0x27E7] else 180),width=self.g(src)['width']+(230 if c in [0x27E6,0x27E7] else 180))
        R[0x23B4]=lambda:self.above(line([(0,0),(0,180),(800,180),(800,0)],48,width=800))
        R[0x23B5]=lambda:self.above(reflect(self.g(0x23B4),False),below=True)
        R[0x23DC]=lambda:self.above(stroke([('moveTo',[(0,0)]),('curveTo',[(200,240),(600,240),(800,0)]),('endPath',[])],48,width=800))
        R[0x23DD]=lambda:self.above(reflect(self.g(0x23DC),False),below=True)
        R[0x23E0]=lambda:self.above(line([(0,0),(180,160),(620,160),(800,0)],48,width=800))
        R[0x23E1]=lambda:self.above(reflect(self.g(0x23E0),False),below=True)
        R[0x3016]=lambda:combine(line([(350,740),(80,500),(80,0),(350,-240)],48,width=440),line([(380,740),(180,470),(180,30),(380,-240)],40),width=440)
        R[0x3017]=lambda:reflect(self.g(0x3016))
        # Geometrical operators and ornaments.
        R[0x25AA]=lambda:rect(100,181,300,381,width=400)
        R[0x25AB]=lambda:line([(100,181),(300,181),(300,381),(100,381)],32,width=400,closed=True)
        R[0x25AC]=lambda:rect(70,130,730,430,width=800)
        R[0x25AD]=lambda:line([(70,130),(730,130),(730,430),(70,430)],42,width=800,closed=True)
        R[0x25B2]=lambda:polygon([(60,0),(360,600),(660,0)],width=720)
        R[0x25BC]=lambda:reflect(self.g(0x25B2),False)
        R[0x25CB]=lambda:self.ring()
        R[0x25CF]=lambda:ellipse(350,281,240,width=700)
        R[0x25EF]=lambda:self.ring(450,281,350,48)
        for c,src in [(0x2661,0x2665),(0x2662,0x2666),(0x2664,0x2660),(0x2667,0x2663)]:R[c]=lambda src=src:self.outline(self.g(src),32)
        R[0x266A]=lambda:combine(ellipse(140,60,100,70),line([(230,60),(230,710)],45),stroke([('moveTo',[(230,710)]),('curveTo',[(450,660),(550,480),(390,350)]),('endPath',[])],65),width=600)
        R[0x2713]=lambda:polygon([(50,250),(130,310),(280,85),(625,710),(680,680),(300,-30),(230,-30)],width=730)
        R[0x2720]=lambda:polygon([(60,560),(220,440),(280,500),(160,660),(540,660),(420,500),(480,440),(640,560),(640,180),(480,300),(420,240),(540,80),(160,80),(280,240),(220,300),(60,180)],width=700)
        R[0x27D8]=lambda:fit(self.g(0x22A5),60,-60,740,650,width=800)
        R[0x27D9]=lambda:reflect(self.g(0x27D8),False)
        R[0x27DA]=lambda:combine(line([(290,-70),(290,632)],48),line([(410,-70),(410,632)],48),line([(50,205),(650,205)],48),line([(50,357),(650,357)],48),width=700)
        R[0x27DB]=lambda:combine(line([(290,-70),(290,632)],48),line([(410,-70),(410,632)],48),line([(50,281),(650,281)],48),width=700)
        R[0x27DC]=lambda:reflect(self.g(0x22B8))
        R[0x27DD]=lambda:lengthen(self.g(0x22A2),500)
        R[0x27DE]=lambda:reflect(self.g(0x27DD))
        R[0x27E0]=lambda:combine(self.g(0x25CA),fit(self.g(0x2212),160,257,550,305),width=self.g(0x25CA)['width'])
        R[0x27E1]=lambda:stroke([('moveTo',[(350,650)]),('curveTo',[(340,460),(210,300),(60,281)]),('curveTo',[(210,260),(340,100),(350,-90)]),('curveTo',[(360,100),(490,260),(640,281)]),('curveTo',[(490,300),(360,460),(350,650)]),('closePath',[])],40,width=700)
        R[0x27E2]=lambda:combine(self.g(0x27E1),line([(25,160),(25,400)],40),width=700)
        R[0x27E3]=lambda:reflect(self.g(0x27E2))
        R[0x2A03]=lambda:combine(self.g(0x22C3),self.dot(self.g(0x22C3)['width']/2,281),width=self.g(0x22C3)['width'])
        R[0x2A05]=lambda:reflect(self.g(0x2A06),False)
        R[0x2A09]=lambda:fit(self.g(0xD7),50,-160,850,720,width=900)
        R[0x2A2F]=lambda:self.g(0xD7)
        R[0x2A95]=lambda:self.relstack(rotate(self.g(0x3D),15),self.g(0x3C),85)
        R[0x2A96]=lambda:reflect(self.g(0x2A95))
        R[0x2B1A]=lambda:combine(*[self.dot(x,y) for x,y in [(100,0),(300,0),(500,0),(100,200),(500,200),(100,400),(300,400),(500,400)]],width=600)
        self.more_rules()

    def more_rules(self):
        R=self.rules
        # Native additional Latin letters and Vietnamese base letters.
        R[0x0110]=lambda:combine(self.g(ord('D')),rect(20,335,400,380),width=self.g(ord('D'))['width'])
        R[0x014A]=lambda:combine(self.g(ord('N')),transform(fit(self.g(ord('j')),0,-230,130,70),dx=self.g(ord('N'))['width']-180),width=self.g(ord('N'))['width'])
        R[0x014B]=lambda:combine(self.g(ord('n')),transform(fit(self.g(ord('j')),0,-230,110,70),dx=self.g(ord('n'))['width']-160),width=self.g(ord('n'))['width'])
        R[0x017F]=lambda:boolean(self.g(ord('f')),rect(206,460,450,535),'difference')
        R[0x0123]=lambda:combine(self.g(ord('g')),transform(self.above(reflect(self.g(0x0326),False)),dx=self.g(ord('g'))['width']/2),width=self.g(ord('g'))['width'])
        for c,base in [(0x01A0,'O'),(0x01A1,'o'),(0x01AF,'U'),(0x01B0,'u')]:
            R[c]=lambda base=base:combine(self.g(ord(base)),transform(self.g(0x031B),dx=bounds(self.g(ord(base)))[2]-25,dy=bounds(self.g(ord(base)))[3]-600),width=self.g(ord(base))['width']+45)
        R[0x03F0]=lambda:sans('ϰ')
        R[0x03F5]=lambda:transform(self.src('mi.epsilon'),yx=-.19,width=self.src('mi.epsilon')['width'])
        # Punctuation and letter-based symbols.
        R[0x2031]=lambda:self.juxtapose(self.g(0x2030),self.src('perthousandzero'),0)
        R[0x203B]=lambda:combine(self.g(0xD7),*[self.dot(x,y) for x,y in [(80,281),(650,281),(365,620),(365,-60)]],width=730)
        R[0x2052]=lambda:combine(line([(120,-10),(540,700)],48),self.dot(140,550),self.dot(520,140),width=660)
        R[0x20A1]=lambda:combine(self.g(ord('C')),line([(220,-100),(370,800)],45),line([(330,-100),(480,800)],45),width=self.g(ord('C'))['width'])
        R[0x2109]=lambda:self.juxtapose(self.g(0xB0),self.g(ord('F')),20)
        R[0x2116]=lambda:self.juxtapose(self.g(ord('N')),combine(fit(self.g(ord('o')),0,430,250,680,width=270),rect(0,350,250,390),width=270),30)
        R[0x2117]=lambda:combine(self.ring(400,355,365,40),fit(self.g(ord('P')),250,100,550,610),width=800)
        R[0x211E]=lambda:combine(self.g(ord('R')),line([(370,260),(680,-100)],45),line([(400,-100),(650,200)],45),width=self.g(ord('R'))['width']+40)
        R[0x2120]=lambda:self.juxtapose(fit(self.g(ord('S')),0,400,260,710,width=280),fit(self.g(ord('M')),0,400,340,710,width=360),20)
        R[0x212E]=lambda:fit(sans('e'),70,0,700,700,width=770)
        R[0x2422]=lambda:combine(self.g(ord('b')),line([(40,570),(270,735)],42),width=self.g(ord('b'))['width'])
        R[0x26AD]=lambda:combine(self.ring(260,281,210,42),self.ring(560,281,210,42),width=820)
        R[0x26AE]=lambda:combine(self.g(0x26AD),line([(330,-30),(520,590)],42),width=820)
        R[0x275A]=lambda:rect(110,-160,285,760,width=395)
        # Box-drawing characters join exactly on their advance boundaries.
        directions={0x2500:'LR',0x2502:'UD',0x250C:'RD',0x2510:'LD',0x2514:'RU',0x2518:'LU',
                    0x251C:'URD',0x2524:'ULD',0x252C:'LRD',0x2534:'LRU',0x253C:'LRUD'}
        for c,ds in directions.items():
            R[c]=lambda ds=ds:combine(*[line([(300,281),{'L':(0,281),'R':(600,281),'U':(300,781),'D':(300,-219)}[d]],45) for d in ds],width=600)
        R[0x2581]=lambda:rect(0,-219,600,-94,width=600)
        R[0x2588]=lambda:rect(0,-219,600,781,width=600)
        for c,density in [(0x2591,1),(0x2592,2),(0x2593,3)]:
            R[c]=lambda density=density:combine(*[rect(x*50,-219+y*50,x*50+50,-169+y*50) for x in range(12) for y in range(20) if (x+y)%4<density],width=600)

    def add_part(self,name,g):
        g=clean(g);g.pop('unicode',None)
        self.new[name]=g;self.notes[name]='native MATH size variant or assembly part'
        self.spec['topAccentAttachments'][name]=round(g['width']/2)
        return name

    def build_math(self):
        # Reuse complete native delimiter recipes, including assembly geometry.
        for code,source,offset in [(0x2225,'sy.bardbl',0),(0x2329,'sy.angbracketleft',0),
                                   (0x232A,'sy.angbracketright',0),(0x27EE,'parenleft',0),(0x27EF,'parenright',0),
                                   (0x27E6,'bracketleft',230),(0x27E7,'bracketright',230),
                                   (0x27EA,'sy.angbracketleft',180),(0x27EB,'sy.angbracketright',180)]:
            name=f'native.u{code:04X}'
            if source not in self.spec['vertGlyphVariants']:continue
            def duplicate(old):
                if not offset:return old
                new=f'{name}.{old}'
                g=self.src(old)
                return self.add_part(new,combine(g,transform(g,dx=offset),width=g['width']+offset))
            variants=[[duplicate(old),advance] for old,advance in self.spec['vertGlyphVariants'][source]]
            self.spec['vertGlyphVariants'][name]=variants
            if source in self.spec['vertGlyphAssembly']:
                parts,ic=self.spec['vertGlyphAssembly'][source]
                self.spec['vertGlyphAssembly'][name]=[[[duplicate(old),*values] for old,*values in parts],ic]
            if source in self.spec['extendedShapes']:self.spec['extendedShapes'].append(name)
        # Multiple integrals need text and display designs just like a single integral.
        for code,count in [(0x222C,2),(0x222D,3),(0x2A0C,4)]:
            name=f'native.u{code:04X}';variants=[]
            for i,(old,advance) in enumerate(self.spec['vertGlyphVariants']['op.integral']):
                g=self.src(old);pitch=.65*g['width']
                result=combine(*[transform(g,dx=k*pitch) for k in range(count)],width=g['width']+(count-1)*pitch)
                part=self.add_part(f'{name}.size{i}',result)
                variants.append([part,advance])
                self.spec['italicsCorrections'][part]=self.spec['italicsCorrections'].get(old,0)
            self.spec['vertGlyphVariants'][name]=variants
        for code in [0x2A03,0x2A05,0x2A09,0x2A11,0x2140]:
            name=f'native.u{code:04X}';g=self.g(code);box=bounds(g)
            large=transform(g,xx=1.4,yy=1.4,dy=AXIS*(1-1.4),width=g['width']*1.4)
            display=self.add_part(name+'.display',large)
            self.spec['vertGlyphVariants'][name]=[[name,round(box[3]-box[1])],[display,round((box[3]-box[1])*1.4)]]
        # Wide accents: preserve the native end shapes, expanding the middle.
        # Zero advance and zero accent attachment centre every size on its base.
        wide=[0x0305,0x0330,0x0332,0x034D,0x20D0,0x20D1,0x20D6,0x20E1,
              0x20E9,0x20EC,0x20ED,0x20EE,0x20EF,0x23B4,0x23B5,0x23DC,0x23DD,0x23E0,0x23E1]
        for code in wide:
            name=f'native.u{code:04X}';g=self.g(code);x0,y0,x1,y1=bounds(g)
            variants=[[name,round(x1-x0)]]
            for size in [1000,1600,2500,4000,6500,10000,16000,24000]:
                if size<=x1-x0:continue
                if code in [0x0330,0x23DC,0x23DD]:
                    h=transform(g,xx=size/(x1-x0),width=0)
                else:
                    h=lengthen(g,size-(x1-x0));h=transform(h,dx=-(size-(x1-x0))/2,width=0)
                variant=self.add_part(f'{name}.wide{size}',h)
                self.spec['topAccentAttachments'][variant]=0
                variants.append([variant,size])
            self.spec['horizGlyphVariants'][name]=variants
        for code in [0x3016,0x3017]:
            name=f'native.u{code:04X}';g=self.g(code);box=bounds(g)
            variants=[[name,round(box[3]-box[1])]]
            for scale in [1.4,2,2.8,4,6]:
                part=self.add_part(f'{name}.size{scale}',transform(g,yy=scale,dy=AXIS*(1-scale),width=g['width']))
                variants.append([part,round((box[3]-box[1])*scale)])
            self.spec['vertGlyphVariants'][name]=variants
        self.spec['extendedShapes']=sorted(set(self.spec['extendedShapes']))


def main():
    model=json.loads(MASTER.read_text());spec=json.loads(SPEC.read_text())
    previous=set(json.loads(RECORD.read_text())) if RECORD.exists() else set()
    for n in previous:model.pop(n,None)
    for key in ['topAccentAttachments','italicsCorrections','vertGlyphVariants','horizGlyphVariants','vertGlyphAssembly','horizGlyphAssembly']:
        spec[key]={n:v for n,v in spec.get(key,{}).items() if n not in previous}
    spec['extendedShapes']=sorted(set(spec.get('extendedShapes',[]))-previous)
    targets=json.loads((ROOT/'source/native-unicode-targets.json').read_text())
    b=Builder(model,spec,targets);failures=[]
    for target in targets:
        try:b.g(target['codepoint'])
        except (KeyError,ValueError) as error:
            failures.append(str(error));b.busy.clear()
    if failures:
        print('\n'.join(failures));raise SystemExit(f'{len(failures)} recipes require work; masters not written')
    b.build_math()
    for name,g in b.new.items():
        if not g['contours'] and (not g.get('unicode') or ud.category(chr(g['unicode'])) not in ['Zs','Cf']):raise ValueError(name+' is empty')
    model.update(b.new)
    MASTER.write_text(json.dumps(model,separators=(',',':')))
    SPEC.write_text(json.dumps(spec,indent=2))
    RECORD.write_text(json.dumps(b.notes,indent=2)+'\n')
    writer=UFOWriter(UFO,formatVersion=3);gs=writer.getGlyphSet()
    for name,g in b.new.items():
        obj=SimpleNamespace(width=g['width'],unicodes=[g['unicode']] if 'unicode' in g else [])
        def draw(p,g=g):
            pen=SegmentToPointPen(p)
            for c in g['contours']:replay(c['commands'],pen)
        gs.writeGlyph(name,obj,drawPointsFunc=draw)
    gs.writeContents();lib=plistlib.loads((UFO/'lib.plist').read_bytes())
    lib['public.glyphOrder']=sorted(set(lib['public.glyphOrder'])|set(b.new));writer.writeLib(lib);writer.close()
    print(f'{len(b.new)} original/native glyphs built; no donor font read')


if __name__=='__main__':main()
