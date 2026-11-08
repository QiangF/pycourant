from ..common import *

#* /MPC 
@dataclass
class Mpc(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/MPC` is not implemented.")

    @property
    def keyword(self):
        return "/MPC"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = []

        return structure
