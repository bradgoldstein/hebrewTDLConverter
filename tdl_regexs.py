
import re

# various regular expressions for parsing lexicon.tdl
# compile them all in one place for efficiency

# regex for header: ;======= POS ======
headings_re = re.compile("|".join(["= VERBS", "= ADJECTIVES", "= ADVERBS", "= PREPOSITIONS", "= FUNCTIONAL"]))
# regex for type: := type &
type_re = re.compile(':=\s*(.*)\s&')
# regex for stem: STEM < "xxxx" >
stem_re = re.compile('STEM\s*<\s*\"(.*)\"\s*>')
# regex for predicate: (~P)REL.PRED xxxx ].
pred_re = re.compile('[^P]REL.PRED\s*([\w-]*)\s?[,\]]')
		
# regex's specifically for verbs
# regex for png: HEAD.CNCRD png-xxx,
png_re = re.compile('HEAD.CNCRD png-(\w*)\W*')
# regex for predicate: (~P)REL.PRED _xxxx_v_rel ].
verb_pred_re = re.compile('[^P]REL.PRED\s*_(\w*)_v_rel')
# regex for tense _xxxx_le
tense_re = re.compile('_([a-z]*)_le')
# regex for realization argxxx-xx-xx_npc_npc_tense
complement_re = re.compile('arg(([0-9]*-?)*(_n?\w?p?c?)*)_\w*')
# regex for PPSORT DEPx-P _x_p_rel
ppsort_re = re.compile('DEP([256])-P ([-_abymlpre]*)\s?[,\]]?')
# regex for arg1_basic_
basic_re = re.compile('arg1_(basic)_')
