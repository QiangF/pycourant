"""PyVista adapter for AnimData → MultiBlock (UnstructuredGrid blocks).

Adapted from vtkhdfwriter.py which wrote VTK-HDF5 format.
This version outputs PyVista datasets.
"""
from typing import Any, Optional
import numpy as np
import os, re
import pyvista as pv
from .animstructs import AnimData

# ── VTK cell types ──────────────────────────────────────────────
vtk_cell_types={
    'vertex': 1,
    'line': 3,
    'quad': 9,
    'hexa': 12,
    'tetra': 10
}

vtk_cell_dimension={
    'vertex': 0,
    'line': 1,
    'quad': 2,
    'hexa': 3,
    'tetra': 3
}

# num points from vtk cell type
vtk_cell_num_points={
    1: 1,
    3: 2,
    9: 4,
    12: 8,
    10: 4
}

# ── Tensor component counts per VTK cell type ───────────────────
vtk_cell_tensor_sizes={
    'vertex': 3,
    'line': 9,
    'quad': 3,
    'tetra': 6,
    'hexa': 6
}

# Symmetric tensor index maps
# For tensors stored as [xx, yy, zz, xy, yz, xz] → full 3x3 matrix
TENSOR_SYMM_6IDX = np.array([
    [0, 3, 5],  # xx, xy, xz
    [3, 1, 4],  # xy, yy, yz
    [5, 4, 2],  # xz, yz, zz
], dtype=int)

TENSOR_SYMM_9IDX = np.array([
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
], dtype=int)

ID_TYPE = np.int32
FLOAT_TYPE = np.float32
CHAR_TYPE = np.uint8

def animdata_to_multiblock(data: AnimData) -> pv.MultiBlock:
    """Convert a single AnimData timestep to a MultiBlock dataset.
    if a part has cells of different dimensions, each dimension is saved separately, name format is partname_dim"""
    multiblock = pv.MultiBlock()

    for cell_type in ['quad','hexa','line']:
        vtk_type=vtk_cell_types[cell_type]
        cell_data=getattr(data, cell_type+'s')
        part_names=getattr(cell_data, cell_type+'PartNames')

        for blockId in range(len(part_names)):
            grid = get_geom_part(
                data=data,
                cell_type=cell_type,
                cell_data=cell_data,
                vtk_type=vtk_type,
                block_id=blockId,
                part_name=part_names[blockId])

            if grid is not None:
                label = extract_part_name(part_names[blockId])
                multiblock.append(grid)
                multiblock.set_block_name(len(multiblock)-1,label)

    # SPH (particles as vertices)
    for sph_part_id in range(len(data.sph.partText)):
        grid = get_sph_part(data, sph_part_id)
        if grid is not None:
            label = extract_part_name(data.sph.partText[sph_part_id])
            multiblock.append(grid)
            multiblock.set_block_name(len(multiblock)-1,label)

    return multiblock

def get_sph_part(data: AnimData, sph_part_id: int) -> Optional[pv.UnstructuredGrid]:
    """Write SPH particle part as an UnstructuredGrid."""
    part_name = data.sph.partText[sph_part_id]

    part_point_ids = data.sph.sphConnectivity
    num_pts = len(part_point_ids)
    if num_pts == 0:
        return None

    # Points — all SPH particles map to their own coordinates
    coordinates = data.nodes.nodeCoordinates
    # FIXED
    coords_2d = coordinates.reshape(-1, 3)  # (N_nodes, 3)
    point_coords = coords_2d[part_point_ids].astype(np.float32)  # clean (N, 3) array

    # Cells: each particle is a vtk_cell_types['vertex'] (1 point)
    # Connectivity: [1, 0, 1, 1, 1, 2, ...] — one cell per vertex
    connectivity = np.empty(num_pts * 2, dtype=ID_TYPE)
    offsets = np.empty(num_pts + 1, dtype=ID_TYPE)
    types = np.full(num_pts, vtk_cell_types['vertex'], dtype=CHAR_TYPE)

    for i in range(num_pts):
        connectivity[i * 2] = 1       # num points in cell
        connectivity[i * 2 + 1] = i   # point index
        offsets[i] = i * 2
    offsets[num_pts] = num_pts * 2

    grid = pv.UnstructuredGrid(connectivity, types, point_coords)

    # Point data
    grid.point_data["NODE_ID"] = part_point_ids.astype(ID_TYPE)

    for array_id in range(len(data.sph.scalText)):
        array_name = data.sph.scalText[array_id]
        values = data.sph.eFunc[
            num_pts * array_id : num_pts * (array_id + 1)
        ]
        grid.point_data[f"SPH_{array_name}"] = values.astype(FLOAT_TYPE)

    # Cell data
    grid.cell_data["Erosion_status"] = data.sph.sphDeletedElems.astype(np.int8)

    grid.cell_data["Part_ID"] = (
        get_part_id_from_name(part_name),
    ) * num_pts
    grid.cell_data["Part_ID"] = np.full(num_pts, get_part_id_from_name(part_name), dtype=ID_TYPE)

    return grid

def get_geom_part(
    data: AnimData,
    cell_type: str,
    cell_data,
    vtk_type: int,
    block_id: int,
    part_name: str,
) -> Optional[pv.UnstructuredGrid]:
    """Write a geometry part (quad/hexa/line) as a PyVista UnstructuredGrid."""

    parts_last_indices=getattr(cell_data, cell_type+'PartLastIndices')
    connectivity=getattr(cell_data, cell_type+'Connectivity')
    scalar_array_names=getattr(cell_data, cell_type+'ScalarArrayNames')
    scalar_arrays=getattr(cell_data, cell_type+'ScalarArrays')
    tensor_array_names=getattr(cell_data, cell_type+'TensorArrayNames')
    tensor_arrays=getattr(cell_data, cell_type+'TensorArrays')
    erosion_array=getattr(cell_data, cell_type+'ErosionArray')
    radioss_ids_array=getattr(cell_data, cell_type+'RadiossIDs')

    first_cell_index = 0 if block_id == 0 else parts_last_indices[block_id - 1]
    last_cell_index = parts_last_indices[block_id] - 1
    num_cells = last_cell_index - first_cell_index + 1
    if num_cells < 0:
        print(f"Warning: incorrect first ({first_cell_index}) & last ({last_cell_index}) cell indices, skipping block {part_name}")
        return None

    num_points_per_cell = vtk_cell_num_points[vtk_type]
    coordinates = data.nodes.nodeCoordinates

    # Extract connectivity for this part's cells
    part_connectivity = connectivity[
        num_points_per_cell * first_cell_index : num_points_per_cell * (last_cell_index + 1)
    ]

    all_types = []
    all_connectivity = []
    tetra_count = 0
    for cell_id in range(num_cells):
        cell_connect = part_connectivity[cell_id * num_points_per_cell : (cell_id + 1) * num_points_per_cell]
        if vtk_type == vtk_cell_types['hexa']:
            # Detect tetras within hexas (degenerate: 4 unique points)
            unique = np.unique(cell_connect)
            if len(unique) == 4:
                vtk_type = vtk_cell_types['tetra']
                all_types.append()
                tetra_count += 1
                cell_connect = unique
        all_types.append(vtk_type)
        all_connectivity.append(cell_connect.tolist())
    print(f"\tFound {tetra_count} tetras / {num_cells} cells")
    all_connectivity = np.array(all_connectivity, dtype=ID_TYPE)
    all_types = np.array(all_types, dtype=CHAR_TYPE)

    # Get unique point IDs used by this part
    part_point_ids = np.unique(all_connectivity[:])

    # Build a local point set (deduplicated)
    coords_2d = coordinates.reshape(-1, 3)  # (N_nodes, 3)
    point_coords = coords_2d[part_point_ids].astype(np.float32)  # clean (N, 3) array

    # Remap connectivity from Radioss IDs to local 0-based indices
    radioss_to_vtk = {pid: i for i, pid in enumerate(part_point_ids)}
    cell_connectivity=[]
    for i in range(len(all_types)):
        num_points_per_cell = vtk_cell_num_points[all_types[i]]
        connectivity=[radioss_to_vtk[pid] for pid in all_connectivity[i]]
        cell_connectivity.extend([num_points_per_cell]+connectivity)

    grid = pv.UnstructuredGrid(
        cell_connectivity,
        all_types,
        point_coords,
    )
    grid.add_field_data(radioss_to_vtk, 'radioss_node_ids', False)

    # ── Cell data ────────────────────────────────────────────
    # Scalar arrays
    for array_id in range(len(scalar_array_names)):
        array_name = scalar_array_names[array_id]
        values = np.asarray(scalar_arrays[array_id])[first_cell_index : last_cell_index + 1]
        grid.cell_data[f"{array_name}"] = values.astype(FLOAT_TYPE)

    # Tensor arrays
    for array_id in range(len(tensor_array_names)):
        tensor_name = tensor_array_names[array_id]
        size = vtk_cell_tensor_sizes[cell_type]
        raw = np.asarray(tensor_arrays[array_id])
        tensor_data = raw[first_cell_index * size : (last_cell_index + 1) * size]
        reshaped = tensor_data.reshape(-1, size)

        # Expand to symmetric 3x3 (9 components) for VTK compatibility
        full_tensors = expand_tensor(reshaped)
        grid.cell_data[f"{tensor_name}"] = full_tensors.astype(FLOAT_TYPE)

    # Erosion status
    grid.cell_data["Erosion_status"] = erosion_array[
        first_cell_index : last_cell_index + 1
    ].astype(np.int8)

    # Part ID
    grid.cell_data["Part_ID"] = np.full(
        num_cells, get_part_id_from_name(part_name), dtype=ID_TYPE
    )

    # Element IDs
    if data.global_params.isNodeNumberingElementSaved:
        grid.cell_data["Element_ID"] = radioss_ids_array[
            first_cell_index : last_cell_index + 1
        ].astype(ID_TYPE)

    # ── Point data ───────────────────────────────────────────
    grid.point_data["NODE_ID"] = part_point_ids.astype(ID_TYPE)

    for array_id in range(len(data.nodes.nodeScalarArrayNames)):
        array_name = data.nodes.nodeScalarArrayNames[array_id]
        values = [
            data.nodes.nodeScalarArrays[array_id][pid]
            for pid in part_point_ids
        ]
        grid.point_data[array_name] = np.array(values, dtype=FLOAT_TYPE)

    for array_id in range(len(data.nodes.nodeVectorArrayNames)):
        vec_name = data.nodes.nodeVectorArrayNames[array_id]
        vec_size = vtk_cell_tensor_sizes['vertex']
        values = [
            data.nodes.nodeVectorArrays[array_id][pid * vec_size : (pid + 1) * vec_size]
            for pid in part_point_ids
        ]
        grid.point_data[vec_name] = np.array(values, dtype=FLOAT_TYPE)
    return grid

# ── Tensor helpers ──────────────────────────────────────────
def expand_tensor(tensor_comp: np.ndarray) -> np.ndarray:
    """Expand compact tensor representation to full 9-component 3x3 symmetric matrix.

    VTK legacy/XML format expects 9 components per tensor (3x3).
    The input array has:
      - 6 components for HEXAHEDRON: [xx, yy, zz, xy, yz, xz]
      - 3 components for QUAD/VERTEX: [xx, yy, zz]
      - 9 components for LINE: full 3x3 (stored as flat)
    """
    num_cells = tensor_comp.shape[0]

    if tensor_comp.shape[1] == 9:
        return tensor_comp  # Already full 3x3

    full = np.zeros((num_cells, 9), dtype=FLOAT_TYPE)

    if tensor_comp.shape[1] == 6:
        # [xx, yy, zz, xy, yz, xz]
        full[:, 0] = tensor_comp[:, 0]  # t00 = xx
        full[:, 4] = tensor_comp[:, 1]  # t11 = yy
        full[:, 8] = tensor_comp[:, 2]  # t22 = zz
        full[:, 1] = tensor_comp[:, 3]  # t01 = xy
        full[:, 5] = tensor_comp[:, 4]  # t12 = yz
        full[:, 2] = tensor_comp[:, 5]  # t02 = xz
        full[:, 3] = tensor_comp[:, 3]  # t10 = xy (symmetric)
        full[:, 7] = tensor_comp[:, 4]  # t21 = yz (symmetric)
        full[:, 6] = tensor_comp[:, 5]  # t20 = xz (symmetric)

    elif tensor_comp.shape[1] == 3:
        # [xx, yy, zz] — diagonal only
        full[:, 0] = tensor_comp[:, 0]
        full[:, 4] = tensor_comp[:, 1]
        full[:, 8] = tensor_comp[:, 2]

    return full

def get_part_id_from_name(part_name: str) -> int:
    name = part_name.strip()
    count = 0
    while count < len(name) and name[count].isdecimal():
        count += 1
    return int(name[:count]) if count > 0 else 0

def extract_part_name(part_name: str) -> str:
    # remove ":"
    if len(part_name.split(":")) == 2:
        id, name = part_name.split(":")
        part_name = f"{name}_{id}"

    clean_name = re.sub(r'[^.\-0-9A-Z_a-z]', '', part_name)

    if not clean_name:
        clean_name='block_unnamed'

    return clean_name
