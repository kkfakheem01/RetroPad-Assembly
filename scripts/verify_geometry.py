from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ._stl_utils import REPO_DIR, find_input_stl, stl_to_main_shape


@dataclass(frozen=True)
class VerificationResult:
    name: str
    ref_volume: float
    cand_volume: float
    volume_delta: float
    symdiff_volume: float


def _shape_volume(shape: object) -> float:
    if hasattr(shape, "volume"):
        return float(getattr(shape, "volume"))
    # Some boolean operations may return a ShapeList; sum contained volumes.
    if hasattr(shape, "__iter__"):
        total = 0.0
        for item in shape:  # type: ignore[assignment]
            if hasattr(item, "volume"):
                total += float(getattr(item, "volume"))
        return float(total)
    raise AttributeError(f"Object has no volume: {type(shape).__name__}")


def _bool_diff(a: object, b: object) -> object | None:
    try:
        return a - b  # type: ignore[operator]
    except Exception:
        return None


def symmetric_difference_volume(a: object, b: object) -> float:
    """
    Compute symmetric-difference volume.

    For solids, this can be computed as:
      V(A △ B) = V(A) + V(B) - 2 * V(A ∩ B)

    This is typically faster than computing both differences for complex shapes.
    """
    va = _shape_volume(a)
    vb = _shape_volume(b)
    try:
        inter = a & b  # type: ignore[operator]
    except Exception:
        # Fall back to differences if intersection isn't available.
        ab = _bool_diff(a, b)
        ba = _bool_diff(b, a)
        vab = 0.0 if ab is None else _shape_volume(ab)
        vba = 0.0 if ba is None else _shape_volume(ba)
        return float(vab + vba)
    vi = 0.0 if inter is None else _shape_volume(inter)
    return float(max(0.0, va + vb - 2.0 * vi))


def verify_part(
    *,
    name: str,
    reference_contains: str,
    candidate_builder: Callable[[], object],
    volume_tol: float = 0.0,
    symdiff_tol: float = 0.0,
) -> VerificationResult:
    ref_path = find_input_stl(reference_contains)
    ref = stl_to_main_shape(ref_path)
    cand = candidate_builder()

    ref_v = _shape_volume(ref)
    cand_v = _shape_volume(cand)
    dv = abs(ref_v - cand_v)
    sym = symmetric_difference_volume(ref, cand)

    if dv > volume_tol:
        raise AssertionError(
            f"{name}: volume mismatch (ref={ref_v:.9g}, cand={cand_v:.9g}, |Δ|={dv:.9g})"
        )
    if sym > symdiff_tol:
        raise AssertionError(f"{name}: symmetric-difference volume non-zero: {sym:.9g}")

    return VerificationResult(
        name=name,
        ref_volume=ref_v,
        cand_volume=cand_v,
        volume_delta=dv,
        symdiff_volume=sym,
    )


def main() -> None:
    # Convenience: verify all four parts when run directly.
    from .retropad_bottom_shell import build as build_bottom
    from .retropad_button import build as build_button
    from .retropad_dpad import build as build_dpad
    from .retropad_top_shell import build as build_top

    results = [
        verify_part(
            name="Bottom Shell",
            reference_contains="bottom shell",
            candidate_builder=build_bottom,
        ),
        verify_part(
            name="Top Shell",
            reference_contains="top shell",
            candidate_builder=build_top,
        ),
        verify_part(
            name="D-Pad",
            reference_contains="d-pad",
            candidate_builder=build_dpad,
        ),
        verify_part(
            name="Button",
            reference_contains="button",
            candidate_builder=build_button,
        ),
    ]

    out_dir = REPO_DIR / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "verification_results.txt"
    lines = []
    for r in results:
        lines.append(
            f"{r.name}: vol(ref)={r.ref_volume:.9g}, vol(cand)={r.cand_volume:.9g}, "
            f"|Δ|={r.volume_delta:.9g}, symdiff={r.symdiff_volume:.9g}"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_path.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()

