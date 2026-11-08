from numpy.typing import NDArray
from ..common import *

#* /HEAT/MAT 
@dataclass
class HeatMat(Keyword):
    ID: int
    # iform deprecated in 2025
    # iform: Literal[0, 1] = 0
    T0: float = 300
    rho0_Cp: float = 0
    # thermal conductivity coeff
    AS: float | None = None
    BS: float | None = None
    T1: float = 1e20
    AL: float | None = None
    BL: float | None = None
    # ETA (η): The plastic heat fraction coefficient
    EFRAC: float = 1.0
    unitID: int | None = None

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [FloatField("T0", 1), FloatField("rho0_Cp", 3), FloatField("AS", 5), FloatField("BS", 7)],
            [FloatField("T1", 1), FloatField("AL", 3), FloatField("BL", 5), FloatField("EFRAC", 7),],
        ]

        return structure
