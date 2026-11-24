#!/usr/bin/env python3
"""Decode the TopoJSON files of USER/html-generated/maps/data (world-110m/50m/10m.json)
into plain GeoJSON, one file per object (countries, regions, land, lakes, rivers, cities).

Usage: python3 topo2geo.py <maps/data dir> <out dir> [--res 110m 50m 10m] [--objects countries regions ...]
"""
import argparse
import json
import os


def decode_arcs(topo):
    tr = topo.get("transform")
    out = []
    for arc in topo["arcs"]:
        if tr:
            (sx, sy), (tx, ty) = tr["scale"], tr["translate"]
            x = y = 0
            pts = []
            for dx, dy in arc:
                x += dx
                y += dy
                pts.append([round(x * sx + tx, 6), round(y * sy + ty, 6)])
        else:
            pts = [list(p) for p in arc]
        out.append(pts)
    return out


def point(topo, p):
    tr = topo.get("transform")
    if not tr:
        return p
    (sx, sy), (tx, ty) = tr["scale"], tr["translate"]
    return [round(p[0] * sx + tx, 6), round(p[1] * sy + ty, 6)]


def line(arcs, idxs):
    pts = []
    for i in idxs:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def geometry(topo, arcs, g):
    t = g.get("type")
    if t is None:
        return None
    if t == "Point":
        return {"type": t, "coordinates": point(topo, g["coordinates"])}
    if t == "MultiPoint":
        return {"type": t, "coordinates": [point(topo, p) for p in g["coordinates"]]}
    if t == "LineString":
        return {"type": t, "coordinates": line(arcs, g["arcs"])}
    if t == "MultiLineString":
        return {"type": t, "coordinates": [line(arcs, l) for l in g["arcs"]]}
    if t == "Polygon":
        return {"type": t, "coordinates": [line(arcs, r) for r in g["arcs"]]}
    if t == "MultiPolygon":
        return {"type": t, "coordinates": [[line(arcs, r) for r in p] for p in g["arcs"]]}
    if t == "GeometryCollection":
        return {"type": t, "geometries": [geometry(topo, arcs, x) for x in g["geometries"]]}
    raise ValueError(t)


def _unwrap_ring(ring):
    out = [list(ring[0])]
    for x, y in ring[1:]:
        px = out[-1][0]
        while x - px > 180:
            x -= 360
        while x - px < -180:
            x += 360
        out.append([x, y])
    return out


def _planar_polygon(rings):
    """Rings of one spherical polygon -> planar shapely geometry inside [-180, 180],
    cut at the antimeridian; a ring that winds around a pole is closed through the pole."""
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union

    shells = []
    holes = []
    for k, r in enumerate(rings):
        u = _unwrap_ring(r)
        span = u[-1][0] - u[0][0]
        if abs(span) > 180:  # encircles a pole (Antarctica): close along the pole latitude
            pole = -90.0 if sum(p[1] for p in u) < 0 else 90.0
            u = u + [[u[-1][0], pole], [u[0][0], pole]]
        (shells if k == 0 else holes).append(u)
    poly = Polygon(shells[0]).buffer(0)
    for h in holes:
        poly = poly.difference(Polygon(h).buffer(0))
    parts = []
    for shift in (-720, -360, 0, 360, 720):
        piece = poly.intersection(box(-180 - shift, -90, 180 - shift, 90))
        if not piece.is_empty:
            parts.append(shapely_translate(piece, shift))
    return unary_union(parts)


def shapely_translate(g, dx):
    from shapely import affinity
    return affinity.translate(g, xoff=dx)


def clean_geometry(geom):
    """GeoJSON polygon geometry (TopoJSON/d3 spherical conventions) -> valid planar RFC 7946 geometry."""
    if geom is None or geom["type"] not in ("Polygon", "MultiPolygon"):
        return geom
    import shapely
    from shapely.geometry import mapping
    from shapely.ops import unary_union

    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    g = unary_union([_planar_polygon(p) for p in polys])
    g = shapely.make_valid(g)
    if g.geom_type == "GeometryCollection":
        g = unary_union([p for p in g.geoms if p.geom_type in ("Polygon", "MultiPolygon")])
    g = shapely.orient_polygons(g, exterior_cw=False) if hasattr(shapely, "orient_polygons") else _orient(g)
    m = mapping(g)
    return {"type": m["type"], "coordinates": _round(m["coordinates"])}


def _orient(g):
    from shapely.geometry.polygon import orient
    from shapely.geometry import MultiPolygon
    if g.geom_type == "Polygon":
        return orient(g, 1.0)
    return MultiPolygon([orient(p, 1.0) for p in g.geoms])


def _round(c):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(c[0], 6), round(c[1], 6)]
    return [_round(x) for x in c]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("out")
    ap.add_argument("--res", nargs="*", default=["110m", "50m", "10m"])
    ap.add_argument("--objects", nargs="*", default=None)
    ap.add_argument("--raw", action="store_true",
                    help="keep d3/TopoJSON conventions (clockwise rings, polygons crossing ±180) instead of planar RFC 7946")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for res in a.res:
        topo = json.load(open(os.path.join(a.data, f"world-{res}.json"), encoding="utf-8"))
        arcs = decode_arcs(topo)
        for name, obj in topo["objects"].items():
            if a.objects and name not in a.objects:
                continue
            feats = []
            for g in obj.get("geometries", [obj]):
                feats.append({"type": "Feature", "id": g.get("id"), "properties": g.get("properties", {}),
                              "geometry": geometry(topo, arcs, g)})
            path = os.path.join(a.out, f"{name}_{res}.geojson")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"type": "FeatureCollection", "features": feats}, f, ensure_ascii=False, separators=(",", ":"))
            print(f"{path}: {len(feats)}")


if __name__ == "__main__":
    main()
