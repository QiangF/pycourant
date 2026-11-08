from ..common import *

#* /TH 
@dataclass
class Th(Keyword):
    ID: int
    attr2: float

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [

        ]

        return structure

#* /TH/INTER
@dataclass
class ThInter(Keyword):
    ID: int
    title: str
    varIDs: List[str]
    objIDs: List[int]

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            VLSequenceOfAtomicField(StringField("varIDs", 1, 1, alignment=TextAlignment.RIGHT)),
            VLSequenceOfAtomicField(IntField("objIDs", 1)),
        ]

        return structure

#* /TH/RBODY
@dataclass
class ThRbody(Keyword):
    ID: int
    title: str
    varIDs: List[str]
    objIDs: List[int]

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure = [
            StringField("title", 1, 10, alignment=TextAlignment.LEFT),
            VLSequenceOfAtomicField(StringField("varIDs", 1, 1, alignment=TextAlignment.RIGHT)),
            VLSequenceOfAtomicField(IntField("objIDs", 1)),
        ]

        return structure

#* /THPART/GRSPRI 
@dataclass
class ThpartGrspri(Keyword):
    """Defines a time-history part for spring groups."""

    ID: int
    title: str
    grelemID: int

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            IntField("grelemID", 1),
        ]

        return structure


#* /THPART/GRTRUS
@dataclass
class ThpartGrtrus(Keyword):
    """Defines a time-history part for truss groups."""

    ID: int
    title: str
    grelemID: int

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            IntField("grelemID", 1),
        ]

        return structure


#* /TITLE
@dataclass
class Title(Keyword):
    """Describes the title."""

    title: str

    @property
    def pre_conditions(self):
        return [(not self.title.startswith("/"), "Titles cannot start with a `/`.")]

    @property
    def structure(self):
        structure: KeywordStructureType = [StringField("title", 1, 10)]

        return structure


#* /TRANSFORM/MATRIX
@dataclass
class TransformMatrix(Keyword):
    ID: int
    title: str
    M: list[list] | NDArray
    T: Sequence[float] | NDArray
    grndID: int | None = None
    subID: int | None = None
    unitID: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.tx = None
        self.ty = None
        self.tz = None
        self.m11 = None
        self.m12 = None
        self.m13 = None
        self.m21 = None
        self.m22 = None
        self.m23 = None
        self.m31 = None
        self.m32 = None
        self.m33 = None

    @property
    def pre_conditions(self):
        return [
            (
                is_exclusive(self.grndID, self.subID),
                "Either `grndID` or `subID` must be provided. Not both.",
            ),
            (has_shape(self.T, (3, 1)), "Shape of `T` must be (3, 1)."),
            (has_shape(self.M, (3, 3)), "Shape of `M` must be (3, 3)."),
        ]

    @property
    def structure(self):

        self.m11, self.m12, self.m13 = self.M[0]
        self.m21, self.m22, self.m23 = self.M[1]
        self.m31, self.m32, self.m33 = self.M[2]
        self.tx, self.ty, self.tz = self.T

        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("grndID", 1),
                FloatField("m11", 2),
                FloatField("m12", 4),
                FloatField("m13", 6),
                FloatField("tx", 8),
                IntField("subID", 10),
            ],
            [
                FloatField("m21", 2),
                FloatField("m22", 4),
                FloatField("m23", 6),
                FloatField("ty", 8),
            ],
            [
                FloatField("m31", 2),
                FloatField("m32", 4),
                FloatField("m33", 6),
                FloatField("ty", 8),
            ],
        ]

        return structure


#* /TRANSFORM/POSITION
@dataclass
class TransformPosition(Keyword):
    ID: int
    title: str
    grndID: int | None = None
    subID: int | None = None
    nodeID_1: int | None = None
    nodeID_2: int | None = None
    nodeID_3: int | None = None
    nodeID_4: int | None = None
    nodeID_5: int | None = None
    nodeID_6: int | None = None
    point_1: list[float] | NDArray | None = None
    point_2: list[float] | NDArray | None = None
    point_3: list[float] | NDArray | None = None
    point_4: list[float] | NDArray | None = None
    point_5: list[float] | NDArray | None = None
    point_6: list[float] | NDArray | None = None
    unitID: int | None = None

    @property
    def pre_conditions(self):
        nodeIDs = (
            self.nodeID_1,
            self.nodeID_2,
            self.nodeID_3,
            self.nodeID_4,
            self.nodeID_5,
            self.nodeID_6,
        )

        points = (
            self.point_1,
            self.point_2,
            self.point_3,
            self.point_4,
            self.point_5,
            self.point_6,
        )

        return [
            (
                is_exclusive(self.grndID, self.subID),
                "Either `grndID` or `subID` must be provided, not both.",
            ),
            (
                not (has_all_nones(nodeIDs) and has_all_nones(points)),
                "No node ids or points provided; keyword definition is incomplete.",
            ),
            (
                is_exclusive(nodeIDs, points),
                "Either node ids or points must be provided, not both.",
            ),
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("grndID", 1),
                IntField("nodeID_1", 2),
                IntField("nodeID_2", 3),
                IntField("nodeID_3", 4),
                IntField("nodeID_4", 5),
                IntField("nodeID_5", 6),
                IntField("nodeID_6", 7),
                IntField("subID", 10),
            ],
        ]

        # We only need to check if one point is defined, the condition that all
        # other points are defined is checked in the `pre_conditions` method.
        if self.point_1:
            for i in range(6):
                fields = []
                for j, c in enumerate(("x", "y", "z")):
                    # Generate the name of the attribute
                    attr = f"{c}_point_{i+1}"

                    # Get point for which we want to expande the coordinates
                    point_i = getattr(self, f"point_{i+1}")

                    # Create the attribute ("x", "y" or "z") and set is corresponding value
                    setattr(self, attr, point_i[j])

                    # Calculate the position on the line in the keyword text representaion.
                    pos = 2 * (1 + j)

                    # Create a `FloatField` for this attribute
                    fields.append(FloatField(attr, pos))

                # Add the fields for this point to the `structure` list.
                structure.append(fields)

                # Prepare for next point.
                fields = []

        return structure


#* /TRANSFORM/ROT
@dataclass
class TransformRot(Keyword):
    ID: int
    title: str
    grndID: int | None = None
    subID: int | None = None
    nodeID_1: int | None = None
    nodeID_2: int | None = None
    point_1: list[float] | NDArray | None = None
    point_2: list[float] | NDArray | None = None
    angle: float = 0.0
    unitID: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        self.x_point_1 = None
        self.y_point_1 = None
        self.z_point_1 = None
        self.x_point_2 = None
        self.y_point_2 = None
        self.z_point_2 = None

    @property
    def pre_conditions(self):

        nodeIDs = [self.nodeID_1, self.nodeID_2]
        points = [self.point_1, self.point_2]

        conditions = [
            (
                is_exclusive(self.grndID, self.subID),
                "Either `grndID` or `subID` must be provided, not both.",
            ),
            (
                not (has_all_nones(nodeIDs) and has_all_nones(points)),
                "No node ids or points provided; keyword definition is incomplete.",
            ),
            (
                is_exclusive(nodeIDs, points),
                "Either node ids or points must be provided, not both.",
            ),
        ]

        if self.point_1 != None:
            conditions.extend(
                [
                    (
                        has_shape(self.point_1, (3, 1)),
                        "Expected 3 coordinates for `point_1`",
                    ),
                    (
                        has_shape(self.point_2, (3, 1)),
                        "Expected 3 coordinates for `point_2`",
                    ),
                ]
            )

        return conditions

    @property
    def structure(self):
        if self.point_1:
            self.x_point_1, self.y_point_1, self.z_point_1 = self.point_1

        if self.point_2:
            self.x_point_2, self.y_point_2, self.z_point_2 = self.point_2

        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("grndID", 1),
                FloatField("x_point_1", 2),
                FloatField("y_point_1", 4),
                FloatField("z_point_1", 6),
                IntField("nodeID_1", 8),
                IntField("nodeID_2", 9),
                IntField("subID", 10),
            ],
            [
                FloatField("x_point_2", 2),
                FloatField("y_point_2", 4),
                FloatField("z_point_2", 6),
                FloatField("angle", 8),
            ],
        ]

        return structure


#* /TRANSFORM/SCA
@dataclass
class TransformSca(Keyword):
    ID: int
    title: str
    grndID: int | None = None
    fscale_x: float = 0.0
    fscale_y: float = 0.0
    fscale_z: float = 0.0
    nodeID_c: int | None = None
    unitID: int | None = None

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("grndID", 1),
                FloatField("fscale_x", 2),
                FloatField("fscale_y", 4),
                FloatField("fscale_z", 6),
                IntField("nodeID_c", 8),
            ],
        ]

        return structure


#* /TRANSFORM/SYM
@dataclass
class TransformSym(Keyword):
    ID: int
    title: str
    grndID: int | None = None
    nodeID_1: int | None = None
    nodeID_2: int | None = None
    point_1: list[float] | NDArray | None = None
    point_2: list[float] | NDArray | None = None
    unitID: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        self.x_point_1 = None
        self.y_point_1 = None
        self.z_point_1 = None
        self.x_point_2 = None
        self.y_point_2 = None
        self.z_point_2 = None

    @property
    def pre_conditions(self):

        nodeIDs = [self.nodeID_1, self.nodeID_2]
        points = [self.point_1, self.point_2]

        conditions = [
            (
                not (has_all_nones(nodeIDs) and has_all_nones(points)),
                "No node ids or points provided; keyword definition is incomplete.",
            ),
            (
                is_exclusive(nodeIDs, points),
                "Either node ids or points must be provided, not both.",
            ),
        ]

        if self.point_1 != None:
            conditions.extend(
                [
                    (
                        has_shape(self.point_1, (3, 1)),
                        "Expected 3 coordinates for `point_1`",
                    ),
                    (
                        has_shape(self.point_2, (3, 1)),
                        "Expected 3 coordinates for `point_2`",
                    ),
                ]
            )

        return conditions

    @property
    def structure(self):
        if self.point_1:
            self.x_point_1, self.y_point_1, self.z_point_1 = self.point_1

        if self.point_2:
            self.x_point_2, self.y_point_2, self.z_point_2 = self.point_2

        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("grndID", 1),
                FloatField("x_point_1", 2),
                FloatField("y_point_1", 4),
                FloatField("z_point_1", 6),
                IntField("nodeID_1", 8),
                IntField("nodeID_2", 9),
            ],
            [
                FloatField("x_point_2", 2),
                FloatField("y_point_2", 4),
                FloatField("z_point_2", 6),
            ],
        ]

        return structure
#* /TRANSFORM/TRA 
@dataclass
class TransformTra(Keyword):
    """Defines a translation for a node group with a defined vector."""

    ID: int
    title: str
    grndID: int | None = None
    x_translation: float | None = 0.0
    y_translation: float | None = 0.0
    z_translation: float | None = 0.0
    nodeID_1: int | None = None
    nodeID_2: int | None = None
    subID: int | None = None
    unitID: int | None = None

    @property
    def pre_conditions(self):
        conditions = [
            (
                is_exclusive(self.grndID, self.subID),
                "Either `grndID` or `subID` must be provided, not both.",
            )
        ]

        return conditions

    @property
    def structure(self):

        if self.nodeID_1 and self.nodeID_2:
            self.x_translation = None
            self.y_translation = None
            self.z_translation = None

        structure: KeywordStructureType = [
            StringField("title", 1, 10),
            [
                IntField("grndID", 1),
                FloatField("x_translation", 2),
                FloatField("x_translation", 4),
                FloatField("x_translation", 6),
                IntField("nodeID_1", 8),
                IntField("nodeID_1", 9),
                IntField("subID", 10),
            ],
        ]

        return structure


#* /TRIA
@dataclass
class Tria(Keyword):
    """Describes the 2D solid elements based on 3 nodes. TRIA elements must be
    defined in the global YZ plane.
    """

    ID: int
    triaIDs: list | tuple | NDArray
    nodeIDs: NDArray

    @property
    def pre_conditions(self):

        return [
            (
                have_same_length(self.triaIDs, self.nodeIDs),
                "Pre-condition `len(triaIDs) == len(nodeIDs)` is violated.",
            )
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            ArrayOfAtomicFields(
                [
                    IntField("triaIDs", 1),
                    IntField("nodeIDs:ID_1|0", 2),
                    IntField("nodeIDs:ID_2|1", 3),
                    IntField("nodeIDs:ID_3|2", 4),
                ]
            )
        ]

        return structure


#* /TRUSS
@dataclass
class Truss(Keyword):
    """Describes one dimension truss elements, which could be used with
    property /PROP/TYPE2 (TRUSS). Truss could only carry axial load (like for
    bar).

    """

    ID: int
    trussIDs: list | tuple | NDArray
    nodeIDs: NDArray

    @property
    def pre_conditions(self):

        return [
            (
                have_same_length(self.trussIDs, self.nodeIDs),
                "Pre-condition `len(trussIDs) == len(nodeIDs)` is violated.",
            )
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            ArrayOfAtomicFields(
                [
                    IntField("trussIDs", 1),
                    IntField("nodeIDs:ID_1|0", 2),
                    IntField("nodeIDs:ID_2|1", 3),
                ]
            )
        ]

        return structure


