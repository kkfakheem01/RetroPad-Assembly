from __future__ import annotations

from pathlib import Path

from ._stl_utils import REPO_DIR, as_compound
from .retropad_bottom_shell import build as build_bottom_shell
from .retropad_button import build as build_button
from .retropad_dpad import build as build_dpad
from .retropad_top_shell import build as build_top_shell


def _button_hole_centers_from_top(
    *,
    top_shape: object,
    btn_diameter: float,
) -> list[tuple[float, float]]:
    """
    Extract the 4 button-hole XY centers from the top cover by sectioning near the
    top surface and finding 4 near-circular loops of the expected size.
    """
    from build123d import Face, Plane, Part, Wire

    top = top_shape  # already positioned
    top_bb = top.bounding_box()

    # Section slightly below the top surface to capture the hole perimeters.
    z_section = float(top_bb.max.Z - 0.10)

    # Intersect with a large rectangular face in the XY plane.
    max_size = float(top_bb.diagonal) * 3.0
    sec_plane = Plane.XY
    sec_face = Face.make_rect(
        2 * max_size,
        2 * max_size,
        Plane(origin=sec_plane.origin + sec_plane.z_dir * z_section, z_dir=sec_plane.z_dir),
    )

    section_edges = Part(top.wrapped).intersect(sec_face)  # type: ignore[attr-defined]
    if section_edges is None:
        return []

    wires = Wire.combine(section_edges.edges())  # type: ignore[union-attr]

    # Filter to candidates sized like the button holes (exclude outer boundary and d-pad cutout)
    d_min = 0.60 * btn_diameter
    d_max = 1.60 * btn_diameter
    candidates: list[tuple[float, Wire]] = []
    for w in wires:
        bb = w.bounding_box()
        sx = float(bb.size.X)
        sy = float(bb.size.Y)
        if sx <= 0 or sy <= 0:
            continue
        if not (d_min <= sx <= d_max and d_min <= sy <= d_max):
            continue
        # "Circularity" score: closer to 1 means more circle-like.
        score = abs(sx - sy) / max(sx, sy)
        candidates.append((score, w))

    if len(candidates) < 4:
        return []

    candidates.sort(key=lambda t: t[0])
    picked = [w for _, w in candidates[:12]]  # keep a small pool of best circles

    # Buttons are on the right side of the controller; use that to disambiguate.
    right_side = []
    for w in picked:
        c = w.bounding_box().center()
        right_side.append((float(c.X), float(c.Y), w))
    right_side.sort(key=lambda t: t[0], reverse=True)

    chosen = right_side[:4]
    if len(chosen) != 4:
        return []

    # Stable ordering isn't required for geometry, but keep deterministic sort.
    chosen.sort(key=lambda t: (t[0], t[1]))
    return [(x, y) for x, y, _ in chosen]


def build() -> object:
    """
    RetroPad assembly as a build123d Compound.

    Notes:
    - The source STLs appear to share XY alignment but have different Z origins
      between top/bottom shells. We compute a Z offset from their bounding boxes
      so they stack correctly.
    - The repository provides one `RetroPad - Button.stl`; we instance it 4 times
      in a diamond layout.
    """
    from build123d import Axis, Compound, Location

    bottom = build_bottom_shell()
    top = build_top_shell()
    dpad = build_dpad()
    button = build_button()

    # Empirical alignment tweak:
    # Bounding-box stacking gets the parts "close", but the outer shell edges
    # still show a visible separation in section view. Nudge the bottom shell up
    # so the top shell's outer edge contacts it.
    bottom_z_adjust = 11.82375  # mm

    bottom_bb = bottom.bounding_box()
    top_bb = top.bounding_box()
    z_offset = float(bottom_bb.max.Z - top_bb.min.Z)

    bottom_pos = bottom.moved(Location((0, 0, bottom_z_adjust)))
    top_pos = top.moved(Location((0, 0, z_offset)))
    dpad_pos = dpad.moved(Location((0, 0, z_offset)))

    btn_bb = button.bounding_box()
    btn_center = btn_bb.center()
    btn_diameter = float(min(btn_bb.size.X, btn_bb.size.Y))
    btn_z_lift = 1.0  # mm

    # Move button so its bbox center is at origin, then place 4 instances.
    button_centered = button.moved(Location((-btn_center.X, -btn_center.Y, -btn_center.Z)))
    hole_centers = _button_hole_centers_from_top(top_shape=top_pos, btn_diameter=btn_diameter)
    if len(hole_centers) == 4:
        buttons = [
            button_centered.moved(Location((cx, cy, float(btn_center.Z) + z_offset + btn_z_lift)))
            for cx, cy in hole_centers
        ]
    else:
        # Fallback: Reasonable center-to-center spacing (mm) for a diamond of 4 buttons.
        offset = 0.9 * btn_diameter
        diamond_centers = [
            (btn_center.X + offset, btn_center.Y),
            (btn_center.X - offset, btn_center.Y),
            (btn_center.X, btn_center.Y + offset),
            (btn_center.X, btn_center.Y - offset),
        ]
        buttons = [
            button_centered.moved(Location((cx, cy, float(btn_center.Z) + z_offset + btn_z_lift)))
            for cx, cy in diamond_centers
        ]

    return Compound(
        label="RetroPad_Assembly",
        children=[
            as_compound([bottom_pos], label="Bottom_Shell"),
            as_compound([top_pos], label="Top_Shell"),
            as_compound([dpad_pos], label="D_Pad"),
            as_compound(buttons, label="Buttons"),
        ],
    )


def main() -> Path:
    from build123d import export_step, export_stl

    out_dir = REPO_DIR / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_stl = out_dir / "RetroPad_Assembly_build123d.stl"
    out_step = out_dir / "RetroPad_Assembly_build123d.stp"

    assy = build()
    export_stl(assy, str(out_stl))
    export_step(assy, str(out_step))
    return out_step


if __name__ == "__main__":
    main()

