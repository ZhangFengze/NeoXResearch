import sys
import struct


def Clamp8(i):
    return i % (1 << 8)


def Clamp32(i):
    return i % (1 << 32)


def ROL32(n, d):
    return ((n << d) % (1 << 32)) | (n >> (32 - d))


def ROR32(n, d):
    return ROL32(n, 32-d)


def LShift8(n, d):
    return (n << d) % (1 << 8)


def RShift8(n, d):
    return n >> d


def BytesToInt32(bytes):
    # return int.from_bytes(bytes, byteorder="little", signed=False)
    return struct.unpack("<I", bytes)[0]


def Int32ToBytes(i):
    # return i.to_bytes(4, byteorder="little", signed=False)
    return struct.pack("<I", i)


def Decrypt(buffer):
    key = 0x18B7A467
    buffer = bytearray(buffer)
    size = len(buffer)

    dword = key
    for i in range(size//4):
        dword = ~(dword ^ ROR32(BytesToInt32(
            buffer[i*4:i*4+4]), 32-(i & 0x1F)))
        buffer[i*4:i*4+4] = Int32ToBytes(Clamp32(dword))

    base = size//4*4
    for i in range(size % 4):
        byte = buffer[base+i]
        byte = (RShift8(byte, 8-i) | LShift8(byte, i)) ^ RShift8(dword, i*8)
        buffer[base+i] = Clamp8(~byte)
    return bytes(buffer)


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as infile:
        data = infile.read()
        data = Decrypt(data)
        with open(sys.argv[2], "wb") as outfile:
            outfile.write(data)
