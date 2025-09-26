#!/usr/bin/env python3

# Flac (native)

from parsers import FType
from helpers import *


# Strategy:
# - add a FAKE application block
# - right after the first streaminginfo block according to the specs
#   (seems to work also right after the magic)


class parser(FType):
	DESC = "Flac / native Free Lossless Audio Codec"
	TYPE = "Flac"
	MAGIC = b"fLaC"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		# Risky? the file is ending with streams of audio data but it seems robust to determine its end.
		self.bAppData = True

		self.bParasite = True
		self.parasite_o = 8 # yes, it's required 
		self.parasite_s = 0xFFFFFF # size stored on 24 bits

		self.cut = 4
		self.prewrap = 2*4 # Header:4, Application ID:4
		self.postwrap = 0


	def getCut(self):
		# get the first block length
		a = b"\0" + self.data[5:5+3]
		l = get4b(a, 0)

		self.cut = 4+4+l
		self.parasite_o = self.cut + self.prewrap
		return self.cut


	def wrap(self, data, id=b"junk"):
		wrapped = b"".join([
			b"\4", # Application block, not last
			int4b(len(data) + 4)[1:], 
			id,
			data
		])
		return wrapped
