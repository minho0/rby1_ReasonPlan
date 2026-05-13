import ast
import re
from typing import List, Optional, Sequence, Tuple

Trajectory = List[Tuple[float, float]]

_TRAJ_MARKERS = (
    "planning trajectory should be:",
    "future planning trajectory should be:",
    "trajectory should be:",
)

_PAIR_RE = re.compile(
    r"\(?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\)?"
)


def _strip_after_marker(text: str) -> str:
    lower = text.lower()
    start = -1
    marker_len = 0
    for marker in _TRAJ_MARKERS:
        idx = lower.rfind(marker)
        if idx >= 0 and idx + len(marker) > start:
            start = idx
            marker_len = len(marker)
    if start >= 0:
        text = text[start + marker_len :]
    return text.strip().strip(". \n\t")


def _normalize_point(point: Sequence[float]) -> Optional[Tuple[float, float]]:
    if len(point) < 2:
        return None
    try:
        return float(point[0]), float(point[1])
    except (TypeError, ValueError):
        return None


def parse_trajectory(text: str, max_points: Optional[int] = None) -> Optional[Trajectory]:
    """Parse ReasonPlan text output into a list of ego-frame (x, y) waypoints.

    Expected examples:
      - "... planning trajectory should be: (0.5, 0.0), (1.0, 0.2)"
      - "planning trajectory should be: [(0.5, 0.0), (1.0, 0.2)]"

    Returns None if no valid 2D waypoint can be parsed.
    """
    if not text:
        return None

    candidate = _strip_after_marker(text)

    # First try a safe Python literal parse. ReasonPlan often emits tuple/list syntax.
    literal_candidates = [candidate]
    if not candidate.startswith("["):
        literal_candidates.append(f"[{candidate}]")

    for literal in literal_candidates:
        try:
            parsed = ast.literal_eval(literal)
        except (SyntaxError, ValueError):
            continue

        if isinstance(parsed, tuple) and len(parsed) >= 2 and all(isinstance(v, (int, float)) for v in parsed[:2]):
            parsed = [parsed]

        if isinstance(parsed, list):
            points: Trajectory = []
            for item in parsed:
                if isinstance(item, (list, tuple)):
                    point = _normalize_point(item)
                    if point is not None:
                        points.append(point)
            if points:
                return points[:max_points] if max_points else points

    # Fallback regex parser for slightly malformed model outputs.
    points = []
    for match in _PAIR_RE.finditer(candidate):
        points.append((float(match.group(1)), float(match.group(2))))
        if max_points and len(points) >= max_points:
            break

    return points or None
