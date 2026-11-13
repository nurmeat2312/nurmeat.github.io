import math,sys,json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
f=TTFont('/tmp/ifont/package/files/instrument-serif-latin-400-italic.woff')
gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
ang=-f['post'].italicAngle; t=math.tan(math.radians(ang))
asc=f['hhea'].ascent; desc=f['hhea'].descent
text='Wellness.'
x=0; d=''; boxes=[]
for ch in text:
    gn=cmap[ord(ch)]; g=gs[gn]
    sp=SVGPathPen(gs); g.draw(TransformPen(sp,(1,0,0,-1,x,0))); d+=sp.getCommands()
    rp=RecordingPen(); g.draw(rp)
    pts=[p for op,a in rp.value for p in a]
    xs=[p[0]-p[1]*t for p in pts]; ys=[p[1] for p in pts]
    boxes.append((ch,x+min(xs),x+max(xs),min(ys),max(ys)))
    x+=g.width
W=x
# pen paths in normalized (u,v) per letter; v=0 baseline(bottom of bbox) .. 1 top
P={
 'W':[('M',0.08,1.0),('L',0.3,0.06),('L',0.5,0.95),('L',0.74,0.06),('L',0.95,1.0)],
 'e':[('M',0.12,0.5),('L',0.9,0.62),('Q',0.85,1.02,0.5,1.0),('Q',0.05,0.95,0.08,0.45),('Q',0.12,0.0,0.5,0.02),('Q',0.8,0.04,0.98,0.28)],
 'l':[('M',0.5,1.0),('L',0.42,0.12),('Q',0.45,0.0,0.95,0.12)],
 'n':[('M',0.02,0.85),('L',0.22,0.98),('L',0.2,0.0),('L',0.24,0.7),('Q',0.5,1.05,0.72,0.92),('L',0.74,0.1),('Q',0.8,0.0,1.0,0.14)],
 's':[('M',0.92,0.78),('Q',0.8,1.02,0.5,1.0),('Q',0.12,0.95,0.2,0.68),('Q',0.3,0.5,0.6,0.42),('Q',0.92,0.28,0.78,0.08),('Q',0.5,-0.05,0.04,0.18)],
 '.':[('M',0.45,0.5),('L',0.55,0.5)],
}
SW={'W':250,'e':175,'l':180,'n':185,'s':175,'.':190}
paths=[]
for ch,x0,x1,y0,y1 in boxes:
    w=x1-x0; h=y1-y0
    def pt(u,v):
        X=x0+u*w; Y=y0+v*h
        X=X+Y*t  # re-slant
        return f'{X:.0f} {-Y:.0f}'
    s=''
    for seg in P[ch]:
        if seg[0] in 'ML': s+=f'{seg[0]}{pt(seg[1],seg[2])}'
        else: s+=f'Q{pt(seg[1],seg[2])} {pt(seg[3],seg[4])}'
    paths.append((ch,s,SW[ch]))
# timing: weights
wt={'W':1.6,'e':1.0,'l':0.6,'n':1.1,'s':0.9,'.':0.25}
tot=sum(wt[c] for c,_,_ in paths); T=1.08; ov=0.035
tcur=0.14; items=[]
for c,s,sw in paths:
    du=T*wt[c]/tot+ov
    items.append((s,sw,tcur,du)); tcur+=du-ov
pad=90; top=-(asc)+60; hgt=asc-desc-60
vb=f'{-pad} {-asc+90} {W+2*pad} {asc-desc-200}'
mask=''.join(f'<path d="{s}" pathLength="1" stroke-width="{sw}" style="--d:{a:.3f}s;--t:{du:.3f}s"/>' for s,sw,a,du in items)
svg=f'''<svg class="wl" viewBox="{vb}" role="presentation" aria-hidden="true" focusable="false"><defs><mask id="wl-mask" maskUnits="userSpaceOnUse" x="{-pad}" y="{-asc}" width="{W+2*pad}" height="{asc-desc}"><g class="wl-pen" fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round">{mask}</g></mask></defs><path class="wl-ink" fill="currentColor" d="{d}"/></svg>'''
open('wellness.svg.txt','w').write(svg)
print(upm,ang,asc,desc,W,vb,'end',tcur,len(svg))
