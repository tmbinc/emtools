import struct, sys, zlib

f = open(sys.argv[1], "rb")

out = None

if len(sys.argv) > 2:
	out = open(sys.argv[2], "wb+")

EBLTAG_HEADER, EBLTAG_PROG, EBLTAG_ERASEPROG, EBLTAG_END = 0, 0xFE01, 0xFD03, 0xFC04

alldata = ""

while True:
	h = f.read(4)
	tag, length = struct.unpack(">HH", h)
	print "tag %04x len %04x" % (tag, length),
	data = f.read(length)

	alldata += h + data

	if tag == EBLTAG_HEADER:
		version, signature, flashAddr, aatCrc, aatBuff = struct.unpack(">HHII128s", data)
		aatBuff = aatBuff[:0x10] + "\xFF\xFF" + aatBuff[0x12:]
		assert aatCrc == (zlib.crc32(aatBuff) & 0xFFFFFFFF)
		print "[HEADER] version=%04x signature=%04x flashAddr=%08x aatCrc=%08x " % (version, signature, flashAddr, aatCrc),
		assert signature == 0xE350

		baseTable, platInfo, microInfo, phyInfo, aatSize, softwareVersion, reserved, timestamp, imageInfo, imageCrc, pageRanges = struct.unpack("<24sBBBBHHI32sI12s", aatBuff[:0x54])

		print "aatBuff[platInfo=%02x microInfo=%02x phyInfo=%02x aatSize=%02x softwareVersion=%04x reserved=%04x timestamp=%08x imageInfo=%s imageCrc=%08x pageRanges=%s" % \
			(platInfo, microInfo, phyInfo, aatSize, softwareVersion, reserved, timestamp, imageInfo, imageCrc, pageRanges.encode('hex'))

		if out:
			out.seek(flashAddr - 0x08000000)
			out.write(aatBuff)
	elif tag == EBLTAG_PROG:
		print "[PROG]", data.encode('hex')
	elif tag == EBLTAG_ERASEPROG:
		flashAddr = struct.unpack(">I", data[:4])[0]
		print "[ERASEPROG] flashAddr=%08x" % flashAddr, data[4:16].encode('hex')
		if out:
			out.seek((flashAddr - 0x08000000) & ~0x7FF)
			out.write("\xFF" * 0x800)
			out.seek(flashAddr - 0x08000000)
			out.write(data[4:])
	elif tag == EBLTAG_END:
		crc = struct.unpack(">I", data)[0]
		ccrc = (zlib.crc32(alldata) ^ 0xFFFFFFFF) & 0xFFFFFFFF
		print "[END] crc=%08x, ccrc=%08x" % (crc, ccrc)
		assert ccrc == 0xDEBB20E3
		break
	else:
		print "UNKNOWN TAG"
		break

rs, re = ord(pageRanges[0]), ord(pageRanges[1])

if out:
	alldata = ""

	for p in range(rs, re + 1):
		out.seek(p * 0x800)
		alldata += out.read(0x800)

		assert zlib.crc32(alldata) & 0xFFFFFFFF == imageCrc

	print "all checks passed."
