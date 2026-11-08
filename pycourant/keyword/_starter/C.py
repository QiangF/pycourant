
from ..common import *

#* /CHECK/RFILE/OFF 
@dataclass
class CheckRfileOff(Keyword):
    @property
    def keyword(self):
        return "/CHECK/RFILE/OFF"


#* /CLOAD 
@dataclass
class Cload(Keyword):
    cloadID: int
    cload_title: str
    fctID_t: int
    dir: Literal[
        "X",
        "Y",
        "Z",
        "XY",
        "XZ",
        "YZ",
        "XYZ",
        "XX",
        "YY",
        "ZZ",
        "XXYY",
        "XXZZ",
        "YYZZ",
        "XXYYZZ",
    ]
    skewID: int
    sensID: int
    grndID: int
    unitID: int | None = None
    a_scale_x: float = 1.0
    f_scale_y: float = 1.0

    @property
    def keyword(self):
        if self.unitID is None:
            return f"/CLOAD/{self.cloadID}"
        else:
            return f"/CLOAD/{self.cloadID}/unitID"

    @property
    def pre_conditions(self):
        return [
            (
                self.dir in get_literal_values(self, "dir"),
                f"Invalid `dir` specifier -> {self.dir}",
            )
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("cload_title", 1, 10),
            [
                IntField("fctID_t", 1),
                StringField("dir", 2, 1, alignment=TextAlignment.CENTER),
                IntField("skewID", 3),
                IntField("sensID", 4),
                IntField("grndID", 5),
                FloatField("a_scale_x", 7),
                FloatField("f_scale_y", 9),
            ],
        ]

        return structure

#* /CLUSTER 
@dataclass
class Cluster(Keyword):
    """Describes an assembly of brick or spring elements for post-processing
    and failure control.

    """

    clusterID: int
    cluster_title: str
    groupID: int
    skewID: int
    i_fail: Literal[0, 1, 2, 3] = 0
    fn_fail: float = 1e30
    fs_fail: float = 1e30
    mt_fail: float = 1e30
    mb_fail: float = 1e30
    a1: float = 1.0
    a2: float = 1.0
    a3: float = 1.0
    a4: float = 1.0
    b1: float = 1.0
    b2: float = 1.0
    b3: float = 1.0
    b4: float = 1.0
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/CLUSTER/{self.clusterID}/{self.unitID}"
        else:
            return f"/CLUSTER/{self.clusterID}"

    @property
    def pre_conditions(self):
        conditions: KeywordPreconditionsType = []

        conditions.append(
            (
                self.i_fail in get_literal_values(self, "i_fail"),
                "Invalid value for `i_fail`. See documentation for details.",
            )
        )

        return conditions

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("cluster_title", 1, 10),
            [
                IntField("groupID", 1),
                IntField("skewID", 2),
                IntField("i_fail", 3),
            ],
        ]

        if self.i_fail != 3:
            structure.extend(
                [
                    FloatField("fn_fail", 1),
                    FloatField("fs_fail", 1),
                    FloatField("mt_fail", 1),
                    FloatField("mb_fail", 1),
                ]
            )
        else:
            structure.extend(
                [
                    [
                        FloatField("fn_fail", 1),
                        FloatField("a1", 3),
                        FloatField("b1", 5),
                    ],
                    [
                        FloatField("fs_fail", 1),
                        FloatField("a2", 3),
                        FloatField("b2", 5),
                    ],
                    [
                        FloatField("mt_fail", 1),
                        FloatField("a3", 3),
                        FloatField("b3", 5),
                    ],
                    [
                        FloatField("mb_fail", 1),
                        FloatField("a4", 3),
                        FloatField("b4", 5),
                    ],
                ]
            )

        return structure


#* /CNODE 
@dataclass
class Cnode(Keyword):
    """Defines the coordinate of common node, which could be merged to the
    nearest selected NODE or CNODE."""

    search_value: float
    cnodeID: int
    x_c: float
    y_c: float
    z_c: float
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/CNODE/{self.search_value}/self.unitID"
        else:
            return f"/CNODE/{self.search_value}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            [
                IntField("cnodeID", 1),
                FloatField("x_c", 2),
                FloatField("y_c", 4),
                FloatField("z_c", 6),
            ]
        ]

        return structure


#* /CONVEC 
@dataclass
class Convec(Keyword):
    """Describes the free or forced convective flux."""
    ID: int
    title: str
    surfID_t: int
    fctID_t: int
    sensID: int
    H: float
    ascale_x: float = 1.0
    fscale_y: float = 1.0
    t_start: float = 0.0
    t_stop: float = 1e30
    unitID: int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10),
            [
                IntField("surfID_t", 1),
                IntField("fctID_t", 2),
                IntField("sensID", 3),
            ],
            [
                FloatField("ascale_x", 1),
                FloatField("fscale_y", 3),
                FloatField("t_start", 5),
                FloatField("t_stop", 7),
                FloatField("H", 9),
            ],
        ]

        return structure


#* /CYL_JOINT 
@dataclass
class CylJoint(Keyword):
    jointID: int
    joint_title: str
    nodeID_1: int
    nodeID_2: int
    grndID: int
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/CYL_JOINT/{self.jointID}/{self.unitID}"
        else:
            return f"/CYL_JOINT/{self.jointID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("joint_title", 1, 10),
            [
                IntField("nodeID_1", 1),
                IntField("nodeID_2", 2),
                IntField("grndID", 3),
            ],
        ]

        return structure
