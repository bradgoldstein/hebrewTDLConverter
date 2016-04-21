
from converter_row import *
import converter_adjective_helpers as adj

#LHS: Added a lexical pointer field and then added a solution to avoid entries that are the same as
#pre-existing ones (same solution as in converter_noun.py and converter_verb.py, see elaboration there.) 
class adjRowConverter(rowConverter):
	# keeps a dictionary from tuples of
	# (stem, pred, definiteness, number) -> list[gender]
	allAdjs = {}

	# load the allAdjs dictionary given a set of tuples (stem, type, predicate)
	# the allAdjs dictionary must be initially empty when this method is called
	@staticmethod
	def loadAllAdjs(adjTuples):
		assert len(adjRowConverter.allAdjs) is 0

		# special case
		for adj in adjTuples:
			if adj[0] == "special_word":
				#adjRowConverter.allAdjs.update({(adj[0],adj[1],0,0): 0})
				adjRowConverter.allAdjs.update({(adj[0],adj[1],0,0, DEFAULT_LEXICAL_POINTER): 0})#LHS: added default lexical pointer
				continue

			adjType = adj[1].split('-')

			# determine the definiteness of the wor
			definiteness = adjType[0]	
			# if the adjective is neither definite nor indefinite, it
			# is a special case
			if definiteness != "def" and definiteness != "indef":
				definiteness = "special"
			
			# determine the number and gender
			numberGender = adjType[1]
			number = numberGender[0]
			if len(numberGender) is 1:
				gender = ''
			else:
				gender = numberGender[1]

			if definiteness == "special":
				number = adj[1] # save the entire type in the number field

			#key = (adj[0], adj[2], definiteness, number)
			#LHS: set a default lexical pointer for all adjs from the pre-existing lexicon
			key = (adj[0], adj[2], definiteness, number, DEFAULT_LEXICAL_POINTER)
			adjRowConverter.allAdjs.update({key: [gender]})

	# print all the adjectives from the dictionary in tdl format
	# takes as input the list of names used so far, and whether to
	# print words with puctuation in them
	@staticmethod
	#def printAllAdjs(lexicon, wantPunctuation, fileName):
	def printAllAdjs(lexicon, fileName):#LHS: no need to check for punctuation here anymore
		fout = open(fileName, 'w')

		for key, value in adjRowConverter.allAdjs.iteritems():
			# if the word is a special exception, just print it out
			if key[0] == "special_word":
				#if not wantPunctuation:#LHS: not needed anymore
					#fout.write(key[1])
					#fout.write('\n')
				fout.write(key[1])
				fout.write('\n')
				continue

			'''# if there is punctuation when we don't want it or vice-versa,
			# dont count it
			has_punct = containsPunct(key[0], key[1])
			if not wantPunctuation and has_punct or wantPunctuation and not has_punct:
				continue'''#LHS: no longer needed

			fout.write(adjRowConverter.rowToTDL(key, value, lexicon))
			fout.write('\n')

		fout.close()

	# adds the row into the allAdjs dictionary
	# this function does nothing if the row is irrelevant
	def addToDictionary(self):
		# skip rows that contain irrelevant nouns
		if self.irrelevant():
			return

		r = self.row  # for readability

		# get the key for the dictionary, and the value (gender)
		#keyTuple = (self.getStem(), self.getPred(), \
			#adj.definiteness(r[definiteness_c]), adj.number(r[number_c]))

                #LHS: get rid of illegal punctuation in pred or stem
		stem = self.getStem()
		pred = self.getPred()
		(stem, pred) = replacePunct(stem, pred)
                		
		keyTuple = (stem, pred, \
			adj.definiteness(r[definiteness_c]), adj.number(r[number_c]), self.getLexicalPointer())#LHS
		gender = adj.gender(r[gender_c], r[transliteration_c])
		# find the already existant genders associated with this key
		genderList = adjRowConverter.allAdjs.get(keyTuple)
		
		preexistingKeyTuple = (stem, pred, \
			adj.definiteness(r[definiteness_c]), adj.number(r[number_c]), DEFAULT_LEXICAL_POINTER)##LHS - the key is unchanged, except the lexical pointer
		preexistingGenderList = adjRowConverter.allAdjs.get(preexistingKeyTuple)##LHS


		# if there are none, add our gender
		if genderList is None:
			if preexistingGenderList is None:#LHS - added this-subcondition. We only want the entry to be added if it doesn't already appear,
                        #including if there's a similar entry in the pre-existing lexicon
				adjRowConverter.allAdjs.update({keyTuple: [gender]})
		# else add the gender to the list
		else:
			genderList.append(gender)

	# returns true if the row is irrelevant
	def irrelevant(self):
		# ignore words with suffixStatus 1
		if self.row[suffixStatus_c] is '1':
			return True
		
		# ignore words with gender 3
		elif self.row[gender_c] is '3':
			return True
		
		# skip all rows with specified Lexical pointers
		elif int(self.row[lexicalPointer_c]) in adj.ignoredLexicalPointers:
			return True
	
		else:
			return False

	# returns the tdl formatted string given key and gender
	# in the allAdjs dictionary
	@staticmethod
	def rowToTDL(key, genders, lexicon):
		# if there is more than one gender associated with that tuple (i.e.
		# masculine and feminine), disregard the gender
		if len(genders) > 1:
			gender = ''

		# otherwise, set the gender to the gender associated with the tuple
		else:
			gender = genders[0]

		# return the .tdl format 
		return ''.join((addToLexicon(replaceSpaceWithUnderscore(key[0]), lexicon),
			" := ",
			key[2], '-',
			key[3],
			gender,
			"-adj-lex &\n  [ STEM < \"",
			breakUpWordWithComma(key[0]),
			"\" >,\n   SYNSEM.LKEYS.KEYREL.PRED _",
			key[1],
			"_j_rel ].\n"))
