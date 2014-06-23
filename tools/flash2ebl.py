import sys, zlib, struct

# converts an EM35x flash image (dumped from 0x08000000, for example via SWI) to an .ebl

is_em358x = True

flash = open(sys.argv[1], "rb")

BOOTLOADER_SIZE = 0x4000 if is_em358x else 0x2000
FLASH_SIZE = 512*1024 if is_em358x else 192*1024
PAGE_SIZE = 0x800
EBLTAG_HEADER, EBLTAG_PROG, EBLTAG_ERASEPROG, EBLTAG_END = 0, 0xFE01, 0xFD03, 0xFC04

BOOTLOADER_PAGES = BOOTLOADER_SIZE / PAGE_SIZE

alldata = ""

image = ""

for i in range(FLASH_SIZE/PAGE_SIZE):
	if i >= BOOTLOADER_PAGES or True:
		page = flash.read(PAGE_SIZE)

	if i < BOOTLOADER_PAGES: # skip loader
		continue

	if not len(page):
		break

	if page == ("\xFF" * PAGE_SIZE):
		break

	if len(page) != 0x800:
		page += "\xFF" * (PAGE_SIZE - len(page))

	if i == BOOTLOADER_PAGES: # header
		aatBuff = page[:0x80]
		page = page[0x80:]
		image += "\xFF" * 0x80 + page
	else:
		image += page

	alldata += struct.pack(">HHI", EBLTAG_ERASEPROG, len(page) + 4, 0x08000000 + i * PAGE_SIZE + PAGE_SIZE - len(page))
	alldata += page

version=0x0201 
signature=0xe350
flashAddr=0x08000000 + BOOTLOADER_SIZE

baseTable, platInfo, microInfo, phyInfo, aatSize, softwareVersion, reserved, timestamp, imageInfo, imageCrc, pageRanges = struct.unpack("<24sBBBBHHI32sI12s", aatBuff[:0x54])

assert aatSize == 0xAC
assert struct.unpack("<H", baseTable[0x10:0x12])[0] == 0xAA7
assert struct.unpack("<H", baseTable[0x12:0x14])[0] & 0xFF00 == 0x100
assert platInfo == 4
#print "microInfo %x" % microInfo
#assert microInfo in [6,8]
microInfo = 6

imageCrc = zlib.crc32(image) & 0xFFFFFFFF

# pageRanges is a series of 12 (skip,check) tuples. We skip the header, but check the image.

pageRanges = chr(BOOTLOADER_PAGES) + chr(i-1) + ("\xFF" * 10)

aatBuff = struct.pack("<24sBBBBHHI32sI12s", baseTable, platInfo, microInfo, phyInfo, aatSize, softwareVersion, reserved, timestamp, imageInfo, imageCrc, pageRanges) + aatBuff[0x54:]

aatBuffp = aatBuff[:0x10] + "\xFF\xFF" + aatBuff[0x12:]

aatCrc = zlib.crc32(aatBuffp) & 0xFFFFFFFF

d = struct.pack(">HHII128s", version, signature, flashAddr, aatCrc, aatBuff)

alldata = struct.pack(">HH", EBLTAG_HEADER, len(d)) + d + alldata

alldata += struct.pack(">HH", EBLTAG_END, 4)
alldata += struct.pack("<I", zlib.crc32(alldata) & 0xFFFFFFFF)

open(sys.argv[2], "wb").write(alldata)
