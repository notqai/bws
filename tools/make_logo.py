import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

BOXES={'B':(18,178),'W':(258,466),'S':(542,654)}
Y0,Y1=58,454
PANELS=[(0,202),(238,490),(522,674)]

def glyph_paths(fontfile, axes):
    f=TTFont(fontfile)
    if 'fvar' in f and axes:
        f=instancer.instantiateVariableFont(f, axes)
    gs=f.getGlyphSet(); cmap=f.getBestCmap()
    out={}
    for ch,(x0,x1) in BOXES.items():
        g=gs[cmap[ord(ch)]]
        bp=BoundsPen(gs); g.draw(bp); bx0,by0,bx1,by1=bp.bounds
        sx=(x1-x0)/(bx1-bx0); sy=(Y1-Y0)/(by1-by0)
        # font y-up -> svg y-down
        t=(sx,0,0,-sy, x0-bx0*sx, Y1+by0*sy)
        sp=SVGPathPen(gs, ntos=lambda v: ('%.1f'%v).rstrip('0').rstrip('.'))
        g.draw(TransformPen(sp,t))
        out[ch]=sp.getCommands()
    return out

def svg(paths, mode='color', title='BWS Engineering Sdn Bhd'):
    clip=''.join(f'<rect x="{a}" y="0" width="{b-a}" height="512"/>' for a,b in PANELS)
    if mode=='color':
        defs=f'''<defs><radialGradient id="bws-glow" cx="346" cy="256" r="400" gradientTransform="translate(346 256) scale(1 .58) translate(-346 -256)" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#7FD6F4"/><stop offset=".3" stop-color="#36B0EA"/><stop offset=".58" stop-color="#4797E6"/><stop offset=".8" stop-color="#1A55E0"/><stop offset="1" stop-color="#0A18D9"/></radialGradient>
<clipPath id="bws-panels">{clip}</clipPath></defs>
<g clip-path="url(#bws-panels)"><rect width="674" height="512" fill="#0A18D9"/><rect width="674" height="512" fill="url(#bws-glow)"/></g>'''
        letters='#FFFFFF'
        body=defs+f'<g fill="{letters}" stroke="{letters}" stroke-width="5" stroke-linejoin="round">'+''.join(f'<path d="{p}"/>' for p in paths.values())+'</g>'
    else:  # mono: panels white, letters knocked out
        mask=f'<defs><mask id="bws-knock"><rect width="674" height="512" fill="#fff"/><g fill="#000">'+''.join(f'<path d="{p}"/>' for p in paths.values())+'</g></mask></defs>'
        body=mask+f'<g fill="{"#FFFFFF" if mode=="white" else "#0A1240"}" mask="url(#bws-knock)">{clip}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 674 512" role="img" aria-labelledby="bws-t"><title id="bws-t">{title}</title>{body}</svg>'

if __name__=='__main__':
    font=sys.argv[1]; axes=dict(a.split('=') for a in sys.argv[2:])
    axes={k:float(v) for k,v in axes.items()}
    print(svg(glyph_paths(font,axes)))

def favicon(mode='color'):
    # three panels only, same width ratios as the mark (202:252:152), square 64 grid
    ws=[202,252,152]; gap=64; total=sum(ws)+2*gap; s=56/total
    x=4; rects=[]
    for w in ws:
        rects.append((x, w*s)); x+=w*s+gap*s
    clip=''.join(f'<rect x="{a:.2f}" y="8" width="{w:.2f}" height="48" rx="1.5"/>' for a,w in rects)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><radialGradient id="g" cx="32" cy="32" r="34" gradientTransform="translate(32 32) scale(1 .62) translate(-32 -32)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#7FD6F4"/><stop offset=".35" stop-color="#36B0EA"/><stop offset=".6" stop-color="#4797E6"/><stop offset=".82" stop-color="#1A55E0"/><stop offset="1" stop-color="#0A18D9"/></radialGradient><clipPath id="c">{clip}</clipPath></defs><g clip-path="url(#c)"><rect width="64" height="64" fill="url(#g)"/></g></svg>'''
