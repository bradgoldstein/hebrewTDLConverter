
import converter_verb as verb
import converter_noun as noun
import converter_adjective as adj
import converter_adverb as adv
from spreadsheetInfo import *

def converterFactory(row):
	# row is a verb
	if row[pos_c] in ['11', '13']:
		return verb.verbRowConverter(row)

	# row is a noun
	if row[pos_c] in ['7','9','10']:
		return noun.nounRowConverter(row)
	
	# row is an adjective
	elif row[pos_c] is '8':
		return adj.adjRowConverter(row)
	
	# row is an adverb
	elif row[pos_c] is '5':
		return adv.advRowConverter(row)
	
	# row is an unknown part of speech
	else:
		return None