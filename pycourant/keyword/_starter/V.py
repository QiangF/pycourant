from ..common import *

#* /VISC/PRONY 
@dataclass
class ViscProny(Keyword):
    """This is an isotropic visco-elastic Maxwell model that can be used to
    add visco-elasticity to certain shell and solid element material models.
    The visco-elasticity is input using a Prony series."""

    matID: int
    M: int = 0
    K_nu: float = 0.0
    i_tab: Literal[0, 1, 2] = 0
    # i_tab > 0
    i_shape: Literal[0, 1] = 0
    # i_tab == 0
    G_i: float | None = None
    beta_i: float | None = None
    K_i: float | None = None
    beta_ki: float | None = None
    # i_tab == 1
    i_func_g: int | None = None
    i_func_k: int | None = None
    xg_scale: float = 1.0
    yg_scale: float = 1.0
    xk_scale: float = 1.0
    yk_scale: float = 1.0
    # i_tab == 2
    i_func_gs: int | None = None
    i_func_gl: int | None = None
    i_func_ks: int | None = None
    i_func_kl: int | None = None
    xgs_scale: float = 1.0
    ygs_scale: float = 1.0
    xgl_scale: float = 1.0
    ygl_scale: float = 1.0
    xks_scale: float = 1.0
    yks_scale: float = 1.0
    xkl_scale: float = 1.0
    ykl_scale: float = 1.0

    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/VISC/PRONY/{self.matID}/{self.unitID}"
        else:
            return f"/VISC/PRONY/{self.matID}"

    @property
    def pre_conditions(self):
        conditions = []

        for attr in ("i_tab", "i_shape"):
            conditions.append(
                (
                    getattr(self, attr) in get_literal_values(self, attr),
                    f"Invalid value for `{attr}`. See documentation for details.",
                )
            )

        return []

    @property
    def structure(self):
        structure: KeywordStructureType = []

        if self.i_tab == 0:
            structure.append(
                [
                    IntField("M", 1),
                    FloatField("K_nu", 3),
                    IntField("i_tab", 5),
                ]
            )

        else:
            structure.append(
                [
                    IntField("M", 1),
                    FloatField("K_nu", 3),
                    IntField("i_tab", 5),
                    IntField("i_shape", 6),
                ]
            )

        if self.i_tab == 0:
            structure.append(
                [
                    FloatField("G_i", 1),
                    FloatField("beta_i", 3),
                    FloatField("K_i", 5),
                    FloatField("beta_ki", 7),
                ]
            )

        elif self.i_tab == 1:
            structure.extend(
                [
                    [
                        IntField("i_func_g", 1),
                        FloatField("xg_scale", 2),
                        FloatField("yg_scale", 4),
                    ],
                    [
                        IntField("i_func_k", 1),
                        FloatField("xk_scale", 2),
                        FloatField("yk_scale", 4),
                    ],
                ]
            )

        elif self.i_tab == 2:
            structure.extend(
                [
                    [
                        IntField("i_func_gs", 1),
                        FloatField("xgs_scale", 2),
                        FloatField("ygs_scale", 4),
                    ],
                    [
                        IntField("i_func_gl", 1),
                        FloatField("xgl_scale", 2),
                        FloatField("ygl_scale", 4),
                    ],
                    [
                        IntField("i_func_ks", 1),
                        FloatField("xks_scale", 2),
                        FloatField("yks_scale", 4),
                    ],
                    [
                        IntField("i_func_kl", 1),
                        FloatField("xkl_scale", 2),
                        FloatField("ykl_scale", 4),
                    ],
                ]
            )

        return structure
