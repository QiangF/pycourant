"""
PyVista MultiBlock converter adapted from vtkhdfwriter.py.txt.

Converts AnimData structures (quads, hexas/tetras, lines, SPH) into
PyVista MultiBlock / UnstructuredGrid datasets instead of writing
to an HDF5 file.

Usage:
    from animstructs import AnimData
    from vtkhdf_to_pyvista import AnimDataToPyVista

    converter = AnimDataToPyVista(logging=True)
    multiblock = converter.write(anim_data)   # pv.MultiBlock
"""
from typing import Any
import numpy as np
import pyvista as pv
from animstructs import AnimData

AUTHORIZED_CHARS = ".-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"

# VTK Types
VTK_VERTEX = 1
VTK_LINE = 3
VTK_QUAD = 9
VTK_HEXAHEDRON = 12
VTK_TETRA = 10

NUM_POINTS_PER_QUAD = 4
NUM_POINTS_PER_HEXA = 8
NUM_POINTS_PER_LINE = 2

# Number of components for each topology type in tensor arrays
VERTEX_TENSOR_SIZE = 3
LINE_TENSOR_SIZE = 9
QUAD_TENSOR_SIZE = 3
HEXA_TENSOR_SIZE = 6


class AnimDataToPyVista:
    """Convert AnimData structure to PyVista MultiBlock datasets.

    Call :meth:`write` for each timestep; it returns a fresh ``pv.MultiBlock``
    containing one ``pv.UnstructuredGrid`` per part (quads, hexas/tetras,
    lines, SPH).  All timesteps are also stored in :attr:`datasets`.
    """

    enableLogging: bool = False
    currentStep: int = 0
    currentData: AnimData | None = None
    static: bool = True

    def __init__(self, logging: bool = False, static: bool = True):
        """Parameters
        ----------
        logging : bool
            Print progress messages.
        static : bool
            Kept for API compatibility with the original HDFWriter.
            (Geometry is always rebuilt fresh for every timestep.)
        """
        self.enableLogging = logging
        self.static = static
        self.datasets: list[pv.MultiBlock] = []

    def write(self, data: AnimData) -> pv.MultiBlock:
        """Convert a single AnimData timestep to a ``pv.MultiBlock``.

        Returns
        -------
        pv.MultiBlock
            One block per part, named after the (sanitised) part name.
        """
        self.currentData = data
        multiblock = pv.MultiBlock()

        self.log("Converting quads", bold=True)
        for blockId in range(data.nodes_quads_params.numberOfQuadParts):
            grid = self._convert_quad_part(blockId)
            if grid is not None:
                name = self.extract_part_name(data.quads.quadPartNames[blockId])
                multiblock[name] = grid

        self.log("Converting hexas and tetras", bold=True)
        for hexa_block_id in range(data.hexahedra_params.numberOfhexaParts):
            grid = self._convert_hexa_part(hexa_block_id)
            if grid is not None:
                name = self.extract_part_name(data.hexas.hexaPartNames[hexa_block_id])
                multiblock[name] = grid

        self.log("Converting lines", bold=True)
        for line_block_id in range(data.lines_params.numberOfLineParts):
            grid = self._convert_line_part(line_block_id)
            if grid is not None:
                name = self.extract_part_name(data.lines.linePartNames[line_block_id])
                multiblock[name] = grid

        self.log("Converting SPH", bold=True)
        for sph_part_id in range(len(data.sph.partText)):
            grid = self._convert_sph_part(sph_part_id)
            if grid is not None:
                name = self.extract_part_name(data.sph.partText[sph_part_id])
                multiblock[name] = grid

        self.datasets.append(multiblock)
        self.currentStep += 1
        self.currentData = None  # type: ignore[assignment]
        return multiblock

    # ------------------------------------------------------------------
    # Part converters
    # ------------------------------------------------------------------
    def _convert_sph_part(self, sph_part_id: int) -> pv.UnstructuredGrid | None:
        part_name = self.currentData.sph.partText[sph_part_id]
        self.log(f"Converting SPH part {part_name}")

        partPointIDs = self.currentData.sph.sphConnectivity
        numPts = partPointIDs.shape[0]
        if numPts == 0:
            return None

        # Points
        coordinates = self.currentData.nodes.nodeCoordinates
        points = np.empty((numPts, 3), dtype=np.float32)
        for i, pid in enumerate(partPointIDs):
            points[i] = coordinates[3 * pid : 3 * pid + 3]

        # Vertex cells: one vertex per SPH particle
        types = np.full(numPts, VTK_VERTEX, dtype=np.uint8)
        connectivity = np.arange(numPts, dtype=np.int32)
        offsets = np.arange(numPts + 1, dtype=np.int32)

        grid = pv.UnstructuredGrid()
        grid.points = points
        grid.cell_connectivity = connectivity
        grid.cell_offsets = offsets
        grid.cell_types = types

        # Point data (scalars)
        for array_id in range(len(self.currentData.sph.scalText)):
            name = f"SPH_{self.currentData.sph.scalText[array_id]}"
            grid.point_data[name] = self.currentData.sph.eFunc[
                numPts * array_id : numPts * (array_id + 1)
            ]

        # Cell data
        grid.cell_data["Erosion_status"] = self.currentData.sph.sphDeletedElems

        # Original node IDs
        grid.point_data["NODE_ID"] = partPointIDs

        return grid

    def _convert_quad_part(self, quad_block_id: int) -> pv.UnstructuredGrid | None:
        part_name = self.currentData.quads.quadPartNames[quad_block_id]
        self.log(f"Converting quad part {part_name}")
        return self._convert_geom_part(
            self.currentData.quads.quadPartLastIndices,
            self.currentData.quads.quadConnectivity,
            self.currentData.quads.quadScalarArrayNames,
            self.currentData.quads.quadScalarArrays,
            self.currentData.quads.quadTensorArrayNames,
            self.currentData.quads.quadTensorArrays,
            self.currentData.quads.quadErosionArray,
            self.currentData.quads.quadRadiossIDs,
            VTK_QUAD,
            quad_block_id,
            part_name,
        )

    def _convert_hexa_part(self, hexa_block_id: int) -> pv.UnstructuredGrid | None:
        part_name = self.currentData.hexas.hexaPartNames[hexa_block_id]
        self.log(f"Converting hexa/tetra part {part_name}")
        return self._convert_geom_part(
            self.currentData.hexas.hexaPartLastIndices,
            self.currentData.hexas.hexaConnectivity,
            self.currentData.hexas.hexaScalarArrayNames,
            self.currentData.hexas.hexaScalarArrays,
            self.currentData.hexas.hexaTensorArrayNames,
            self.currentData.hexas.hexaTensorArrays,
            self.currentData.hexas.hexaErosionArray,
            self.currentData.hexas.hexaRadiossIDs,
            VTK_HEXAHEDRON,
            hexa_block_id,
            part_name,
        )

    def _convert_line_part(self, line_block_id: int) -> pv.UnstructuredGrid | None:
        part_name = self.currentData.lines.linePartNames[line_block_id]
        self.log(f"Converting line part {part_name}")
        return self._convert_geom_part(
            self.currentData.lines.linePartLastIndices,
            self.currentData.lines.lineConnectivity,
            self.currentData.lines.lineScalarArrayNames,
            self.currentData.lines.lineScalarArrays,
            self.currentData.lines.lineTensorArrayNames,
            self.currentData.lines.lineTensorArrays,
            self.currentData.lines.lineErosionArray,
            self.currentData.lines.lineRadiossIDs,
            VTK_LINE,
            line_block_id,
            part_name,
        )

    def _convert_geom_part(
        self,
        partsLastIndices: np.ndarray,
        connectivity: np.ndarray,
        scalarArrayNames: list[str],
        scalarArrays: np.ndarray,
        tensorArrayNames: list[str],
        tensorArrays: np.ndarray,
        erosionArray: np.ndarray,
        radiossIDsArray: np.ndarray,
        vtk_type: int,
        blockId: int,
        part_name: str,
    ) -> pv.UnstructuredGrid | None:
        """Convert a single geometrical part to a ``pv.UnstructuredGrid``."""
        firstCellIndex = 0 if blockId == 0 else partsLastIndices[blockId - 1]
        lastCellIndex = partsLastIndices[blockId] - 1
        numCells = lastCellIndex - firstCellIndex + 1
        if numCells <= 0:
            self.log(
                f"Warning: empty block {part_name} "
                f"(first={firstCellIndex}, last={lastCellIndex})",
                bold=True,
            )
            return None

        coordinates = self.currentData.nodes.nodeCoordinates
        numPointsPerCell = self.get_num_point_for_geometry(vtk_type)
        part_connectivity = connectivity[
            numPointsPerCell * firstCellIndex : numPointsPerCell * (lastCellIndex + 1)
        ]

        # ------------------------------------------------------------------
        # Build cell topology (connectivity, offsets, types)
        # ------------------------------------------------------------------
        types = np.full(numCells, vtk_type, dtype=np.uint8)

        if vtk_type == VTK_HEXAHEDRON:
            tetra_count = 0
            connect_offset = 0
            new_connectivity = np.zeros(8 * numCells, dtype=np.int32)
            offsets = np.zeros(numCells + 1, dtype=np.int32)

            for cellId in range(numCells):
                connect = part_connectivity[cellId * 8 : (cellId + 1) * 8]
                unique = np.unique(connect)
                if len(unique) == 4:
                    types[cellId] = VTK_TETRA
                    tetra_count += 1
                    new_connectivity[connect_offset : connect_offset + 4] = unique
                    connect_offset += 4
                else:
                    new_connectivity[connect_offset : connect_offset + 8] = connect
                    connect_offset += 8
                offsets[cellId + 1] = connect_offset

            self.log(f"\tFound {tetra_count} tetras / {numCells} cells")
            part_connectivity = new_connectivity[: 8 * numCells - 4 * tetra_count]
        else:
            offsets = np.array(
                [numPointsPerCell * i for i in range(numCells + 1)], dtype=np.int32
            )

        # ------------------------------------------------------------------
        # Points: extract unique nodes and remap connectivity
        # ------------------------------------------------------------------
        partPointIDs = np.unique(part_connectivity)
        numPoints = len(partPointIDs)

        points = np.empty((numPoints, 3), dtype=np.float32)
        for i, pid in enumerate(partPointIDs):
            points[i] = coordinates[3 * pid : 3 * pid + 3]

        radiossPointIdToVTKPointId = {pid: i for i, pid in enumerate(partPointIDs)}
        cellConnectivity = np.array(
            [radiossPointIdToVTKPointId[cid] for cid in part_connectivity],
            dtype=np.int32,
        )

        # ------------------------------------------------------------------
        # Assemble PyVista grid
        # ------------------------------------------------------------------
        grid = pv.UnstructuredGrid()
        grid.points = points
        grid.cell_connectivity = cellConnectivity
        grid.cell_offsets = offsets
        grid.cell_types = types

        # ------------------------------------------------------------------
        # Cell data
        # ------------------------------------------------------------------
        dimension = self.get_element_dimension(vtk_type)

        # Scalars
        for arrayId in range(len(scalarArrayNames)):
            name = f"{scalarArrayNames[arrayId]}_{dimension}D"
            grid.cell_data[name] = scalarArrays[arrayId][
                firstCellIndex : lastCellIndex + 1
            ]

        # Tensors
        for arrayId in range(len(tensorArrayNames)):
            size = self.get_tensor_num_comp(vtk_type)
            name = f"{tensorArrayNames[arrayId]}_{dimension}D"
            grid.cell_data[name] = np.reshape(
                tensorArrays[arrayId][
                    firstCellIndex * size : (lastCellIndex + 1) * size
                ],
                (-1, size),
            )

        # Erosion / Part ID / Element ID
        grid.cell_data["Erosion_status"] = erosionArray[
            firstCellIndex : lastCellIndex + 1
        ]
        part_id = self.get_part_id_from_name(part_name)
        grid.cell_data["Part_ID"] = np.full(numCells, part_id, dtype=np.int32)
        if self.currentData.global_params.isNodeNumberingElementSaved:
            grid.cell_data["Element_ID"] = radiossIDsArray[
                firstCellIndex : lastCellIndex + 1
            ]

        # ------------------------------------------------------------------
        # Point data
        # ------------------------------------------------------------------
        grid.point_data["NODE_ID"] = partPointIDs

        for arrayId in range(len(self.currentData.nodes.nodeScalarArrayNames)):
            arr = np.array(
                [
                    self.currentData.nodes.nodeScalarArrays[arrayId][pid]
                    for pid in partPointIDs
                ],
                dtype=np.float32,
            )
            grid.point_data[self.currentData.nodes.nodeScalarArrayNames[arrayId]] = arr

        for arrayId in range(len(self.currentData.nodes.nodeVectorArrayNames)):
            size = self.get_tensor_num_comp(VTK_VERTEX)
            arr = np.array(
                [
                    self.currentData.nodes.nodeVectorArrays[arrayId][
                        pid * size : (pid + 1) * size
                    ]
                    for pid in partPointIDs
                ],
                dtype=np.float32,
            )
            grid.point_data[self.currentData.nodes.nodeVectorArrayNames[arrayId]] = arr

        return grid

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def log(self, *args, **kwargs):
        if self.enableLogging:
            print(*args, **kwargs)

    @staticmethod
    def get_tensor_num_comp(vtk_type: int) -> int:
        if vtk_type == VTK_QUAD:
            return QUAD_TENSOR_SIZE
        elif vtk_type == VTK_HEXAHEDRON:
            return HEXA_TENSOR_SIZE
        elif vtk_type == VTK_LINE:
            return LINE_TENSOR_SIZE
        elif vtk_type == VTK_VERTEX:
            return VERTEX_TENSOR_SIZE
        raise ValueError(f"Unsupported VTK type {vtk_type}")

    @staticmethod
    def get_element_dimension(vtk_type: int) -> int:
        if vtk_type == VTK_QUAD:
            return 2
        elif vtk_type in (VTK_HEXAHEDRON, VTK_TETRA):
            return 3
        elif vtk_type == VTK_LINE:
            return 1
        raise ValueError(f"Unsupported VTK type {vtk_type}")

    @staticmethod
    def get_num_point_for_geometry(vtk_type: int) -> int:
        if vtk_type == VTK_QUAD:
            return NUM_POINTS_PER_QUAD
        elif vtk_type == VTK_HEXAHEDRON:
            return NUM_POINTS_PER_HEXA
        elif vtk_type == VTK_LINE:
            return NUM_POINTS_PER_LINE
        raise ValueError(f"Unsupported VTK type {vtk_type}")

    @staticmethod
    def get_part_id_from_name(part_name: str) -> int:
        name = part_name.strip()
        count = 0
        while count < len(name) and name[count].isdecimal():
            count += 1
        return int(name[:count]) if count > 0 else 0

    @staticmethod
    def extract_part_name(name: str) -> str:
        transformed = name
        if len(transformed.split(":")) == 2:
            id_str, name_str = transformed.split(":")
            transformed = f"{name_str}_{id_str}"

        transformed = "".join(
            char for char in transformed if char in AUTHORIZED_CHARS
        )

        if not transformed:
            transformed = "block_" + "".join(
                char for char in name if char in AUTHORIZED_CHARS
            )

        if not transformed or (
            not transformed[0].isalpha() and transformed[0] != "_"
        ):
            transformed = "block_" + transformed

        return transformed
