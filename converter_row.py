
from spreadsheetInfo import *
from utfToTransliteration import *
from converter_helpers import *

class rowConverter():
	def __init__(self, row):
		self.row = row
	
	# adds the row into that part of speech's internal dictionary
	# this function does nothing if the row is irrelevant
	def addToDictionary(self):
		pass

	# returns true if the row is irrelevant	 
	def irrelevant(self):
		return True

	# returns True if the stem or lemma contains (.), (') or (")
	def containsPunct(self):
		# if .' or " in the stem, return True
		if '\'' in self.row[transliteration_c] or \
		   '\"' in self.row[transliteration_c] or \
		   '.' in self.row[transliteration_c]:
			return True

		# if .' or " in the lemma, return True
		if '\'' in self.getPred() or \
		   '\"' in self.getPred() or \
		   '.' in self.getPred():
			return True
	
		# no ' or " present
		else:
			return False

	# returns the stem for this row
	def getStem(self):
		return self.row[transliteration_c]

	# consturcts the hebrew transliteration of the predicate of the row
	def getPred(self):
		p = ""
		# append and return the transliteration for each letter
		for letter in self.row[lemma_c]:
			p += transliteration[ord(letter)-223] # defined in utfToTransliteration.py
		return p
