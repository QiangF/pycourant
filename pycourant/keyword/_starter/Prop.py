from ..common import *

#* /PROP/TYPE1(Shell)
@dataclass
class PropShell(Keyword):
    ID: int
    title: str
    thick: float
    Ishell: int = 0
    Ismstr: int = 0
    Ish3n: int = 0
    Idril: int = 0
    Ipinch: int = 0
    Ithick: int = 0
    Iplas: int = 0
    N: int = 0
    Pthick_fail: float = 0
    hm: float = 0
    hf: float = 0
    hr: float = 0
    dm: float = 0.0
    dn: float = 0.0
    Ashear: float = 0.0
    unitID: int | None = None

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField("Ishell", 1),
                IntField("Ismstr", 2),
                IntField("Ish3n", 3),
                IntField("Idril", 4),
                IntField("Ipinch", 5),
                FloatField("Pthick_fail", 7),
            ], 
            [
                FloatField("hm", 1),
                FloatField("hf", 3),
                FloatField("hr", 5),
                FloatField("dm", 7),
                FloatField("dn", 9),
            ],
            [
                IntField("N", 1),
                FloatField("thick", 3),
                FloatField("Ashear", 5),
                IntField("Ithick", 8),
                IntField("Iplas", 9),
            ]
        ]

        return structure

#* /PROP/TYPE8 
@dataclass
class PropType8(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/PROP/TYPE8` is not implemented.")

    @property
    def keyword(self):
        return "/PROP/TYPE8"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure


#* /PROP/TYPE14(Solid)
@dataclass
class PropSolid(Keyword):
    ID: int
    title: str
    Icpre: Literal[-1, 0, 1, 2, 3]

    IndentationError: Literal[1, 2, 3, 4, 10, 11, 12] = 4
    Itetra10: Literal[0, 1000, 2, 3] | None = None
    # Itetra
    Itetra4: Literal[0, 1000, 1, 3] = 0
    Iframe: Literal[-1, 0, 1, 2] = 0
    Inpts: int = 0
    # Inpts: Sequence[int] = [2, 2, 2]
    Isolid: Literal[0, 1, 2, 14, 16, 17, 18, 24] = 1
    Ismstr: Literal[-1, 0, 1, 2, 3, 4, 10, 11, 12] = 4
    dn: float = 0.0
    qa: float = 0.0
    qb: float = 0.05
    h: float = 0.0
    lambda_v: float = 0.0
    mu_v: float = 0.0
    # dt_min
    dt_min: float = 0.0
    # 2022
    Istrain:int = 0
    IHKT:int = 0

    # 2025
    vdef_min: float = 0.0
    vdef_max: float = 0.0
    aps_max: float = 0.0
    col_min: float = 0.0

    ndir: int | None = None
    sphpartID: int | None = None
    i_control: int | None = None
    unitID: int | None = None

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField("Isolid", 1),
                IntField("Ismstr", 2),
                IntField("Icpre", 4),
                IntField("Itetra10", 5),
                IntField("Inpts", 6),
                IntField("Itetra4", 7),
                IntField("Iframe", 8),
                FloatField("dn", 9),
            ], 
            [
                FloatField("qa", 1),
                FloatField("qb", 3),
                FloatField("h", 5),
                FloatField("lambda_v", 7),
                FloatField("mu_v", 9),
            ],
            [
                FloatField("dt_min", 1),
                FloatField("vdef_min", 3),
                FloatField("vdef_max", 5),
                FloatField("aps_max", 7),
                FloatField("col_min", 9),
            ],
            [
                IntField("ndir", 1),
                IntField("sphpartID", 2),
                IntField("i_control", 3),
            ]
        ]

        return structure
