from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable


REPO_DIR = Path(__file__).resolve().parents[1]

# This workspace vendors the build123d source under `./build123d/`.
# Add its `src/` to sys.path so `import build123d` resolves correctly.
VENDORED_BUILD123D_SRC = REPO_DIR / "build123d" / "src"
if VENDORED_BUILD123D_SRC.exists():
    sys.path.insert(0, str(VENDORED_BUILD123D_SRC))

from build123d import Compound, Mesher, Shape  # noqa: E402


def find_input_stl(contains: str, input_dir: Path | None = None) -> Path:
    """Find exactly one STL in `input/` whose name contains `contains`."""
    input_dir = input_dir or (REPO_DIR / "input")
    matches = sorted([p for p in input_dir.glob("*.stl") if contains.lower() in p.name.lower()])
    if not matches:
        available = "\n".join(f"  - {p.name}" for p in sorted(input_dir.glob("*")))
        raise FileNotFoundError(
            f"Couldn't find an STL in {input_dir} containing '{contains}'.\n"
            f"Available files:\n{available if available else '  (none)'}"
        )
    if len(matches) > 1:
        names = ", ".join(p.name for p in matches)
        raise FileExistsError(
            f"Found multiple STLs containing '{contains}': {names}\n"
            f"Please keep only one matching file in {input_dir}."
        )
    return matches[0]


def _bbox_volume(s: Shape) -> float:
    bb = s.bounding_box()
    sz = bb.size
    return float(sz.X * sz.Y * sz.Z)


def stl_to_shapes(path: str | Path) -> list[Shape]:
    """Convert STL triangles into build123d shapes (Shell/Solid) via Mesher."""
    mesher = Mesher()
    return mesher.read(str(path))


def stl_to_main_shape(path: str | Path) -> Shape:
    """Return the largest shape extracted from the STL."""
    shapes = stl_to_shapes(path)
    if not shapes:
        raise ValueError(f"No shapes extracted from STL: {path}")
    return max(shapes, key=_bbox_volume)


def as_compound(children: Iterable[Shape], label: str | None = None) -> Compound:
    comp = Compound(children=list(children))
    if label is not None:
        comp.label = label
    return comp

