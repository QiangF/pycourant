import sys, os, shutil, importlib
import warnings
warnings.filterwarnings("ignore")
sys.dont_write_bytecode = True
import argparse
import time
import pathlib

pyroll_path = os.path.expanduser('~/Documents/pyroll')
lib_path = os.path.join(pyroll_path, 'lib')
if not pyroll_path in sys.path:
    sys.path.append(pyroll_path)
    sys.path.append(lib_path)

from anim2vtkhdf.animtovtkhdf import AnimToVTKHDF

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="AnimToVTKHDF",
        description="Convert Radioss Anim files to the VTKHDF format",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="do not show the conversion operation details",
    )
    parser.add_argument(
        "-n",
        "--nostatic",
        action="store_true",
        help="do not write cells as static. Use when the connectivity does not change between time steps. If not set, only points and field values will be changed at each timestep.",
    )
    parser.add_argument(
        "infiles",
        nargs="*",
        type=pathlib.Path,
        help="input files to convert. All files must be part of a same time series, and have the same fields",
    )
    parser.add_argument("outfile", type=str, help="output file")

    args = parser.parse_args()
    converter = AnimToVTKHDF(verbose=not args.quiet, static=not args.nostatic)

    try:
        converter.convert(inputf=args.infiles, outputf=args.outfile)
    except ValueError as err:
        print(
            f"Could not write {args.infiles} as VTKHDF file {args.outfile}: {err.args}"
        )
