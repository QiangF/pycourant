from ..common import *

#* /KEY 
@dataclass
class Key(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/KEY` is not implemented.")

    @property
    def keyword(self):
        return "/KEY"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure
