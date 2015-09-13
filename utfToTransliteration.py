# Converts the hebrew form of the letter to the English transliteration
transliteration = {
	1 : 'a',
	2 : 'b',
	3 : 'g',
	4 : 'd',
	5 : 'h',
	6 : 'w',
	7 : 'z',
	8 : 'x',
	9 : 'v',
	10 : 'i',
	11 : 'k',
	12 : 'k',
	13 : 'l',
	14 : 'm',
	15 : 'm',
	16 : 'n',
	17 : 'n',
	18 : 's',
	19 : 'y',
	20 : 'p',
	21 : 'p',
	22 : 'c',
	23 : 'c',
	24 : 'q',
	25 : 'r',
	26 : 'e',
	27 : 't',
	-177 : '.',
	-178 : '-',
	-180 : '+',
	-184 : '\'',
	-189 : '\"'
}

utf8_heb_to_transliteration = {
	u'\u05D0' : 'a',
	u'\u05D1' : 'b',
	u'\u05D2' : 'g',
	u'\u05D3' : 'd',
	u'\u05D4' : 'h',
	u'\u05D5' : 'w',	
	u'\u05D6' : 'z',
	u'\u05D7' : 'x',	
	u'\u05D8' : 'v',	
	u'\u05D9' : 'i',	
	u'\u05DA' : 'k',	
	u'\u05DB' : 'k',	
	u'\u05DC' : 'l',	
	u'\u05DD' : 'm',	
	u'\u05DE' : 'm',	
	u'\u05DF' : 'n',	
	u'\u05E0' : 'n',	
	u'\u05E1' : 's',	
	u'\u05E2' : 'y',	
	u'\u05E3' : 'p',	
	u'\u05E4' : 'p',	
	u'\u05E5' : 'c',	
	u'\u05E6' : 'c',	
	u'\u05E7' : 'q',	
	u'\u05E8' : 'r',	
	u'\u05E9' : 'e',	
	u'\u05EA' : 't'
}

def utfToTransliteration(c):
	c -= 223
	# since there might be arbitrary values in the dictionary, print out a
	# message so that the character can be added into the dictionary
	if c not in transliteration:
		print "not in!", c
	else:
		return transliteration[c]

def utf8ToTransliteration(hebrew):
	heb = hebrew.decode('utf-8')
	english = ""
	for h in heb:
		english += utf8_heb_to_transliteration[h]
	return english


