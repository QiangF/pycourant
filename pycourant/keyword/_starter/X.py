from ..common import *

#* /XELEM 
@dataclass
class Xelem(Keyword):
    """Describes the multi-strand element. It could be use with /PROP/TYPE28
    (NSTRAND), and it could be used for belt modelization by taking nodes upon
    the dummy."""

    partID: int
    elemID: int
    grndID: int
    # TODO: Check if elemID/grndID should actually be arrays instead of single values.

    @property
    def keyword(self):
        return f"/XELEM/{self.partID}"

    @property
    def pre_conditions(self):
        return []

    @property
    def structure(self):
        structure: KeywordStructureType = [
            [IntField("elemID", 1), IntField("grndID", 2)]
        ]

        return structure


#* /XREF 
@dataclass
class Xref(Keyword):
    partID: int
    xref_title: str
    nodeIDs: list | tuple | NDArray
    xc_yc_zc: NDArray
    n_itrs: int = 100
    unitID: int | None = None

    @property
    def keyword(self):
        if self.unitID:
            return f"/XREF/{self.partID}/{self.unitID}"
        else:
            return f"/XREF/{self.partID}"

    @property
    def pre_conditions(self):
        # If both `nodeIDs` and `xc_yc_zc` reference the same array, there is
        # no need to check the length
        return [
            (
                have_same_length(self.nodeIDs, self.xc_yc_zc),
                "Pre-condition `len(nodeIDs) == len(xc_yc_zc)` is violated.",
            )
        ]

    @property
    def structure(self):
        structure: KeywordStructureType = [
            StringField("xref_title", 1, 10),
            IntField("n_itrs", 1),
            ArrayOfAtomicFields(
                (
                    IntField("nodeIDs", 1),
                    FloatField("xc_yc_zc:xc|0", 2),
                    FloatField("xc_yc_zc:yc|1", 4),
                    FloatField("xc_yc_zc:xc|2", 6),
                )
            ),
        ]

        return structure
