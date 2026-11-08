from numpy.typing import NDArray
from ..common import *

#* /FAIL/JOHNSON
@dataclass
class FailJohnson(Keyword):
    ID: int
    D1: float
    D2: float
    D3: float
    D4: float
    D5: float
    epsilon_dot_0: float
    Ifail_sh: int = 1
    Ifail_so: int = 1
    EPSFmin: float = 0
    Dadv: int = 1
    Ixfem: int = 1
    failID: int | None = None
    unitID: int | None = None

    @property
    def pre_conditions(self):
        return []
    @property
    def structure(self):
        structure: KeywordStructureType = [
            [FloatField("D1", 1), FloatField("D2", 3), FloatField("D3", 5), FloatField("D4", 7), FloatField("D5", 9),],
            [FloatField("epsilon_dot_0", 1), IntField("Ifail_sh", 3), IntField("Ifail_so", 4), FloatField("EPSFmin", 5), FloatField("Dadv", 7), IntField("Ixfem", 10)],
        ]
        if self.failID != None:
            structure.append(IntField("failID", 1))
        return structure

# 对于超出函数定义范围的自变量，系统会采用线性外推（Linear Extrapolation）
# 会顺着由最后两个已知点所确定的斜率（Slope）一直延伸计算下去
#* /FUNCT
@dataclass
class Funct(Keyword):
    ID: int
    title: str
    x_y: list | tuple | NDArray

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def pre_conditions(self) -> KeywordPreconditionsType:
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
        ]

        structure.extend(
            [
                ArrayOfAtomicFields(
                    [
                        FloatField("x_y:|0", 1),
                        FloatField("x_y:|1", 3),
                    ]
                ),
            ]
        )

        return structure
