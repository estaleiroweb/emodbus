BYTE_ORDER = {
    '@': {'byte order': 'native', 'size': 'native', 'alignment': 'native', },
    '=': {'byte order': 'native', 'size': 'standard', 'alignment': 'none', },
    '<': {'byte order': 'little-endian', 'size': 'standard', 'alignment': 'none', },
    '>': {'byte order': 'big-endian', 'size': 'standard', 'alignment': 'none', },
    '!': {'byte order': 'network (=big-endian)', 'size': 'standard', 'alignment': 'none', },
}
'''
### Link

https://docs.python.org/3/library/struct.html

### Table

| Character | Byte order             | Size     | Alignment
|:----------|:-----------------------|:---------|:------------
| @         | native                 | native   | native
| =         | native                 | standard | none
| <         | little-endian          | standard | none
| >         | big-endian             | standard | none
| !         | network (= big-endian) | standard | none
'''

class ByteOrder:
    NONE = '@'
    NAVITE = '='
    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'
    NETWORK = '!'

class Encode:
    ASCII = 'ascii'
    UTF8 = 'utf-8'
    
ENCODE_ASCII = 'ascii'
ENCODE_UTF8 = 'utf-8'


CHAR_FORMAT = {
    'x': {'cType': 'pad byte', 'pyType': 'no value', 'size': None, },
    'c': {'cType': 'char', 'pyType': 'str', 'size': 1, },
    'b': {'cType': 'signed char', 'pyType': 'int', 'size': 1, },
    'B': {'cType': 'unsigned char', 'pyType': 'int', 'size': 1, },
    '?': {'cType': '_Bool', 'pyType': 'bool', 'size': 1, },
    'h': {'cType': 'short', 'pyType': 'int', 'size': 2, },
    'H': {'cType': 'unsigned short', 'pyType': 'int', 'size': 2, },
    'i': {'cType': 'int', 'pyType': 'int', 'size': 4, },
    'I': {'cType': 'unsigned int', 'pyType': 'int', 'size': 4, },
    'l': {'cType': 'long', 'pyType': 'int', 'size': 4, },
    'L': {'cType': 'unsigned long', 'pyType': 'int', 'size': 4, },
    'q': {'cType': 'long long', 'pyType': 'int', 'size': 8, },
    'Q': {'cType': 'unsigned long long', 'pyType': 'int', 'size': 8, },
    'n': {'cType': 'ssize_t', 'pyType': 'int', 'size': (1, 8), },
    'N': {'cType': 'size_t', 'pyType': 'int', 'size': (1, 8), },
    'e': {'cType': '(6)', 'pyType': 'float', 'size': 2, },
    'f': {'cType': 'float', 'pyType': 'float', 'size': 4, },
    'd': {'cType': 'double', 'pyType': 'float', 'size': 8, },
    's': {'cType': 'char[]', 'pyType': 'str', 'size': (0, 65535), },
    'p': {'cType': 'char[]', 'pyType': 'str', 'size': (0, 65535), },
    'P': {'cType': 'void*', 'pyType': 'int', 'size': (0, 65535), },
}
'''
    https://docs.python.org/3/library/struct.html

    | Format | C Type             | Python type | Size |
    | ------ | ------------------ | ----------- | ---- |
    | x      | pad byte           | no value    |      |
    | c      | char               | bytes       | 1    |
    | b      | signed char        | int         | 1    |
    | B      | unsigned char      | int         | 1    |
    | ?      | _Bool              | bool        | 1    |
    | h      | short              | int         | 2    |
    | H      | unsigned short     | int         | 2    |
    | i      | int                | int         | 4    |
    | I      | unsigned int       | int         | 4    |
    | l      | long               | int         | 4    |
    | L      | unsigned long      | int         | 4    |
    | q      | long long          | int         | 8    |
    | Q      | unsigned long long | int         | 8    |
    | n      | ssize_t            | int         |      |
    | N      | size_t             | int         |      |
    | e      | (6)                | float       | 2    |
    | f      | float              | float       | 4    |
    | d      | double             | float       | 8    |
    | s      | char[]             | bytes       |      |
    | p      | char[]             | bytes       |      |
    | P      | void*              | int         |      |
'''

