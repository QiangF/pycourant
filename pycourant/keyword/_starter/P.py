from ..common import *

#* /PART 
@dataclass
class Part(Keyword):
    ID: int
    title: str
    matID: int
    subsetID: int
    thick: float | None = None
    unitID: int | None = None
    propID: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()

    @property
    def pre_conditions(self) -> KeywordPreconditionsType:
        return []

    @property
    def structure(self):
        data: List = [
            IntField("propID", 1),
            IntField("matID", 2),
            IntField("subsetID", 3)
        ]
        if self.thick:
            data.append(FloatField("thick", 4))

        structure: KeywordStructureType = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
        ]

        structure.append(data)

        return structure 


