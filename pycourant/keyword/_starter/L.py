from ..common import *

#* /LOAD/PRESSURE
@dataclass
class LoadPressure(Keyword):
    ID: int
    title:str
    surfID:int
    fctID:int
    Ascale_x: float = 1.0
    Fscale_y: float = 1.0
    unitID:int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField("surfID", 1),
            ],
            [
                IntField("fctID", 1),
                FloatField('Ascale_x', 3),
                FloatField('Fscale_y', 5),
            ],
        ]
        return structure
