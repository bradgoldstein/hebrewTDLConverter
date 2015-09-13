#converter_adjective_helpers.py - helper functions for converter_adjective.py

from spreadsheetInfo import *

ignoredLexicalPointers = [29061]
# adjectives that have undefined gender and are masculine
undefinedMasculine = ['hpletim', 'pletim', 'htawrvi', 'tawrvi', 'htyeiti', 'tyeiti', 'htyeitiim', 'tyeitiim']
# adjectives that have undefined gender and are feminine
undefinedFeminine = ['hdtih', 'dtih']

# determine the definiteness of an adjective
def definiteness(definite):
	# adjective with definiteness (1) is definite
	if definite is '1':
		return "def"
	
	# adjective with definiteness (2,3,-) is indefnite
	else:
		return "indef"

# determine the number of an adjective
def number(num):
	# adjectives with number (3) are plural
	if num is '3':
		return "p"

	# all other adjectives are singluar
	else:
		return "s"

# determine the number of an adjective
def gender(gen, trans):
	# gender with value (1) is masculine
	if gen is '1':
		return "m"
	
	# gender with value (2) is feminine
	elif gen is '2':
		return "f"
	
	# unspecified gender with transliteration in the undefinedMasculine list are masculine
	elif trans in undefinedMasculine:
		return "m"
	
	# unspecified gender with transliteration in the undefinedFeminine list are feminine
	elif trans in undefinedFeminine:
		return "f"
	
	# hi"d has no gender
	else:
		return ""
