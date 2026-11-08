from ..common import *

#* Include
@dataclass
class Include(Keyword):
    file: str

    @property
    def keyword(self):
        return f"#INCLUDE {self.file}"

#* /IMPDISP
@dataclass
class Impdisp(Keyword):
    ID: int
    title: str
    fctID_t: int
    dir: str
    grndID: int
    skewID: int = 0
    sensID: int = 0
    Icoor: int = 0
    Ascale_x: float = 1.0
    Fscale_y: float = 1.0
    Tstart: float = 0
    Tstop: float = 0
    unitID: int | None = None

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField('fctID_t', 1),
                StringField('dir', 2, 1, alignment=TextAlignment.RIGHT),
                IntField('skewID', 3),
                IntField('sensID', 4),
                IntField('grndID', 5),
                IntField('Icoor', 7),
            ],
            [
                FloatField('Ascale_x', 1),
                FloatField('Fscale_y', 3),
                FloatField('Tstart', 5),
                FloatField('Tstop', 7),
            ],
        ]

        return structure

#* /IMPVEL
@dataclass
class Impvel(Keyword):
    ID: int
    title: str
    fctID_t: int
    dir: str
    grndID: int
    frameID: int = 0
    skewID: int = 0
    sensID: int = 0
    Icoor: int = 0
    Ascale_x: float = 1.0
    Fscale_y: float = 1.0
    Tstart: float = 0
    Tstop: float = 0
    unitID: int | None = None

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField('fctID_t', 1),
                StringField('dir', 2, 1, alignment=TextAlignment.RIGHT),
                IntField('skewID', 3),
                IntField('sensID', 4),
                IntField('grndID', 5),
                IntField('frameID', 6),
                IntField('Icoor', 7),
            ], 
            [
                FloatField('Ascale_x', 1),
                FloatField('Fscale_y', 3),
                FloatField('Tstart', 5),
                FloatField('Tstop', 7),
            ], 
        ]

        return structure


#* /IMPTEMP
@dataclass
class Imptemp(Keyword):
    ID: int
    title: str
    fctID_t: int
    grndID: int
    sensID: int = 0
    Ascale_x: float = 1.0
    Fscale_y: float = 1.0
    Tstart: float = 0
    Tstop: float = 0
    unitID: int | None = None

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                IntField('fctID_t', 1),
                IntField('sensID', 2),
                IntField('grndID', 3),
            ], 
            [
                FloatField('Ascale_x', 1),
                FloatField('Fscale_y', 3),
                FloatField('Tstart', 5),
                FloatField('Tstop', 7),
            ],
        ]

        return structure

#* /INIVEL
@dataclass
class Inivel(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/INIVEL` is not implemented.")

    @property
    def keyword(self):
        return "/INIVEL"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure

#* /INITEMP
@dataclass
class Initemp(Keyword):
    ID: int
    title: str
    grndID: int
    T0: float
    fld_type: int = 0
    
    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                FloatField('T0', 1),
                IntField('grndID', 3),
                IntField('fld_type', 4),
            ],
        ]

        return structure


#* /INIVEL/NODE
@dataclass
class InivelNode(Keyword):
    attr1: int
    attr2: float

    def __post_init__(self):
        raise NotImplementedError("Keyword `/INIVEL/NODE` is not implemented.")

    @property
    def keyword(self):
        return "/INIVEL/NODE"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure

#* INIVEL/TRA
@dataclass
class InivelTra(Keyword):
    ID: int
    title: str
    grndID: int
    vx: float
    vy: float
    vz: float
    skewID: int = 0
    unitID: int | None = None

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            [
                FloatField('vx', 1),
                FloatField('vy', 3),
                FloatField('vz', 5),
                IntField('grndID', 7),
                IntField('skewID', 8),
            ], 
        ]

        return structure

#* /IOFLAG
@dataclass
class Ioflag(Keyword):
    Ipri: int = 0
    Igtyp: int = 0
    Ioutp: int = 0
    Ioutyy: int = 0
    Irootyy: int = 0
    Idrot: int = 0

    @property
    def structure(self):
        structure = [
            [
                IntField('Ipri', 1),
                # IntField('Igtyp', 3),
                IntField('Ioutp', 4),
                IntField('Ioutyy', 5),
                IntField('Irootyy', 6),
                IntField('Idrot', 7), 
            ]
        ]

        return structure
