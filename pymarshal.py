# -*- coding: utf-8 -*-
import types
import cStringIO

TYPE_NULL = '0'
TYPE_NONE = 'N'
TYPE_FALSE = 'F'
TYPE_TRUE = 'T'
TYPE_STOPITER = 'S'
TYPE_ELLIPSIS = '.'
TYPE_INT = 'i'
TYPE_INT64 = 'I'
TYPE_FLOAT = 'f'
TYPE_COMPLEX = 'x'
TYPE_LONG = 'l'
TYPE_STRING = 's'
TYPE_INTERNED = 't'
TYPE_STRINGREF = 'R'
TYPE_TUPLE = '('
TYPE_LIST = '['
TYPE_DICT = '{'
TYPE_CODE = 'c'
TYPE_UNICODE = 'u'
TYPE_UNKNOWN = '?'
TYPE_SET = '<'
TYPE_FROZENSET = '>'


UNKNOWN_BYTECODE = 0


class _NULL:
    pass


class _Marshaller:
    dispatch = {}

    def __init__(self, writefunc, opmap=None):
        self._write = writefunc
        self._opmap = opmap or {}

    def dump(self, x):
        try:
            self.dispatch[type(x)](self, x)
        except KeyError:
            for tp in type(x).mro():
                func = self.dispatch.get(tp)
                if func:
                    break
            else:
                raise ValueError("unmarshallable object")
            func(self, x)

    def w_long64(self, x):
        self.w_long(x)
        self.w_long(x >> 32)

    def w_long(self, x):
        a = chr(x & 0xff)
        x >>= 8
        b = chr(x & 0xff)
        x >>= 8
        c = chr(x & 0xff)
        x >>= 8
        d = chr(x & 0xff)
        self._write(a + b + c + d)

    def w_short(self, x):
        self._write(chr((x) & 0xff))
        self._write(chr((x >> 8) & 0xff))

    def dump_none(self, x):
        self._write(TYPE_NONE)

    dispatch[type(None)] = dump_none

    def dump_bool(self, x):
        if x:
            self._write(TYPE_TRUE)
        else:
            self._write(TYPE_FALSE)

    dispatch[bool] = dump_bool

    def dump_stopiter(self, x):
        if x is not StopIteration:
            raise ValueError("unmarshallable object")
        self._write(TYPE_STOPITER)

    dispatch[type(StopIteration)] = dump_stopiter

    def dump_ellipsis(self, x):
        self._write(TYPE_ELLIPSIS)

    try:
        dispatch[type(Ellipsis)] = dump_ellipsis
    except NameError:
        pass

    # In Python3, this function is not used; see dump_long() below.
    def dump_int(self, x):
        y = x >> 31
        if y and y != -1:
            self._write(TYPE_INT64)
            self.w_long64(x)
        else:
            self._write(TYPE_INT)
            self.w_long(x)

    dispatch[int] = dump_int

    def dump_long(self, x):
        self._write(TYPE_LONG)
        sign = 1
        if x < 0:
            sign = -1
            x = -x
        digits = []
        while x:
            digits.append(x & 0x7FFF)
            x = x >> 15
        self.w_long(len(digits) * sign)
        for d in digits:
            self.w_short(d)

    try:
        long
    except NameError:
        dispatch[int] = dump_long
    else:
        dispatch[long] = dump_long

    def dump_float(self, x):
        write = self._write
        write(TYPE_FLOAT)
        s = repr(x)
        write(chr(len(s)))
        write(s)

    dispatch[float] = dump_float

    def dump_complex(self, x):
        write = self._write
        write(TYPE_COMPLEX)
        s = repr(x.real)
        write(chr(len(s)))
        write(s)
        s = repr(x.imag)
        write(chr(len(s)))
        write(s)

    try:
        dispatch[complex] = dump_complex
    except NameError:
        pass

    def dump_string(self, x):
        # XXX we can't check for interned strings, yet,
        # so we (for now) never create TYPE_INTERNED or TYPE_STRINGREF
        self._write(TYPE_STRING)
        self.w_long(len(x))
        self._write(x)

    dispatch[bytes] = dump_string

    def dump_unicode(self, x):
        self._write(TYPE_UNICODE)
        s = x.encode('utf8')
        self.w_long(len(s))
        self._write(s)

    try:
        unicode
    except NameError:
        dispatch[str] = dump_unicode
    else:
        dispatch[unicode] = dump_unicode

    def dump_tuple(self, x):
        self._write(TYPE_TUPLE)
        self.w_long(len(x))
        for item in x:
            self.dump(item)

    dispatch[tuple] = dump_tuple

    def dump_list(self, x):
        self._write(TYPE_LIST)
        self.w_long(len(x))
        for item in x:
            self.dump(item)

    dispatch[list] = dump_list

    def dump_dict(self, x):
        self._write(TYPE_DICT)
        for key, value in x.items():
            self.dump(key)
            self.dump(value)
        self._write(TYPE_NULL)

    dispatch[dict] = dump_dict

    def dump_code(self, x):
        self._write(TYPE_CODE)
        self.w_long(x.co_argcount)
        self.w_long(x.co_nlocals)
        self.w_long(x.co_stacksize)
        self.w_long(x.co_flags)
        # self.dump(x.co_code)

        self.dump(self._transform_opcode(x.co_code))

        self.dump(x.co_consts)
        self.dump(x.co_names)
        self.dump(x.co_varnames)
        self.dump(x.co_freevars)
        self.dump(x.co_cellvars)
        self.dump(x.co_filename)
        self.dump(x.co_name)
        self.w_long(x.co_firstlineno)
        self.dump(x.co_lnotab)

    try:
        dispatch[types.CodeType] = dump_code
    except NameError:
        pass

    def _transform_opcode(self, x):
        if not self._opmap:
            return x
            
        opcode = bytearray(x)
        old_addr = range(len(x)) # 记录对应的旧地址，用来修复jump

        c = 0
        while c < len(opcode):
            n = opcode[c]
            if n == 160:
                print("!!!! 160")
            
            if n== 110:
                print("!!!! 110")

            # 169相当于LOAD_CONST接LOAD_CONST
            if n == 169:
                opcode[c]=153
                opcode[c+3]=153

            # 186相当于LOAD_CONST接MAKE_FUNCTION
            if n==186:
                opcode[c]=153
                opcode[c+3]=136

            # 202相当于LOAD_ATTR接LOAD_ATTR
            if n==202:
                opcode[c]=96
                opcode[c+3]=96
            
            # 143相当于CALL_FUNCTION接POP_TOP
            # POP_TOP无参，插入到后面
            if n==143:
                opcode[c]=131
                opcode=opcode[:c+3]+ bytearray([38]) + opcode[c+3:]
                old_addr=old_addr[:c+3]+[old_addr[c+2]]+old_addr[c+3:]

            # 231相当于LOAD_CONST接RETURN_VALUE
            # RETURN_VALUE无参，插入到后面
            if n==231:
                opcode[c]=153
                opcode=opcode[:c+3]+ bytearray([83]) + opcode[c+3:]
                old_addr=old_addr[:c+3]+[old_addr[c+2]]+old_addr[c+3:]

            # 173相当于LOAD_FAST 0 接LOAD_CONST
            # LOAD_FAST参数固定0
            if n==173:
                opcode=opcode[:c]+bytearray([97,0,0,153])+opcode[c+1:]
                old_addr=old_addr[:c]+[old_addr[c]]*4+old_addr[c+1:]

            # 203相当于LOAD_FAST接LOAD_FAST
            if n==203:
                opcode[c]=97
                opcode[c+3]=97

            # 124相当于LOAD_FAST接LOAD_CONST
            if n==124:
                opcode[c]=97
                opcode[c+3]=153

            # 227相当于LOAD_FAST接LOAD_ATTR
            if n==227:
                opcode[c]=97
                opcode[c+3]=96

            # 205相当于LOAD_FAST接CALL_FUNCTION
            if n==205:
                opcode[c]=97
                opcode[c+3]=131

            # 208相当于LOAD_GLOBAL接LOAD_FAST
            if n==208:
                opcode[c]=155
                opcode[c+3]=97

            # 247相当于CALL_FUNCTION接STORE_FAST
            if n==247:
                opcode[c]=131
                opcode[c+3]=104

            # 168相当于LOAD_ATTR接LOAD_FAST
            if n==168:
                opcode[c]=96
                opcode[c+3]=97

            # 194相当于MAKE_FUNCTION接STORE_NAME
            if n==194:
                opcode[c]=136
                opcode[c+3]=145

            # 69相当于LOAD_LOCALS接RETURN_VALUE
            # 都不需要参数，插入
            if n==69:
                opcode=opcode[:c]+bytearray([50,83])+opcode[c+1:]
                old_addr=old_addr[:c]+[old_addr[c]]*2+old_addr[c+1:]

            # 210相当于COMPARE_OP接POP_JUMP_IF_FALSE
            if n==210:
                opcode[c]=114
                opcode[c+3]=148

            # 220相当于 LOAD_CONST LOAD_CONST STORE_MAP
            if n==220:
                opcode[c]=153
                opcode[c+3]=153
                opcode=opcode[:c+6]+bytearray([8])+opcode[c+6:]
                old_addr=old_addr[:c+6]+[old_addr[c+5]]+old_addr[c+6:]

            # 207相当于 STORE_NAME LOAD_CONST
            if n==207:
                opcode[c]=145
                opcode[c+3]=153

            # 214相当于 CALL_FUNCTION CALL_FUNCTION
            if n==214:
                opcode[c]=131
                opcode[c+3]=131

            # 201相当于LOAD_GLOBAL CALL_FUNCTION POP_TOP
            if n==201:
                opcode[c]=155
                opcode[c+3]=131
                opcode=opcode[:c+6]+bytearray([38])+opcode[c+6:]
                old_addr=old_addr[:c+6]+[old_addr[c+5]]+old_addr[c+6:]

            # 179相当于LOAD_ATTR CALL_FUNCTION
            if n==179:
                opcode[c]=96
                opcode[c+3]=131

            # 192相当于LOAD_ATTR LOAD_GLOBAL
            if n==192:
                opcode[c]=96
                opcode[c+3]=155

            # 150相当于LOAD_ATTR CALL_FUNCTION POP_TOP
            if n==150:
                opcode[c]=96
                opcode[c+3]=131
                opcode=opcode[:c+6]+bytearray([38])+opcode[c+6:]
                old_addr=old_addr[:c+6]+[old_addr[c+5]]+old_addr[c+6:]

            # 98相当于LOAD_CONST LOAD_FAST
            if n==98:
                opcode[c]=153
                opcode[c+3]=97
            
            # 244相当于LOAD_GLOBAL CALL_FUNCTION
            if n==244:
                opcode[c]=155
                opcode[c+3]=131

            # 190相当于LOAD_CONST IMPORT_NAME
            if n==190:
                opcode[c]=153
                opcode[c+3]=134

            # 209相当于LOAD_CONST CALL_FUNCTION
            if n==209:
                opcode[c]=153
                opcode[c+3]=131

            # 185相当于LOAD_FAST STORE_ATTR
            if n==185:
                opcode[c]=97
                opcode[c+3]=132

            # 162相当于LOAD_FAST CALL_FUNCTION POP_TOP
            if n==162:
                opcode[c]=97
                opcode[c+3]=131
                opcode=opcode[:c+6]+bytearray([38])+opcode[c+6:]
                old_addr=old_addr[:c+6]+[old_addr[c+5]]+old_addr[c+6:]

            # 215相当于LOAD_CONST COMPARE_OP
            if n==215:
                opcode[c]=153
                opcode[c+3]=114

            # 188相当于LOAD_CONST BINARY_SUBSCR
            # BINARY_SUBSCR不需要参数，插入
            if n==188:
                opcode[c]=153
                opcode=opcode[:c+3]+ bytearray([10]) + opcode[c+3:]
                old_addr=old_addr[:c+3]+[old_addr[c+2]]+old_addr[c+3:]

            # 79相当于POP_TOP POP_TOP POP_TOP
            # 都无参，插入
            if n==79:
                opcode=opcode[:c]+bytearray([38,38,38])+opcode[c+1:]
                old_addr=old_addr[:c]+[old_addr[c]]*3+old_addr[c+1:]
            
            # 20相当于BINARY_SUBSCR RETURN_VALUE
            # 都无参，插入
            if n==20:
                opcode=opcode[:c]+bytearray([10,83])+opcode[c+1:]
                old_addr=old_addr[:c]+[old_addr[c]]*2+old_addr[c+1:]

            # 222相当于POP_TOP LOAD_CONST
            # POP_TOP无参，插入
            if n==222:
                opcode=opcode[:c]+bytearray([38,153])+opcode[c+1:]
                old_addr=old_addr[:c]+[old_addr[c]]*2+old_addr[c+1:]

            # 180相当于POP_TOP JUMP_FORWARD
            # POP_TOP无参，插入
            if n==180:
                opcode=opcode[:c]+bytearray([38,156])+opcode[c+1:]
                old_addr=old_addr[:c]+[old_addr[c]]*2+old_addr[c+1:]

            # 248相当于LOAD_CONST STORE_MAP
            # STORE_MAP无参，插入
            if n==248:
                opcode[c]=153
                opcode=opcode[:c+3]+bytearray([8])+opcode[c+3:]
                old_addr=old_addr[:c+3]+[old_addr[c+2]]+old_addr[c+3:]

            # 119相当于STORE_FAST LOAD_FAST
            if n==119:
                opcode[c]=104
                opcode[c+3]=97

            # 199相当于STORE_FAST LOAD_GLOBAL
            if n==199:
                opcode[c]=104
                opcode[c+3]=155


            try:
                # 手动补充 std ExTENDED_ARG 145 -> neox 160 
                if n==160:
                    n=145
                else:
                    n = self._opmap[opcode[c]]
            except:
                print("unknown %s" % opcode[c])
                # print("unknown %s, set 255" % opcode[c])
                # n=255

            opcode[c] = n

            if n < 90:
                c += 1
            else:
                c += 3

        c=0
        while c < len(opcode):
            n = opcode[c]

            #define JUMP_FORWARD	110	/* Number of bytes to skip */
            #define SETUP_LOOP	120	/* Target address (relative) */
            #define SETUP_EXCEPT	121	/* "" */
            #define SETUP_FINALLY	122	/* "" */
            #define SETUP_WITH 143
            if n==110 or n==120 or n==121 or n==122 or n==143:
                to_skip = opcode[c+1] + (opcode[c+2] << 8)

                self_old_addr = old_addr[c+3]
                self_new_addr = old_addr.index(self_old_addr)

                target_old_addr = self_old_addr+to_skip
                target_new_addr = old_addr.index(target_old_addr)

                new_to_skip = target_new_addr-self_new_addr

                opcode[c+1] = new_to_skip % (1 << 8)
                opcode[c+2] = new_to_skip >> 8
                pass

            #define JUMP_IF_FALSE_OR_POP 111 /* Target byte offset from beginning of code */
            #define JUMP_IF_TRUE_OR_POP 112	/* "" */
            #define JUMP_ABSOLUTE	113	/* "" */
            #define POP_JUMP_IF_FALSE 114	/* "" */
            #define POP_JUMP_IF_TRUE 115	/* "" */
            if n == 111 or n == 112 or n == 113 or n == 114 or n == 115:

                target = opcode[c+1]+(opcode[c+2] << 8)
                new_target = old_addr.index(target)
                opcode[c+1] = new_target % (1 << 8)
                opcode[c+2] = new_target >> 8

            if n < 90:
                c += 1
            else:
                c += 3

        return str(opcode)

    def dump_set(self, x):
        self._write(TYPE_SET)
        self.w_long(len(x))
        for each in x:
            self.dump(each)

    try:
        dispatch[set] = dump_set
    except NameError:
        pass

    def dump_frozenset(self, x):
        self._write(TYPE_FROZENSET)
        self.w_long(len(x))
        for each in x:
            self.dump(each)

    try:
        dispatch[frozenset] = dump_frozenset
    except NameError:
        pass


class _Unmarshaller:
    dispatch = {}

    def __init__(self, readfunc):
        self._read = readfunc
        self._stringtable = []

    def load(self):
        c = self._read(1)
        if not c:
            raise EOFError
        try:
            return self.dispatch[c](self)
        except KeyError:
            raise ValueError("bad marshal code: %c (%d)" % (c, ord(c)))

    def r_short(self):
        lo = ord(self._read(1))
        hi = ord(self._read(1))
        x = lo | (hi << 8)
        if x & 0x8000:
            x = x - 0x10000
        return x

    def r_long(self):
        s = self._read(4)
        a = ord(s[0])
        b = ord(s[1])
        c = ord(s[2])
        d = ord(s[3])
        x = a | (b << 8) | (c << 16) | (d << 24)
        if d & 0x80 and x > 0:
            x = -((1 << 32) - x)
            return int(x)
        else:
            return x

    def r_long64(self):
        a = ord(self._read(1))
        b = ord(self._read(1))
        c = ord(self._read(1))
        d = ord(self._read(1))
        e = ord(self._read(1))
        f = ord(self._read(1))
        g = ord(self._read(1))
        h = ord(self._read(1))
        x = a | (b << 8) | (c << 16) | (d << 24)
        x = x | (e << 32) | (f << 40) | (g << 48) | (h << 56)
        if h & 0x80 and x > 0:
            x = -((1 << 64) - x)
        return x

    def load_null(self):
        return _NULL

    dispatch[TYPE_NULL] = load_null

    def load_none(self):
        return None

    dispatch[TYPE_NONE] = load_none

    def load_true(self):
        return True

    dispatch[TYPE_TRUE] = load_true

    def load_false(self):
        return False

    dispatch[TYPE_FALSE] = load_false

    def load_stopiter(self):
        return StopIteration

    dispatch[TYPE_STOPITER] = load_stopiter

    def load_ellipsis(self):
        return Ellipsis

    dispatch[TYPE_ELLIPSIS] = load_ellipsis

    dispatch[TYPE_INT] = r_long

    dispatch[TYPE_INT64] = r_long64

    def load_long(self):
        size = self.r_long()
        sign = 1
        if size < 0:
            sign = -1
            size = -size
        x = 0
        for i in range(size):
            d = self.r_short()
            x = x | (d << (i * 15))
        return x * sign

    dispatch[TYPE_LONG] = load_long

    def load_float(self):
        n = ord(self._read(1))
        s = self._read(n)
        return float(s)

    dispatch[TYPE_FLOAT] = load_float

    def load_complex(self):
        n = ord(self._read(1))
        s = self._read(n)
        real = float(s)
        n = ord(self._read(1))
        s = self._read(n)
        imag = float(s)
        return complex(real, imag)

    dispatch[TYPE_COMPLEX] = load_complex

    def load_string(self):
        n = self.r_long()
        return self._read(n)

    dispatch[TYPE_STRING] = load_string

    def load_interned(self):
        n = self.r_long()
        ret = intern(self._read(n))
        self._stringtable.append(ret)
        return ret

    dispatch[TYPE_INTERNED] = load_interned

    def load_stringref(self):
        n = self.r_long()
        return self._stringtable[n]

    dispatch[TYPE_STRINGREF] = load_stringref

    def load_unicode(self):
        n = self.r_long()
        s = self._read(n)
        ret = s.decode('utf8')
        return ret

    dispatch[TYPE_UNICODE] = load_unicode

    def load_tuple(self):
        return tuple(self.load_list())

    dispatch[TYPE_TUPLE] = load_tuple

    def load_list(self):
        n = self.r_long()
        list = [self.load() for i in range(n)]
        return list

    dispatch[TYPE_LIST] = load_list

    def load_dict(self):
        d = {}
        while 1:
            key = self.load()
            if key is _NULL:
                break
            value = self.load()
            d[key] = value
        return d

    dispatch[TYPE_DICT] = load_dict

    def load_code(self):
        argcount = self.r_long()
        nlocals = self.r_long()
        stacksize = self.r_long()
        flags = self.r_long()
        code = self.load()
        consts = self.load()
        names = self.load()
        varnames = self.load()
        freevars = self.load()
        cellvars = self.load()
        filename = self.load()
        name = self.load()
        firstlineno = self.r_long()
        lnotab = self.load()
        return types.CodeType(argcount, nlocals, stacksize, flags, code, consts,
                              names, varnames, filename, name, firstlineno,
                              lnotab, freevars, cellvars)

    dispatch[TYPE_CODE] = load_code

    def load_set(self):
        n = self.r_long()
        args = [self.load() for i in range(n)]
        return set(args)

    dispatch[TYPE_SET] = load_set

    def load_frozenset(self):
        n = self.r_long()
        args = [self.load() for i in range(n)]
        return frozenset(args)

    dispatch[TYPE_FROZENSET] = load_frozenset


def dump(x, f, opmap=None):
    m = _Marshaller(f.write, opmap)
    m.dump(x)


def load(f):
    um = _Unmarshaller(f.read)
    return um.load()


def loads(content):
    io = cStringIO.StringIO(content)
    return load(io)


def dumps(x, opmap=None):
    io = cStringIO.StringIO()
    dump(x, io, opmap)
    io.seek(0)
    return io.read()