import ast
import glob
import os
import pathlib
import re
from pathlib import Path
from typing import Any, Optional
import pyparsing as pp


# ---------------------------------------------------------------------------
# pyparsing grammar for brace blocks
# ---------------------------------------------------------------------------

_IGNORE = pp.quotedString | pp.cStyleComment | pp.pythonStyleComment
_BRACE_BLOCK = pp.nestedExpr("{", "}", ignore_expr=_IGNORE)

_BLOCK = pp.Group(
    pp.Word(pp.alphas)("name")
    + pp.Optional(
        pp.Suppress("(") + pp.SkipTo(")")("header") + pp.Suppress(")")
    )
    + _BRACE_BLOCK("body")
)


def parse_cfg_blocks(text: str) -> dict[str, list[dict[str, str]]]:
    """
    Parse top-level ``BLOCKNAME(...) { ... }`` constructs from a cfg file,
    correctly handling nested braces (e.g. conditional cards).
    """
    blocks: dict[str, list[dict[str, str]]] = {}
    for r in _BLOCK.searchString(text):
        body = "".join(r.body[0]) if r.body else ""
        header = r.header if "header" in r else ""
        blocks.setdefault(r.name, []).append({"header": header, "body": body})
    return blocks


# ---------------------------------------------------------------------------
# data_hierarchy.cfg support
# ---------------------------------------------------------------------------

def parse_data_hierarchy(hierarchy_file: Path) -> list[str]:
    """
    Extract keyword identifiers (e.g. ``/MAT/LAW90``) from
    ``data_hierarchy.cfg``.  Adjust the regex if your registry uses a
    different syntax.
    """
    text = hierarchy_file.read_text()
    keywords = re.findall(r"(/[A-Za-z][\w/]*)", text)
    seen: set[str] = set()
    unique: list[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
    return unique


def find_cfg_for_keyword(keyword: str, cfg_root: Path) -> Optional[Path]:
    """Locate the ``.cfg`` file that defines a keyword like ``/MAT/LAW90``."""
    parts = [p for p in keyword.strip("/").split("/") if p]
    if not parts:
        return None
    leaf = parts[-1]

    candidates = [
        cfg_root.joinpath(*parts, f"{leaf}.cfg"),
        cfg_root.joinpath(*parts, f"{leaf.lower()}.cfg"),
        cfg_root.joinpath(*parts[:-1], f"{leaf}.cfg"),
        cfg_root.joinpath(*parts[:-1], f"{leaf.lower()}.cfg"),
    ]
    for c in candidates:
        if c.exists():
            return c

    # Fallback: recursive filename search
    for pattern in (f"{leaf}.cfg", f"{leaf.lower()}.cfg"):
        matches = list(cfg_root.rglob(pattern))
        if matches:
            return matches[0]
    return None


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class hm_parser:

    def __init__(self, fileName):
        with open(fileName, "r") as r:
            self.file = r.read()
        self._blocks: Optional[dict[str, list[dict[str, str]]]] = None
        self.format()
        self.default()
        self.attributes()

    # -- helpers --------------------------------------------------------

    def _get_blocks(self) -> dict[str, list[dict[str, str]]]:
        if self._blocks is None:
            self._blocks = parse_cfg_blocks(self.file)
        return self._blocks

    @staticmethod
    def _split_statements(code: str) -> list[str]:
        """
        Split on ``;`` while respecting quoted strings, so values such as
        ``key = "a;b"`` are preserved.
        """
        statements: list[str] = []
        current: list[str] = []
        in_string: Optional[str] = None
        escape = False
        for ch in code:
            if escape:
                current.append(ch)
                escape = False
            elif ch == "\\":
                current.append(ch)
                escape = True
            elif in_string:
                current.append(ch)
                if ch == in_string:
                    in_string = None
            elif ch in ('"', "'"):
                current.append(ch)
                in_string = ch
            elif ch == ";":
                statements.append("".join(current))
                current = []
            else:
                current.append(ch)
        if current:
            statements.append("".join(current))
        return statements

    def convertDictionary(self, code: str) -> dict[str, Any]:
        """
        Convert ``key = value;`` statements into a Python dictionary using
        ``ast.literal_eval`` (safe, no ``eval``).
        """
        dictionary: dict[str, Any] = {}
        for statement in self._split_statements(code):
            statement = statement.strip()
            if not statement or "=" not in statement:
                continue
            try:
                key, value = statement.split("=", 1)
                dictionary[key.strip()] = ast.literal_eval(value.strip())
            except (ValueError, SyntaxError):
                # Skip malformed / non-literal entries
                pass
        return dictionary

    # -- block parsers ---------------------------------------------------

    def format(self):
        blocks = self._get_blocks()
        format_blocks = blocks.get("FORMAT", [])
        if not format_blocks:
            raise ValueError("No FORMAT block found in cfg file")

        # Re-use the first FORMAT block (original behaviour) but keep all
        # available blocks accessible for future conditional-card support.
        header = format_blocks[0]["header"]
        body = format_blocks[0]["body"]
        fmts = f"FORMAT({header}){{{body}}}"

        self.fmts: dict[str, Any] = {}
        m = re.search(r"HEADER\((.*)\)", fmts, re.M)
        self.fmts["HEADER"] = m.group(1) if m else ""
        self.fmts["VERSION"] = header

        CARDS = re.findall(r'CARD\("(.*);', fmts, re.M)
        COMMENTS = re.findall(r"COMMENT\((.*)\)", fmts, re.M)

        self.fmts["STRACTURE"] = ""
        self.fmts["VARIABLE"] = []
        for i, card in enumerate(CARDS):
            if i > 0 and i - 1 < len(COMMENTS):
                self.fmts["STRACTURE"] += "\t\t\t" + COMMENTS[i - 1] + ",\n"
            data = card.split('",')
            self.fmts["STRACTURE"] += (
                '\t\t\t"' + data[0] + '"%(' + data[1] + ",\n"
            )
            for var in data[1].replace(")", "").split(","):
                var = var.strip()
                if var:
                    self.fmts["VARIABLE"].append(var)

    def default(self):
        blocks = self._get_blocks()
        defaults = blocks.get("DEFAULTS", [])
        self.dflt = (
            self.convertDictionary(defaults[0]["body"]) if defaults else {}
        )

    def attributes(self):
        blocks = self._get_blocks()
        attrs = blocks.get("ATTRIBUTES", [])
        self.attr = ""
        if not attrs:
            return

        attr_text = attrs[0]["body"]
        for element in attr_text.split(";"):
            element = element.strip()
            if not element or "=" not in element:
                continue
            name, type_info = element.split("=", 1)
            name = name.strip()
            annotation, comment = self.typeConverter(type_info.strip())

            line = f"    {name}: {annotation}"
            if comment:
                line += f"  # {comment}"
            self.attr += line + "\n"

    def typeConverter(self, text: str) -> tuple[str, str]:
        """Return ``(python_annotation, comment)`` for a type descriptor."""
        m = re.search(r'"([^"]*)"', text)
        comment = m.group(1) if m else ""

        if "FLOAT" in text:
            return "float", comment
        if "INT" in text:
            return "int", comment
        if "STRING" in text:
            return "str", comment
        return "Any", text.strip()


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class generator:
    def __init__(self, fileName, ParsedObject):
        base = fileName.replace(".cfg", "")
        self.file = base
        p = pathlib.Path(base)
        self.onedir = os.path.join(*p.parts[-2:])
        self.Name = self.onedir.replace("/", "").replace("\\", "")
        self.data = ParsedObject

        self.readmaster()
        self.replace()
        self.createDataclass()

    def readmaster(self):
        with open("master.py", "r") as master:
            self.code = master.read()

    def replace(self):
        # Put defaulted fields last so the generated ``def structure(...)``
        # signature is always valid Python.
        variables = list(self.data.fmts["VARIABLE"])
        non_defaults: list[str] = []
        defaults: list[str] = []
        for var in variables:
            if var in self.data.dflt:
                defaults.append(f"{var}={self.data.dflt[var]!r}")
            else:
                non_defaults.append(var)
        inputs = ",".join([" " + v for v in non_defaults + defaults])
        if inputs:
            inputs += ","

        rep = {
            "$NAME": self.Name,
            "$ATTRIBUTES": self.data.attr,
            "$FORMAT": self.data.fmts["STRACTURE"],
            "$KEYWORD": self.onedir,
            "$VARIABLE": inputs,
        }
        rep = {re.escape(k): v for k, v in rep.items()}
        pattern = re.compile("|".join(rep.keys()))
        self.code = pattern.sub(lambda m: rep[re.escape(m.group(0))], self.code)

    def createDataclass(self):
        with open(f"{self.Name}.py", "w") as product:
            product.write(self.code)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def files() -> list[str]:
    """Fallback: recursively collect every ``.cfg`` under the cwd."""
    return glob.glob(os.getcwd() + "/**/*.cfg", recursive=True)


def main():
    # Adjust to match your hm_cfg_files layout.
    cfg_root = Path("hm_cfg_files/config/CFG/radioss2022")
    hierarchy_file = cfg_root / "data_hierarchy.cfg"

    if hierarchy_file.exists():
        keywords = parse_data_hierarchy(hierarchy_file)
        print(f"Found {len(keywords)} keywords in {hierarchy_file}")
        targets: list[Path] = []
        for kw in keywords:
            cfg = find_cfg_for_keyword(kw, cfg_root)
            if cfg is None:
                print(f"[WARN] No cfg file found for {kw}")
            else:
                targets.append(cfg)
    else:
        print(f"[WARN] {hierarchy_file} not found; falling back to glob")
        targets = [Path(f) for f in files()]

    for cfg in targets:
        try:
            parsed = hm_parser(str(cfg))
            generator(str(cfg), parsed)
            print(f"[OK] {cfg}")
        except Exception as exc:
            print(f"[ERROR] {cfg}: {exc}")


if __name__ == "__main__":
    main()
