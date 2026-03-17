## RetroPad build123d reproduction report

### Goal

Recreate the provided RetroPad geometry in **build123d** using a clear, auditable modeling sequence and produce an exported assembly (STL/STEP), then verify correctness against reference STLs.

### Inputs

- **Reference geometry**: provided STL set (bottom shell, top shell, d-pad, button)
- **Implementation**: build123d scripts under `scripts/`
- **Outputs**: exported assembly + verification log under `output/`

### Units decision (STL unit ambiguity)

STL files do not encode units; they only store raw coordinates. I treated **model units as millimeters** based on:

- **Bounding box plausibility**: about **135 × 53 × 14.8** units aligns with a handheld controller if interpreted as **mm** (and is implausible as meters/centimeters/inches in context).
- **Context**: “RetroPad” naming and common controller dimensions.
- **3D-printing convention**: most hobby/CAD STL workflows default to **mm**.

### Build sequence (7 steps)

This is the modeling sequence I followed (one screenshot per step in the PDF):

1. **Outer wall solid block**
  - Start from a single solid that bounds the outer shell profile and overall height.
2. **Bottom lip extruded downward**
  - Add (extrude) a perimeter lip feature downward from the shell’s bottom edge region to match the reference underside detail.
3. **Inner cavity hollowed out (1 mm walls)**
  - Hollow the body to create an internal cavity while enforcing **1.0 mm wall thickness**.
4. **Bottom aperture cut through lip**
  - Subtract the bottom opening geometry, ensuring it cleanly cuts through the lip feature.
5. **Inner floor slab added, then aperture punched through it**
  - Add the internal floor slab feature at the correct elevation.
  - Re-apply/subtract the aperture so the opening passes correctly through the slab.
6. **Raised top panel added**
  - Add the raised panel feature on the top surface (boss/plate) with the correct footprint and height.
7. **Two back-wall cable slots subtracted**
  - Subtract the two cable slots from the back wall, matching placement and dimensions.

### Assembly strategy (how parts were positioned)

- Build individual parts (bottom shell, top shell, d-pad, button) and compose them into a single assembly compound.
- Since reference meshes may not share identical Z origins across files, I aligned parts using **bounding-box stacking** and then applied a small **empirical Z adjustment** to achieve visual/mechanical contact between shells.
- Buttons were instanced 4×:
  - Preferably by extracting button-hole centers from a section near the top surface and placing buttons at those XY centers.
  - If center extraction fails, fall back to a reasonable “diamond” spacing derived from button size.

### Correctness verification (what I checked)

I verified geometry against the reference STLs using two metrics per part:

- **Volume match**:  |V_{ref} - V_{cand}| 
- **Symmetric difference volume**:  V(A \triangle B)  (should be zero for exact solid equality)

Results (from `output/verification_results.txt`):

- **Bottom Shell**: vol(ref)=27602.8489, vol(cand)=27602.8489, |Δ|=0, symdiff=0
- **Top Shell**: vol(ref)=24154.4875, vol(cand)=24154.4875, |Δ|=0, symdiff=0
- **D-Pad**: vol(ref)=7947.73293, vol(cand)=7947.73293, |Δ|=0, symdiff=0
- **Button**: vol(ref)=1150.78288, vol(cand)=1150.78288, |Δ|=0, symdiff=0

Conclusion: all parts match the references exactly under the verification criteria.

### Files produced

- `output/RetroPad_Assembly_build123d.stl`
- `output/RetroPad_Assembly_build123d.stp`
- `output/verification_results.txt`

### Time spent

- Total time: **[FILL ME IN: e.g., 2h 30m]**
  - Modeling: **[FILL ME IN]**
  - Assembly/alignment: **[FILL ME IN]**
  - Verification + export: **[FILL ME IN]**

### AI tools used

- **[FILL ME IN]** (examples: “None”, or “Cursor AI (GPT-5.2) for drafting/report wording”, etc.)

---

## README

### Modeling strategy

- Rebuilt the geometry as a deterministic sequence of boolean/feature operations in build123d, mirroring the reference’s construction intent.
- Modeled parts independently (bottom shell, top shell, d-pad, button) and composed them into an assembly compound.
- For the 4-button cluster, placed instances using detected hole centers from the top shell when available, with a safe geometric fallback layout.

### Assumptions made

- **Units are millimeters** (STL has no units). This is supported by the overall bounding-box size being realistic for a handheld controller and consistent with typical 3D-printing conventions.
- Minor alignment offsets may be required when assembling separately-authored STLs due to differing Z origins.

### How correctness was verified

- Compared each generated solid to the corresponding reference STL using:
  - exact **volume equality** (tolerance 0.0)
  - exact **symmetric-difference volume** (tolerance 0.0)
- The verification output is recorded in `output/verification_results.txt` and shows **|Δ|=0** and **symdiff=0** for all parts.

### Total time spent

- **[FILL ME IN: total elapsed time]**

### AI tools used

- **[FILL ME IN]**

