from numpy.typing import NDArray
from ..common import *

#* /RADIATION 
@dataclass
class Radiation(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/RADIATION` is not implemented.")

    @property
    def keyword(self):
        return "/RADIATION"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure

#* /RBODY 
@dataclass
class Rbody(Keyword):
    ID: int
    title: str
    nodeID: int
    grndID: int
    surfID: int
    Jxx: float = 0
    Jyy: float = 0
    Jzz: float = 0
    Jxy: float = 0
    Jyz: float = 0
    Jxz: float = 0
    mass: float = 0
    Ifail: Literal[0, 1] | None = None
    Ioptoff: Literal[0, 1] = 0
    Ispher: Literal[0, 1, 2, 3] = 0
    sensID: int = 0
    skewID: int = 0
    Ikrem: Literal[0, 1] = 0
    Icog: Literal[0, 1, 2, 3, 4] = 2
    unitID: int | None = None

    @property
    def pre_conditions(self) -> KeywordPreconditionsType:
        return []
    
    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField('nodeID', 1),
                IntField('sensID', 2),
                IntField('skewID', 3),
                IntField('Ispher', 4),
                FloatField('mass', 5),
                IntField('grndID', 7),
                IntField('Ikrem', 8),
                IntField('Icog', 9),
                IntField('surfID', 10),
            ], 
            [
                FloatField('Jxx', 1),
                FloatField('Jyy', 3),
                FloatField('Jzz', 5),
            ], 
            [
                FloatField('Jxy', 1),
                FloatField('Jyz', 3),
                FloatField('Jxz', 5),
            ],
            IntField('Ioptoff', 1), 
        ]

        return structure




