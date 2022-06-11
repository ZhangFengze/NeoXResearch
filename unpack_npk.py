import os
import pathlib
import sys
import lz4.block
import mmh3


def StringID(s):
    return mmh3.hash(s, 0x9747B28C, signed=False)


def main(npk, outDir):
    os.makedirs(outDir, exist_ok=True)
    with open(npk, "rb") as infile:
        content = infile.read()
        magic = content[0:4]
        assert(magic == b'NXPK')

        fileCount = int.from_bytes(content[4:8], "little")
        print(f"{fileCount} files")

        entriesOffset = int.from_bytes(content[20:24], "little")
        entries = content[entriesOffset:entriesOffset+28*fileCount]

        for i in range(fileCount):
            entry = entries[i*28:i*28+28]

            id = int.from_bytes(entry[:4], "little")
            offset = int.from_bytes(entry[4:8], "little")
            inNpkSize = int.from_bytes(entry[8:12], "little")
            plainSize = int.from_bytes(entry[12:16], "little")
            compressType = int.from_bytes(entry[24:26], "little")
            encryptType = int.from_bytes(entry[26:27], "little")
            print(f"entry:{i}    id:{id:0X}    offset:{offset:08X}    inNpkSize:{inNpkSize:6}    plainSize:{plainSize:6}   compressType:{compressType}   entryptType:{encryptType}")

            assert(compressType == 2)
            assert(encryptType == 0)
            compressed = content[offset:offset+inNpkSize]
            decompressed = lz4.block.decompress(
                compressed, uncompressed_size=plainSize)

            with open(pathlib.Path(outDir)/f"{id:08X}", "wb") as outfile:
                outfile.write(decompressed)

        print(f'redirect.nxs -> {StringID("redirect.nxs"):08X}')


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
