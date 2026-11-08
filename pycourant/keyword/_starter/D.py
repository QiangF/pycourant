from ..common import *

#* /DAMP
@dataclass
class Damp(Keyword):
    dampID: int
    damp_title: str
    grndID: int
    skewID: int
    t_start: float
    t_stop: float = 1.0e30
    a: float | None = None
    b: float | None = None
    ax: float | None = None
    ay: float | None = None
    az: float | None = None
    axx: float | None = None
    ayy: float | None = None
    azz: float | None = None
    bx: float | None = None
    by: float | None = None
    bz: float | None = None
    bxx: float | None = None
    byy: float | None = None
    bzz: float | None = None

    @property
    def keyword(self):
        return f"/DAMP/{self.dampID}"

    @property
    def pre_conditions(self):
        # TODO: check consistency for short/long format definitions
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [StringField("damp_title", 1, 10)]

        # Note: it is tempting to use `all((self.a, self.b))`, but this will
        # fail if `a` or `b` equals 0 (or 0.0). We specifically want to test
        # for `None`.
        if None not in (self.a, self.b):
            structure.extend(
                [
                    [
                        FloatField("a", 1),
                        FloatField("b", 3),
                        IntField("grndID", 5),
                        IntField("skewID", 6),
                        FloatField("t_start", 7),
                        FloatField("t_stop", 9),
                    ]
                ]
            )

        else:
            structure.extend(
                [
                    [
                        FloatField("ax", 1),
                        FloatField("bx", 3),
                        IntField("grndID", 5),
                        IntField("skewID", 6),
                        FloatField("t_start", 7),
                        FloatField("t_stop", 9),
                    ],
                    [
                        FloatField("ay", 1),
                        FloatField("by", 3),
                    ],
                    [
                        FloatField("az", 1),
                        FloatField("bz", 3),
                    ],
                    [
                        FloatField("axx", 1),
                        FloatField("bxx", 3),
                    ],
                    [
                        FloatField("ayy", 1),
                        FloatField("byy", 3),
                    ],
                    [
                        FloatField("azz", 1),
                        FloatField("bzz", 3),
                    ],
                ]
            )

        return structure


#* /DAMP/INTER
@dataclass
class DampInter(Keyword):
    """The card is intended to apply Rayleigh damping to the nodes inside of
    specified contact to increase its stability and reduce results scattering
    due to small variations of initial or boundary conditions."""

    dampID: int
    damp_title: str
    grndID: int
    skewID: int
    t_start: float
    nb_time_step: int = 20
    t_stop: float = 1.0e30
    a: float | None = None
    b: float | None = None
    ax: float | None = None
    ay: float | None = None
    az: float | None = None
    axx: float | None = None
    ayy: float | None = None
    azz: float | None = None
    bx: float | None = None
    by: float | None = None
    bz: float | None = None
    bxx: float | None = None
    byy: float | None = None
    bzz: float | None = None

    @property
    def keyword(self):
        return f"/DAMP/INTER/{self.dampID}"

    @property
    def pre_conditions(self):
        # TODO: check consistency for short/long format definitions
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("damp_title", 1, 10),
            IntField("nb_time_step", 1),
        ]

        # Note: it is tempting to use `all((self.a, self.b))`, but this will
        # fail if `a` or `b` equals 0 (or 0.0). We specifically want to test
        # for `None`.
        if None not in (self.a, self.b):
            structure.extend(
                [
                    [
                        FloatField("a", 1),
                        FloatField("b", 3),
                        IntField("grndID", 5),
                        IntField("skewID", 6),
                        FloatField("t_start", 7),
                        FloatField("t_stop", 9),
                    ]
                ]
            )

        else:
            structure.extend(
                [
                    [
                        FloatField("ax", 1),
                        FloatField("bx", 3),
                        IntField("grndID", 5),
                        IntField("skewID", 6),
                        FloatField("t_start", 7),
                        FloatField("t_stop", 9),
                    ],
                    [
                        FloatField("ay", 1),
                        FloatField("by", 3),
                    ],
                    [
                        FloatField("az", 1),
                        FloatField("bz", 3),
                    ],
                    [
                        FloatField("axx", 1),
                        FloatField("bxx", 3),
                    ],
                    [
                        FloatField("ayy", 1),
                        FloatField("byy", 3),
                    ],
                    [
                        FloatField("azz", 1),
                        FloatField("bzz", 3),
                    ],
                ]
            )

        return structure


#* /DEF_SHELL
@dataclass
class Def_shell(Keyword):
    """This keyword is used to set default values for certain parameters in all shell
    properties, but options could still be changed in each property set input and
    in this case, the latter will prevail.

    """

    i_shell: Literal[0, 1, 2, 3, 4, 12, 24] = 1
    i_smstr: Literal[-2, -1, 0, 1, 2, 3, 4] = 2
    i_thick: Literal[-2, -1, 0, 1, 2] = 2
    i_plas: Literal[-2, -1, 0, 1, 2] = 2
    i_strain: Literal[0, 1, 2] = 1
    i_sh3n: Literal[0, 1, 2, 30, 31] = 2
    i_dril: Literal[0, 1, 2] = 2

    @property
    def pre_conditions(self):
        conditions = []

        for attr in (
            "i_shell",
            "i_smstr",
            "i_thick",
            "i_plas",
            "i_strain",
            "i_sh3n",
            "i_dril",
        ):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        return conditions

    @property
    def structure(self):
        return [
            [
                IntField("i_shell", 1),
                IntField("i_smstr", 2),
                IntField("i_thick", 3),
                IntField("i_plas", 4),
                IntField("i_strain", 5),
                IntField("i_sh3n", 8),
                IntField("i_dril", 9),
            ]
        ]


#* /DEF_SOLID
@dataclass
class Def_solid(Keyword):
    """Used to set default values for certain parameters in all solid properties and
    thick shells. The default values defined here will be overwritten by any values
    entered on the individual property input.

    """

    i_solid: Literal[0, 1, 2, 14, 15, 16, 17, 18, 24] = 1
    i_smstr: Literal[-2, -1, 0, 1, 2, 3, 4, 10, 11, 12] = 4
    i_cpre: Literal[-2, -1, 0, 1, 2, 3] = 1
    i_tetra4: Literal[0, 1, 3, 1000] = 0
    i_tetra10: Literal[0, 2, 3, 1000] = 0
    i_mas: Literal[0, 1, 2] = 2
    i_frame: Literal[-2, -1, 0, 1, 2] = 1

    @property
    def pre_conditions(self):
        conditions = []

        for attr in (
            "i_solid",
            "i_smstr",
            "i_cpre",
            "i_tetra4",
            "i_tetra10",
            "i_mas",
            "i_frame",
        ):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [
                IntField("i_solid", 1),
                IntField("i_smstr", 2),
                IntField("i_cpre", 3),
                IntField("i_tetra4", 5),
                IntField("i_tetra10", 6),
                IntField("i_mas", 7),
                IntField("i_frame", 8),
            ]
        ]

        return structure


#* /DEFAULT/INTER/TYPE2
@dataclass
class DefaultInterType2(Keyword):
    """Defines interfaces TYPE2 default values."""

    ignore: Literal[0, 1, 2, 3, 1000] = 1000
    spot_flag: Literal[0, 1, 2, 4, 5, 20, 21, 22, 25, 27, 28, 30] = 5
    i_search: Literal[0, 1, 2] = 2
    i_del2: Literal[0, 1, 2, 1000] = 1000
    i_stf: Literal[0, 1, 2, 3, 4, 5] = 2

    @property
    def keyword(self):
        return "/DEFAULT/INTER/TYPE2"

    @property
    def pre_conditions(self):
        conditions = []

        for attr in ("ignore", "spot_flag", "i_search", "i_del2", "i_stf"):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("__blank__", 1, 10),
            [
                IntField("ignore", 3),
                IntField("spot_flag", 4),
                IntField("i_search", 6),
                IntField("i_del2", 7),
            ],
        ]

        if self.spot_flag in {25, 27, 28}:
            structure.append([IntField("i_stf", 7)])

        return structure

#* /DFS/DETPLAN/NODE
@dataclass
class DfsDetplanNode(Keyword):
    """Describes a planar detonation wave."""

    detpID: int
    pID: int
    nID: int
    t_det: float = 0.0
    matID: int = 0
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/DFS/DETPLAN/NODE/{self.detpID}/{self.unitID}"
        else:
            return f"/DFS/DETPLAN/NODE/{self.detpID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            [FloatField("t_det", 7), IntField("matID", 9), IntField("pID", 10)],
            IntField("nID", 10),
        ]

        return structure


#* /DFS/DETPOINT
@dataclass
class DfsDetpoint(Keyword):
    """Locates the detonation point and set lighting time for an explosive
    material law."""

    detpointID: int
    x_det: float = 0.0
    y_det: float = 0.0
    z_det: float = 0.0
    t_det: float = 0.0
    matID: float = 0

    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/DFS/DETPOINT/{self.detpointID}/{self.unitID}"
        else:
            return f"/DFS/DETPOINT/{self.detpointID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            [
                FloatField("x_det", 1),
                FloatField("y_det", 3),
                FloatField("z_det", 5),
                FloatField("t_det", 7),
                IntField("matID", 9),
            ]
        ]

        return structure


#* /DFS/DETPOINT/NODE
@dataclass
class DfsDetpointNode(Keyword):
    detpointID: int
    t_det: float
    nodeID: int
    matID: int = 0
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/DFS/DETPOINT/NODE/{self.detpointID}/{self.unitID}"
        else:
            return f"/DFS/DETPOINT/NODE/{self.detpointID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            [
                FloatField("t_det", 7),
                IntField("matID", 9),
                IntField("nodeID", 10),
            ]
        ]

        return structure
