#!/usr/bin/env python3

# MP3 (with an ID3v1 footer)

from parsers import FType


class parser(FType):
	DESC = "ID3v1 [Tag]"
	TYPE = "ID3v1"
	MAGIC = b"TAG"

	def __init__(self, data=""):
		FType.__init__(self, data)
		self.data = data

		# the L3Frames should start at offset 0 in a pure ID3v1 file
		self.start_o = 0

		# we could put fake data in trailing 00s of the Tag field
		self.bParasite = False

		self.bAppData = False # it's a footer


	def identify(self):
		return self.data[-128:].startswith(self.MAGIC)
