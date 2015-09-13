# Reads the current lexicon and extracts the existing lexical entries.
# Creates a map of lexical entries to the number of occurences in the lexicon

import sys
from tdl_regexs import *

# list of types and stems of words that don't have predicates
# if this type and stem are encountered, generate an empty predicate
wordsWithoutPredicates = [["arg12-14_verb-cop_past_le","hih"],
                         ["arg12-14_verb-cop_past_le","hith"],
                         ["arg12-14_pron-cop_present_le","hwa"],
                         ["arg12-14_pron-cop_present_le","hia"],
                         ["acc-marking-lex","at"],
                         ["nmc-complementizer-lex-item","e"]]


# list of all the wordTuples for each part of speech
# the indexing for the partsOfSpeechList is as follows:
    # 0: Nouns
    # 1: Verbs
    # 2: Adjectives
    # 3: Adverbs
    # 4: Prepositions
    # 5: Functional
posList_indices_c = {"noun": 0,
                     "verb": 1,
                     "adjective": 2,
                     "adverb": 3,
                     "preposition": 4,
                     "functional": 5}
partsOfSpeechList = []

def updatePOS(currentPOS):
    if currentPOS is "noun":
        return "verb"
    elif currentPOS is "verb":
        return "adjective"
    elif currentPOS is "adjective":
        return "adverb"
    elif currentPOS is "adverb":
        return "preposition"
    elif currentPOS is "preposition":
        return "functional"
    else:
        print "unknown part of speech"
        sys.exit(0)

def getExistantEntries(fileName):
    # open the file
    try:
        fin = open(fileName, 'r')
    except:
        (type, detail) = sys.exc_info()[:2]
        print "\n*** %s: %s: %s ***" % (fileName, type, detail)
        exit()

    wordTuples = set() # set of tuples of (stem, type, predicate)

    currentPOS = "noun"

    wordType = "" # holds the next word's type
    wordStem = "" # holds the next word's stem
    wordPred = "" # holds the next word's predicate

    idiomatic = False # True whenever the parsing though idiomatic entries
    specialWord = False # True whenever the word has a peculiar structure

    for line in fin:

        if line[0] == ';': # line is a comment
            # the following lines are idiomatic
            if ";;Idiomatic" in line:
                idiomatic = True

            # line tells us about POS's
            if headings_re.search(line):
                # following lines are no longer idiomatic
                idiomatic = False
                # update the proper POS
                currentPOS = updatePOS(currentPOS)
                # append the previous POS list to the list
                partsOfSpeechList.append(wordTuples)
                wordTuples = set() # reinitialize
            continue

        # skip idiomatic entries (don't keep track of them)
        if idiomatic:
            continue

        # if the word is a verb or special form, add it separately with stem "special form",
        # and the entire tdl format in the word type
        if currentPOS is "verb" and specialWord is False \
                or "np-qpart-lex-item" in line or "adjp-qpart-lex-item" in line:
            
            typeCheck = type_re.search(line)
            # found the type
            if typeCheck:
                wordType = typeCheck.group(1)
                specialWord = True
                wordType = line
            continue
        if specialWord is True:
            wordType += line
            if "]." in line:
                specialWord = False
                if currentPOS == "verb":
                    wordTuples.add(("", wordType, ""))
                else:
                    wordTuples.add(("special_word", wordType, ""))
            continue

        typeCheck = type_re.search(line)
        # found the type, go to the next line to find the stem
        if typeCheck:
            wordType = typeCheck.group(1)
            continue

        stemCheck = stem_re.search(line)
        # found the word stem, go to the next line to find the predicate
        if stemCheck:
            wordStem = stemCheck.group(1)
            # make a list of all stems (there can be more than one)
            # associated with the word
            stems = wordStem.split("\", \"")
           
            # if there is more than one stem, save it internally with a space
            # to be consistent with the dinflections.csv file
            if len(stems) > 1:
                wordStem = ""
                for s in stems:
                    wordStem += (' ' + s)
                wordStem = wordStem.strip()
            continue

        predCheck = pred_re.search(line)
        # found the predicate, not add the tuple (type, stem, predicate) into
        # the unique word tuples set
        if predCheck:
            wordPred = predCheck.group(1)

            # strip the predicate of pos identifiers and underscores
            # the only two word predicate is "yl idi", so handle it
            # separately
            if wordPred == "_yl_idi_p_rel":
                wordPred = "yl_idi"
            else:
                wordPred = wordPred.split('_')[1]

            wordTuples.add((wordStem, wordType, wordPred))
            wordStem, wordType, wordPred = "", "", ""
            continue

        # if the type and stem don't have a predicate, generate a tuple,
        # (type, stem, "") and add it into the unique word tuples set
        if [wordType, wordStem] in wordsWithoutPredicates:
            wordTuples.add((wordStem, wordType, ""))
            wordStem, wordType, wordPred = "", "", ""

    # append the list of functional words to the list
    partsOfSpeechList.append(wordTuples)

#     for i in partsOfSpeechList[1]:
#         print i
#
# getExistantEntries("lexica/lexicon.tdl")
