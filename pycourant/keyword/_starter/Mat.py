from ..common import *

#* MATPLASJOHNS
# /mat/law2(plas_johns)
@dataclass
class MatPlas_johns(Keyword):
    """This law represents an isotropic elasto-plastic material using the
    Johnson-Cook material model.  This model expresses material stress as a
    function of strain, strain rate and temperature. A built-in failure
    criterion based on the maximum plastic strain is available.

    """

    ID: int
    title: str
    rho_i: float
    E: float
    nu: float
    I_flag: Literal[0, 1] = 0
    VP: int = 0
    P_min: float = -1e30

    # for i_flage=0
    a: float | None = None
    b: float | None = None
    n: float = 1.0
    eps_max_p: float = 1e30
    sigma_max_0: float = 1e30

    # for I_flag = 1
    sigma_y: float | None = None
    UTS: float | None = None

    c: float = 0.0
    eps_dot_0: float | None = None
    ICC: Literal[0, 1, 2] = 0
    F_smooth: Literal[0, 1] = 0
    F_cut: float = 1e30
    C_hard: float = 0
    m: float = 1.0
    T_melt: float = 1e30
    rho_C_p: float | None = None
    T_r: float = 300.0
    T_max: float = 1e20
    unitID: int | None = None

    @property
    def pre_conditions(self):
        conditions = []

        for attr in ("I_flag", "ICC", "F_smooth"):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            FloatField("rho_i", 1),
            [
                FloatField("E", 1),
                FloatField("nu", 3),
                IntField("I_flag", 5),
                IntField("VP", 6),
                FloatField("P_min", 7),
            ],
        ]

        if self.I_flag == 0:
            structure.extend(
                [
                    [
                        FloatField("a", 1),
                        FloatField("b", 3),
                        FloatField("n", 5),
                        FloatField("eps_max_p", 7),
                        FloatField("sigma_max_0", 9),
                    ]
                ]
            )
        elif self.I_flag == 1:
            structure.extend(
                [
                    [
                        FloatField("sigma_y", 1),
                        FloatField("UTS", 3),
                        FloatField("eps_uts", 5),
                        FloatField("eps_max_p", 7),
                        FloatField("sigma_max_0", 9),
                    ]
                ]
            )

        structure.extend(
            [
                [
                    FloatField("c", 1),
                    FloatField("eps_dot_0", 3),
                    IntField("ICC", 5),
                    IntField("F_smooth", 6),
                    FloatField("F_cut", 7),
                    FloatField("C_hard", 9),
                ],
                [
                    FloatField("m", 1),
                    FloatField("T_melt", 3),
                    FloatField("rho_C_p", 5),
                    FloatField("T_r", 7),
                    FloatField("T_max", 9),
                ],
            ]
        )

        return structure
