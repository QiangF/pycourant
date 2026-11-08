from ..common import *

#* /ACCEL
@dataclass
class Accel(Keyword):
    """Defines accelerometers using a node and a skew system."""

    ID: int
    title: str
    nodeID: int
    skewID: int
    f_cut: float
    unitID: int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [IntField("nodeID", 1), IntField("skewID", 2), FloatField("f_cut", 4)],
        ]

        return structure

#* /ACTIV
@dataclass
class Activ(Keyword):
    """Describes the deactivation/activation of element groups."""

    ID: int
    title: str
    sensID: int
    grbricID: int
    grquadID: int
    grshelID: int
    grtrusID: int
    grbeamID: int
    grsprID: int
    grsh3nID: int
    i_form: Literal[1, 2] = 1
    unitID: int | None = None
    t_start: None | float = None
    t_stop: float = 1e30

    @property
    def pre_conditions(self):
        i_form_valid = True if self.i_form in (1, 2) else False

        conditions = [
            (i_form_valid, f"Pre-condition `i_form in [1, 2]` not met."),
        ]

        if self.i_form == 2:
            t_start_is_present = True if (self.i_form == 2 and self.t_start) else False

            conditions.append(
                (
                    t_start_is_present,
                    "If `i_form == 2` then `t_start` must be provided.",
                ),
            )
        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("sensID", 1),
                IntField("grbricID", 2),
                IntField("grquadID", 3),
                IntField("grshelID", 4),
                IntField("grtrusID", 5),
                IntField("grbeamID", 6),
                IntField("grsprID", 7),
                IntField("grsh3nID", 8),
                IntField("i_form", 10),
            ],
        ]

        if self.i_form == 2:
            structure.append([FloatField("t_start", 1), FloatField("t_stop", 3)])

        return structure


#* /ADMAS
@dataclass
class Admas(Keyword):
    """Assign additional non-structural mass to nodes or a group of nodes."""

    admasID: int
    admas_title: str
    type: Literal[0, 1, 2, 3, 4, 5, 6, 7]
    unitID: int | None = None
    mass: None | float | List[float] = None
    grndID: int | None = None
    surfID: int | None = None
    grpartID: int | None = None
    mass_per_unit_area: None | float = None
    nodeID: None | List[int] = None
    partID: None | List[int] = None
    iflag: None | Literal[0, 1] | List[Literal[0, 1]] = 0

    @property
    def keyword(self):
        if self.unitID is None:
            return f"/ADMAS/{self.type}/{self.admasID}"
        else:
            return f"/ADMAS/{self.type}/{self.admasID}/{self.unitID}"

    @property
    def pre_conditions(self):
        print(self.type)
        conditions: KeywordPreconditionsType = [
            (
                self.type in {0, 1, 2, 3, 4, 5, 6, 7},
                "Pre-condition `type in [0, 1, 2, 3, 4, 5, 6, 7]` not met.",
            ),
        ]

        if self.type in {3, 4}:
            conditions.append(
                (
                    self.iflag in {0, 1},
                    "Pre-condition `iflag in [0, 1]` not met.",
                ),
            )

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [StringField("admas_title", 1, 10)]

        if self.type in (0, 1):
            structure.append([FloatField("mass", 1), IntField("grndID", 3)])

        elif self.type == 2:
            structure.append(
                [FloatField("mass_per_unit_area", 1), IntField("surfID", 3)]
            )

        elif self.type in (3, 4):
            structure.append(
                [
                    FloatField("mass", 1),
                    IntField("grpartID", 3),
                    IntField("iflag", 4),
                ]
            )

        elif self.type == 5:

            structure.append(
                ArrayOfAtomicFields([FloatField("mass", 1), IntField("nodeID", 3)])
            )

        elif self.type in (6, 7):
            structure.append(
                ArrayOfAtomicFields(
                    [
                        FloatField("mass", 1),
                        IntField("partID", 3),
                        IntField("iflag", 4),
                    ]
                )
            )

        return structure


#* /ADMESH/GLOBAL 
@dataclass
class AdmeshGlobal(Keyword):
    """Defines the global parameters for adaptive meshing."""

    levelmax: int
    ladmrule: Literal[0, 1]
    time_delay: float
    idt: Literal[0, 1]

    @property
    def keyword(self):
        return "/ADMESH/GLOBAL"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [
                IntField("levelmax", 1),
                IntField("ladmrule", 2),
                FloatField("time_delay", 3),
                IntField("idt", 5),
            ]
        ]

        return structure


#* /ADMESH/SET 
@dataclass
class AdmeshSet(Keyword):
    """Defines the criteria for adaptive meshing in parts."""

    adsetID: int
    adset_title: str
    angle_criterion: float
    inilev: int
    thkerr: float
    partIDs: List[int]

    @property
    def keyword(self):
        return f"/ADMESH/SET/{self.adsetID}"

    @property
    def pre_conditions(self):
        return [
            (len(self.partIDs) > 0, "Pre-condition `len(partIDs) > 0` is violated."),
            (len(self.partIDs) <= 10, "Pre-condition `len(partIDs)` is violated."),
            (self.inilev > 0, "Pre-condition `inilev > 0` is violated."),
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("adset_title", 1, 10),
            [
                FloatField("angle_criterion", 1),
                IntField("inilev", 3),
                FloatField("thkerr", 4),
            ],
            [IntField(f"partIDs:{i}", i + 1) for i in range(len(self.partIDs))],
        ]

        return structure


#* /ADMESH/STATE/SHELL 
@dataclass
class AdmeshStateShell(Keyword):
    """Describes the state of shells in adaptive meshing."""

    shellID: int
    shellID1: int
    shellID2: int
    shellID3: int
    shellID4: int
    actlev: int
    imapping: Literal[-1, 0, 1]

    @property
    def keyword(self):
        return "/ADMESH/STATE/SHELL"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [
                IntField("shellID", 1),
                IntField("shellID1", 2),
                IntField("shellID2", 3),
                IntField("shellID3", 4),
                IntField("shellID4", 5),
                IntField("actlev", 6),
                IntField("imapping", 7),
            ]
        ]

        return structure


#* /ADMESH/STATE/SH3N 
@dataclass
class AdmeshStateSh3n(Keyword):
    """Describes the state of 3-node shells in a multi-stage analysis using
    adaptive meshing."""

    sh3nID: int
    sh3nID1: int
    sh3nID2: int
    sh3nID3: int
    sh3nID4: int
    actlev: int
    imapping: Literal[-1, 0, 1]

    @property
    def keyword(self):
        return "/ADMESH/STATE/SH3N"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [
                IntField("sh3nID", 1),
                IntField("sh3nID1", 2),
                IntField("sh3nID2", 3),
                IntField("sh3nID3", 4),
                IntField("sh3nID4", 5),
                IntField("actlev", 6),
                IntField("imapping", 7),
            ]
        ]

        return structure


#* /ALE/BCS 
@dataclass
class ALEBcs(Keyword):
    """Describes the ALE boundary conditions."""

    bcsID: int
    bcs_title: float
    grilag: List[Literal[0, 1]]
    skewID: int
    grndID: int

    @property
    def keyword(self):
        return f"/ALE/BCS/{self.bcsID}"

    @property
    def pre_conditions(self):
        return [
            (len(self.grilag) == 6, "Pre-condition `len(grilag) == 6` is violated.")
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("bcs_title", 1, 10),
            [
                BoolField("grilag", 1, 6, [4, 5, 6, 8, 9, 10]),
                IntField("skewID", 2),
                IntField("grndID", 3),
            ],
        ]

        return structure


#* /ALE/CLOSE 
@dataclass
class ALEClose(Keyword):
    """Describes the treatment of element closure."""

    propID: int
    htest: float
    hclose: None | float = None

    def __post_init__(self):
        super().__post_init__()
        if self.hclose is None:
            self.hclose = 0.1 * self.htest

    @property
    def keyword(self):
        return f"/ALE/CLOSE/{self.propID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [FloatField("htest", 1), FloatField("hclose", 3)]
        ]

        return structure

#* /ALE/MUSCL 
@dataclass
class ALEMuscl(Keyword):
    """Allows for a second order monotonic upstream-centered scheme for
    conservation laws (MUSCL) reconstruction of volume fraction fields when
    using multi-material laws and for full full second order scheme (time and
    space) when using material law LAW151."""

    beta: float
    iflag: Literal[0, 1] = 0

    @property
    def keyword(self):
        return "/ALE/MUSCL"

    @property
    def pre_conditions(self):
        return [
            (0.0 < self.beta < 2.0, "Pre-condition `0.0 < beta < 2.0` is violated.")
        ]

    @property
    def structure(self):
        structure = [[FloatField("beta", 1), IntField("iflag", 3)]]

        return structure


#* /ALE/SOLVER/FINT 
@dataclass
class ALESolverFint(Keyword):
    """This option defines the numerical method for internal force
    integration.  This is relevant only for brick element and ALE legacy solver
    (momentum equation solved with FEM)."""

    iform: Literal[0, 1, 2, 3] = 3

    @property
    def keyword(self):
        return "/ALE/SOLVER/FINT"

    @property
    def pre_conditions(self):
        return [
            (
                self.iform in {0, 1, 2, 3},
                "Pre-condition `iform in {0,1,2,3} is violated.",
            )
        ]

    @property
    def structure(self):
        structure = [IntField("iform", 1)]

        return structure


#* /AMS 
@dataclass
class Ams(Keyword):
    """Describes the part group on which the advanced mass scaling is applied."""

    grpartID: int

    @property
    def keyword(self):
        return "/AMS"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [IntField("grpartID", 1)]

        return structure


#* /ANALY
@dataclass
class Analy(Keyword):
    """Defines the type of analysis and sets analysis flags."""

    n_2D3D: Literal[0, 1, 2] = 0
    i_parith: Literal[0, 1, 2] = 0
    i_subcycle: Literal[0, 2] = 0

    @property
    def pre_conditions(self):
        return [
            (
                self.n_2D3D in {0, 1, 2},
                "Pre-condtion `n_2D3D in {0, 1, 2} is violated.",
            ),
            (
                self.i_parith in {0, 1, 2},
                "Pre-condtion `i_parith in {0, 1, 2} is violated.",
            ),
            (
                self.i_subcycle in {0, 2},
                "Pre-condtion `i_subcycle in {0, 2} is violated.",
            ),
        ]

    @property
    def structure(self):
        return [
            [
                IntField("n_2D3D", 1),
                IntField("i_parith", 3),
                IntField("i_subcycle", 4),
            ]
        ]


#* /ANIM/VERS 
@dataclass
class AnimVers(Keyword):
    """Defines the animation file version."""

    anim_vers: int = 44

    @property
    def keyword(self):
        return "/ANIM/VERS"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [IntField("anim_vers", 1)]

        return structure
