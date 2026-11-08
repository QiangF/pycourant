from typing import Any
import h5py as h5
import numpy as np
from animstructs import AnimData

AUTHORIZED_CHARS = ".-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
VTKHDF_VERSION = (2, 2)

# Numpy types
FLOAT_TYPE = "f4"
ID_TYPE = "i4"
CHAR_TYPE = "uint8"

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


class HDFWriter:
    """Append AnimData structure to a VTKHDF file.
    Open it and set up groups and resizable datasets on the first timesteps,
    and append data on the next ones."""

    enableLogging: bool = False
    currentStep: int = 0
    currentData: AnimData
    root: h5.Group

    def __init__(
        self, outputf: str, num_steps: int, logging: bool = False, static=True
    ):
        self.outputf = outputf
        self.numSteps = num_steps
        self.enableLogging = logging
        self.static = static
        self.fileHandle = h5.File(self.outputf, "w")

    def close(self):
        self.fileHandle.close()

    def write(self, data: AnimData):
        """Append data to open file. Data should have the same parts as the previous steps if any."""
        self.currentData = data

        if self.currentStep == 0:
            self.root = self.fileHandle.create_group("VTKHDF", track_order=True)
            self.write_metadata(self.root, b"PartitionedDataSetCollection")

        self.log("Writing quads", bold=True)
        for blockId in range(data.nodes_quads_params.numberOfQuadParts):
            self.write_quad_part(blockId)

        self.log("Writing hexas and tetras", bold=True)
        for hexa_block_id in range(data.hexahedra_params.numberOfhexaParts):
            self.write_hexa_part(hexa_block_id)

        self.log("Writing lines", bold=True)
        for line_block_id in range(data.lines_params.numberOfLineParts):
            self.write_line_part(line_block_id)

        self.log("Writing SPH", bold=True)
        for sph_part_id in range(len(data.sph.partText)):
            self.write_sph_part(sph_part_id)

        if self.currentStep == self.numSteps - 1:
            self.write_assembly()

        self.currentStep += 1
        self.currentData = None  # type: ignore # Free memory/Trigger GC

    def write_sph_part(self, sph_part_id: int):
        part_name = self.currentData.sph.partText[sph_part_id]
        group = self.setup_block_ug(part_name)

        self.log(f"Writing SPH part {part_name}")

        # Write points
        partPointIDs = self.currentData.sph.sphConnectivity
        self.add_or_create_dataset(
            group,
            "NumberOfPoints",
            data=(len(partPointIDs),),
            dtype=ID_TYPE,
            maxshape=(None,),
        )
        radiossPointIdToVTKPointId = {}
        self.write_points(
            group,
            radiossPointIdToVTKPointId,
            self.currentData.nodes.nodeCoordinates,
            partPointIDs,
        )

        # Write vertex cells
        numPts = self.currentData.sph.sphConnectivity.shape[0]
        self.add_or_create_dataset(
            group,
            "Connectivity",
            data=tuple(range(numPts)),
            dtype=ID_TYPE,
            maxshape=(None,),
        )
        self.add_or_create_dataset(
            group, "NumberOfCells", data=(numPts,), dtype=ID_TYPE, maxshape=(None,)
        )
        self.add_or_create_dataset(
            group,
            "NumberOfConnectivityIds",
            data=(self.currentData.sph.sphConnectivity.shape[0],),
            dtype=ID_TYPE,
            maxshape=(None,),
        )
        self.add_or_create_dataset(
            group,
            "Offsets",
            data=tuple(range(numPts + 1)),
            dtype=ID_TYPE,
            maxshape=(None,),
        )
        self.add_or_create_dataset(
            group,
            "Types",
            data=(VTK_VERTEX,) * numPts,
            dtype=CHAR_TYPE,
            maxshape=(None,),
        )

        # Write point data
        for array_id in range(len(self.currentData.sph.scalText)):
            self.add_or_create_dataset(
                group["PointData"],
                f"SPH_{self.currentData.sph.scalText[array_id]}",
                data=self.currentData.sph.eFunc[
                    numPts * array_id : numPts * (array_id + 1)
                ],
                dtype=FLOAT_TYPE,
                maxshape=(None,),
            )

        # TODO: write tensors, find example of SPH with tensor arrays
        self.add_or_create_dataset(
            group["CellData"],
            "Erosion_status",
            data=self.currentData.sph.sphDeletedElems,
            dtype="i1",
            maxshape=(None,),
        )


        self.append_to_steps_group(group)

    def write_quad_part(self, quad_block_id: int):
        """Write the quad part with the given id to file"""
        part_name = self.currentData.quads.quadPartNames[quad_block_id]
        group = self.setup_block_ug(part_name)
        self.log(f"Writing quad part {part_name}")
        self.write_geom_part(
            group,
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
        self.append_to_steps_group(group)

    def write_hexa_part(self, hexa_block_id: int):
        """Write the hexa/tetra part with the given id to file"""
        part_name = self.currentData.hexas.hexaPartNames[hexa_block_id]
        group = self.setup_block_ug(part_name)
        self.log(f"Writing hexa/tetra part {part_name}")
        self.write_geom_part(
            group,
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
        self.append_to_steps_group(group)

    def write_line_part(self, line_block_id: int):
        """Write the line part with the given id to file"""
        part_name = self.currentData.lines.linePartNames[line_block_id]
        group = self.setup_block_ug(part_name)
        self.log(f"Writing line part {part_name}")
        self.write_geom_part(
            group,
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
        self.append_to_steps_group(group)

    def setup_block_ug(self, name: str) -> h5.Group:
        """Create UnstructuredGrid block in the VTKHDF file"""
        group = self.create_or_retrieve_group(
            self.root,
            self.extract_part_name(name),
            track_order=True,
        )
        self.write_metadata(group, b"UnstructuredGrid")
        self.create_or_retrieve_group(group, "PointData", track_order=True)
        self.create_or_retrieve_group(group, "CellData", track_order=True)
        return group

    def write_geom_part(
        self,
        group: h5.Group,
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
    ):
        """Write geometrical part with the given VTK type to disk. If `static` has been set,
        only the first timestep will write cell types, connectivity and offsets.
        All parts write points and array data."""

        firstCellIndex = 0 if blockId == 0 else partsLastIndices[blockId - 1]
        lastCellIndex = partsLastIndices[blockId] - 1
        numCells = lastCellIndex - firstCellIndex + 1
        if numCells < 0:
            self.log(
                f"Warning: incorrect first ({firstCellIndex}) & last ({lastCellIndex}) cell indices, ignoring block {group.name}",
                bold=True,
            )
            del self.root[group.name]
            return
        coordinates = self.currentData.nodes.nodeCoordinates
        numPointsPerCell = self.get_num_point_for_geometry(vtk_type)  # Quads
        radiossPointIdToVTKPointId = {}
        part_connectivity = connectivity[
            numPointsPerCell * firstCellIndex : numPointsPerCell * (lastCellIndex + 1)
        ]

        # Create connectivity array, deducing actual cell type for 3D cells:
        # tetras will have duplicate points compared to hexas.
        # Cell types, connectivity and offsets do not change when the cells are static
        if self.currentStep == 0 or not self.static:
            types = [vtk_type] * numCells
            offsets = []
            # Some tetras can be defined as hexas with 4 distinct points
            if vtk_type == VTK_HEXAHEDRON:
                tetra_count = 0
                connect_offset = 0
                new_connectivity = np.zeros(8 * numCells, dtype=np.int32)
                offsets = [0] * (numCells + 1)

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
                offsets = [numPointsPerCell * i for i in range(numCells + 1)]

        # Retrive point ids used in the part connectivity
        partPointIDs = np.unique(part_connectivity)

        self.add_or_create_dataset(
            group,
            "NumberOfPoints",
            data=(len(partPointIDs),),
            dtype=ID_TYPE,
            maxshape=(None,),
        )
        self.add_or_create_dataset(
            group, "NumberOfCells", data=(numCells,), dtype=ID_TYPE, maxshape=(None,)
        )
        self.add_or_create_dataset(
            group,
            "NumberOfConnectivityIds",
            data=(len(part_connectivity),),
            dtype=ID_TYPE,
            maxshape=(None,),
        )

        self.write_points(group, radiossPointIdToVTKPointId, coordinates, partPointIDs)

        if self.currentStep == 0 or not self.static:
            self.write_cell_info(
                group, radiossPointIdToVTKPointId, part_connectivity, types, offsets
            )

        self.write_cell_data(
            group,
            scalarArrayNames,
            scalarArrays,
            tensorArrayNames,
            tensorArrays,
            erosionArray,
            radiossIDsArray,
            firstCellIndex,
            lastCellIndex,
            vtk_type,
            part_name,
        )

        self.write_point_data(group, partPointIDs)

    def write_points(
        self, group, radiossPointIdToVTKPointId, coordinates, partPointIDs
    ):
        """Fill points coordinates array for the current timestep,
        as well as the point mapping array from Radioss ids to VTK ids"""

        # Create HDF5 group for points, create mapping between Radioss and VTK pointIds
        numPoints = len(partPointIDs)
        pointsDS = None
        pt_offset = 0
        if self.currentStep == 0:
            pointsDS = group.create_dataset(
                "Points",
                shape=(numPoints, 3),
                dtype=FLOAT_TYPE,
                maxshape=(None, 3),
            )
        else:
            pointsDS = group["Points"]
            origLen = pointsDS.shape[0]
            pt_offset = origLen
            pointsDS.resize(origLen + numPoints, axis=0)

        # Iterate over unique point ids
        point_coords = np.fromiter(
            (coordinates[3 * pid : 3 * pid + 3] for pid in partPointIDs),
            dtype=np.dtype((FLOAT_TYPE, 3)),
        )
        pointCount = 0
        for pid in partPointIDs:
            radiossPointIdToVTKPointId[pid] = pointCount
            pointCount += 1

        # Copy the whole array at once (faster than setting individual points)
        pointsDS[pt_offset:, :] = point_coords

    def write_cell_info(
        self, group, radiossPointIdToVTKPointId, part_connectivity, types, offsets
    ):
        """Write cell types, connectivity and offsets to file"""

        # Translate connectivity from Radioss to VTK point ids
        cellConnectivity = [radiossPointIdToVTKPointId[id] for id in part_connectivity]

        self.add_or_create_dataset(
            group, "Types", data=types, dtype=CHAR_TYPE, maxshape=(None,)
        )
        self.add_or_create_dataset(
            group,
            "Connectivity",
            data=cellConnectivity,
            dtype=ID_TYPE,
            maxshape=(None,),
        )
        self.add_or_create_dataset(
            group, "Offsets", data=offsets, dtype=ID_TYPE, maxshape=(None,)
        )

    def write_cell_data(
        self,
        group: h5.Group,
        scalarArrayNames: list[str],
        scalarArrays: np.ndarray,
        tensorArrayNames: list[str],
        tensorArrays: np.ndarray,
        erosionArray: np.ndarray,
        radiossIDsArray: np.ndarray,
        firstCellIndex: int,
        lastCellIndex: int,
        vtk_type: int,
        part_name: str,
    ):
        # Discriminate cell data fields on dimension of
        dimension = self.get_element_dimension(vtk_type)

        """Write cell fields to file"""
        # Create cell scalar arrays
        for arrayId in range(len(scalarArrayNames)):
            self.add_or_create_dataset(
                group["CellData"],
                f"{scalarArrayNames[arrayId]}_{dimension}D",
                data=(scalarArrays[arrayId][firstCellIndex : lastCellIndex + 1]),
                dtype=FLOAT_TYPE,
                maxshape=(None,),
            )

        # Create cell tensor arrays, reshaping them to get
        # the number of columns equal to the number of components
        # in the tensor array for the current topology type
        for arrayId in range(len(tensorArrayNames)):
            size = self.get_tensor_num_comp(vtk_type)
            self.add_or_create_dataset(
                group["CellData"],
                f"{tensorArrayNames[arrayId]}_{dimension}D",
                data=(
                    np.reshape(
                        tensorArrays[arrayId][
                            firstCellIndex * size : (lastCellIndex + 1) * size
                        ],
                        (-1, size),
                    )
                ),
                dtype=FLOAT_TYPE,
                maxshape=(None, size),
            )

        # Erosion corresponds to deleted cells
        self.add_or_create_dataset(
            group["CellData"],
            "Erosion_status",
            data=erosionArray[firstCellIndex : lastCellIndex + 1],
            dtype="i1",
            maxshape=(None,),
        )

        # Fetch part ID from the part name
        self.add_or_create_dataset(
            group["CellData"],
            "Part_ID",
            data=(self.get_part_id_from_name(part_name),)
            * (lastCellIndex - firstCellIndex + 1),
            dtype="i4",
            maxshape=(None,),
        )

        # Radioss Cell IDs
        if self.currentData.global_params.isNodeNumberingElementSaved:
            self.add_or_create_dataset(
                group["CellData"],
                "Element_ID",
                data=radiossIDsArray[firstCellIndex : lastCellIndex + 1],
                dtype="i4",
                maxshape=(None,),
            )

    def write_point_data(self, group, partPointIDs):
        """Write point fields to file"""
        # Keep original node ids in a point field scalar array
        self.add_or_create_dataset(
            group["PointData"],
            "NODE_ID",
            data=partPointIDs,
            maxshape=(None,),
            dtype=ID_TYPE,
        )

        # Create scalar node arrays
        for arrayId in range(len(self.currentData.nodes.nodeScalarArrayNames)):
            array = [
                self.currentData.nodes.nodeScalarArrays[arrayId][pid]
                for pid in partPointIDs
            ]
            self.add_or_create_dataset(
                group["PointData"],
                self.currentData.nodes.nodeScalarArrayNames[arrayId],
                data=array,
                dtype=FLOAT_TYPE,
                maxshape=(None,),
            )

        # Create node vector arrays
        for arrayId in range(len(self.currentData.nodes.nodeVectorArrayNames)):
            size = self.get_tensor_num_comp(VTK_VERTEX)
            array = [
                self.currentData.nodes.nodeVectorArrays[arrayId][
                    pid * size : (pid + 1) * size
                ]
                for pid in partPointIDs
            ]
            self.add_or_create_dataset(
                group["PointData"],
                self.currentData.nodes.nodeVectorArrayNames[arrayId],
                data=array,
                dtype=FLOAT_TYPE,
                maxshape=(None, size),
            )

    def create_or_retrieve_group(self, group, groupname: str, **kwargs) -> h5.Group:
        """Return group if it exists, create it otherwise."""
        if groupname in group.keys():
            return group[groupname]
        else:
            return group.create_group(groupname, **kwargs)

    def append_to_steps_group(self, group: h5.Group):
        """Append data to steps group, for the reader to know where to start reading each timestep."""
        if self.numSteps == 1 or not group.name:
            return

        if self.currentStep == 0:
            steps = group.create_group("Steps")
            steps.attrs["NSteps"] = (self.numSteps,)
            steps.create_dataset("PointOffsets", shape=(self.numSteps,), dtype=ID_TYPE)
            steps.create_dataset("PartOffsets", shape=(self.numSteps,), dtype=ID_TYPE)
            steps.create_dataset("CellOffsets", shape=(self.numSteps,), dtype=ID_TYPE)
            steps.create_dataset(
                "ConnectivityIdOffsets", shape=(self.numSteps,), dtype=ID_TYPE
            )
            steps.create_dataset("Values", shape=(self.numSteps,), dtype=ID_TYPE)

            steps["PointOffsets"][0] = 0
            steps["PartOffsets"][0] = 0
            steps["CellOffsets"][0] = 0
            steps["ConnectivityIdOffsets"][0] = 0
            steps["Values"][0] = 0

            cell_data_offsets = steps.create_group("CellDataOffsets")
            for cell_data_array in group["CellData"].keys():
                cell_data_offsets.create_dataset(
                    cell_data_array, shape=(self.numSteps,), dtype=ID_TYPE
                )
                cell_data_offsets[cell_data_array][0] = 0

            point_data_offsets = steps.create_group("PointDataOffsets")
            for point_data_array in group["PointData"].keys():
                point_data_offsets.create_dataset(
                    point_data_array, shape=(self.numSteps,), dtype=ID_TYPE
                )
                point_data_offsets[point_data_array][0] = 0
        else:
            steps = group["Steps"]
            steps["PointOffsets"][self.currentStep] = (
                steps["PointOffsets"][self.currentStep - 1]
                + group["NumberOfPoints"][self.currentStep - 1]
            )
            steps["Values"][self.currentStep] = self.currentStep
            if self.static:
                steps["PartOffsets"][self.currentStep] = 0
            else:
                steps["PartOffsets"][self.currentStep] = self.currentStep

            if not self.static:
                steps["CellOffsets"][self.currentStep] = (
                    steps["CellOffsets"][self.currentStep - 1]
                    + group["NumberOfCells"][self.currentStep - 1]
                )
                steps["ConnectivityIdOffsets"][self.currentStep] = (
                    steps["ConnectivityIdOffsets"][self.currentStep - 1]
                    + group["NumberOfConnectivityIds"][self.currentStep - 1]
                )
            else:
                steps["CellOffsets"][self.currentStep] = 0
                steps["ConnectivityIdOffsets"][self.currentStep] = 0

            cell_data_offsets = steps["CellDataOffsets"]
            for cell_data_array in group["CellData"].keys():
                cell_data_offsets[cell_data_array][self.currentStep] = (
                    cell_data_offsets[cell_data_array][self.currentStep - 1]
                    + group["NumberOfCells"][self.currentStep - 1]
                )

            point_data_offsets = steps["PointDataOffsets"]
            for point_data_array in group["PointData"].keys():
                point_data_offsets[point_data_array][self.currentStep] = steps[
                    "PointOffsets"
                ][self.currentStep]

    def write_assembly(self):
        """Write PDC assembly to file, using symlinks to block data. Only needs to be done once"""
        self.log("Creating assembly", bold=True)
        assembly = self.root.create_group("Assembly", track_order=True)
        all_part_names = (
            self.currentData.quads.quadPartNames
            + self.currentData.hexas.hexaPartNames
            + self.currentData.lines.linePartNames
            + self.currentData.sph.partText
        )

        part_count = 0
        for part_name in all_part_names:
            fmtName = self.extract_part_name(part_name)
            if fmtName not in self.root:
                continue
            assembly.create_group(fmtName, track_order=True)
            assembly[f"{fmtName}/{fmtName}"] = h5.SoftLink(f"/VTKHDF/{fmtName}")
            self.root[f"/VTKHDF/{fmtName}"].attrs.create(
                "Index", part_count, dtype=ID_TYPE
            )
            part_count += 1

    def write_metadata(self, group, ascii_type):
        """Write VTKHDF metadata for the current root group. Only needs to be done on the first timestep"""
        group.attrs["Version"] = VTKHDF_VERSION
        group.attrs.create(
            "Type", ascii_type, dtype=h5.string_dtype("ascii", len(ascii_type))
        )

    def add_or_create_dataset(
        self,
        group: h5.Group | h5.Dataset | h5.Datatype,
        name: str,
        data: tuple[Any] | np.ndarray,
        **kwargs,
    ):
        """Create dataset on the first time step, add data to it on the next ones"""
        if len(data) == 0:
            return

        if not isinstance(group, h5.Group):
            raise ValueError(f"Expected a group, got {type(group)}")

        if self.currentStep == 0:
            return group.create_dataset(name, data=data, **kwargs)
        else:
            if name not in group.keys():
                raise ValueError(
                    f"Could not find {name} in group {group.name}. Make sure all provided files have the exact same field and parts"
                )
            dataset: h5.Dataset = group[name]
            origLen = dataset.shape[0]
            dataset.resize(origLen + len(data), axis=0)
            dataset[origLen:] = data
            return dataset

    def log(self, *args, **kwargs):
        if self.enableLogging:
            print(*args, **kwargs)

    @staticmethod
    def get_tensor_num_comp(vtk_type: int):
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
    def get_element_dimension(vtk_type: int):
        if vtk_type == VTK_QUAD:
            return 2
        elif vtk_type == VTK_HEXAHEDRON or vtk_type == VTK_TETRA:
            return 3
        elif vtk_type == VTK_LINE:
            return 1

        raise ValueError(f"Unsupported VTK type {vtk_type}")

    @staticmethod
    def get_num_point_for_geometry(vtk_type: int):
        if vtk_type == VTK_QUAD:
            return NUM_POINTS_PER_QUAD
        elif vtk_type == VTK_HEXAHEDRON:
            return NUM_POINTS_PER_HEXA
        elif vtk_type == VTK_LINE:
            return NUM_POINTS_PER_LINE

        raise ValueError(f"Unsupported VTK type {vtk_type}")

    @staticmethod
    def get_part_id_from_name(part_name: str):
        name = part_name.strip()
        count = 0
        while name[count].isdecimal():
            count += 1
        return int(name[:count])

    @staticmethod
    def extract_part_name(name: str) -> str:
        transformed = name
        if len(transformed.split(":")) == 2:
            id, name = transformed.split(":")
            transformed = f"{name}_{id}"

        transformed = "".join(char for char in transformed if char in AUTHORIZED_CHARS)

        if not transformed:
            transformed = "block_" + "".join(
                char for char in name if char in AUTHORIZED_CHARS
            )

        if (not transformed[0].isalpha()) or transformed[0] == "_":
            transformed = "block_" + transformed

        return transformed
