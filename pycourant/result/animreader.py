import dataclasses
import pathlib

from .animstructs import AnimData, HeaderParameters, HierarchyData, HierarchyElement, NodesAndQuadsHeaders, NodesData, QuadsData, HexahedraHeaders, HexahedraData, LinesHeaders, LinesData, SPHData, TimeHistoryData
from .binreader import BinReader
MAGIC_HEADER_VALUE = 0x542C
STANDARD_STRING_SIZE = 50

class AnimReader:
    """Open and parse a Radioss Anim file, store data in a AnimData structure.
    Sample parser can be found here: https://github.com/OpenRadioss/OpenRadioss/blob/main/tools/anim_to_vtk/src/anim_to_vtk.cpp
    """

    enableLogging: bool = False

    def __init__(self, inputf: str, logging: bool = False):
        self.inputf = inputf
        self.enableLogging = logging

    def read(self) -> AnimData:
        self.br = BinReader(pathlib.Path(self.inputf).read_bytes())

        self.log("Reading Anim file parameters", bold=True)
        self.params = self.readParams()
        self.log("Parsing quads and nodes", bold=True)
        nodes_quads_params, nodes, quads = self.readNodesAndQuads()

        self.log("Parsing hexahedra", bold=True)
        hexcounts, hexas = self.readHexahedra()

        self.log("Parsing lines", bold=True)
        linecounts, lines = self.readLines()

        self.log("Parsing hierarchy", bold=True)
        hierarchy = self.readHierarchy()

        self.log("Parsing NODES/ELTS for time history", bold=True)
        th = self.readTimeHistory()
        
        self.log("Parsing SPH", bold=True)
        sph = self.readSPH()

        return AnimData(
            global_params=self.params,
            nodes_quads_params=nodes_quads_params,
            hexahedra_params=hexcounts,
            lines_params=linecounts,
            nodes=nodes,
            quads=quads,
            hexas=hexas,
            lines=lines,
            hierarchy=hierarchy,
            sph=sph,
            th=th
        )

    def readParams(self) -> HeaderParameters:
        tag = self.br.readInt32()
        if tag != MAGIC_HEADER_VALUE:
            raise ValueError(
                f"Header {hex(tag)} not recognized. Expected {hex(MAGIC_HEADER_VALUE)}"
            )

        params = HeaderParameters()
        params.time = self.br.readFloat32()
        params.timeDescription = self.br.readString(81)
        params.animationDescription = self.br.readString(81)
        params.runDescription = self.br.readString(81)
        params.isMassSaved = self.br.readIntAsBool()
        params.isNodeNumberingElementSaved = self.br.readIntAsBool()
        params.is3DGeometrySaved = self.br.readIntAsBool()
        params.is1DGeometrySaved = self.br.readIntAsBool()
        params.isHierarchySaved = self.br.readIntAsBool()
        params.isNodeElementListForTimeHistory = self.br.readIntAsBool()
        params.isNewSkewForTensor2DSaved = self.br.readIntAsBool()
        params.isSPHSaved = self.br.readIntAsBool()
        params.unused1 = self.br.readIntAsBool()
        params.unused2 = self.br.readIntAsBool()

        self.log(params)
        return params

    def readNodesAndQuads(self) -> tuple[NodesAndQuadsHeaders, NodesData, QuadsData]:
        counts = NodesAndQuadsHeaders()
        for param in dataclasses.fields(NodesAndQuadsHeaders):
            setattr(counts, param.name, self.br.readInt32())
        self.log(counts)

        nodes = NodesData()
        quads = QuadsData()
        nodes.skews = self.br.readFloatVectorFromShorts(counts.numberOfSkews * 6)
        nodes.nodeCoordinates = self.br.readFloat32Vector(counts.numberOfNodes * 3)
        quads.quadConnectivity = self.br.readInt32Vector(counts.numberOfQuads * 4)
        quads.quadErosionArray = self.br.readInt8Vector(counts.numberOfQuads)
        quads.quadPartLastIndices = self.br.readInt32Vector(counts.numberOfQuadParts)
        quads.quadPartNames = self.br.readStringVector(counts.numberOfQuadParts, STANDARD_STRING_SIZE)
        nodes.nodeNorms = self.br.readFloatVectorFromShorts(counts.numberOfNodes * 3)

        # Scalar arrays
        nodes.nodeScalarArrayNames = self.br.readStringVector(
            counts.numberOfNodalScalarArrays, 81
        )
        quads.quadScalarArrayNames = self.br.readStringVector(
            counts.numberOfQuadScalarArrays, 81
        )
        nodes.nodeScalarArrays = self.br.readFloat32Matrix(
            counts.numberOfNodes, counts.numberOfNodalScalarArrays
        )
        quads.quadScalarArrays = self.br.readFloat32Matrix(
            counts.numberOfQuads, counts.numberOfQuadScalarArrays
        )

        # Vector arrays
        nodes.nodeVectorArrayNames = self.br.readStringVector(
            counts.numberOfNodalVectorArrays, 81
        )
        nodes.nodeVectorArrays = self.br.readFloat32Matrix(
            counts.numberOfNodes * 3, counts.numberOfNodalVectorArrays
        )
        quads.quadTensorArrayNames = self.br.readStringVector(
            counts.numberOfQuadTensorArrays, 81
        )
        quads.quadTensorArrays = self.br.readFloat32Matrix(
            counts.numberOfQuads * 3, counts.numberOfQuadTensorArrays
        )

        self.log(f"Quad parts: {quads.quadPartNames}")
        self.log(f"Node scalar arrays: {nodes.nodeScalarArrayNames}")
        self.log(f"Quad scalar arrays: {quads.quadScalarArrayNames}")
        self.log(f"Node vector arrays: {nodes.nodeVectorArrayNames}")
        self.log(f"Quad tensor arrays: {quads.quadTensorArrayNames}")

        # Mass
        if self.params.isMassSaved:
            quads.quadMassArray = self.br.readFloat32Vector(counts.numberOfQuads)
            nodes.nodeMassArray = self.br.readFloat32Vector(counts.numberOfNodes)

        # Numbering
        if self.params.isNodeNumberingElementSaved:
            nodes.nodeRadiossIDs = self.br.readInt32Vector(counts.numberOfNodes)
            quads.quadRadiossIDs = self.br.readInt32Vector(counts.numberOfQuads)

        # Hierarchy (unused)
        if self.params.isHierarchySaved:
            nodes.partSubsets = self.br.readFloat32Vector(counts.numberOfQuadParts)
            nodes.partMaterials = self.br.readInt32Vector(counts.numberOfQuadParts)
            nodes.partProperties = self.br.readInt32Vector(counts.numberOfQuadParts)

        return counts, nodes, quads

    def readHexahedra(self) -> tuple[HexahedraHeaders, HexahedraData]:
        hexcounts = HexahedraHeaders()
        hexas = HexahedraData()

        if not self.params.is3DGeometrySaved:
            self.log("3D Geometry is not saved, skipping")
            return hexcounts, hexas

        for param in dataclasses.fields(HexahedraHeaders):
            setattr(hexcounts, param.name, self.br.readInt32())

        self.log(hexcounts)

        hexas.hexaConnectivity = self.br.readInt32Vector(
            hexcounts.numberOfHexahedra * 8
        )
        hexas.hexaErosionArray = self.br.readInt8Vector(hexcounts.numberOfHexahedra)
        hexas.hexaPartLastIndices = self.br.readInt32Vector(hexcounts.numberOfhexaParts)
        hexas.hexaPartNames = self.br.readStringVector(hexcounts.numberOfhexaParts, STANDARD_STRING_SIZE)

        hexas.hexaScalarArrayNames = self.br.readStringVector(
            hexcounts.numberOfhexaScalarArrays, 81
        )
        hexas.hexaScalarArrays = self.br.readFloat32Matrix(
            hexcounts.numberOfHexahedra, hexcounts.numberOfhexaScalarArrays
        )

        hexas.hexaTensorArrayNames = self.br.readStringVector(
            hexcounts.numberOfhexaTensorArrays, 81
        )
        hexas.hexaTensorArrays = self.br.readFloat32Matrix(
            hexcounts.numberOfHexahedra * 6, hexcounts.numberOfhexaTensorArrays
        )

        self.log(f"Hexa Parts: {hexas.hexaPartNames}")
        self.log(f"Hexa scalar arrays: {hexas.hexaScalarArrayNames}")
        self.log(f"Hexa tensor arrays: {hexas.hexaTensorArrayNames}")

        if self.params.isMassSaved:
            hexas.hexaMassArray = self.br.readFloat32Vector(hexcounts.numberOfHexahedra)

        if self.params.isNodeNumberingElementSaved:
            hexas.hexaRadiossIDs = self.br.readInt32Vector(hexcounts.numberOfHexahedra)

        # Hierarchy (unused)
        if self.params.isHierarchySaved:
            hexas.partSubsets = self.br.readFloat32Vector(hexcounts.numberOfhexaParts)
            hexas.partMaterials = self.br.readInt32Vector(hexcounts.numberOfhexaParts)
            hexas.partProperties = self.br.readInt32Vector(hexcounts.numberOfhexaParts)

        return hexcounts, hexas

    def readLines(self) -> tuple[LinesHeaders, LinesData]:
        linecounts = LinesHeaders()
        lines = LinesData()

        if not self.params.is1DGeometrySaved:
            self.log("1D Geometry is not saved, skipping")
            return linecounts, lines

        linecounts.numberOfLines = self.br.readInt32()
        linecounts.numberOfLineParts = self.br.readInt32()
        linecounts.numberOfLineScalarArrays = self.br.readInt32()
        linecounts.numberOfLineTensorArrays = self.br.readInt32()
        linecounts.isLineSkewSaved = self.br.readIntAsBool()

        self.log(linecounts)

        lines.lineConnectivity = self.br.readInt32Vector(linecounts.numberOfLines * 2)
        lines.lineErosionArray = self.br.readInt8Vector(linecounts.numberOfLines)
        lines.linePartLastIndices = self.br.readInt32Vector(
            linecounts.numberOfLineParts
        )
        lines.linePartNames = self.br.readStringVector(linecounts.numberOfLineParts, STANDARD_STRING_SIZE)

        lines.lineScalarArrayNames = self.br.readStringVector(
            linecounts.numberOfLineScalarArrays, 81
        )
        lines.lineScalarArrays = self.br.readFloat32Matrix(
            linecounts.numberOfLines, linecounts.numberOfLineScalarArrays
        )

        lines.lineTensorArrayNames = self.br.readStringVector(
            linecounts.numberOfLineTensorArrays, 81
        )
        lines.lineTensorArrays = self.br.readFloat32Matrix(
            linecounts.numberOfLines * 9, linecounts.numberOfLineTensorArrays
        )

        self.log(f"Line Parts: {lines.linePartNames}")
        self.log(f"Line scalar arrays: {lines.lineScalarArrayNames}")
        self.log(f"Line tensor arrays: {lines.lineTensorArrayNames}")

        if linecounts.isLineSkewSaved:
            lines.lineSkewArray = self.br.readFloat32Vector(linecounts.numberOfLines)

        if self.params.isMassSaved:
            lines.lineMassArray = self.br.readFloat32Vector(linecounts.numberOfLines)

        if self.params.isNodeNumberingElementSaved:
            lines.lineRadiossIDs = self.br.readInt32Vector(linecounts.numberOfLines)

        # Hierarchy (unused)
        if self.params.isHierarchySaved:
            lines.partSubsets = self.br.readFloat32Vector(linecounts.numberOfLineParts)
            lines.partMaterials = self.br.readInt32Vector(linecounts.numberOfLineParts)
            lines.partProperties = self.br.readInt32Vector(linecounts.numberOfLineParts)

        return linecounts, lines

    def readHierarchy(self) -> HierarchyData:
        hierarchy = HierarchyData()
        if not self.params.isHierarchySaved:
            return hierarchy

        num_subsets = self.br.readInt32()
        for _ in range(num_subsets):
            h = HierarchyElement()
            h.subsetText = self.br.readString(STANDARD_STRING_SIZE)
            h.numParent = self.br.readInt32()
            
            num_subset_child = self.br.readInt32()
            h.subsetChild = self.br.readInt32Vector(num_subset_child)
            
            num_subpart_2D = self.br.readInt32()
            h.subset2D = self.br.readInt32Vector(num_subpart_2D)

            num_subpart_3D = self.br.readInt32()
            h.subset2D = self.br.readInt32Vector(num_subpart_3D)

            num_subpart_1D = self.br.readInt32()
            h.subset1D = self.br.readInt32Vector(num_subpart_1D)

            hierarchy.elements.append(h)

        nb_materials = self.br.readInt32()
        nb_properties = self.br.readInt32()
        hierarchy.materialNames = self.br.readStringVector(nb_materials, STANDARD_STRING_SIZE)
        hierarchy.materialTypes = self.br.readInt32Vector(nb_materials)
        hierarchy.propertiesNames = self.br.readStringVector(nb_properties, STANDARD_STRING_SIZE)
        hierarchy.propertiesTypes = self.br.readInt32Vector(nb_properties)

        return hierarchy
    
    def readTimeHistory(self) -> TimeHistoryData:
        th = TimeHistoryData()

        if not self.params.isNodeElementListForTimeHistory:
            return th

        nbNodesTH = self.br.readInt32()
        nbElts2DTH = self.br.readInt32()
        nbElts3DTH = self.br.readInt32()
        nbElts1DTH = self.br.readInt32()

        # TODO: unused. Only read to offset properly what is read afterwards
        th.nodesTH = self.br.readInt32Vector(nbNodesTH)
        th.nodesTHNames = self.br.readStringVector(nbNodesTH, STANDARD_STRING_SIZE)
        
        th.elems2DTH = self.br.readInt32Vector(nbElts2DTH)
        th.elems2DTHNames = self.br.readStringVector(nbElts2DTH, STANDARD_STRING_SIZE)
        
        th.elems3DTH = self.br.readInt32Vector(nbElts3DTH)
        th.elems3DTHNames = self.br.readStringVector(nbElts3DTH, STANDARD_STRING_SIZE)
        
        th.elems1DTH = self.br.readInt32Vector(nbElts1DTH)
        th.elems1DTHNames = self.br.readStringVector(nbElts1DTH, STANDARD_STRING_SIZE)
    
    def readSPH(self) -> SPHData:
        sph = SPHData()
        if not self.params.isSPHSaved:
            return sph

        nbElemsSPH = self.br.readInt32()
        nbPartsSPH = self.br.readInt32()
        nbEFuncsSPH = self.br.readInt32()
        nbTensSPH = self.br.readInt32()

        sph.sphConnectivity = self.br.readInt32Vector(nbElemsSPH)
        sph.sphDeletedElems = self.br.readInt8Vector(nbElemsSPH)

        sph.defParts = self.br.readInt32Vector(nbPartsSPH)
        sph.partText = self.br.readStringVector(nbPartsSPH, STANDARD_STRING_SIZE)

        self.log(f"SPH parts: {sph.partText}")

        sph.scalText = self.br.readStringVector(nbEFuncsSPH, 81)
        sph.eFunc = self.br.readFloat32Vector(nbEFuncsSPH * nbElemsSPH)

        sph.tensText = self.br.readStringVector(nbTensSPH, 81)
        sph.tensVal = self.br.readFloat32Vector(nbElemsSPH * nbTensSPH * 6)

        if self.params.isMassSaved:
            sph.sphMass = self.br.readFloat32Vector(nbElemsSPH)
        if self.params.isNodeNumberingElementSaved:
            sph.nodeNum = self.br.readInt32Vector(nbElemsSPH)
        if self.params.isHierarchySaved:
            sph.numParent = self.br.readInt32Vector(nbPartsSPH)
            sph.matPart = self.br.readInt32Vector(nbPartsSPH)
            sph.propPart = self.br.readInt32Vector(nbPartsSPH)

        return sph
    

    def log(self, *args, **kwargs):
        if self.enableLogging:
            print(*args, **kwargs)
