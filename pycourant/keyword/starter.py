"""
Provides a low-level interface for generating OpenRadioss starter files.
"""
from datetime import datetime
from pathlib import Path
from ..constants import LINE_SEPARATOR
# from .common import Keyword
from .common import *
from ._starter.A import *
from ._starter.B import *
from ._starter.C import *
from ._starter.D import *
from ._starter.E import *
from ._starter.F import *
from ._starter.G import *
from ._starter.H import *
from ._starter.I import *
from ._starter.Inter import *
from ._starter.K import *
from ._starter.L import *
from ._starter.M import *
from ._starter.Mat import *
from ._starter.N import *
from ._starter.P import *
from ._starter.Prop import *
from ._starter.Q import *
from ._starter.R import *
from ._starter.S import *
from ._starter.T import *
from ._starter.U import *
from ._starter.V import *
from ._starter.X import *


class Starter:
    """Represents the starter part of an OpenRadioss simulation. It features a
    very natural syntax for selecting keyword templates and providing them with
    the parameters they need for instantation:

    """

    def __init__(self, add_header=True, add_separator=False):
        """Initializes a new starter instance."""

        self.add_header = add_header
        self.add_separator = add_separator
        self._keywords = []
        self._runname = ""

    @property
    def runname(self) -> str:
        return self._runname

    def add(self, keyword: Keyword) -> None:
        if not isinstance(keyword, Keyword):
            raise ValueError(
                "Argument `keyword` must be an instance of a subclass of `Keyword`"
            )

        if len(self._keywords) == 0:
            if not isinstance(keyword, Begin):
                raise RuntimeError("The first keyword to add must be `/BEGIN`.")
            else:
                self._runname = keyword.runname

        self._keywords.append(keyword)

    def write(
        self, index=0, folder: str | Path | None = None, assume_yes=False
    ) -> None:
        """Writes the keywords to a file."""
        if folder is None:
            folder = Path().cwd()
        elif isinstance(folder, str):
            folder = Path(folder)

        filepath = folder.joinpath(f"{self.runname}_{index:04d}.rad")

        if filepath.is_file() and not assume_yes:
            overwrite_file = input(
                f"File `{filepath.name}` already exists. Overwrite? [yes/no (default=no)] "
            )

            if not overwrite_file.lower() in ("y", "yes"):
                return

        # Serialize the keywords
        with open(filepath, "w") as fd:
            if self.add_header:
                now = datetime.now().isoformat()
                fd.write("#RADIOSS STARTER\n")
                fd.write(f"# File created at {now}\n")
                fd.write("#\n")

            for keyword in self._keywords:
                if self.add_separator:
                    fd.write(LINE_SEPARATOR)
                    fd.write("\n")

                keyword.write(fd)
