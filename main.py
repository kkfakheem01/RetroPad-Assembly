"""
RetroPad assembly (build123d)
============================

Convenience entrypoint that exports the build123d-based assembly STL.

The canonical scripts live under `scripts/`:
- `scripts/retropad_assembly.py` (full assembly w/ 4-button diamond)
- `scripts/verify_geometry.py` (volume + symmetric-difference validation)
"""

from __future__ import annotations

from scripts.retropad_assembly import main


if __name__ == "__main__":
    main()