from ..common import *

#* /*/SEG
# ref. /GR /Element
@dataclass
class Seg(Keyword):
    ID: int
    title: str
    dim: int
    elemIDs: list | tuple | NDArray # 1D
    nodeIDs: list | tuple | NDArray  # 1D
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
                case 2:
                    self.node_n = 4
                    self.name = 'SurfSeg'
                case 1:
                    if self.analysis_type=='2D':
                        self.name = 'SurfSeg'
                    else:
                        self.name = 'LineSeg'
                    self.node_n = 2

    
    @property
    def structure(self):
        self.nids = np.reshape(self.nodeIDs, (-1, self.node_n))
        node_def = [IntField("elemIDs", 1),]
        for i in range(self.node_n):
            node_def.append(IntField(f"nids:|{i}", i + 2),)
            
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            ArrayOfAtomicFields(node_def)
        ]
        return structure


#* /SHELL
# see /Element

#* /SPMD
@dataclass
class Spmd(Keyword):
    Domdec: int = 0
    Nproc: int = 0
    Dkword: int = 0
    Nthread: int = 0

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [
                IntField("Domdec", 1),
                IntField("Nproc", 2),
                IntField("Dkword", 4),
                IntField("Nthread", 6),
             ]
        ]

        return structure

#* /SUBSET
@dataclass
class Subset(Keyword):
    ID: int
    title: str
    subIDs: List[int]

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def pre_conditions(self) -> KeywordPreconditionsType:
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            VLSequenceOfAtomicField(IntField("subIDs", 1)),
        ]

        return structure

#* /SURF
@dataclass
class Surf(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/SURF` is not implemented.")

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure

#* /SURF/GRSHEL
@dataclass
class SurfGrshel(Keyword):
    ID: int
    title: str
    itemIDs: List[int]
    unitID: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def pre_conditions(self) -> KeywordPreconditionsType:
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            VLSequenceOfAtomicField(IntField("itemIDs", 1)),
        ]

        return structure

#* /SURF/SEG
# see /SEG

#* /SURF/SURF
@dataclass
class SurfSurf(Keyword):
    ID: int
    title: str
    itemIDs: List[int]
    unitID: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def pre_conditions(self) -> KeywordPreconditionsType:
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            VLSequenceOfAtomicField(IntField("itemIDs", 1)),
        ]

        return structure
