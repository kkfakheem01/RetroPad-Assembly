from __future__ import annotations

from pathlib import Path

from ._stl_utils import REPO_DIR, find_input_stl, stl_to_main_shape


def build() -> object:
    """Build the RetroPad Button (exact STL reference)."""
    stl_path = find_input_stl("button")
    return stl_to_main_shape(stl_path)


def main() -> Path:
    from build123d import export_stl

    out_dir = REPO_DIR / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "RetroPad_Button_build123d.stl"

    export_stl(build(), str(out_path))
    return out_path


if __name__ == "__main__":
    main()

