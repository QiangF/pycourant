from ..common import *

#* /NBCS 
@dataclass
class Nbcs(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/NBCS` is not implemented.")

    @property
    def keyword(self):
        return "/NBCS"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = []

        return structure


#* /NODE
# ref. /SEG
@dataclass
class Node(Keyword):
    ids: NDArray
    values: NDArray
    unitID: int | None = None

    @property
    def structure(self):
        node_def = [IntField("ids", 1),]
        for i in range(3):
            node_def.append(FloatField(f"values:|{i}", i * 2 + 2),)

        structure: KeywordStructureType = [
            ArrayOfAtomicFields(node_def)
        ]
        return structure

#* /PARAMETER 
@dataclass
class Parameter(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/PARAMETER` is not implemented.")

    @property
    def keyword(self):
        return "/PARAMETER"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = []

        return structure
