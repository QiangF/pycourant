import dataclasses
import numpy as np


@dataclasses.dataclass
class HeaderParameters:
    time: float = 0.0
    timeDescription: str = ""
    animationDescription: str = ""
    runDescription: str = ""
    isMassSaved: bool = False
    isNodeNumberingElementSaved: bool = False
    is3DGeometrySaved: bool = False
    is1DGeometrySaved: bool = False
    isHierarchySaved: bool = False
    isNodeElementListForTimeHistory: bool = False
    isNewSkewForTensor2DSaved: bool = False
    isSPHSaved: bool = False
    unused1: bool = False
    unused2: bool = False


@dataclasses.dataclass
class NodesAndQuadsHeaders:
    numberOfNodes: int = 0
    numberOfQuads: int = 0
    numberOfQuadParts: int = 0
    numberOfNodalScalarArrays: int = 0
    numberOfQuadScalarArrays: int = 0
    numberOfNodalVectorArrays: int = 0
    numberOfQuadTensorArrays: int = 0
    numberOfSkews: int = 0


@dataclasses.dataclass
class NodesData:
    skews: list[float] = dataclasses.field(default_factory=list)
    nodeNorms: list[float] = dataclasses.field(default_factory=list)
    nodeCoordinates: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    nodeScalarArrayNames: list[str] = dataclasses.field(default_factory=list)
    nodeScalarArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    nodeVectorArrayNames: list[str] = dataclasses.field(default_factory=list)
    nodeVectorArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    nodeMassArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    nodeRadiossIDs: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    partSubsets: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    partMaterials: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    partProperties: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )


@dataclasses.dataclass
class QuadsData:
    quadConnectivity: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    quadErosionArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    quadPartLastIndices: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    quadScalarArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    quadTensorArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    quadMassArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    quadRadiossIDs: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    quadPartNames: list[str] = dataclasses.field(default_factory=list)
    quadScalarArrayNames: list[str] = dataclasses.field(default_factory=list)
    quadTensorArrayNames: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class HexahedraHeaders:
    numberOfHexahedra: int = 0
    numberOfhexaParts: int = 0
    numberOfhexaScalarArrays: int = 0
    numberOfhexaTensorArrays: int = 0


@dataclasses.dataclass
class HexahedraData:
    hexaConnectivity: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    hexaErosionArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    hexaPartLastIndices: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    hexaScalarArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    hexaScalarArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    hexaMassArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    hexaRadiossIDs: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    partSubsets: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    partMaterials: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    partProperties: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    hexaPartNames: list[str] = dataclasses.field(default_factory=list)
    hexaScalarArrayNames: list[str] = dataclasses.field(default_factory=list)
    hexaTensorArrayNames: list[str] = dataclasses.field(default_factory=list)
    hexaTensorArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )


@dataclasses.dataclass
class LinesHeaders:
    numberOfLines: int = 0
    numberOfLineParts: int = 0
    numberOfLineScalarArrays: int = 0
    numberOfLineTensorArrays: int = 0
    isLineSkewSaved: bool = False


@dataclasses.dataclass
class LinesData:
    lineConnectivity: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    lineErosionArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    linePartLastIndices: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    lineScalarArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    lineTensorArrays: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    lineSkewArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    lineMassArray: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    lineRadiossIDs: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    partSubsets: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    partMaterials: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    partProperties: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )

    linePartNames: list[str] = dataclasses.field(default_factory=list)
    lineScalarArrayNames: list[str] = dataclasses.field(default_factory=list)
    lineTensorArrayNames: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class HierarchyElement:
    numParent: int = 0
    subsetText: str = ""
    subsetChild: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    subset1D: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    subset2D: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    subset3D: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))


@dataclasses.dataclass
class HierarchyData:
    elements: list[HierarchyElement] = dataclasses.field(default_factory=list)
    materialNames: list[str] = dataclasses.field(default_factory=list)
    materialTypes: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    propertiesNames: list[str] = dataclasses.field(default_factory=list)
    propertiesTypes: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )


@dataclasses.dataclass
class TimeHistoryData:
    nodesTH: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    nodesTHNames: list[str] = dataclasses.field(default_factory=list)

    elems1DTH: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    elems1DTHNames: list[str] = dataclasses.field(default_factory=list)

    elems2DTH: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    elems2DTHNames: list[str] = dataclasses.field(default_factory=list)

    elems3DTH: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    elems3DTHNames: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class SPHData:
    sphConnectivity: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    sphDeletedElems: np.ndarray = dataclasses.field(
        default_factory=lambda: np.ndarray((0))
    )
    defParts: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    partText: list[str] = dataclasses.field(default_factory=list)
    
    scalText: list[str] = dataclasses.field(default_factory=list)
    eFunc: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))

    tensText: list[str] = dataclasses.field(default_factory=list)
    tensVal: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    sphMass: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    nodeNum: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))

    numParent: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    matPart: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))
    propPart: np.ndarray = dataclasses.field(default_factory=lambda: np.ndarray((0)))


@dataclasses.dataclass
class AnimData:
    # Metadata
    global_params: HeaderParameters
    nodes_quads_params: NodesAndQuadsHeaders
    hexahedra_params: HexahedraHeaders
    lines_params: LinesHeaders
    th: TimeHistoryData

    # Actual data
    nodes: NodesData
    quads: QuadsData
    hexas: HexahedraData
    lines: LinesData
    sph: SPHData

    hierarchy: HierarchyData
