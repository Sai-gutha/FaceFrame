"""
Face Mesh Overlay Rendering
===========================

Draws MediaPipe's face landmark topology over the camera frame, so the scan
reads as a tracked wireframe rather than a scatter of dots.

WHY THIS MODULE EXISTS:
mediapipe 1.0 removed the `mp.solutions` package outright -- `mediapipe.python`
is not importable at all -- which took `drawing_utils.draw_landmarks` and the
`FACEMESH_*` constants with it. The Tasks API still ships the same topology,
re-exported publicly as `vision.FaceLandmarksConnections`, but no drawing
helper, so we render it here. Go through that public export rather than
`mediapipe.tasks.python.vision.face_landmarker` -- the two resolve to the same
object today, but only the former is supported surface.

PERFORMANCE NOTES:
- Connection sets are deduplicated, thinned and converted to index arrays once
  at import. Per frame we only fancy-index with them, never re-walk the
  Connection objects or recompute the thinning.
- Each style draws in a single batched `cv2.polylines` call. The alternative --
  one `cv2.line` per edge -- costs around a thousand Python-to-C round trips
  per frame on the tessellation style.
- Measured warm at 1280x720: tessellation 1.0 ms, contours 0.2 ms, plus 0.1 ms
  for the landmark-to-pixel conversion shared by every style.
"""

from collections import namedtuple

import cv2
import numpy as np
from mediapipe.tasks.python import vision

# ============================================================================
# CONNECTION TOPOLOGY
# ============================================================================

def _edges(*connection_sets):
    """
    Flatten one or more Connection lists into a deduplicated index array.

    Deduplication treats an edge as undirected, so (a, b) and (b, a) collapse to
    one entry. This matters twice over on the tessellation, where 1234 of the
    2556 listed edges are repeats -- each interior edge is shared by two
    triangles and listed once per triangle:

      - Antialiased strokes composite, so a doubled edge blends twice and comes
        out brighter. Drawing the raw list makes roughly half the mesh brighter
        than the rest, which reads as uneven rather than as shading.
      - It halves the rasterizing work for identical geometry.

    Args:
        *connection_sets: lists of FaceLandmarksConnections.Connection, each
                          exposing .start and .end landmark indices

    Returns:
        int32 array of shape (N, 2) holding [start, end] index pairs
    """
    seen = set()
    pairs = []
    for connections in connection_sets:
        for c in connections:
            key = (min(c.start, c.end), max(c.start, c.end))
            if key not in seen:
                seen.add(key)
                pairs.append((c.start, c.end))
    return np.array(pairs, dtype=np.int32)


# The full triangulated web across the whole face -- the dense wireframe the
# face mesh is recognisable for. The triangulation follows facial geometry, so
# density alone carries the 3D read; no shading is involved. Kept as its own
# constant so the undiluted mesh stays available; TESSELLATION below is the
# thinned version actually drawn.
TESSELLATION_FULL = _edges(vision.FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION)

# Feature outlines only. Two gaps in FACE_LANDMARKS_CONTOURS have to be filled
# by hand, both confirmed by rendering it:
#   - it stops at landmark 466, so it misses the irises at 469-477, which exist
#     only because our model emits 478 points. Without them the eyes are holes.
#   - it carries no nose contour at all. That matters here more than in a
#     generic face app: the nose bridge is where the glasses actually sit.
CONTOURS = _edges(
    vision.FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS,
    vision.FaceLandmarksConnections.FACE_LANDMARKS_NOSE,
    vision.FaceLandmarksConnections.FACE_LANDMARKS_LEFT_IRIS,
    vision.FaceLandmarksConnections.FACE_LANDMARKS_RIGHT_IRIS,
)

# Just the face outline -- the same 36-point ring used as a depth occluder in
# 3D try-on implementations, kept here as a minimal "locked on" indicator.
OVAL = _edges(vision.FaceLandmarksConnections.FACE_LANDMARKS_FACE_OVAL)

# ============================================================================
# THINNING
# ============================================================================
# The full tessellation reads as too much mesh on a face. Thinning it is not a
# matter of dropping edges: removing edges individually punches gaps in the
# surface and looks like damage. Removing whole vertices instead merges the
# triangles around each one into a single larger cell, which reads as a coarser
# mesh -- which is the intent.

MESH_DENSITY_REDUCTION = 0.25


def _feature_vertices(*connection_sets):
    """Collect the landmark indices that carry facial features."""
    vertices = set()
    for connections in connection_sets:
        for c in connections:
            vertices.add(c.start)
            vertices.add(c.end)
    return vertices


# Features thinning must never touch. The irises are deliberately absent: they
# live at 469-477 while the tessellation stops at 467, so they are not part of
# this mesh and cannot be thinned out of it.
_FEATURE_VERTICES = _feature_vertices(
    vision.FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS,
    vision.FaceLandmarksConnections.FACE_LANDMARKS_NOSE,
    vision.FaceLandmarksConnections.FACE_LANDMARKS_FACE_OVAL,
)


def _thin(edges, protected, reduction):
    """
    Reduce edge count by removing an independent set of non-feature vertices.

    No two removed vertices are adjacent, so each removal leaves one clean
    polygonal cell instead of tearing a strip through the surface, and every
    surviving vertex keeps at least one edge. Feature vertices are excluded from
    removal, so eyes, lips, nose and silhouette stay exactly as crisp as before.

    Highest-degree vertices are removed first: they sit in the densest regions,
    which are the ones worth calming, and each retires the most edges.

    Depends only on mesh topology, never on landmark positions, so the result is
    identical every run and costs nothing per frame.

    Args:
        edges: (N, 2) deduplicated index array
        protected: set of landmark indices that must not be removed
        reduction: target fraction of edges to drop, 0..1

    Returns:
        int32 array of shape (M, 2) with M <= N
    """
    adjacency = {}
    for a, b in edges:
        adjacency.setdefault(int(a), set()).add(int(b))
        adjacency.setdefault(int(b), set()).add(int(a))

    candidates = sorted(
        (v for v in adjacency if v not in protected),
        key=lambda v: (-len(adjacency[v]), v),
    )

    goal = int(len(edges) * reduction)
    removed = set()
    blocked = set()
    dropped = 0
    for v in candidates:
        if dropped >= goal:
            break
        if v in blocked:
            continue
        removed.add(v)
        blocked |= adjacency[v]  # neighbours are no longer removable
        dropped += len(adjacency[v])

    kept = [(a, b) for a, b in edges if int(a) not in removed and int(b) not in removed]
    return np.array(kept, dtype=np.int32)


# 1322 edges -> 992, a 25% reduction, with all facial features intact.
TESSELLATION = _thin(TESSELLATION_FULL, _FEATURE_VERTICES, MESH_DENSITY_REDUCTION)

# ============================================================================
# STYLES
# ============================================================================

_Style = namedtuple("_Style", "name edges color thickness min_points")


def _style(name, edges, color, thickness):
    """Build a style, recording how many landmarks its edges require."""
    min_points = 0 if edges is None else int(edges.max()) + 1
    return _Style(name, edges, color, thickness, min_points)


# Cycle order for the 'm' key. Tessellation leads: the white wireframe is the
# look this overlay is meant to have, and after deduplication and thinning it
# costs under 1 ms per frame at 720p. Colours are BGR.
STYLES = (
    _style("tessellation", TESSELLATION, (255, 255, 255), 1),
    _style("contours", CONTOURS, (235, 225, 200), 1),
    _style("oval", OVAL, (184, 146, 80), 2),
    _style("off", None, None, 0),
)


def next_style(style_index):
    """Advance to the next style in the cycle."""
    return (style_index + 1) % len(STYLES)


def style_name(style_index):
    """Human-readable name of the current style, for the on-screen hint."""
    return STYLES[style_index % len(STYLES)].name


# ============================================================================
# RENDERING
# ============================================================================

def to_pixels(landmarks, width, height):
    """
    Convert normalized landmarks to integer pixel coordinates in one pass.

    Args:
        landmarks: sequence of NormalizedLandmark (x, y in 0..1)
        width, height: frame dimensions in pixels

    Returns:
        int32 array of shape (len(landmarks), 2) holding [x, y] per landmark
    """
    coords = np.empty((len(landmarks), 2), dtype=np.float32)
    for i, lm in enumerate(landmarks):
        coords[i, 0] = lm.x
        coords[i, 1] = lm.y
    coords[:, 0] *= width
    coords[:, 1] *= height
    return coords.astype(np.int32)


def draw(frame, points, style_index):
    """
    Draw the mesh onto the frame in place.

    Call this before any glasses overlay -- the overlay is meant to sit on top
    of the mesh, not under it.

    Args:
        frame: BGR frame, modified in place
        points: (N, 2) pixel coordinates from to_pixels()
        style_index: index into STYLES

    Returns:
        True if anything was drawn, False if the style is off or the landmark
        set is too small for it.
    """
    style = STYLES[style_index % len(STYLES)]
    if style.edges is None or len(points) < style.min_points:
        return False

    # points[edges] -> (num_edges, 2, 2): one 2-point polyline per edge, drawn
    # in a single call rather than looped over in Python.
    segments = points[style.edges]
    cv2.polylines(frame, segments, False, style.color, style.thickness, cv2.LINE_AA)
    return True
