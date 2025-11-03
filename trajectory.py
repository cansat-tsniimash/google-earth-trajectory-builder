from collections import namedtuple
import fastkml
from fastkml import kml, StyleUrl
from fastkml.enums import AltitudeMode
from pygeoif.geometry import Polygon, LineString, MultiPolygon

INPUT = '../traj.csv'
OUTPUT = '../traj.kml'

stream = open(INPUT, mode="r")

Point = namedtuple("Point", ["lon", "lat", "height"])
points = []

stream.readline()
while True:
    line = stream.readline()
    if not line:
        break

    line = line.strip()
    lon, lat, height = line.split(",")
    point = Point(float(lon), float(lat), float(height))
    points.append(point)


polygons = []
prev_point = points[0]
for i in range(1, len(points)):
    cur_point = points[i]
    polygon = [
        prev_point,
        cur_point,
        Point(cur_point.lon, cur_point.lat, 0),
        Point(prev_point.lon, prev_point.lat, 0),
        prev_point,
    ]

    polygons.append(polygon)
    prev_point = cur_point


k = kml.KML()

polystyle = fastkml.styles.PolyStyle(color='ccccccaa', outline=1)
linestyle = fastkml.styles.LineStyle(color='ff0000ff', width=10)
projstyles = fastkml.styles.Style(id='projstyles', styles=[polystyle, linestyle])

linestyle = fastkml.styles.LineStyle(color='ff0000ff', width=10)
trajstyles = fastkml.styles.Style(id='linestyles', styles=[linestyle])

d = kml.Document(
    id='docid', name='Траектория полёта',
    styles=[projstyles, trajstyles]
)
k.append(d)

f = kml.Folder(id='fid', name='Траектория')
d.append(f)

geometry = fastkml.geometry.MultiGeometry(
    geometry=MultiPolygon([(x, [],) for x in polygons]),
    altitude_mode=AltitudeMode.absolute,
)
p = kml.Placemark(name='name', style_url=StyleUrl(url='#projstyles'), kml_geometry=geometry)
f.append(p)

geometry = fastkml.geometry.LineString(
    geometry=LineString(points),
    altitude_mode=AltitudeMode.absolute,
)
p = kml.Placemark(style_url=StyleUrl(url='#linestyles'), kml_geometry=geometry)
f.append(p)

with open(OUTPUT, mode="w") as outstream:
    outstream.write(k.to_string(prettyprint=True))
