# -*- coding: utf-8 -*-
"""Vectorised ray/triangle intersection, for the checks that fire thousands of rays.

600_profile.py measured Part.Shape.common(line) at 2.6 ms. 406_coverage.py fires 187 rays
against 28 parts at 3 poses -- 15,708 of them, 40 seconds of boolean algebra to answer a
question about straight lines. Tessellating the same part costs 0.04 s and a Moller-Trumbore
test against the resulting triangles is microseconds per ray.

The approximation is the tessellation deflection, which is a controlled 0.05 mm here, against
features measured in millimetres. Where exactness matters -- interference volumes -- the BRep
boolean stays; this is for the line-of-sight questions, where it never did.

No FreeCAD import: feed it triangles. That also means it can be unit-tested and reused from a
headless shard.
"""
import numpy as np


class Mesh(object):
    """Triangles as (N,3,3). Build once per part, query any number of rays."""

    def __init__(self, tris):
        self.t = np.asarray(tris, dtype=np.float64).reshape(-1, 3, 3)
        self.v0 = self.t[:, 0, :]
        self.e1 = self.t[:, 1, :] - self.v0
        self.e2 = self.t[:, 2, :] - self.v0
        self.lo = self.t.min(axis=1).min(axis=0)
        self.hi = self.t.max(axis=1).max(axis=0)

    @classmethod
    def from_shape(cls, shape, deflection=0.05):
        pts, facets = shape.tessellate(deflection)
        p = np.array([[v.x, v.y, v.z] for v in pts], dtype=np.float64)
        f = np.array(facets, dtype=np.int64)
        return cls(p[f])

    def hits(self, origin, direction, tmax=1e9):
        """distances along `direction` at which the ray meets the mesh, sorted"""
        o = np.asarray(origin, dtype=np.float64)
        d = np.asarray(direction, dtype=np.float64)
        d = d / np.linalg.norm(d)
        # slab test against the whole mesh first: one comparison kills most parts outright
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = (self.lo - o) / d
            t2 = (self.hi - o) / d
        tn = np.nanmax(np.minimum(t1, t2))
        tf = np.nanmin(np.maximum(t1, t2))
        if not (tf >= max(tn, 0.0)):
            return np.empty(0)
        pv = np.cross(d, self.e2)
        det = np.einsum("ij,ij->i", self.e1, pv)
        ok = np.abs(det) > 1e-12
        inv = np.zeros_like(det)
        inv[ok] = 1.0 / det[ok]
        tv = o - self.v0
        u = np.einsum("ij,ij->i", tv, pv) * inv
        ok &= (u >= -1e-9) & (u <= 1.0 + 1e-9)
        qv = np.cross(tv, self.e1)
        v = np.einsum("j,ij->i", d, qv) * inv
        ok &= (v >= -1e-9) & (u + v <= 1.0 + 1e-9)
        t = np.einsum("ij,ij->i", self.e2, qv) * inv
        ok &= (t > 1e-7) & (t < tmax)
        return np.sort(t[ok])

    def first(self, origin, direction, tmax=1e9):
        h = self.hits(origin, direction, tmax)
        return float(h[0]) if h.size else None

    def first_many(self, origins, directions, tmax=1e9):
        """Nearest hit for a BATCH of rays -> (N,) array, nan where there is no hit.

        Honest about what this buys. Brute force is O(rays x triangles) however it is
        written, and batching only removes python/numpy call overhead -- measured at 1369 us
        per ray for 2000 rays against 3600 triangles, against 1167 us looping. What makes it
        quick in practice is that the real parts are ~2000 triangles and the real queries are
        ~200 rays, so a single pass is 400k pair-tests rather than millions. For anything
        larger this wants a BVH, which is deliberately not here: the measurement does not
        justify it yet.
        """
        o = np.asarray(origins, dtype=np.float64).reshape(-1, 3)
        d = np.asarray(directions, dtype=np.float64).reshape(-1, 3)
        d = d / np.linalg.norm(d, axis=1, keepdims=True)
        n = o.shape[0]
        out = np.full(n, np.nan)
        # (n, T, 3) broadcasts; chunk so the temporary stays reasonable
        T = self.t.shape[0]
        chunk = max(1, int(4e6 // max(1, T)))
        for s0 in range(0, n, chunk):
            oc, dc = o[s0:s0 + chunk], d[s0:s0 + chunk]
            pv = np.cross(dc[:, None, :], self.e2[None, :, :])
            det = np.einsum("tj,ntj->nt", self.e1, pv)
            ok = np.abs(det) > 1e-12
            inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
            tv = oc[:, None, :] - self.v0[None, :, :]
            u = np.einsum("ntj,ntj->nt", tv, pv) * inv
            ok &= (u >= -1e-9) & (u <= 1.0 + 1e-9)
            qv = np.cross(tv, self.e1[None, :, :])
            v = np.einsum("nj,ntj->nt", dc, qv) * inv
            ok &= (v >= -1e-9) & (u + v <= 1.0 + 1e-9)
            tt = np.einsum("tj,ntj->nt", self.e2, qv) * inv
            ok &= (tt > 1e-7) & (tt < tmax)
            tt = np.where(ok, tt, np.inf)
            m = tt.min(axis=1)
            out[s0:s0 + chunk] = np.where(np.isfinite(m), m, np.nan)
        return out


def transformed(mesh, placement):
    """a copy of `mesh` under a FreeCAD Placement (rotation + translation)"""
    m = placement.toMatrix()
    R = np.array([[m.A11, m.A12, m.A13],
                  [m.A21, m.A22, m.A23],
                  [m.A31, m.A32, m.A33]], dtype=np.float64)
    tr = np.array([m.A14, m.A24, m.A34], dtype=np.float64)
    return Mesh(mesh.t.reshape(-1, 3).dot(R.T).reshape(-1, 3, 3) + tr)
