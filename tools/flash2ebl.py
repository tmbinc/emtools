import sys, zlib, struct

# converts an EM35x flash image (dumped from 0x08000000, for example via SWI) to an .ebl

flash = open(sys.argv[1], "rb")

pagen = 0

EBLTAG_HEADER, EBLTAG_PROG, EBLTAG_ERASEPROG, EBLTAG_END = 0, 0xFE01, 0xFD03, 0xFC04

alldata = ""

image = ""

for i in range(0x2E000/0x800):
	page = flash.read(0x800)

	if not len(page):
		break

	if i < 4: # skip loader
		continue

	if page == ("\xFF" * 0x800):
		break

	if i == 4: # header
		aatBuff = page[:0x80]
		page = page[0x80:]
		image += "\xFF" * 0x80 + page
	else:
		image += page

	alldata += struct.pack(">HHI", EBLTAG_ERASEPROG, len(page) + 4, 0x08000000 + i * 0x800 + 0x800 - len(page))
	alldata += page

version=0x0201 
signature=0xe350 
flashAddr=0x08002000

baseTable, platInfo, microInfo, phyInfo, aatSize, softwareVersion, reserved, timestamp, imageInfo, imageCrc, pageRanges = struct.unpack("<24sBBBBHHI32sI12s", aatBuff[:0x54])

imageCrc = zlib.crc32(image) & 0xFFFFFFFF
pageRanges = chr(4) + chr(i-1) + ("\xFF" * 10)

aatBuff = struct.pack("<24sBBBBHHI32sI12s", baseTable, platInfo, microInfo, phyInfo, aatSize, softwareVersion, reserved, timestamp, imageInfo, imageCrc, pageRanges) + aatBuff[0x54:]

aatBuffp = aatBuff[:0x10] + "\xFF\xFF" + aatBuff[0x12:]

aatCrc = zlib.crc32(aatBuffp) & 0xFFFFFFFF

d = struct.pack(">HHII128s", version, signature, flashAddr, aatCrc, aatBuff)

alldata = struct.pack(">HH", EBLTAG_HEADER, len(d)) + d + alldata

alldata += struct.pack(">HH", EBLTAG_END, 4)
alldata += struct.pack("<I", zlib.crc32(alldata) & 0xFFFFFFFF)

open(sys.argv[2], "wb").write(alldata)
