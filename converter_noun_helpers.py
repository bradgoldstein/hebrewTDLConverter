# converter_noun_helpers.py - helper functions for nounRowConverter

from spreadsheetInfo import *
from sys import exit

'''
# only pronouns that we are interested in including in the lexicon
wantedPronouns = ["ani", "anw", "anwki", "anxnw", "at", "ath", "atm", "atn", 
	"hia", "hwa", "hm", "hn"] '''

# LHS: later decision - we don't want to include any automatically created pronouns, we simply create them ourselves (but with a PRED that isn't "hwa").
wantedPronouns = []

# returns True if the word is a pronoun not in the list of wantedPronouns,
# and false otherwise
def irrelevantPronoun(word, pos):
	if pos != 9: # not a pronoun
		return False
	
	elif word not in wantedPronouns:
		return True
	
	else:
		return False

# determine the "type" of noun (common, proper, possissive, construct, etc.)
# and its definiteness. Return this as a tuple (definiteness, type)
def definitenessNounType(pos, suffixStatus, png, definite):
	if pos == 10: # proper noun
		return ("", "proper")

	# nouns that have a value for png are possessive nouns (bc they have a possessor)
	elif png != '-':
		return ("", "poss-cmn")
	
	elif pos == 7: # common nouns
		if suffixStatus == '1': # common noun with construct state true
			return ("", "cs")
		
		else: # all other common nouns
			return (definiteness(definite), "cmn")
	
	elif pos == 9: # pronoun
		return ("", "nom-pron")
	
	# error, no type has been found
	print "\n*** %s: %s: %s ***" % (pos, suffixStatus, png)
	exit()

# determine definiteness of the noun
def definiteness(i):
	# definiteness values (1,4,5) are definite
	if i in ['1', '4', '5']:
		return "def-"

	# definiteness values (2,3) are indefinite
	elif i in ['2', '3']:
		return "indef-"

	# definiteness value (-) should be ignored 
	return ""

# returns a tuple (person, number, gender)
def png(p, num, g):
	return (person(p), number(num), gender(g))

# determines the "person" of the noun (1,2,3)
def person(p):
	# person value of (-,3) is third person
	if p in ['-', '3']:
		return "3"

	# person value of (1) is first person 
	elif p == '1':
		return "1"

	# person value of (2) is second person	
	elif p == '2':
		return "2"

	# error, unknown person
	print "\n*** unknown person: %s ***" % (p)
	exit()

# determines the "number" of the noun
def number(num):
	# number value of (1,-) is singular
	if num in ['1', '-']:
		return "s"

	# number value of (2, 3, 4) is plural 
	elif num in ['2', '3', '4']:
		return "p"

	# number value of (5) is unspecified
	return ""

# determines the "gender" of the noun - (m/f)
def gender(g):
	# gender value of (1) is masculine
	if g == '1':
		return "m"

	# gender value of (2) is feminine	
	elif g == '2':
		return "f"

	# gender value of (3,-) is unspecified
	return "" 

# determines the person, number, gender of the possessor, and returns it as a tuple
def possessorPNG(png):
	if png == '-': # undefined
		return ('', '', '')
	png = int(png)
	assert png < 13 and png > 0
	if png == 1: # 1st/MF/Sg
		return ('1', 's', '')
	elif png == 2: # 2nd/F/Sg
		return ('2', 's', 'f')
	elif png == 3: # 2nd/M/Sg
		return ('2', 's', 'm')
	elif png == 4: # 3rd/M/Sg
		return ('3', 's', 'm')
	elif png == 5: # 3rd/F/Sg
		return ('3', 's', 'f')
	elif png == 6: # 1st/MF/Pl
		return ('1', 'p', '')
	elif png == 7: # 2nd/M/Pl
		return ('2', 'p', 'm')
	elif png == 8: # 2nd/F/Pl
		return ('2', 'p', 'f')
	elif png == 10: # 3rd/M/Pl
		return ('3', 'p', 'm')
	elif png == 11: # 3rd/M/Pl
		return ('3', 'p', 'f')
	elif png == 12: # 3rd/MF/Pl
		return ('3' , 'p', '')
	else:
		return ('', '', '')
