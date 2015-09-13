
from converter_row import *

class advRowConverter(rowConverter):
	# keeps a set of tuples of (stem, pred)
	allAdvs = set()

	# load the allAdvs set given a set of tuples (stem, type, predicate)
	# the allAdvs set must be initially empty when this method is called
	@staticmethod
	def loadAllAdvs(advTuples):
		assert len(advRowConverter.allAdvs) is 0

		for adv in advTuples:
			advRowConverter.allAdvs.add((adv[0],adv[2]))

	# print all the adjectives from the set in tdl format
	# takes as input the list of names used so far, and whether to
	# print words with puctuation in them
	@staticmethod
	def printAllAdvs(lexicon, wantPunctuation, fileName):
		fout = open(fileName, 'w')

		for tup in advRowConverter.allAdvs:
			# if there is punctuation when we don't want it or vice-versa,
			# dont count it
			has_punct = containsPunct(tup[0], tup[1])
			if not wantPunctuation and has_punct or wantPunctuation and not has_punct:
				continue

			fout.write(advRowConverter.rowToTDL(tup, lexicon))
			fout.write('\n')

		fout.close()

	# adds the row into the allAdvs dictionary
	# this function does nothing if the row is irrelevant
	def addToDictionary(self):
		# skip rows that contain irrelevant nouns
		if self.irrelevant():
			return

		advRowConverter.allAdvs.add((self.getStem(), self.getPred()))

	# returns true if the row is irrelevant
	def irrelevant(self):
		# ignore entries that have a suffixStatus of (2)
		if self.row[suffixStatus_c] == '2':
			return True

		# ignore entries that have any value in the "png" column, except "-".
		elif self.row[png_c] != '-':
			return True

		# otherwise it's a relevant adverb
		else:
			return False
		

	# returns the tdl formatted string given the stem and predicate
	# in the allAdjs dictionary
	@staticmethod
	def rowToTDL(tup, lexicon):
		# return the .tdl format
		return ''.join((addToLexicon(replaceSpaceWithUnderscore(tup[0]), lexicon),
			" := adverb-lex &\n  [ STEM < \"",
			breakUpWordWithComma(tup[0]),
			"\" >,\n   SYNSEM.LKEYS.KEYREL.PRED _",
			tup[1],
			"_r_rel ].\n"))
