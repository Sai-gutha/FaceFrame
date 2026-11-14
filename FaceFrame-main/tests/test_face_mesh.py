"""
Face mesh topology tests
========================

Verifies the claims src/face_mesh.py makes about deduplication and thinning.
The load-bearing one is that thinning does not punch holes: removing a vertex
is only safe if the ring of its former neighbours still encloses the gap, which
turns the surrounding triangles into one larger cell instead of an opening.

Runs standalone with no extra dependencies:

    python tests/test_face_mesh.py

Also collects under pytest if that ever gets added to the project.
"""

import os
import sys
from collections import defaultdict, deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

import face_mesh


# ============================================================================
# HELPERS
# ============================================================================

def _adjacency(edges):
    """Undirected adjacency map from an (N, 2) edge array."""
    adj = defaultdict(set)
    for a, b in edges:
        adj[int(a)].add(int(b))
        adj[int(b)].add(int(a))
    return adj


def _removed_vertices():
    """Vertices dropped by thinning: present in the full mesh, absent after."""
    full = set(face_mesh.TESSELLATION_FULL.flatten().tolist())
    kept = set(face_mesh.TESSELLATION.flatten().tolist())
    return sorted(full - kept)


# ============================================================================
# DEDUPLICATION
# ============================================================================

def test_no_duplicate_edges_in_any_style():
    """An edge appearing twice blends twice under LINE_AA and renders brighter."""
    for style in face_mesh.STYLES:
        if style.edges is None:
            continue
        pairs = [frozenset((int(a), int(b))) for a, b in style.edges]
        assert len(pairs) == len(set(pairs)), f"{style.name} has duplicate edges"


def test_no_self_loops():
    for style in face_mesh.STYLES:
        if style.edges is None:
            continue
        assert not any(a == b for a, b in style.edges), f"{style.name} has a self-loop"


def test_dedup_removed_the_expected_count():
    """MediaPipe lists every interior edge once per adjoining triangle."""
    raw = 2556  # len(FACE_LANDMARKS_TESSELATION)
    assert len(face_mesh.TESSELLATION_FULL) == 1322
    assert raw - len(face_mesh.TESSELLATION_FULL) == 1234


# ============================================================================
# THINNING
# ============================================================================

def test_thinning_hits_the_target_reduction():
    before, after = len(face_mesh.TESSELLATION_FULL), len(face_mesh.TESSELLATION)
    actual = 1 - after / before
    target = face_mesh.MESH_DENSITY_REDUCTION
    assert abs(actual - target) < 0.02, f"reduction {actual:.3f}, expected ~{target}"


def test_removed_vertices_form_an_independent_set():
    """Adjacent removals would merge two cells into one oversized gap."""
    adj = _adjacency(face_mesh.TESSELLATION_FULL)
    removed = set(_removed_vertices())
    for v in removed:
        assert not (adj[v] & removed), f"vertex {v} was removed alongside a neighbour"


def test_no_orphaned_vertices():
    """Every vertex that survives must still be attached to something."""
    adj_full = _adjacency(face_mesh.TESSELLATION_FULL)
    kept = set(face_mesh.TESSELLATION.flatten().tolist())
    removed = set(_removed_vertices())
    for v in adj_full:
        if v not in removed:
            assert v in kept, f"vertex {v} survived thinning but lost every edge"


def test_removing_a_vertex_leaves_a_closed_cell_not_a_hole():
    """
    The claim under review.

    A hole means an open boundary. After removing v, the ring of its former
    neighbours must (a) leave every ring member with at least two neighbours
    inside the ring, and (b) stay connected. Both together mean the ring
    encloses the gap, so the surrounding triangles read as one larger cell.

    Extra chords across a ring are fine -- they subdivide the cell further,
    which is more mesh, not a hole.
    """
    adj_full = _adjacency(face_mesh.TESSELLATION_FULL)
    adj_thin = _adjacency(face_mesh.TESSELLATION)

    for v in _removed_vertices():
        ring = adj_full[v]
        degrees = {r: len(adj_thin[r] & ring) for r in ring}
        assert min(degrees.values()) >= 2, (
            f"removing vertex {v} left an open boundary: "
            f"ring degrees {sorted(degrees.values())}"
        )

        start = next(iter(ring))
        seen, queue = {start}, deque([start])
        while queue:
            for n in adj_thin[queue.popleft()] & ring:
                if n not in seen:
                    seen.add(n)
                    queue.append(n)
        assert seen == ring, (
            f"removing vertex {v} left a disconnected ring: "
            f"reached {len(seen)} of {len(ring)}"
        )


def test_feature_vertices_are_never_thinned():
    """Eyes, lips, nose and silhouette must stay exactly as crisp as before."""
    removed = set(_removed_vertices())
    protected = face_mesh._FEATURE_VERTICES
    in_mesh = set(face_mesh.TESSELLATION_FULL.flatten().tolist())
    for v in protected & in_mesh:
        assert v not in removed, f"feature vertex {v} was thinned away"


def test_thinning_is_deterministic():
    """Recomputing must give the identical array, or the mesh would flicker."""
    again = face_mesh._thin(
        face_mesh.TESSELLATION_FULL,
        face_mesh._FEATURE_VERTICES,
        face_mesh.MESH_DENSITY_REDUCTION,
    )
    assert np.array_equal(again, face_mesh.TESSELLATION)


def test_thinning_depends_only_on_topology():
    """Shuffling edge order must not change which vertices get removed."""
    shuffled = face_mesh.TESSELLATION_FULL.copy()
    rng = np.random.default_rng(0)
    rng.shuffle(shuffled)
    out = face_mesh._thin(
        shuffled, face_mesh._FEATURE_VERTICES, face_mesh.MESH_DENSITY_REDUCTION
    )
    assert set(map(tuple, map(sorted, out))) == set(
        map(tuple, map(sorted, face_mesh.TESSELLATION))
    )


# ============================================================================
# RENDERING CONTRACT
# ============================================================================

def test_all_indices_are_within_the_landmark_range():
    for style in face_mesh.STYLES:
        if style.edges is None:
            continue
        assert int(style.edges.max()) < 478, f"{style.name} indexes past landmark 477"
        assert int(style.edges.min()) >= 0


def test_min_points_matches_the_edge_set():
    for style in face_mesh.STYLES:
        if style.edges is None:
            assert style.min_points == 0
        else:
            assert style.min_points == int(style.edges.max()) + 1


def test_draw_declines_rather_than_crashing_on_short_landmark_sets():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    points = np.zeros((10, 2), dtype=np.int32)  # far too few
    for i in range(len(face_mesh.STYLES)):
        assert face_mesh.draw(frame, points, i) is False
    assert not frame.any(), "declined draw still touched the frame"


def test_draw_marks_the_frame_for_every_active_style():
    rng = np.random.default_rng(1)
    points = rng.integers(20, 220, size=(478, 2)).astype(np.int32)
    for i, style in enumerate(face_mesh.STYLES):
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        drew = face_mesh.draw(frame, points, i)
        assert drew == (style.edges is not None)
        assert frame.any() == drew


def test_style_cycle_returns_to_the_start():
    i = 0
    for _ in range(len(face_mesh.STYLES)):
        i = face_mesh.next_style(i)
    assert i == 0


# ============================================================================
# RUNNER
# ============================================================================

if __name__ == "__main__":
    tests = [(n, o) for n, o in sorted(globals().items())
             if n.startswith("test_") and callable(o)]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL  {name}\n          {exc}")

    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    print(f"mesh: {len(face_mesh.TESSELLATION_FULL)} -> {len(face_mesh.TESSELLATION)} edges, "
          f"{len(_removed_vertices())} vertices removed")
    sys.exit(1 if failures else 0)
