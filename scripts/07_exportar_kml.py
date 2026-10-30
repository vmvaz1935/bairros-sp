# Exporta os bairros para KML (Google My Maps / Google Earth)
import json, html, hashlib, shapely
from shapely.geometry import shape
def color(name):  # KML usa aabbggrr
    h=hashlib.md5(name.encode()).hexdigest(); return '99'+h[4:6]+h[2:4]+h[0:2]
def rings(poly):
    def r(c): return ' '.join(f'{x:.5f},{y:.5f}' for x,y in c)
    s=f'<outerBoundaryIs><LinearRing><coordinates>{r(poly.exterior.coords)}</coordinates></LinearRing></outerBoundaryIs>'
    s+=''.join(f'<innerBoundaryIs><LinearRing><coordinates>{r(i.coords)}</coordinates></LinearRing></innerBoundaryIs>' for i in poly.interiors)
    return f'<Polygon>{s}</Polygon>'
def kml(feats, title, tol):
    out=[f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{html.escape(title)}</name>']
    for f in feats:
        p=f['properties']; g=shape(f['geometry']).simplify(tol,preserve_topology=True)
        parts=[q for q in shapely.get_parts(g) if q.area>0]
        geom=rings(parts[0]) if len(parts)==1 else '<MultiGeometry>'+''.join(rings(q) for q in parts)+'</MultiGeometry>'
        desc=f"Distrito: {p['distrito']}<br>Área: {p['area_km2']:.2f} km²<br>Endereços (CNEFE 2022): {p['enderecos']}"
        out.append(f'<Placemark><name>{html.escape(p["bairro"])}</name><description><![CDATA[{desc}]]></description>'
                   f'<Style><LineStyle><color>ff333333</color><width>1</width></LineStyle><PolyStyle><color>{color(p["bairro"])}</color></PolyStyle></Style>{geom}</Placemark>')
    out.append('</Document></kml>'); return ''.join(out)
B=json.load(open('dados/bairros_sp.geojson'))['features']
# 1 arquivo de ~3,5 MB e 1.854 itens: cabe no limite do Google My Maps (5 MB, 2.000 itens por camada)
open('kml/bairros_sp.kml','w').write(kml(B,'Bairros de São Paulo',0.00004))

