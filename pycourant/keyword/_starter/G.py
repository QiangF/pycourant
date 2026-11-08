from numpy.typing import NDArray
from ..common import *

#* /GRPART 
@dataclass
class Grpart(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/GRPART` is not implemented.")

    @property
    def keyword(self):
        return "/GRPART"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure


#* /GRQUAD 
@dataclass
class Grquad(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/GRQUAD` is not implemented.")

    @property
    def keyword(self):
        return "/GRQUAD"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure


#* /GRSH3N 
@dataclass
class Grsh3n(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/GRSH3N` is not implemented.")

    @property
    def keyword(self):
        return "/GRSH3N"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure

#* /GR
# ref. /*/SEG /Element
@dataclass
class Gr(Keyword):
    ID: int
    title: str
    dim: int | str
    # gmsh.model.getEntitiesForPhysicalGroup(dim, tag)
    # Return tags
    itemIDs: list | tuple | NDArray  # 1D
    unitID: int | None = None

    @property
    def keyword(self):
        match self.dim:
            case 0:
                result = f"/GRNOD/NODE/{self.ID}"
            case 1:
                result = f"/GRTRUS/TRUS/{self.ID}"
            case 2:
                result = f"/GRSHEL/SHEL/{self.ID}"
            case 3:
                result = f"/GRBRICK/BRICK/{self.ID}"
            case "grnod":
                result = f"/GRNOD/GRNOD/{self.ID}"

            
        if self.unitID is None:
            return result
        else:
            return f"{result}/{self.unitID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            VLSequenceOfAtomicField(IntField("itemIDs", 1)),
        ]
        return structure
