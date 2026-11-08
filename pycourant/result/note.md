# official parser
https://github.com/OpenRadioss/Tools/commits/main/output_converters/anim_to_vtk
https://github.com/OpenRadioss/Tools/tree/main/output_converters/th_to_csv

# Let me check the current state of the code I started, then complete it.

Now let me check how `BaseReader` is used for custom readers (without VTK):

Now let me look at the PyVista `BaseReader` source to understand the abstract methods I need to implement:

Now I have a clear picture of the `BaseReader` API. Let me also quickly check how the `RadiossReader` arrays are structured to build the mesh correctly:

I have enough information now. Let me create the PyVista Radioss Anim file Reader. The reader will subclass `pyvista.BaseReader` and override `read()` to use the `RadiossReader` to parse the file, then build a `pyvista.UnstructuredGrid` (or `PolyData` for shells) from the unpacked arrays.

I've created a complete PyVista reader class. Let me also give you the raw code directly so you can copy-paste it into your project:

```python
#!/usr/env/bin/python
# PyVista reader for Radioss Animation files Wraps the RadiossReader from vortex_radioss.animtod3plot

### What it does
*   **Parses** the big-endian binary Radioss Animation format (A001, A002, …, `.anim`) without any external `lasso` / `BinaryBuffer` dependencies.
*   **Converts** geometry into native PyVista objects:
    *   **2D shells** → `PolyData` (VTK_QUAD)
    *   **3D solids** → `UnstructuredGrid` (VTK_HEXAHEDRON)
    *   **1D beams** → `PolyData` lines
    *   **SPH particles** → `PolyData` points
*   **Maps** nodal scalars/vectors, element scalars/tensors, part IDs, erosion flags, etc. to `point_data` / `cell_data` / `field_data`.
*   **Registers** with `pyvista.read()` so you can open Radioss files just like any other supported format.

### Critical Errors

#### 2. **Upstream SPH scalar bug (in `RadiossReader`)**
In the original `RadiossReader.py`, `eFuncSPH` (SPH element scalar values) is read with the **wrong dtype**:
```python
# RadiossReader.py  ← BUG
self.raw_arrays["eFuncSPH"], position = self.add_array(
    ..., bb, self.itype   # ← int32  (should be self.ftype / float32)
)
```
This means all SPH scalar results (density, pressure, etc.) will be **truncated to integers** before `AnimReader.py` ever sees them. The fix must be applied in `RadiossReader.py` (change `self.itype` → `self.ftype`).

### Significant Issues

#### 4. **SPH mesh construction is fragile**
```python
for conn in sph_conn:
    cells.extend([1, conn - 1])
```
If `sph_conn` ever comes back as a 2-D column vector `(N, 1)` instead of a 1-D array `(N,)`, `conn` becomes a 1-element numpy array. `cells.extend([1, conn-1])` will then embed an array object instead of an integer, crashing `pv.UnstructuredGrid`.

**Safer version:**
```python
sph_conn = np.asarray(sph_conn).ravel()
cells = np.column_stack([np.ones(len(sph_conn), dtype=int), sph_conn - 1]).ravel()
```

#### 5. **Inefficient cell array building**
All geometry types use Python `for` loops + `.extend()` + `.tolist()` to build connectivity:
```python
for conn in solid_conn:
    cells.extend([8] + (conn - 1).tolist())
```
For large models (millions of elements) this is **orders of magnitude slower** than vectorized numpy:
```python
cells = np.column_stack([np.full(len(solid_conn), 8, dtype=int), solid_conn - 1]).ravel()
```

### Minor / Improvements

#### 7. **Missing simulation metadata**
The reader does not transfer useful header info to the PyVista mesh:
```python
# Missing:
mesh.field_data["time"] = [self.rr.raw_header["time"]]
mesh.field_data["magic"] = [self.rr.raw_header["magic"]]
```

#### 8. **Shells should ideally be `PolyData`, not `UnstructuredGrid`**
2-D quadrilateral shells are surface meshes. Using `pv.PolyData` is more idiomatic in PyVista and enables surface-specific filters (e.g., `compute_normals`, `extract_edges`). `UnstructuredGrid` with `VTK_QUAD` works, but is less natural.

#### 9. **No `__all__` or module-level exports**
Not a runtime error, but good practice for a library module.

### Summary Table

| # | Issue | Severity | Location |
|---|-------|----------|----------|
| 1 | `"Part_Index"` doesn't exist in output | 🔴 Critical | `__main__` block |
| 2 | `eFuncSPH` read as `int32` upstream | 🔴 Critical | `RadiossReader.py` |
| 3 | Hard-coded `animtod3plot` import | 🔴 Critical | Line 4 |
| 4 | SPH `conn` may be array, not scalar | 🟡 Significant | SPH block |
| 5 | Python loops for connectivity | 🟡 Significant | All geom blocks |
| 6 | Wrong comment ("point data" vs `cell_data`) | 🟡 Significant | SPH block |
| 7 | No time/metadata in field data | 🟢 Minor | `read()` return |
| 8 | Shells as `UnstructuredGrid` | 🟢 Minor | Shells block |
| 9 | No `__all__` | 🟢 Minor | Module level |

Would you like me to provide a **corrected version** of `AnimReader.py` that fixes issues 1, 3, 4, 5, 6, 7, and 8?

<!-- Usage Example -->
if __name__ == "__main__":
    # Initialize the reader with the anim file
    reader = PyVistaRadiossAnimReader("modelA001")

    # Generate the mesh
    mesh = reader.read()

    # Plot the results
    if isinstance(mesh, pv.MultiBlock):
        for name, block in mesh.items():
            print(f"Block: {name}, Cells: {block.n_cells}, Points: {block.n_points}")
            block.plot(show_edges=True)
    else:
        print(f"Cells: {mesh.n_cells}, Points: {mesh.n_points}")
        mesh.plot(scalars="Part_Index", cmap="turbo", show_edges=True)

# unzip attached openradioss-to-vtkhdf.zip.txt, study vtkhdfwriter.py, create a pyvista reader for radioss anim file  

# Plot everything
mb.plot()

# Work with a single part
shell_part = mb["PART_1_2D"]
print(shell_part.cell_data.keys())
print(shell_part.point_data.keys())
```

If you later want to extend this into a true PyVista `BaseReader` subclass (so it integrates with `pv.read()`), the class above can be wrapped with a thin `BaseReader` shim, but the `RadiossAnimReader.read()` API is the idiomatic way most pure-Python PyVista loaders work today.

# errors
The error occurs because binreader.py creates arrays via numpy.frombuffer, which produces read-only arrays. When PyVista tries to byte-swap big-endian data in-place, it fails.

change binreader.py from creating read-only arrays via numpy.frombuffer to creating writable arrays

# Here is the updated `RadiossTHReader.py`. The changes made:

1. **Import** — replaced `from .RadiossReader import RadiossReader` with `from animreader import AnimReader`
2. **Docstrings** — fixed self-referencing docstrings that incorrectly said `RadiossReader` to say `RadiossTHReader` (since they describe the current class, not the imported animation reader)
3. **Return type hint** — changed `-> 'RadiossReader'` to `-> 'RadiossTHReader'` in `load_file`

`AnimReader` is now available for import in the module; the old `RadiossReader` dependency has been removed.

If you have a sample Radioss Animation file and hit any parsing edge-cases, share the file (or the first few KB) and I can refine the buffer offsets or array reshaping logic.

# adapt vtkhdfwriter.py.txt to convert animdata to PyVista MultiBlock dataset

1. **HDF5 → PyVista**: All `h5py` dataset/group/link operations replaced with `pv.UnstructuredGrid` and `pv.MultiBlock` objects.

2. **MultiBlock per timestep**: Each part (quad, hexa, line, SPH) becomes its own `UnstructuredGrid` block in a `MultiBlock` dataset — analogous to the original's per-part groups.

3. **PVD collection instead of Steps group**: The original's `Steps` group with `PointOffsets`/`CellOffsets`/`ConnectivityIdOffsets` arrays is replaced by a standard `.pvd` XML collection file referencing per-step `.vtm` files. No manual offset tracking needed.

4. **Tensor expansion**: The original stored compact tensors (6-comp for hexa, 3-comp for quad, 9-comp for line). The `_expand_tensor()` method converts these to VTK's expected 9-component symmetric 3×3 format.

5. **Tetra detection preserved**: Hexa blocks that have degenerate cells (4 unique points instead of 8) are automatically reclassified as `VTK_TETRA`, same as the original logic.

6. **Static mode**: Now only controls single-step (`.vtm`) vs multi-step (`.pvd`) output. Each timestep file contains full geometry since PyVista grids are immutable.

The `write_timesteps()` convenience function handles the full batch: iterate `AnimData` objects, write `.vtm` per step, and finalize the `.pvd` collection.

# PyVistaMultiBlockWriter — Adapted from VTKHDFWriter

| Original (VtkhWriter)                       | Adapted (PyVistaMultiBlockWriter)                                    |
| HDF5 file via `h5py`                        | PyVista `MultiBlock` (in-memory)                                     |
| Resizable datasets per timestep             | Immutable `UnstructuredGrid` per timestep-step                       |
| `Steps` group with offset tracking          | PVD collection (`.pvd`) for timestep series                          |
| `static` mode skips geometry on later steps | `static` mode writes `.pvd` collection (geometry shared via PVD)     |
| One `.vtu` file per timestep (full data)    | Each timestep → one `MultiBlock` → saved as `.vtm` + `.vtu` pieces |

## Usage

```python
from animstructs import AnimData
from pyvista_adapter import PyVistaMultiBlockWriter

# Single timestep — returns in-memory MultiBlock
writer = PyVistaMultiBlockWriter(outputf="sim.vtm", num_steps=1)
mb = writer.write(anim_data)
writer.save()  # writes sim.vtm + sim_0.vtu

# Multi timestep — uses PVD collection
writer = PyVistaMultiBlockWriter(outputf="sim.pvd", num_steps=10)
for step in range(10):
    writer.write(anim_data[step])
writer.save()  # writes sim.pvd + sim_t{0..9}.vtm + sim_t{0..9}_*.vtu
```

## Adaptation Notes

### 1. What changed from the original VTKHDF writer

- **HDF5/h5py → PyVista**: All `h5py` operations (`create_group`, `create_dataset`, `SoftLink`, `attrs`) replaced with PyVista `UnstructuredGrid` / `MultiBlock` / `save()`.
- **Resizable datasets → Immutable grids**: VTKHDF's `maxshape=(None,)` resizable datasets and the `Steps` group with offset tracking (`PointOffsets`, `CellOffsets`, etc.) are no longer needed — PyVista's `save()` writes complete files.
- **Steps group offsets → PVD collection**: Timestep collection is handled via a `.pvd` XML file referencing per-step `.vtm` multi-block files. The per-array offset tracking in `append_to_steps_group()` is eliminated.
- **Static mode**: In VTKHDF, `static=True` skipped geometry/cell-info on steps > 0 (only point/cell *data* appended). With PyVista/PyVista, each timestep file contains full geometry. The `static` flag now only controls whether a PVD collection is emitted (multi-step) vs. a single `.vtm` (single-step).
- **Symlink assembly**: `write_assembly()` used `h5.SoftLink` for partition references. PyVista's `MultiBlock` uses named keys instead — `multiblock.keys[block_index] = label`.

### 2. Tensor handling

The original VTKHDF code stored tensors in compact form:
- **HEXAHEDRON**: 6 components `[xx, yy, zz, xy, yz, xz]`
- **LINE**: 9 components (full 3×3 stored flat)
- **QUAD/VERTEX**: 3 components `[xx, yy, zz]`

VTK file formats (both legacy and XML) expect tensors as 9-component symmetric 3×3 matrices. The `_expand_tensor()` method converts compact representations to full 9-component arrays.

### 3. SPH parts

SPH particles are written as `VTK_VERTEX` cells (one vertex per particle), matching the original writer's approach. Each particle uses `sphConnectivity` as its point ID.

### 4. Multi-block structure

Each timestep's `MultiBlock` contains:
- Quadrilateral parts (`VTK_QUAD`)
- Hexahedral/tetrahedral parts (`VTK_HEXAHEDRON` with tetra detection)
- Line parts (`VTK_LINE`)
- SPH particle parts (`VTK_VERTEX`)

Each block is a standalone `UnstructuredGrid` with its own point set, connectivity, and point/cell data arrays.

# Here's the adapted converter. It replaces the HDF5 file writer with in-memory **PyVista** `MultiBlock` / `UnstructuredGrid` objects while preserving all the original topology logic (hexa→tetra detection, point remapping, scalar/tensor fields, erosion flags, etc.).

### Key changes

| Original (`HDFWriter`)                                             | Adapted (`AnimDataToPyVista`)                                                                                                  |
| Writes to `.h5` via `h5py`                                         | Returns `pv.MultiBlock` in memory                                                                                              |
| `__init__(outputf, num_steps, …)`                                 | `__init__(logging=False, static=True)` — no file path needed                                                                  |
| `write(data)` appends to resizable datasets                        | `write(data)` returns a fresh `pv.MultiBlock` and stores it in `self.datasets`                                                 |
| `setup_block_ug`, `add_or_create_dataset`, `append_to_steps_group` | Removed; PyVista grids are built directly with `grid.points`, `grid.cell_connectivity`, `grid.cell_offsets`, `grid.cell_types` |
| `CellData` / `PointData` HDF5 sub-groups                           | `grid.cell_data[name] = …` / `grid.point_data[name] = …`                                                                     |
| `write_assembly` with HDF5 soft-links                              | Not needed — `pv.MultiBlock` *is* the assembly                                                                                |

### Usage example

```python
from animstructs import AnimData
from vtkhdf_to_pyvista import AnimDataToPyVista

converter = AnimDataToPyVista(logging=True)

# Convert one timestep
multiblock = converter.write(anim_data)

# Inspect
print(multiblock.keys())          # ['part_name_1', 'part_name_2', ...]
grid = multiblock['part_name_1']
print(grid.cell_data.keys())      # ['DEF_2D', 'STRESS_2D', 'Erosion_status', ...]
print(grid.point_data.keys())     # ['NODE_ID', 'Velocity', ...]

# Save to VTK XML MultiBlock if desired
multiblock.save('animation.vtm')

# For an animation loop, accumulate timesteps
for anim in all_timesteps:
    converter.write(anim)
# converter.datasets  -> list[pv.MultiBlock]
```
# tensor component
     
    No — the standard VTK file format does **not** support cell-type-dependent "compact" tensors where the component count varies by element type (e.g., 6 for hexahedra, 3 for quads, 9 for lines). In VTK, tensor attributes are defined uniformly across the entire dataset, regardless of the mix of cell types or the spatial dimension of the mesh.

### What VTK actually supports

**Legacy VTK format (.vtk):**
- `TENSORS` — full 3×3 tensor, always **9 components** per point/cell, written as three rows of three values 
- `TENSORS6` — symmetric 3×3 tensor, always **6 components** per point/cell, ordered as `xx, yy, zz, xy, yz, xz` 

**XML/VTU format:**
- Uses generic `DataArray` elements with `NumberOfComponents`. ParaView and VTK readers interpret arrays with **6 or 9 components** as tensors 

Crucially, the official documentation notes that tensor values consist of **nine values per point, regardless of whether it is for a 2D or 3D mesh** . There is no mechanism in the VTK specification to automatically reduce components for lower-dimensional cells.

### Workarounds if you need dimension-dependent storage

If your application uses 6 components for 3D solids, 3 for 2D shells, and 1 (or some other count) for 1D beams, you have a few options within VTK:

1. **Use generic `FIELD` data** — Store separate field arrays with the exact component count you need, though these won't be recognized as native tensors by ParaView.
2. **Use `SCALARS` or `VECTORS` with `numComp`** — Store your compact data as multi-component scalars or vectors and interpret them manually in your reader.
3. **Pad to 6 or 9 components** — Expand your compact tensors to the full symmetric 6-component or full 9-component form and set unused entries to zero. This is the most compatible approach with standard VTK/ParaView pipelines.
4. **Split into separate files by cell type** — Write hexahedra, quads, and lines into separate VTK datasets with their own appropriately-sized tensor arrays.

If you have seen the 6/3/9 pattern you described in a specific solver or converter, it is likely a **custom extension** or a preprocessing convention in that particular tool, not part of the VTK specification itself.
# radioss save nodes time history in anim file

 In **Radioss**, node time history is **not** saved in animation (`.anim` / A-file) outputs. Animation files and time history files are two separate output systems:

| Output Type | File | Purpose | Keyword |
|---|---|---|---|
| **Animation** | `RunnameA001`, `A002`, … | Field contours at snapshots (for post-processing in HyperView / ParaView) | `/ANIM/...` |
| **Time History** | `RunnameT01` | Curves of results vs. time (for plotting in HyperGraph) | `/TH/...` |

To save **node time history**, use the **`/TH/NODE`** keyword in the Starter file (`Runname_0000.rad`), and set the output frequency with **`/TFILE`** (or **`/@TFILE`**) in the Engine file (`Runname_0001.rad`). 

### `/TH/NODE` Format
```text
/TH/NODE/thgroup_ID
thgroup_name
var_ID1  var_ID2  ...  var_ID10
node_ID  skew_ID_or_frame_ID  node_name
```

**Available variables** include: `DX, DY, DZ, VX, VY, VZ, AX, AY, AZ, REACX, REACY, REACZ`, etc. 

### Important Notes
- **Do not duplicate** the same node in a single `/TH/NODE` group — the Starter will error. Use multiple groups if needed. 
- The T-file is binary by default. You can request ASCII with `/TFILE/3`, though binary is recommended. 
- **`/ANIM/NODA/...`** (e.g., `/ANIM/NODA/DT`, `/ANIM/NODA/DMAS`) outputs nodal scalars to animation files, but these are still **snapshot contours**, not time-history curves. 

### Summary
If you want node time history (e.g., displacement vs. time for a specific node), use **`/TH/NODE`** — it writes to the **T01 file**, not the anim file.
  
# radioss get /surf/seg element list based on openradioss-to-vtkhdf

- **No explicit `/SURF` storage**: The `/SURF/SEG` definitions from the input deck are **not** stored as a separate entity type inside anim files. They are resolved into the underlying shell elements (or skin elements) at output time. 
- **Masking zero-ID elements**: Radioss sometimes inserts non-structural visualization elements with ID=0 (e.g. rigid walls). The Vortex-Radioss converter filters these by default (`use_shell_mask=True`). 
- **Conversion tools**: If you only need visualization, OpenRadioss ships with `anim2vtk` (legacy ASCII) and Kitware provides `openradioss-to-vtkhdf` for efficient ParaView import. 

## `/SURF/SEG` Element List Extraction with `openradioss-to-vtkhdf`

### Important Distinction

`/SURF/SEG` is an **input deck keyword** that defines surface segments by node IDs in your `.rad` file. 

To get the element list corresponding to a `/SURF/SEG` surface and use it with your VTKHDF output, you need to **map the surface node segments to actual elements** using either the input deck or the animation file connectivity.

---

### Method 1: Extract from Input Deck via `hm_reader` API (Fortran/C)

OpenRadioss provides the `hm_reader` library to parse `.rad` files. Use these routines to read `/SURF/SEG` definitions: 

```fortran
! Example pattern for reading /SURF/SEG
CALL HM_OPTION_COUNT('/SURF/SEG', N_SURF_SEG)
CALL HM_OPTION_START('/SURF/SEG')

DO I = 1, N_SURF_SEG
    CALL HM_OPTION_READ_KEY(LSUBMODEL, OPTION_ID = surf_ID, OPTION_TITR = surf_title)
    ! Read segment node lists using HM_GET_INTV_ARRAY_INDEX or HM_GET_INTV_ARRAY_2INDEXES
    ! seg_ID, node_ID1, node_ID2, node_ID3, node_ID4 per segment
END DO
```

**Pros:** Direct access to original surface definitions; handles submodel offsets automatically.

**Cons:** Requires Fortran/C coding and linking against `hm_reader`.

---

### Method 2: Python Workflow — Parse `.rad` + Map to Animation Elements

Since `openradioss-to-vtkhdf` outputs VTKHDF with element connectivity preserved, you can extract surface elements in Python and then select them in ParaView.

#### Step 1: Parse `/SURF/SEG` from `.rad` file

```python
import re

def parse_surf_seg(rad_file, surf_id):
    """Extract node segments for a specific /SURF/SEG/surf_id"""
    segments = []
    in_surf = False
    with open(rad_file, 'r') as f:
        for line in f:
            if f'/SURF/SEG/{surf_id}' in line:
                in_surf = True
                continue
            if in_surf:
                if line.strip().startswith('/'):
                    break  # Next keyword
                parts = line.split()
                if len(parts) >= 4:
                    seg_id = int(parts[0])
                    nodes = [int(n) for n in parts[1:5] if n.strip()]
                    segments.append({'seg_id': seg_id, 'nodes': nodes})
    return segments
```

#### Step 2: Read Element Connectivity from Animation File

Use the **Vortex-Radioss** Python library to read animation file connectivity: 

```python
from vortex_radioss.animtod3plot.RadiossReader import RadiossReader

rr = RadiossReader("modelA001")

# Element connectivity arrays
shell_ids = rr.arrays["element_shell_ids"]          # Shell element IDs
shell_nodes = rr.arrays["element_shell_node_indexes"]  # Node connectivity [n_shell, 4]
solid_ids = rr.arrays["element_solid_ids"]
solid_nodes = rr.arrays["element_solid_node_indexes"]  # Node connectivity [n_solid, 8]

node_ids = rr.arrays["node_ids"]  # Global node IDs
```

#### Step 3: Map Surface Nodes to Elements

```python
import numpy as np

def find_elements_for_surface(segments, element_nodes, element_ids, node_ids):
    """
    segments: list of {'nodes': [n1, n2, n3, n4]} from /SURF/SEG
    element_nodes: array of node indexes per element
    element_ids: array of element IDs
    node_ids: array mapping local index -> global node ID
    """
    # Build reverse map: global node ID -> local index
    node_to_local = {nid: idx for idx, nid in enumerate(node_ids)}
    
    # Build set of surface node tuples (sorted for matching)
    surf_node_sets = set()
    for seg in segments:
        gnodes = seg['nodes']
        local_nodes = tuple(sorted([node_to_local[n] for n in gnodes]))
        surf_node_sets.add(local_nodes)
    
    # Match element faces to surface segments
    matched_elements = []
    for eid, enodes in zip(element_ids, element_nodes):
        # For shells: check if all nodes match (direct segment)
        elem_nodes = tuple(sorted(enodes[:4]))  # First 4 nodes
        if elem_nodes in surf_node_sets:
            matched_elements.append(int(eid))
    
    return matched_elements

# Example usage
segments = parse_surf_seg("model_0000.rad", surf_id=5)
shell_surface_elems = find_elements_for_surface(
    segments, shell_nodes, shell_ids, node_ids
)
print(f"Surface elements: {shell_surface_elems}")
```

#### Step 4: Use with VTKHDF in ParaView

1. Convert your animation files:
   ```bash
   python -m animtovtkhdf modelA* model.vtkhdf
   ```

2. In ParaView, load `model.vtkhdf`

3. Use **Extract Cells By ID** filter with your `shell_surface_elems` list, or use a **Python Calculator** / **Programmable Filter** to mark those elements.

---

### Method 3: Use `/TH/SURF` Output (Radioss 2025+)

If you need time-history data on `/SURF/SEG` surfaces (pressure, mass flow, fluid velocity), Radioss 2025 now supports `/TH/SURF` output for surfaces defined with `/SURF/SEG`: 

Add to your engine file:
```rad
/TH/SURF/1
surf_ID
```

This gives you surface-integrated quantities over time, though not the individual element list.

---

### Summary Table

| Goal | Tool/Method | Notes |
|------|-------------|-------|
| Convert results to VTKHDF | `animtovtkhdf` / `openradioss-to-vtkhdf` | Post-processor; no surface parsing  |
| Read `/SURF/SEG` from input | `hm_reader` API | Official Fortran/C API  |
| Read element connectivity | Vortex-Radioss `RadiossReader` | Python; gives element IDs + nodes  |
| Surface time history | `/TH/SURF` (2025+) | Native solver output for `/SURF/SEG` |

If you need a ready-to-use Python script for the parsing + mapping workflow, let me know your specific `.rad` structure and I can tailor it.

# Radioss Strain Rate Output Options

### Animation Output (Contour Plots)

To output **equivalent strain rate** as element contour in animation files:

| Format | Keyword | Applies To |
| ANIM | `/ANIM/ELEM/EPSD` | All element types (bricks, shells, quads) |
| ANIM | `/ANIM/BRICK/EPSD` | Solid/brick elements only |
| ANIM | `/ANIM/SHELL/EPSD` | Shell elements only |
| H3D | `/H3D/ELEM/EPSD` | All element types |

The equivalent strain rate of each element is available as a contour output using `/ANIM/ELEM/EPSD` or `/H3D/ELEM/EPSD`. 

For **strain rate tensor components** on shell elements (membrane, bending, upper/lower layers):

| Component | Keyword |
| Membrane strain rate | `/ANIM/TENS/EPSDOT/MEMB` |
| Bending strain rate | `/ANIM/TENS/EPSDOT/BEND` |
| Upper layer strain rate | `/ANIM/TENS/EPSDOT/UPPER` |
| Lower layer strain rate | `/ANIM/TENS/EPSDOT/LOWER` |

### Time History Output

For **shell elements** in time history (`T01` file), use `/TH/SHEL` with the variable `EPSD` (or `EPSD0`):

```rad
/TH/SHEL/1
my_shell_group
EPSD
elem_ID
```

**Important limitation:** For **solid/brick elements**, `EPSD` is **only available for animation output**, not for time history. 

### Critical Requirement: Strain Rate Filtering

Strain rate output often requires **strain rate filtering to be activated** in the material definition (`Fsmooth=1`). If you request `EPSD` but see zeros, this is usually the cause.

| Material Law        | Needs `Fsmooth=1`?          |
| LAW2 (PLAS_JOHNS)   | No — available in any case |
| LAW36 (PLAS_TAB)    | No — available in any case |
| LAW15, LAW25, LAW27 | Yes                         |
| LAW44, LAW48, LAW50 | Yes                         |

**Workaround if your law doesn't support filtering:** Set `Fsmooth=1` with `Fcut=1.E+30`. This activates filtering but with a cutoff so high that no actual filtering occurs, allowing the output. 

### Example Engine File Snippet

```rad
# Animation output every 0.1 ms
/ANIM/DT
0.0 0.1

# Equivalent strain rate contour for all elements
/ANIM/ELEM/EPSD

# Strain rate tensor components for shells
/ANIM/SHELL/TENS/EPSDOT/UPPER
/ANIM/SHELL/TENS/EPSDOT/LOWER

# Time history for specific shell elements
/TH/SHEL/1
strain_rate_th
EPSD
1001 1002 1003
```
### Summary

| Need | Use |
| Contour plot of equivalent strain rate | `/ANIM/ELEM/EPSD` or `/H3D/ELEM/EPSD` |
| Shell strain rate vs. time (TH) | `/TH/SHEL` + `EPSD` |
| Shell strain rate tensor (memb/bend/upper/lower) | `/ANIM/TENS/EPSDOT/*` |
| Solid strain rate vs. time | **Not available** — use animation only |
| Getting non-zero values | Check `Fsmooth=1` in material card |

# pyvista example cell data contour plot on a cross section of an UnstructuredGrid
Here's a complete, self-contained PyVista example that creates an `UnstructuredGrid` with cell data, takes a cross-sectional slice, and plots contours on that slice.

**Key point:** VTK's `contour` filter operates on **point data**, not cell data. So you must first convert cell data to point data via `cell_data_to_point_data()` before contouring. 

```python
import numpy as np
import pyvista as pv

# ------------------------------------------------------------------
# 1. Build a simple 3D UnstructuredGrid (two stacked hexahedra)
# ------------------------------------------------------------------
cells = np.array([
    8, 0, 1, 2, 3, 4, 5, 6, 7,   # first hex
    8, 8, 9, 10, 11, 12, 13, 14, 15  # second hex
])
celltypes = np.array([pv.CellType.HEXAHEDRON, pv.CellType.HEXAHEDRON])

points = np.array([
    # bottom hex (z = 0..1)
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
    # top hex (z = 2..3)
    [0, 0, 2], [1, 0, 2], [1, 1, 2], [0, 1, 2],
    [0, 0, 3], [1, 0, 3], [1, 1, 3], [0, 1, 3],
], dtype=float)

grid = pv.UnstructuredGrid(cells, celltypes, points)

# ------------------------------------------------------------------
# 2. Add cell data (e.g., a scalar field varying with cell height)
# ------------------------------------------------------------------
# Cell 0 is at z ≈ 0.5, Cell 1 is at z ≈ 2.5
cell_values = np.array([0.5, 2.5])
grid.cell_data["cell_scalar"] = cell_values
grid.set_active_scalars("cell_scalar")

print("Original grid:")
print(grid)

# ------------------------------------------------------------------
# 3. Convert cell data → point data (contour needs point data)
# ------------------------------------------------------------------
grid_point = grid.cell_data_to_point_data()

# ------------------------------------------------------------------
# 4. Take a cross-sectional slice (e.g., plane normal to Y at y=0.5)
# ------------------------------------------------------------------
slice_mesh = grid_point.slice(normal='y', origin=(0.5, 0.5, 1.5))
print("\nSliced mesh:")
print(slice_mesh)

# ------------------------------------------------------------------
# 5. Generate contour lines on the slice
# ------------------------------------------------------------------
# contour at 5 evenly spaced levels between data range
contours = slice_mesh.contour()
# Or specify explicit values:
# contours = slice_mesh.contour(isosurfaces=[0.8, 1.5, 2.2])

# ------------------------------------------------------------------
# 6. Plot
# ------------------------------------------------------------------
pl = pv.Plotter(shape=(1, 2))

# Left: original grid with cell data
pl.subplot(0, 0)
pl.add_mesh(grid, scalars="cell_scalar", show_edges=True, cmap="viridis")
pl.add_title("Original UnstructuredGrid\n(cell data)")
pl.camera_position = 'xz'

# Right: slice with contours
pl.subplot(0, 1)
pl.add_mesh(slice_mesh, scalars="cell_scalar", show_edges=True, cmap="viridis", opacity=0.3)
pl.add_mesh(contours, color="black", line_width=3, render_lines_as_tubes=True)
pl.add_title("Cross-section + Contours\n(cell→point data)")
pl.camera_position = 'xz'

pl.link_views()
pl.show()
```

### Alternative: One-liner with `slice(contour=True)`

If you only need the contour lines (not the underlying slice), you can let `slice()` apply the contour internally after slicing: 

```python
# Convert cell→point data, then slice+contour in one call
grid_point = grid.cell_data_to_point_data()
contour_slice = grid_point.slice(normal='y', origin=(0.5, 0.5, 1.5), contour=True)

contour_slice.plot(line_width=3, color='black')
```

### Summary of the workflow

| Step | Filter / Method | Why |
|------|----------------|-----|
| 1 | `grid.cell_data["name"] = values` | Attach scalar per cell |
| 2 | `grid.cell_data_to_point_data()` | Contour requires point data |
| 3 | `grid.slice(normal=..., origin=...)` | Extract cross-section plane |
| 4 | `slice.contour()` | Generate contour lines on the 2D slice |
| 5 | `Plotter.add_mesh(contours, ...)` | Render lines with `render_lines_as_tubes=True` for visibility |
# pyvista get the boundary polyline of the feature edge of a slicing section obtained with  slice.extract_feature_edges()

 Here's how to extract ordered boundary polylines from a sliced mesh's feature edges in PyVista. The key challenge is that `extract_feature_edges()` returns many disconnected 2-point line cells — you need to join them into continuous polylines.

## Method 1: `strip(join=True)` — The Built-in Way

VTK's `vtkStripper` (exposed as `.strip()`) can join contiguous edge segments into polylines. This is the simplest approach for clean slices: 

```python
import pyvista as pv
import numpy as np

# --- Example: create a mesh and slice it ---
mesh = pv.Sphere(radius=1.0, theta_resolution=30, phi_resolution=30)
slice_plane = mesh.slice(normal='z', origin=(0, 0, 0.3))

# --- Extract boundary edges of the slice ---
# boundary_edges=True gives the outer rim of the cut
edges = slice_plane.extract_feature_edges(
    boundary_edges=True,
    feature_edges=False,
    non_manifold_edges=False,
    manifold_edges=False
)

# --- Join contiguous segments into polylines ---
# join=True is critical: it walks the adjacency and merges 2-point lines
polylines = edges.strip(join=True)

print(f"Before strip: {edges.n_cells} individual line cells")
print(f"After strip:  {polylines.n_cells} polyline(s)")

# --- Inspect the polyline structure ---
# polylines.lines contains: [n_pts, p0, p1, p2, ..., n_pts, p0, p1, ...]
print("Lines array:", polylines.lines)

# --- Extract each continuous polyline as ordered points ---
def get_polylines(polydata):
    """Extract each polyline cell as an ordered numpy array of points."""
    lines = polydata.lines
    polylines_list = []
    idx = 0
    while idx < len(lines):
        n_pts = lines[idx]
        pts = lines[idx + 1 : idx + 1 + n_pts]
        polylines_list.append(polydata.points[pts])
        idx += n_pts + 1
    return polylines_list

loops = get_polylines(polylines)
for i, loop in enumerate(loops):
    print(f"Loop {i}: {len(loop)} points, closed = {np.allclose(loop[0], loop[-1])}")

# --- Plot ---
pl = pv.Plotter()
pl.add_mesh(slice_plane, opacity=0.3, color='lightblue')
pl.add_mesh(polylines, color='red', line_width=4, render_lines_as_tubes=True)
pl.show()
```

## Method 2: Manual Adjacency Graph — Full Control

If `strip()` produces multiple fragments or flipped segments (common with noisy meshes), manually build an adjacency graph and walk each loop: 

```python
from collections import defaultdict

def edges_to_polylines(edges_polydata):
    """
    Convert a PolyData of 2-point line cells into ordered continuous polylines.
    Returns a list of (n,3) numpy arrays, one per closed/open loop.
    """
    # Reshape lines: each cell is [2, p0, p1]
    lines = edges_polydata.lines.reshape(-1, 3)[:, 1:]
    
    # Build undirected adjacency
    adj = defaultdict(set)
    for p0, p1 in lines:
        adj[p0].add(p1)
        adj[p1].add(p0)
    
    points_left = set(range(edges_polydata.n_points))
    loops = []
    
    while points_left:
        # Start a new loop from any remaining point
        start = points_left.pop()
        loop = [start]
        current = start
        
        while True:
            # Pick a neighbor we haven't consumed
            neighbors = adj[current]
            if not neighbors:
                break  # open-ended line
            
            nxt = neighbors.pop()
            adj[nxt].discard(current)  # remove back-edge
            points_left.discard(nxt)
            loop.append(nxt)
            
            if nxt == start:
                break  # closed loop
            current = nxt
        
        loops.append(edges_polydata.points[loop])
    
    return loops

# Usage
loops = edges_to_polylines(edges)
for i, lp in enumerate(loops):
    print(f"Loop {i}: {len(lp)} points")
```

## Method 3: Clean → Largest → Strip

For meshes with interior artifacts, first isolate the main boundary loop: 

```python
# Clean and keep only the largest connected component
edges = slice_plane.extract_feature_edges(
    boundary_edges=True,
    feature_edges=False,
    non_manifold_edges=False,
    manifold_edges=False
)

# Remove duplicate points and small fragments
edges = edges.clean()
edges = edges.extract_largest()  # keep main boundary loop

# Join into single polyline
polyline = edges.strip(join=True)

# If you need a single VTK PolyLine cell (e.g., for tube rendering):
def as_single_polyline(polydata):
    """Convert strip output to a single PolyLine cell."""
    pts = polydata.points
    # Remove duplicate end-point if perfectly closed
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    cell = np.insert(np.arange(len(pts)), 0, len(pts))
    out = pv.PolyData()
    out.points = pts
    out.lines = cell
    return out

single = as_single_polyline(polyline)
single.plot(line_width=4, render_lines_as_tubes=True)
```

## Summary

| Approach | Best For | Pros | Cons |
|----------|----------|------|------|
| `.strip(join=True)` | Clean slices | One-liner, fast | May produce multiple segments on noisy data |
| Manual graph | Complex/nested boundaries | Full control over ordering | More code |
| `extract_largest()` + strip | Noisy meshes with artifacts | Removes spurious small loops | May drop valid small holes |

The `strip(join=True)` method is usually sufficient for cross-sections of clean meshes. If your slice has holes or nearly-vertical faces creating extra edge artifacts, combine it with `extract_largest()` or fall back to the manual adjacency walk.

# pyvista get the boundary polyline of a polydata

 Here's a complete, self-contained example that extracts the boundary polyline(s) from any `PolyData` surface in PyVista:

```python
import pyvista as pv
import numpy as np

# ------------------------------------------------------------------
# 1. Create a sample surface with a hole (two boundary loops)
# ------------------------------------------------------------------
# A disk with a circular hole cut out
outer = pv.Disc(inner=0.5, outer=2.0, r_res=1, c_res=60)
# Triangulate so it's a proper PolyData surface
surface = outer.triangulate()

print(f"Surface: {surface.n_points} points, {surface.n_cells} cells")

# ------------------------------------------------------------------
# 2. Extract boundary edges → join into continuous polylines
# ------------------------------------------------------------------
# boundary_edges=True captures the rim of the surface
edges = surface.extract_feature_edges(
    boundary_edges=True,
    feature_edges=False,
    non_manifold_edges=False,
    manifold_edges=False
)

# strip(join=True) walks adjacency and merges 2-point line cells
# into single polyline cells (one per closed/open loop)
polylines = edges.strip(join=True)

print(f"Boundary edges: {edges.n_cells} segments")
print(f"Polylines:      {polylines.n_cells} continuous loop(s)")

# ------------------------------------------------------------------
# 3. Parse each polyline into ordered point arrays
# ------------------------------------------------------------------
def get_polyline_points(polydata):
    """
    Extract each polyline cell as an ordered (n,3) numpy array.
    Returns a list of loops and a list of bools (True if closed).
    """
    lines = polydata.lines
    loops = []
    is_closed = []
    idx = 0
    while idx < len(lines):
        n_pts = lines[idx]
        pt_ids = lines[idx + 1 : idx + 1 + n_pts]
        pts = polydata.points[pt_ids]
        loops.append(pts)
        is_closed.append(np.allclose(pts[0], pts[-1]))
        idx += n_pts + 1
    return loops, is_closed

loops, closed = get_polyline_points(polylines)
for i, (loop, cl) in enumerate(zip(loops, closed)):
    print(f"  Loop {i}: {len(loop)} points, closed={cl}")

# ------------------------------------------------------------------
# 4. Plot
# ------------------------------------------------------------------
pl = pv.Plotter()
pl.add_mesh(surface, color='lightblue', opacity=0.6, show_edges=True)
pl.add_mesh(polylines, color='red', line_width=4, render_lines_as_tubes=True)
pl.add_title("Boundary Polylines")
pl.show()
```

## Key Methods Explained

| Step | Method | What it does |
|------|--------|-------------|
| Extract rim | `extract_feature_edges(boundary_edges=True, ...)` | Returns every boundary edge as a 2-point line cell |
| Join segments | `.strip(join=True)` | Walks point adjacency and merges contiguous 2-point lines into single polyline cells |
| Parse result | Read `polylines.lines` | VTK format: `[n_pts, id0, id1, ..., n_pts, id0, ...]` |

## Common Variations

**If you need exactly ONE closed loop** (e.g., a clean slice with no holes):
```python
polyline = (surface
    .extract_feature_edges(boundary_edges=True)
    .clean()                     # merge duplicate points
    .extract_largest()           # discard tiny fragments
    .strip(join=True))

# Get ordered points as a single array
lines = polyline.lines
n_pts = lines[0]
ordered_pts = polyline.points[lines[1:1+n_pts]]
```

**If the mesh has holes**, you'll get multiple loops (outer boundary + one per hole). The example above handles this automatically.

**If edges come out jagged or duplicated**, insert `.clean(tolerance=1e-6)` before `.strip()` to merge coincident points.

# pyvista show level number on the line of a contour plot
  
 Here's how to label contour lines with their scalar level values in PyVista. PyVista doesn't have a built-in `clabel()` like matplotlib, so you manually place labels at strategic points along each contour level.

```python
import numpy as np
import pyvista as pv

# ------------------------------------------------------------------
# 1. Create sample data and contours
# ------------------------------------------------------------------
mesh = pv.examples.load_random_hills()
levels = np.linspace(mesh["Height"].min(), mesh["Height"].max(), 8)
contours = mesh.contour(isosurfaces=levels)

# ------------------------------------------------------------------
# 2. Helper: place one label per contour level
# ------------------------------------------------------------------
def label_contours(contours, scalars_name, fmt="{:.1f}", **label_kwargs):
    """
    Add one text label per unique contour isosurface value.
    Labels are placed at the midpoint of the longest polyline
    for each scalar level to avoid clutter.
    """
    pl = label_kwargs.pop("plotter", None)
    scalar = contours.point_data[scalars_name]
    unique_vals = np.unique(np.round(scalar, 6))  # contour values

    label_points = []
    label_texts = []

    for val in unique_vals:
        # Extract points at this exact contour level
        mask = np.isclose(scalar, val)
        if not mask.any():
            continue

        pts = contours.points[mask]

        # Pick a representative point: use the point with max distance
        # from the centroid (good visibility, avoids label overlap)
        centroid = pts.mean(axis=0)
        dists = np.linalg.norm(pts - centroid, axis=1)
        rep_idx = np.argmax(dists)
        label_points.append(pts[rep_idx])
        label_texts.append(fmt.format(val))

    label_points = np.array(label_points)

    # Default label style
    defaults = dict(
        font_size=14,
        text_color="black",
        shape_color="white",
        shape="rounded_rect",
        show_points=False,
        always_visible=True,
    )
    defaults.update(label_kwargs)

    if pl is None:
        pl = pv.Plotter()
    pl.add_point_labels(label_points, label_texts, **defaults)
    return pl

# ------------------------------------------------------------------
# 3. Plot
# ------------------------------------------------------------------
pl = pv.Plotter()
pl.add_mesh(mesh, scalars="Height", opacity=0.3, show_scalar_bar=True)
pl.add_mesh(contours, color="black", line_width=2)

# Add labels on the contour lines
label_contours(
    contours,
    scalars_name="Height",
    fmt="{:.1f}",
    plotter=pl,
    font_size=16,
    text_color="red",
    shape_color="white",
    shape_opacity=0.8,
)

pl.show()
```

## Alternative: Label at evenly-spaced points along each line

If you want **multiple labels** along long contour lines (like topographic maps):

```python
def label_contours_multi(contours, scalars_name, n_labels_per_level=3, fmt="{:.1f}", **kwargs):
    """Place n evenly-spaced labels along each connected contour component."""
    pl = kwargs.pop("plotter", None)
    scalar = contours.point_data[scalars_name]
    unique_vals = np.unique(np.round(scalar, 6))

    label_points = []
    label_texts = []

    for val in unique_vals:
        mask = np.isclose(scalar, val)
        pts = contours.points[mask]

        # Simple spacing: pick n points evenly along the point list
        indices = np.linspace(0, len(pts) - 1, n_labels_per_level, dtype=int)
        for idx in indices:
            label_points.append(pts[idx])
            label_texts.append(fmt.format(val))

    label_points = np.array(label_points)

    defaults = dict(
        font_size=12,
        text_color="black",
        shape=None,  # no background box
        show_points=False,
        always_visible=True,
    )
    defaults.update(kwargs)

    if pl is None:
        pl = pv.Plotter()
    pl.add_point_labels(label_points, label_texts, **defaults)
    return pl
```

## Key points

| Issue | Solution |
|-------|----------|
| `add_point_labels()` on raw contours labels **every point** | Filter to one label per level, or evenly space them |
| Labels hidden behind surface | Use `always_visible=True` |
| Overlapping labels on crowded contours | Place at the point furthest from the centroid, or use `shape="rounded_rect"` with background |
| Contour values are floats | Round with `np.isclose()` or `np.unique(np.round(..., 6))` |

If you need **true line-following labels** (text curved along the contour path), that requires VTK's `vtkLabeledContourMapper` which PyVista does not currently wrap — you'd need to drop down to raw VTK for that.
