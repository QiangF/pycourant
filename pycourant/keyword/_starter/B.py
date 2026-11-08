from ..common import *

#* /BCS 
@dataclass
class Bcs(Keyword):
    """Defines boundary conditions on node groups for translational and rotational motion."""

    ID: int
    title: str
    trarot: Sequence[Literal[0, 1]]
    skewID: int
    grndID: int

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10),
            [
                BoolField("trarot", 1, 6, [4, 5, 6, 8, 9, 10]),
                IntField("skewID", 2),
                IntField("grndID", 3),
            ],
        ]

        return structure


#* /BCS/CYCLIC -
@dataclass
class BcsCyclic(Keyword):
    """Defines a cyclic boundary condition on a structure in a fixed
    cylindrical coordinate system."""

    ID: int
    title: str
    grndID_1: int
    grndID_2: int
    skewID: int = 0

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10),
            [
                IntField("skewID", 1),
                IntField("grndID_1", 2),
                IntField("grndID_2", 3),
            ],
        ]

        return structure


#* /BCS/LAGMUL 
@dataclass
class BcsLagmul(Keyword):
    """Defines boundary conditions on node groups using Lagrange multipliers.
    This keyword is not available for SPMD computation."""

    ID: int
    title: str
    trarot: str
    skewID: int
    grndID: int

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10),
            [
                BoolField("trarot", 1, 6, [4, 5, 6, 8, 9, 10]),
                IntField("skewID", 2),
                IntField("grndID", 3),
            ],
        ]

        return structure


#* /BEAM 
@dataclass
class Beam(Keyword):
    """Describes the beam elements. Two properties (/PROP/TYPE3 (BEAM) and
    /PROP/TYPE18 (INT_BEAM)) are available for this beam element. The
    properties describing a beam element are all defined in a local beam
    coordinate system.
    """
    ID: int
    beamIDs: List[int]
    nodeIDs: NDArray

    @property
    def pre_conditions(self):
        return [
            (
                len(self.beamIDs) == len(self.nodeIDs),
                "Pre-condition `len(beamIDs) == len(nodeIDs)` is violated.",
            )
        ]

    @property
    def structure(self):
        structure = [
            ArrayOfAtomicFields(
                [
                    IntField("beamIDs", 1),
                    IntField("nodeIDs:ID_1|0", 2),
                    IntField("nodeIDs:ID_2|1", 3),
                    IntField("nodeIDs:ID_3|2", 4),
                ]
            )
        ]

        return structure

#* /BEGIN 
@dataclass
class Begin(Keyword):
    # All the variables referenced in the block
    runname: str
    invers: Literal[
        90, 100, 110, 120, 130, 140, 2017, 2018, 2019, 2020, 2021, 2022, 2025, 2026
    ] = 2025
    input_mass_unit: VALID_MASS_LITERALS = "kg"
    input_length_unit: VALID_LENGTH_LITERALS = "m"
    input_time_unit: VALID_TIME_LITERALS = "s"
    work_mass_unit: VALID_MASS_LITERALS = "kg"
    work_length_unit: VALID_LENGTH_LITERALS = "m"
    work_time_unit: VALID_TIME_LITERALS = "s"

    @property
    def pre_conditions(self):
        return [
            (len(self.runname) <= 80, "`runname` too long (>80)"),
            (
                self.invers in get_literal_values(self, "invers"),
                "Invalid version (see documentation for valid versions).",
            ),
            (
                self.input_mass_unit in get_args(VALID_MASS_LITERALS),
                f"Invalid input mass unit `{self.input_mass_unit}`.",
            ),
            (
                self.input_length_unit in get_args(VALID_LENGTH_LITERALS),
                f"Invalid input length unit `{self.input_length_unit}`.",
            ),
            (
                self.input_time_unit in get_args(VALID_TIME_LITERALS),
                f"Invalid input time unit `{self.input_time_unit}`.",
            ),
            (
                self.work_mass_unit in get_args(VALID_MASS_LITERALS),
                f"Invalid work mass unit `{self.work_mass_unit}`.",
            ),
            (
                self.work_length_unit in get_args(VALID_LENGTH_LITERALS),
                f"Invalid work length unit `{self.work_length_unit}`.",
            ),
            (
                self.work_time_unit in get_args(VALID_TIME_LITERALS),
                f"Invalid work time unit `{self.work_time_unit}`.",
            ),
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("runname", 1, 8),
            IntField("invers", 1),
            [
                StringField("input_mass_unit", 1, 2),
                StringField("input_length_unit", 3, 2),
                StringField("input_time_unit", 5, 2),
            ],
            [
                StringField("work_mass_unit", 1, 2),
                StringField("work_length_unit", 3, 2),
                StringField("work_time_unit", 5, 2),
            ],
        ]

        return structure


#* /BEM/DAA 
@dataclass
class BemDaa(Keyword):
    ID: int
    title: str
    surfID: int
    gravID: int
    rho: float
    C: float
    x_s: float
    y_s: float
    z_s: float
    p_min: float = 1.0e-30
    i_form: Literal[1, 2] = 1
    i_pri: Literal[1, 2] = 1
    i_pres: Literal[1, 2] = 1
    k_form: Literal[1, 2] = 1
    freesurf: Literal[1, 2] = 1
    afterflow: Literal[1, 2] = 2
    integr: Literal[1, 2] = 2
    p_m: float | None = None
    theta: float | None = None
    a: float | None = None
    a_theta: float | None = None
    fctID_p: int | None = None
    fscale_p: float | None = None
    x_c: float | None = None
    y_c: float | None = None
    z_c: float | None = None
    x_a: float | None = None
    y_a: float | None = None
    z_a: float | None = None
    dir_x: float | None = None
    dir_y: float | None = None
    dir_z: float | None = None
    unitID: int | None = None

    @property
    def pre_conditions(self):
        conditions = []

        for attr in (
            "i_form",
            "i_pri",
            "i_pres",
            "k_form",
            "freesurf",
            "afterflow",
            "integr",
        ):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        if self.i_pres == 1:
            is_complete, not_defined = check_if_all_values_are_present(
                self, ("p_m", "theta", "a", "a_theta")
            )

            conditions.append(
                (
                    is_complete,
                    f"Mandatory parameter(s) `{not_defined}` is/are not defined (i_pres = 1)",
                )
            )

        if self.i_pres == 2:
            is_complete, not_defined = check_if_all_values_are_present(
                self, ("fctID_p", "fscale_p", "x_c", "y_c", "z_c")
            )

            conditions.append(
                (
                    is_complete,
                    f"Mandatory parameter(s) `{not_defined}` is/are not defined (i_pres = 2)",
                )
            )

        if self.gravID > 0 or self.freesurf == 2:
            is_complete, not_defined = check_if_all_values_are_present(
                self, ("x_a", "y_a", "z_a", "dir_x", "dir_y", "dir_z")
            )

            conditions.append(
                (
                    is_complete,
                    f"Mandatory parameter(s) `{not_defined}` is/are not defined (i_pres = 2)",
                )
            )

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [IntField("surfID", 1), IntField("gravID", 2)],
            [
                FloatField("rho", 1),
                FloatField("C", 3),
                FloatField("p_min", 5),
            ],
            [
                FloatField("x_s", 1),
                FloatField("y_s", 3),
                FloatField("z_s", 5),
            ],
            [
                IntField("i_form", 1),
                IntField("i_pri", 2),
                IntField("i_pres", 3),
                IntField("k_form", 6),
                IntField("freesurf", 7),
                IntField("afterflow", 8),
                IntField("integr", 9),
            ],
        ]

        if self.i_pres == 1:
            structure.append(
                [
                    FloatField("p_m", 1),
                    FloatField("theta", 3),
                    FloatField("a", 5),
                    FloatField("a_theta", 7),
                ]
            )
        elif self.i_pres == 2:
            structure.extend(
                [
                    [IntField("fctID_p", 1), FloatField("fscale_p", 3)],
                    [
                        FloatField("x_c", 1),
                        FloatField("y_c", 3),
                        FloatField("z_c", 5),
                    ],
                ]
            )

        if self.gravID > 0 or self.freesurf == 2:
            structure.extend(
                [
                    [
                        FloatField("x_a", 1),
                        FloatField("y_a", 3),
                        FloatField("z_a", 5),
                    ],
                    [
                        FloatField("dir_x", 1),
                        FloatField("dir_y", 3),
                        FloatField("dir_z", 5),
                    ],
                ]
            )

        return structure


#* /BEM/FLOW 
@dataclass
class BemFlow(Keyword):
    """Describes the incompressible fluid flow by boundary elements method."""

    ID: int
    title: str
    surfID_ex: int
    n_io: int
    fctID_fsp: int
    grnID_aux: int
    i_test: int
    rho: float
    i_vinf: int
    i_pri: int
    fctID_v: int
    dir_x: float
    dir_y: float
    dir_z: float
    i_inside: Literal[1, 2] = 1
    fscale_fsp: float = 1.0
    ascale_fsp: float = 1.0
    tole: float = 1e-5
    # If `n_io > 0` insert `n_io` times
    surfID_io: List[int] | None = None
    fctID_nv: List[int] | None = None
    fctID_p: List[int] | None = None
    fscale_nv: List[float] | None = None
    fscale_p: List[float] | None = None
    ascale_t: List[float] | None = None
    # Formulation flags
    i_form: Literal[1, 2] = 1
    dt_flow: float = 0.0
    fscale_v: float = 1.0
    ascale_v: float = 1.0
    unitID: int | None = None

    @property
    def pre_conditions(self):
        conditions: KeywordPreconditionsType = []

        for attr in ("i_inside", "i_form"):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        if self.n_io > 0:
            for attr in (
                "surfID_io",
                "fctID_nv",
                "fctID_p",
                "fscale_nv",
                "fscale_p",
                "ascale_t",
            ):
                o = getattr(self, attr)
                conditions.append(
                    (isinstance(o, Sequence), f"Attribute `{attr}` must be a sequence")
                )

                if isinstance(o, Sequence):
                    conditions.append(
                        (
                            len(o) == self.n_io,
                            (
                                f"Invalid number of entries in `{attr}`. "
                                "See documentation for details."
                            ),
                        )
                    )

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("surfID_ex", 1),
                IntField("n_io", 2),
                IntField("i_inside", 3),
                IntField("fctID_fsp", 4),
                FloatField("fscale_fsp", 5),
                FloatField("ascale_fsp", 7),
            ],
            [
                IntField("grnID_aux", 1),
                IntField("i_test", 2),
                FloatField("tole", 3),
            ],
            [FloatField("rho", 1), IntField("i_vinf", 3)],
        ]

        if self.n_io > 0:
            structure.append(
                ArrayOfAtomicFields(
                    [
                        IntField("surfID_io", 1),
                        IntField("fctID_nv", 2),
                        IntField("fctID_p", 3),
                        FloatField("fscale_nv", 5),
                        FloatField("fscale_p", 7),
                        FloatField("ascale_t", 9),
                    ]
                )
            )

        structure.extend(
            [
                [
                    IntField("i_form", 1),
                    IntField("i_pri", 2),
                    FloatField("dt_flow", 3),
                ],
                [
                    IntField("fctID_v", 1),
                    FloatField("fscale_v", 2),
                    FloatField("ascale_v", 4),
                ],
                [
                    FloatField("dir_x", 1),
                    FloatField("dir_y", 3),
                    FloatField("dir_z", 5),
                ],
            ]
        )

        return structure


#* /BOX/BOX 
@dataclass
class BoxBox(Keyword):
    """Describes the box as a result of the combination of a predefined list of boxes."""

    ID: int
    title: str
    boxIDs: List[int]

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            VLSequenceOfAtomicField(IntField("boxIDs", 1)),
        ]

        return structure


#* /BRICK
# see /Element

#* /BRIC20 
@dataclass
class Bric20(Keyword):
    """Describes 3D solid elements (20 node brick elements). This quadratic
    element should be used with the property /PROP/SOLID.

    """

    ID: int
    elemIDs: List[int] | NDArray
    nodeIDs: List[Tuple[int, ...]] | NDArray

    @property
    def pre_conditions(self):

        return [
            (
                len(self.elemIDs) > 0,
                "Pre-condition `len(elemIDs) > 0` is violated.",
            ),
            (
                len(self.nodeIDs) > 0,
                "Pre-condition `len(nodeIDs) > 0` is violated.",
            ),
            (
                len(self.elemIDs) == len(self.nodeIDs),
                "Pre-condition `len(elemIDs) == len(nodeIDs)` is violated.",
            ),
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            MultiLineArrayOfAtomicFields(
                [
                    ArrayOfAtomicFields(
                        [
                            IntField("elemIDs", 1),
                            IntField("nodeIDs:ID_1|0", 2),
                            IntField("nodeIDs:ID_2|1", 3),
                            IntField("nodeIDs:ID_3|2", 4),
                            IntField("nodeIDs:ID_4|3", 5),
                            IntField("nodeIDs:ID_5|4", 6),
                            IntField("nodeIDs:ID_6|5", 7),
                            IntField("nodeIDs:ID_7|6", 8),
                            IntField("nodeIDs:ID_8|7", 9),
                        ]
                    ),
                    ArrayOfAtomicFields(
                        [
                            IntField("nodeIDs:ID_9|8", 1),
                            IntField("nodeIDs:ID_10|9", 2),
                            IntField("nodeIDs:ID_11|10", 3),
                            IntField("nodeIDs:ID_12|11", 4),
                            IntField("nodeIDs:ID_13|12", 5),
                            IntField("nodeIDs:ID_14|13", 6),
                            IntField("nodeIDs:ID_15|14", 7),
                            IntField("nodeIDs:ID_16|15", 8),
                        ]
                    ),
                    ArrayOfAtomicFields(
                        [
                            IntField("nodeIDs:ID_17|16", 1),
                            IntField("nodeIDs:ID_18|17", 2),
                            IntField("nodeIDs:ID_19|18", 3),
                            IntField("nodeIDs:ID_20|19", 4),
                        ]
                    ),
                ]
            )
        ]

        return structure
