"""
PyVista reader for OpenRadioss ANIM animation files.

Depends on the companion modules from openradioss-to-vtkhdf:
    animstructs.py, animreader.py, binreader.py

Example
-------
>>> import pyvista as pv
>>> from radioss_reader import read_radioss_anim
>>> mesh = read_radioss_anim("modelA001")
>>> mesh.plot()
"""

from __future__ import annotations

import numpy as np
import pyvista as pv

from .animstructs import AnimData
from .animreader import AnimReader

# -----------------------------------------------------------------------------
# VTK cell type constants
# -----------------------------------------------------------------------------
VTK_VERTEX = 1
VTK_LINE = 3
VTK_QUAD = 9
VTK_TETRA = 10
VTK_HEXAHEDRON = 12

# Tensor component counts per topology (matches vtkhdfwriter.py)
_TENSOR_SIZE = {
    VTK_VERTEX: 3,
    VTK_LINE: 9,
    VTK_QUAD: 3,
    VTK_HEXAHEDRON: 6,
    VTK_TETRA: 6,
}

_DIM = {
    VTK_VERTEX: 0,
    VTK_LINE: 1,
    VTK_QUAD: 2,
    VTK_TETRA: 3,
    VTK_HEXAHEDRON: 3,
}


def _safe(arr: np.ndarray) -> np.ndarray:
    """Return a writable copy of an array (needed because frombuffer arrays are read-only)."""
    if not arr.flags.writeable:
        return arr.copy()
    return arr


def read_radioss_anim(filename: str) -> pv.MultiBlock:
    """Read a Radioss ANIM file into a PyVista MultiBlock dataset.

    Parameters
    ----------
    filename : str
        Path to the Radioss ANIM file.

    Returns
    -------
    pyvista.MultiBlock
        MultiBlock dataset containing one ``pyvista.UnstructuredGrid`` per
        part (quads, hexas/tetras, lines, SPH).
    """
    reader = RadiossAnimReader(filename)
    return reader.read()


class RadiossAnimReader:
    """PyVista-compatible reader for a single Radioss ANIM file."""

    def __init__(self, filename: str):
        self.filename = filename
        self._data: AnimData | None = None

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def read(self) -> pv.MultiBlock:
        """Parse the ANIM file and return a ``pyvista.MultiBlock``."""
        if self._data is None:
            self._data = AnimReader(self.filename).read()
        return self._to_multiblock(self._data)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _to_multiblock(self, data: AnimData) -> pv.MultiBlock:
        blocks = pv.MultiBlock()

        # --- 2D quads --------------------------------------------------------
        for i in range(data.nodes_quads_params.numberOfQuadParts):
            grid = self._extract_quad_part(data, i)
            if grid.n_cells:
                name = (
                    data.quads.quadPartNames[i]
                    if i < len(data.quads.quadPartNames)
                    else f"QuadPart_{i}"
                )
                blocks[name] = grid

        # --- 3D hexas / tetras -----------------------------------------------
        for i in range(data.hexahedra_params.numberOfhexaParts):
            grid = self._extract_hexa_part(data, i)
            if grid.n_cells:
                name = (
                    data.hexas.hexaPartNames[i]
                    if i < len(data.hexas.hexaPartNames)
                    else f"HexaPart_{i}"
                )
                blocks[name] = grid

        # --- 1D lines --------------------------------------------------------
        for i in range(data.lines_params.numberOfLineParts):
            grid = self._extract_line_part(data, i)
            if grid.n_cells:
                name = (
                    data.lines.linePartNames[i]
                    if i < len(data.lines.linePartNames)
                    else f"LinePart_{i}"
                )
                blocks[name] = grid

        # --- SPH -------------------------------------------------------------
        for i in range(len(data.sph.partText)):
            grid = self._extract_sph_part(data, i)
            if grid.n_points:
                name = (
                    data.sph.partText[i]
                    if i < len(data.sph.partText)
                    else f"SPHPart_{i}"
                )
                blocks[name] = grid

        return blocks

    # -------------------------------------------------------------------------
    # Geometry extractors
    # -------------------------------------------------------------------------
    def _extract_quad_part(self, data: AnimData, block_id: int) -> pv.UnstructuredGrid:
        first, last, n_cells = self._part_range(
            data.quads.quadPartLastIndices, block_id
        )
        if n_cells <= 0:
            return pv.UnstructuredGrid()

        conn = data.quads.quadConnectivity[4 * first : 4 * (last + 1)]
        unique_pts = np.unique(conn)
        mapping = {int(old): new for new, old in enumerate(unique_pts)}
        points = data.nodes.nodeCoordinates.reshape(-1, 3)[unique_pts]

        cells = np.empty(n_cells * 5, dtype=np.int64)
        cells[0::5] = 4
        for i in range(n_cells):
            cells[1 + 5 * i : 5 + 5 * i] = [
                mapping[int(c)] for c in conn[4 * i : 4 * i + 4]
            ]

        grid = pv.UnstructuredGrid(
            cells, np.full(n_cells, VTK_QUAD, dtype=np.uint8), points
        )
        self._attach_cell_data(
            grid,
            data.quads.quadScalarArrayNames,
            data.quads.quadScalarArrays,
            data.quads.quadTensorArrayNames,
            data.quads.quadTensorArrays,
            data.quads.quadErosionArray,
            data.quads.quadRadiossIDs,
            first,
            last,
            VTK_QUAD,
        )
        self._attach_point_data(grid, data, unique_pts)
        grid.field_data["Time"] = [data.global_params.time]
        return grid

    def _extract_hexa_part(self, data: AnimData, block_id: int) -> pv.UnstructuredGrid:
        first, last, n_cells = self._part_range(
            data.hexas.hexaPartLastIndices, block_id
        )
        if n_cells <= 0:
            return pv.UnstructuredGrid()

        conn = data.hexas.hexaConnectivity[8 * first : 8 * (last + 1)]
        cell_arrays = []
        types = []
        all_nodes = set()

        for i in range(n_cells):
            c = conn[8 * i : 8 * (i + 1)]
            uniq = np.unique(c)
            if len(uniq) == 4:
                cell_arrays.append(uniq.astype(np.int64))
                types.append(VTK_TETRA)
                all_nodes.update(uniq)
            else:
                cell_arrays.append(c.astype(np.int64))
                types.append(VTK_HEXAHEDRON)
                all_nodes.update(c)

        unique_pts = np.array(sorted(all_nodes), dtype=np.int64)
        mapping = {int(old): new for new, old in enumerate(unique_pts)}
        points = data.nodes.nodeCoordinates.reshape(-1, 3)[unique_pts]

        cells = []
        for carr in cell_arrays:
            cells.append(len(carr))
            cells.extend(mapping[int(node)] for node in carr)
        cells = np.array(cells, dtype=np.int64)
        types = np.array(types, dtype=np.uint8)

        grid = pv.UnstructuredGrid(cells, types, points)
        self._attach_cell_data(
            grid,
            data.hexas.hexaScalarArrayNames,
            data.hexas.hexaScalarArrays,
            data.hexas.hexaTensorArrayNames,
            data.hexas.hexaTensorArrays,
            data.hexas.hexaErosionArray,
            data.hexas.hexaRadiossIDs,
            first,
            last,
            VTK_HEXAHEDRON,
        )
        self._attach_point_data(grid, data, unique_pts)
        grid.field_data["Time"] = [data.global_params.time]
        return grid

    def _extract_line_part(self, data: AnimData, block_id: int) -> pv.UnstructuredGrid:
        first, last, n_cells = self._part_range(
            data.lines.linePartLastIndices, block_id
        )
        if n_cells <= 0:
            return pv.UnstructuredGrid()

        conn = data.lines.lineConnectivity[2 * first : 2 * (last + 1)]
        unique_pts = np.unique(conn)
        mapping = {int(old): new for new, old in enumerate(unique_pts)}
        points = data.nodes.nodeCoordinates.reshape(-1, 3)[unique_pts]

        cells = np.empty(n_cells * 3, dtype=np.int64)
        cells[0::3] = 2
        for i in range(n_cells):
            cells[1 + 3 * i : 3 + 3 * i] = [
                mapping[int(c)] for c in conn[2 * i : 2 * i + 2]
            ]

        grid = pv.UnstructuredGrid(
            cells, np.full(n_cells, VTK_LINE, dtype=np.uint8), points
        )
        self._attach_cell_data(
            grid,
            data.lines.lineScalarArrayNames,
            data.lines.lineScalarArrays,
            data.lines.lineTensorArrayNames,
            data.lines.lineTensorArrays,
            data.lines.lineErosionArray,
            data.lines.lineRadiossIDs,
            first,
            last,
            VTK_LINE,
        )
        self._attach_point_data(grid, data, unique_pts)
        grid.field_data["Time"] = [data.global_params.time]
        return grid

    def _extract_sph_part(self, data: AnimData, sph_id: int) -> pv.UnstructuredGrid:
        if not data.sph.partText:
            return pv.UnstructuredGrid()

        # Determine element range for this SPH part
        if len(data.sph.defParts) > 0 and sph_id < len(data.sph.defParts):
            first = 0 if sph_id == 0 else int(data.sph.defParts[sph_id - 1])
            last = int(data.sph.defParts[sph_id]) - 1
            n_pts = max(0, last - first + 1)
            if n_pts <= 0:
                return pv.UnstructuredGrid()
            sph_nodes = data.sph.sphConnectivity[first : last + 1].astype(np.int64)
        else:
            # Fallback: all SPH elements (matches legacy vtkhdfwriter behaviour)
            n_pts = data.sph.sphConnectivity.shape[0]
            sph_nodes = data.sph.sphConnectivity.astype(np.int64)
            first, last = 0, n_pts - 1

        points = data.nodes.nodeCoordinates.reshape(-1, 3)[sph_nodes]

        cells = np.column_stack(
            [np.ones(n_pts, dtype=np.int64), np.arange(n_pts, dtype=np.int64)]
        ).ravel()

        grid = pv.UnstructuredGrid(
            cells, np.full(n_pts, VTK_VERTEX, dtype=np.uint8), points
        )

        # SPH scalar data (stored per-element; mapped to points because SPH == vertex)
        nb_elems_total = data.sph.sphConnectivity.shape[0]
        if data.sph.eFunc.size and data.sph.scalText:
            for array_id, name in enumerate(data.sph.scalText):
                start = array_id * nb_elems_total + first
                end = array_id * nb_elems_total + last + 1
                grid.point_data[f"SPH_{name}"] = _safe(data.sph.eFunc[start:end])

        # Erosion
        if data.sph.sphDeletedElems.size:
            grid.point_data["Erosion_status"] = _safe(
                data.sph.sphDeletedElems[first : last + 1]
            )

        # Node ID + nodal fields
        grid.point_data["NODE_ID"] = _safe(sph_nodes)
        self._attach_point_data(grid, data, sph_nodes)

        grid.field_data["Time"] = [data.global_params.time]
        return grid

    # -------------------------------------------------------------------------
    # Data attachment
    # -------------------------------------------------------------------------
    @staticmethod
    def _attach_cell_data(
        grid: pv.UnstructuredGrid,
        scalar_names: list[str],
        scalar_arrays: np.ndarray,
        tensor_names: list[str],
        tensor_arrays: np.ndarray,
        erosion_array: np.ndarray,
        radioss_ids: np.ndarray,
        first: int,
        last: int,
        vtk_type: int,
    ) -> None:
        dim = _DIM[vtk_type]

        # Scalar cell data
        if scalar_arrays.size and scalar_names:
            for array_id, name in enumerate(scalar_names):
                grid.cell_data[f"{name}_{dim}D"] = _safe(
                    scalar_arrays[array_id][first : last + 1]
                )

        # Tensor cell data
        if tensor_arrays.size and tensor_names:
            n_comp = _TENSOR_SIZE[vtk_type]
            for array_id, name in enumerate(tensor_names):
                flat = tensor_arrays[array_id][first * n_comp : (last + 1) * n_comp]
                grid.cell_data[f"{name}_{dim}D"] = _safe(flat.reshape(-1, n_comp))

        # Erosion flag
        if erosion_array.size:
            grid.cell_data["Erosion_status"] = _safe(
                erosion_array[first : last + 1]
            )

        # Original Radioss element IDs
        if radioss_ids.size:
            grid.cell_data["Element_ID"] = _safe(
                radioss_ids[first : last + 1]
            )

    @staticmethod
    def _attach_point_data(
        grid: pv.UnstructuredGrid, data: AnimData, unique_pts: np.ndarray
    ) -> None:
        unique_pts = unique_pts.astype(np.int64)

        # Original node IDs
        grid.point_data["NODE_ID"] = _safe(unique_pts)

        # Node scalar arrays
        if data.nodes.nodeScalarArrays.size and data.nodes.nodeScalarArrayNames:
            for array_id, name in enumerate(data.nodes.nodeScalarArrayNames):
                grid.point_data[name] = _safe(
                    data.nodes.nodeScalarArrays[array_id][unique_pts]
                )

        # Node vector arrays (3 components per node)
        if data.nodes.nodeVectorArrays.size and data.nodes.nodeVectorArrayNames:
            n_comp = _TENSOR_SIZE[VTK_VERTEX]  # == 3
            flat = data.nodes.nodeVectorArrays  # shape (n_arrays, n_nodes*3)
            for array_id, name in enumerate(data.nodes.nodeVectorArrayNames):
                # Gather components for each requested node
                idx = np.column_stack(
                    [
                        unique_pts * n_comp,
                        unique_pts * n_comp + 1,
                        unique_pts * n_comp + 2,
                    ]
                ).ravel()
                vectors = flat[array_id][idx].reshape(-1, n_comp)
                grid.point_data[name] = _safe(vectors)

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------
    @staticmethod
    def _part_range(last_indices: np.ndarray, block_id: int) -> tuple[int, int, int]:
        """Return (first_cell, last_cell, n_cells) for a part block."""
        first = 0 if block_id == 0 else int(last_indices[block_id - 1])
        last = int(last_indices[block_id]) - 1
        n = last - first + 1
        return first, last, n
