from ..common import *

#* /EIG 
@dataclass
class Eig(Keyword):
    """Defines the eigen modes and static modes computation for flexible bodies."""

    eigID: int
    eig_title: str
    trarot: str
    ifile: Literal[0, 1]
    cutfreq: float  # TODO: maybe check source code if cutfreq is indeed a float.
    nbloc: int
    grndID: int = 0
    grnd_bc: int = 0
    nmod: int = 100
    inorm: int = 0
    incv: int = 2
    freqmin: float = 0.045
    ipri: int = 0
    niter: int = 300
    tol: float = 0.0
    filename: str | None = None
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID is None:
            return f"/EIG/{self.eigID}"
        else:
            return f"EIG/{self.eigID}/{self.unitID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("eig_title", 1, 10),
            [
                IntField("grndID", 1),
                IntField("grnd_bc", 2),
                BoolField("trarot", 3, 6, [4, 5, 6, 8, 9, 10]),
                IntField("ifile", 4),
            ],
            [
                IntField("nmod", 1),
                IntField("inorm", 2),
                FloatField("cutfreq", 3),
                FloatField("freqmin", 5),
            ],
            [
                IntField("nbloc", 1),
                IntField("incv", 2),
                IntField("niter", 3),
                IntField("ipri", 4),
                FloatField("tol", 5),
            ],
        ]

        if self.ifile == 1:
            structure.append(StringField("filename", 1, 10))

        return structure


#* /Element
# ref. /*/SEG

@dataclass
class Element(Keyword):
    """Defines a hexahedral solid element or thick shell element with 8 nodes.
    The element type and formulation are defined on the /PROP card.
    """
    # id is partID
    ID: int
    dim: int
    # gmsh.model.mesh.getElements
    # Return `elementTypes', `elementTags', `nodeTags'
    items: NDArray
    analysis_type: str = '3D' # 2D or 3D
    unitID: int | None = None

    def __post_init__(self) -> None:
            self._text_alignment = {
                # Note: specifying an alignment for a `BoolField` has no effect
                # because the string representation of a `BoolField` is always
                # exactly 10 characters (so, as wide as the field). Add it here,
                # because it allows us to process the fields regardless of its
                # specific type.
                BoolField: TextAlignment.CENTER,
                FloatField: TextAlignment.RIGHT,
                IntField: TextAlignment.RIGHT,
                # StringField: TextAlignment.CENTER,
                StringField: TextAlignment.LEFT,
            }

            # Both starter and engine keywords can be treated in the same way if
            # the keyword category equals `KeywordCategory.GENERIC`. If either a
            # starter or an engine keyword needs special treatment, use
            # `KeywordCategory.STARTER` or `KeywordCategory.ENGINE` respectively.
            self.category: KeywordCategory = KeywordCategory.GENERIC
            match self.dim:
                case 3:
                    self.node_n = 8
                    self.name = 'Brick'
                case 2:
                    self.node_n = 4
                    if self.analysis_type=='2D':
                        # 进行 2D 分析时需将单元类型从 Shell 改为 QUAD
                        self.name = 'Quad'
                    else:
                        self.name = 'Shell'
                    self.thick = 0,
                    self.phi_s = 0, 
                case 1:
                    self.node_n = 2
                    self.name = 'Truss'

    @property
    def structure(self):
        item_definition = []
        for i in range(self.node_n + 1):
            item_definition.append(IntField(f"items:|{i}", i + 1),)
        if self.dim == 2:
            item_definition.extend([FloatField(f"phi_s", 7), FloatField(f"thick", 9),])

        structure: KeywordStructureType = [
            ArrayOfAtomicFields(item_definition)
        ]
        return structure

#* /END
@dataclass
class End(Keyword):
    """Declares that end of input deck has been reached."""

    @property
    def keyword(self):
        return "/END"
