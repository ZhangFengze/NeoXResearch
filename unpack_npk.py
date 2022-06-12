import pathlib2
import sys
import lz4.block
import mmh3
import struct


def BytesToUInt32(bytes):
    # return int.from_bytes(bytes, byteorder="little", signed=False)
    return struct.unpack("<I", bytes)[0]


def BytesToUInt16(bytes):
    return struct.unpack("<H", bytes)[0]


def BytesToUInt8(bytes):
    return struct.unpack("<B", bytes)[0]


def StringID(s):
    return mmh3.hash(s, 0x9747B28C, signed=False)


def main(npk, outDir):
    redirectID = "%08X" % (StringID("redirect.nxs"))

    pathlib2.Path(outDir).mkdir(exist_ok=True, parents=True)
    with open(npk, "rb") as infile:
        content = infile.read()
        magic = content[0:4]
        assert(magic == b'NXPK')

        fileCount = BytesToUInt32(content[4:8])

        entriesOffset = BytesToUInt32(content[20:24])
        entries = content[entriesOffset:entriesOffset+28*fileCount]

        for i in range(fileCount):
            entry = entries[i*28:i*28+28]

            id = BytesToUInt32(entry[:4])
            id = "%08X" % (id)
            offset = BytesToUInt32(entry[4:8])
            inNpkSize = BytesToUInt32(entry[8:12])
            plainSize = BytesToUInt32(entry[12:16])
            compressType = BytesToUInt16(entry[24:26])
            encryptType = BytesToUInt8(entry[26:27])

            assert(compressType == 2)
            assert(encryptType == 0)
            compressed = content[offset:offset+inNpkSize]
            decompressed = lz4.block.decompress(
                compressed, uncompressed_size=plainSize)

            name = "redirect.nxs" if id == redirectID else id
            with open(str(pathlib2.Path(outDir) / name), "wb") as outfile:
                outfile.write(decompressed)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
