from ..common import *

#* /INTER/TYPE5
@dataclass
class InterType5(Keyword):
    ID: int
    title:str
    grndID_s:int
    surfID_m:int
    Ibag:int = 0
    Idel:int = 0

    Stfac:float = 0
    fric:float = 0.3
    gap:float = 0
    Tstart:float = 0
    Tstop:float = 0

    Ibc:Sequence[Literal[0, 1]] = (0, 0, 0)
    Irm:int = 0
    Inacti:float = 0

    Ifric:int = 0
    Ifiltr:int = 0
    Xfreq:float = 0
    sensID:int = 0
    Ptlim:float = 0

    C1:float = 0
    C2:float = 0
    C3:float = 0
    C4:float = 0
    C5:float = 0

    C6:float = 0
    unitID:int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField("grndID_s", 1),
                IntField("surfID_m", 2),
                IntField("Ibag", 7),
                IntField("Idel", 8),
            ],
            [
                FloatField("Stfac", 1),
                FloatField("fric", 3),
                FloatField("gap", 5),
                FloatField("Tstart", 7),
                FloatField("Tstop", 9),
            ],
            [
                BoolField("Ibc", 1, 3, [8, 9, 10]),
                IntField("Irm", 3),
                FloatField("Inacti", 4),
            ],
            [
                IntField("Ifric", 1),
                IntField("Ifiltr", 2),
                FloatField("Xfreq", 3),
                IntField("sensID", 6),
                FloatField("Ptlim", 7),
            ],
        ]
        if self.Ifric > 0:
            structure.append([
                FloatField("C1", 1),
                FloatField("C2", 3),
                FloatField("C3", 5),
                FloatField("C4", 7),
                FloatField("C5", 9),
            ], )
            structure.append([
                FloatField("C6", 1),
            ], )
        return structure

#* /INTER/TYPE7
@dataclass
class InterType7(Keyword):
    ID:int
    title:str
    grndID_s:int
    surfID_m:int
    fric:float
    Istf:int = 0
    Igap:int = 0
    Ibag:int = 0
    Idel:int = 0
    Icurv:int = 0
    Iadm:int = 0
    gap_max:float = 0
    gap_min:float = 0.1
    Fpen_max:float = 0
    st_min:float = 0
    st_max:float = 0
    dt_min:float = 0
    Tstart:float = 0
    Tstop:float = 0
    mesh_size:float = 0
    Ithe:Literal[0, 1] = 0
    Itied:Literal[0, 1, 2] = 0
    Irem_gap:Literal[0, 1, 2] = 0
    Irem_i2:int = 0
    Fscale_gap:float = 0
    st_fac:float = 0
    Ibc:Sequence[Literal[0, 1]] = (0, 0, 0)
    Inacti:float = 0
    vis_s:float = 0
    vis_f:float = 0
    bumult:float = 0
    Ifric:int = 0
    Ifiltr:int = 0
    Xfreq:float = 0
    Iform:int = 0
    sensID:int = 0
    fctIDf:int = 0
    ascale_f:float = 0
    fctID_k:int = 0
    # heat exchange coefficient
    Kthe:float = 0
    # interface temperature
    Tint:float = 0
    Ithe_form:int = 0
    ascale_k:float = 0
    # radiation factor
    Frad:float = 0
    # max distance for radiation
    Drad:float = 0
    # friction heat factor of secondary
    fheat_s:float = 0
    # friction heat factor of main
    fheat_m:float = 0
    unitID:int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField("grndID_s", 1),
                IntField("surfID_m", 2),
                IntField("Istf", 3),
                IntField("Ithe", 4),
                IntField("Igap", 5),
                IntField("Ibag", 7),
                IntField("Idel", 8),
                IntField("Icurv", 9),
                IntField("Iadm", 10),   
            ],
            [
                FloatField("Fscale_gap", 1),
                FloatField("gap_max", 3),
                FloatField("Fpen_max", 5),
            ],
            [
                FloatField("st_min", 1),
                FloatField("st_max", 3),
                FloatField("mesh_size", 5),
                FloatField("dt_min", 7),
                IntField("Irem_gap", 9),
                IntField("Irem_i2", 10),
            ]]
        structure.extend([
            [
            FloatField("st_fac", 1),
            FloatField("fric", 3),
            FloatField("gap_min", 5),
            FloatField("Tstart", 7),
            FloatField("Tstop", 9),
            ],
            [
                BoolField("Ibc", 1, 3, [8, 9, 10]),
                FloatField("Inacti", 3),
                FloatField("vis_s", 5),
                FloatField("vis_f", 7),
                FloatField("bumult", 9),
            ],
            [
                IntField("Ifric", 1),
                IntField("Ifiltr", 2),
                FloatField("Xfreq", 3),
                IntField("Iform", 5),
                IntField("sensID", 6),
                IntField("fctIDf", 7),
                FloatField("ascale_f", 8),
            ],
        ])

        if self.Ithe > 0:
            structure.append([
                FloatField("Kthe", 1),
                IntField("fctID_k", 3),
                FloatField("Tint", 5),
                IntField("Ithe_form", 7),
                FloatField("ascale_k", 8),
            ], )
            structure.append([
                FloatField("Frad", 1),
                FloatField("Drad", 3),
                FloatField("fheat_s", 5),
                FloatField("fheat_m", 7),
            ], )
        return structure

#* /INTER/TYPE11
@dataclass
class InterType11(Keyword):
    ID: int
    title:str
    lineID_s:int
    lineID_m:int
    Istf:int = 0
    Ithe:Literal[0, 1] = 0
    Igap:int = 0
    Irem_gap:Literal[0, 1, 2] = 0
    Idel:int = 0

    st_min:float = 0
    st_max:float = 0
    mesh_size:float = 0
    dt_min:float = 0
    Iform:int = 0
    sensID:int = 0

    st_fac:float = 0
    fric:float = 0.3
    gap_min:float = 0.1
    Tstart:float = 0
    Tstop:float = 0

    Ibc:Sequence[Literal[0, 1]] = (0, 0, 0)
    Inacti:float = 0
    vis_s:float = 0
    vis_f:float = 0
    bumult:float = 0

    fricID:int = 0

    # heat exchange coefficient
    Kthe:float = 0
    fctIDk:int = 0
    Ascale_k:float = 0
    # interface temperature
    Tint:float = 0
    Ithe_form:int = 0

    # radiation factor
    Frad:float = 0
    # max distance for radiation
    Drad:float = 0

    unitID:int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField("lineID_s", 1),
                IntField("lineID_m", 2),
                IntField("Istf", 3),
                IntField("Ithe", 4),
                IntField("Igap", 5),
                IntField("Irem_gap", 7),
                IntField("Idel", 8),
            ],
            [
                FloatField("st_min", 1),
                FloatField("st_max", 3),
                FloatField("mesh_size", 5),
                FloatField("dt_min", 7),
                IntField("Iform", 9),
                IntField("sensID", 10),
            ],
            [
                FloatField("st_fac", 1),
                FloatField("fric", 3),
                FloatField("gap_min", 5),
                FloatField("Tstart", 7),
                FloatField("Tstop", 9),
            ],
            [
                BoolField("Ibc", 1, 3, [8, 9, 10]),
                FloatField("Inacti", 4),
                FloatField("vis_s", 5),
                FloatField("vis_f", 7),
                FloatField("bumult", 9),
            ]
        ]
        if self.Ithe > 0:
            structure.append([
                FloatField("Kthe", 1),
                IntField("fctIDk", 3),
                FloatField("Ascale_k", 4),
                FloatField("Tint", 6),
                IntField("Ithe_form", 8),
            ], )
            structure.append([
                FloatField("Frad", 1),
                FloatField("Drad", 3),
            ], )
        return structure
