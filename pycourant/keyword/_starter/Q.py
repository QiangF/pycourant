from ..common import *

#* /QUAD 
@dataclass
class Quad(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/QUAD` is not implemented.")

    @property
    def keyword(self):
        return "/QUAD"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure
