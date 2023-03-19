import math
import struct
from abc import ABC, abstractmethod
from inspect import currentframe, getframeinfo
from mandrake import AllMethods
from .constants import *

class ModbusTypeInteface(AllMethods):
    defaultByteOrder = ByteOrder.BIG_ENDIAN
    # def __new__(cls):
    # print ("__new__ magic method is called")
    # inst = object.__new__(cls)
    # return inst

    def __init__(self, args: dict = {}) -> None:
        # print("__init__ magic method is called")
        super().__init__()

        self._start_init()
        self._range = args.get('_range', [1, 1])
        self._dec = args.get('_dec', None)
        self._structFormat = None
        self._charFormat = args.get('_charFormat', 's')

        self.encoding = args.get('encoding', ENCODE_ASCII)
        self.byteOrder = args.get('byteOrder', self.defaultByteOrder)
        self.value = args.get('value', 0)
        self.raw = args.get('raw', None)
        self.len = args.get('len', 1)
        self.bytes = args.get('bytes', self.__dict__['bytes'])
        self.bits = args.get('bits', self.__dict__['bits'])
        self.dec = args.get('dec', None)
        self.unsigned = args.get('unsigned', False)
        self.format = args.get('format', '%s')
        self.callbBackFunction = None  # function (obj)
        self._end_init()

    # def __del__(self):
        # print("__del__ Destructor magic method is called")


class Any(ABC, ModbusTypeInteface):
    def _set_raw(self, value: bytes):
        if value is None:
            return
        t = type(value)
        if t == list:
            if len(value) == 0:
                return
            if self.bytes == 1:
                fL = '>b'
                fU = '>B'
            else:
                fL = '>h'
                fU = '>H'
            v = [struct.pack(fL if i < 0 else fU, i) for i in value]
            v = b''.join(v)
        elif t != bytes:
            return
        else:
            v = value
        self.__dict__['raw'] = v
        self.__dict__['value'] = struct.unpack(self._structFormat, v)[0]

    def _set_value(self, value: 'int|float|str'):
        self.__dict__['value'] = value
        self.__dict__['raw'] = struct.pack(self._structFormat, value)

    def _set_len(self, value: int):
        if value is None:
            return
        value = max([value,  math.ceil(self._range[0]/2)])
        value = min([value,  math.ceil(self._range[1]/2)])

        self.__dict__['len'] = value
        self.__dict__['bytes'] = value*2
        self.__dict__['bits'] = self.__dict__['bytes']*8

    def _set_bytes(self, value: int):
        if value is None:
            return
        value = max([value, self._range[0]])
        value = min([value, self._range[1]])

        self.__dict__['bytes'] = value
        self.__dict__['len'] = math.ceil(self.__dict__['bytes']/2)
        self.__dict__['bits'] = self.__dict__['bytes']*8

    def _set_bits(self, value: int):
        if value is None:
            return
        value = max([value, self._range[0]*8])
        value = min([value, self._range[1]*8])

        self.__dict__['bits'] = value
        self.__dict__['bytes'] = math.ceil(self.__dict__['bits']/8)
        self.__dict__['len'] = math.ceil(self.__dict__['bytes']/2)

    def _set_byteOrder(self, value):
        self.__dict__['byteOrder'] = value
        self.__dict__['_structFormat'] = self.byteOrder+self._charFormat

    def _set__charFormat(self, value):
        self.__dict__['_charFormat'] = value
        self.__dict__['_structFormat'] = self.byteOrder+self._charFormat


class Bit(Any):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [1, 2],
        'bits': 1,
        'format': '%d',
        '_charFormat': 's',
    } | args)

    def _set_raw(self, value):
        super()._set_raw(value)
        v = bin(self.__dict__['value'])[2:]
        v = v[-1*self.bits]
        # v = [int(x) for x in v]
        self.__dict__['value'] = v

    def _set_value(self, value: 'str'):
        super()._set_value(int('0b'+value, 2))


class Byte(Any):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        'format': '%d',
        '_charFormat': 'b',
    } | args)


class UByte(Byte):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'B',
    } | args)


class Short(Any):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [2, 2],
        'bytes': 2,
        'format': '%d',
        '_charFormat': 'h',
    } | args)


class UShort(Short):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'H',
    } | args)


class Int(Short):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [4, 4],
        'bytes': 4,
        '_charFormat': 'i',
    } | args)


class UInt(Int):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'I',
    } | args)


class Long(Int):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'l',
    } | args)


class ULong(Long):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'L',
    } | args)


class LongLong(Long):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [8, 8],
        'bytes': 8,
        'format': '%d',
        '_charFormat': 'q',
    } | args)


class ULongLong(LongLong):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'Q',
    } | args)


class Dec(Short):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        'format': '%.2f',
    } | args)

    def _set_dec(self, value: int):
        self.__dict__['dec'] = value
        self.__dict__['_dec'] = math.pow(10, value)

    def _set_raw(self, value):
        if value is None:
            return
        super()._set_raw(value)
        v=self.__dict__['value']/self._dec
        self.__dict__['value'] =v

    def _set_value(self, value):
        super()._set_value(value*self._dec)


class UDec(Dec):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'L',
    } | args)


class LongDec(Dec):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [4, 4],
        'bytes': 4,
        '_charFormat': 'l',
    } | args)


class ULongDec(Dec):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'L',
    } | args)


class LongLongDec(Dec):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [8, 8],
        'bytes': 8,
        '_charFormat': 'q',
    } | args)


class ULongLongDec(Dec):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_charFormat': 'Q',
    } | args)


class ShortFloat(Short):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        'format': '%.3f',
        '_charFormat': 'e',
    } | args)


class Float(Int):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        'format': '%.5f',
        '_charFormat': 'f',
    } | args)


class Double(LongLong):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        'format': '%.5f',
        '_charFormat': 'd',
    } | args)


class Char(Any):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        'format': '%s',
        'value': '',
        'byteOrder': ByteOrder.NONE,
        '_charFormat': 'c',
    } | args)


class Str(Char):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [1, 255],
        'bytes': 50,
        '_charFormat': 's',
    } | args)


class Char2(Str):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [2, 2],
        'bytes': 2,
        'len': 2,
    } | args)


class Char4(Str):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [4, 4],
        'bytes': 4,
    } | args)


class Char8(Str):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [8, 8],
        'bytes': 8,
    } | args)


class Char16(Str):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [16, 16],
        'bytes': 16,
    } | args)


class Char32(Str):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [32, 32],
        'bytes': 32,
    } | args)


class Char64(Str):
    def __init__(self, args: dict = {}) -> None: super().__init__({
        '_range': [64, 64],
        'bytes': 64,
    } | args)
