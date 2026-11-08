import numpy

SIZE_INT8 = 1
SIZE_INT16 = 2
SIZE_INT32 = 4
SIZE_FLOAT32 = 4

ENDIANNESS = ">"
dt_int32 = numpy.dtype(numpy.int32).newbyteorder(">")
dt_int16 = numpy.dtype(numpy.int16).newbyteorder(">")
dt_int8 = numpy.dtype(numpy.int8).newbyteorder(">")
dt_float32 = numpy.dtype(numpy.float32).newbyteorder(">")


class BinReader:
    """Binry data reader. Uses numpy and struct to read single values,
    vectors and matrices of fixed-size types from a given byte array,
    keeping a pointer to last read byte"""

    cursor: int = 0

    def __init__(self, data: bytes):
        self.data = data

    def readInt32(self) -> int:
        return int(self.readInt32Vector(1)[0])

    def readIntAsBool(self) -> bool:
        return self.readInt32() != 0

    def readFloat32(self) -> float:
        return float(self.readFloat32Vector(1)[0])

    def readFloatVectorFromShorts(self, size: int) -> list[float]:
        arr = [
            float(val) / 3000
            for val in numpy.frombuffer(
                self.data, dtype=dt_int16, count=size, offset=self.cursor
            )
        ]
        self.cursor += SIZE_INT16 * size
        return arr

    def readFloat32Vector(self, size: int) -> numpy.ndarray:
        arr = numpy.frombuffer(
            self.data, dtype=dt_float32, count=size, offset=self.cursor
        )
        self.cursor += SIZE_FLOAT32 * size
        return arr

    def readFloat32Matrix(
        self, numberOfFloats: int, numberOfArrays: int
    ) -> numpy.ndarray:
        return numpy.array(
            [self.readFloat32Vector(numberOfFloats) for _ in range(numberOfArrays)]
        )

    def readInt32Vector(self, size: int) -> numpy.ndarray:
        arr = numpy.frombuffer(
            self.data, dtype=dt_int32, count=size, offset=self.cursor
        )
        self.cursor += SIZE_INT32 * size
        return arr

    def readInt8Vector(self, size: int) -> numpy.ndarray:
        arr = numpy.frombuffer(self.data, dtype=dt_int8, count=size, offset=self.cursor)
        self.cursor += SIZE_INT8 * size
        return arr

    def readStringVector(self, numberOfStrings: int, stringSize: int) -> list[str]:
        return [self.readString(stringSize) for _ in range(numberOfStrings)]

    def readString(self, size: int) -> str:
        return self.getBytes(size).decode("ascii").strip().rstrip("\x00")

    def getBytes(self, size: int) -> bytes:
        raw = self.data[self.cursor : self.cursor + size]
        self.cursor += size
        return raw
