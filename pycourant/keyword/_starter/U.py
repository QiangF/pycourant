from ..common import *

#* /UNIT 
@dataclass
class Unit(Keyword):
    """Defines a local unit system for the keywords listed below."""

    unit_title: str
    mass_unit: VALID_MASS_LITERALS
    length_unit: VALID_LENGTH_LITERALS
    time_unit: VALID_TIME_LITERALS
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/UNIT/{self.unitID}"
        else:
            return "/UNIT"

    @property
    def pre_conditions(self):
        conditions = [
            (
                self.mass_unit in get_args(VALID_MASS_LITERALS),
                f"Invalid input mass unit `{self.mass_unit}`.",
            ),
            (
                self.length_unit in get_args(VALID_LENGTH_LITERALS),
                f"Invalid input length unit `{self.length_unit}`.",
            ),
            (
                self.time_unit in get_args(VALID_TIME_LITERALS),
                f"Invalid input time unit `{self.time_unit}`.",
            ),
        ]

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("unit_title", 1, 10),
            [
                StringField("mass_unit", 1, 2),
                StringField("length_unit", 3, 2),
                StringField("time_unit", 5, 2),
            ],
        ]

        return structure


#* /UPWIND 
@dataclass
class Upwind(Keyword):
    """Describes the upwind coefficient."""

    eta_1: float = 1.0
    eta_2: float = 1.0
    eta_3: float = 1.0

    @property
    def keyword(self):
        return "/UPWIND"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [
                FloatField("eta_1", 1),
                FloatField("eta_2", 3),
                FloatField("eta_3", 5),
            ]
        ]

        return structure
