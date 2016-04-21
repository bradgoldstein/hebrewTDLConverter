# This file gives the functionality for converting dinflections.csv
# to a tdl lexical type (for example like those in lexicon.tdl)
# to run, type python CSVToTDLLexicalType.py part_of_speech > outfile.tdl
# where part_of_speech is the part of speech that you want to convert
# to TDL. (e.g. noun, adjective)

#LHS: there is no need to specify part_of_speech in the command

from sys import argv
from collections import defaultdict
from converter_row import *
from converter_noun import *
from converter_adjective import *
from converter_adverb import *
from converter_verb import *
from CSV_helpers import openCSV
import converter_factory as factory
from getExistantEntries import *#LHS, so, partsOfSpeechList is accessible, as well as posList_indices_c

if __name__ == '__main__':
    lexicon_c = defaultdict(int) # a dictionary with all the stems and the number of times they appear

    # Call the function with the original file, lexicon.tdl
    print "loading the existing tdl lexicon..."
    getExistantEntries("lexica/lexicon.tdl")#LHS: parse the pre-existing lexicon

    print "loading existing nouns into noun converter..."
    nounRowConverter.loadAllNouns(partsOfSpeechList[posList_indices_c["noun"]])#LHS: meaning, partOFSpeechList[0], according to getExistantEntries.py;
    #LHS: what is passed to loadAllNouns is a list that contains a set of tuples (stem, type, predicate) of all the preexisting types of this specific POS
    print "loading existing adjectives into adjective converter..."
    adjRowConverter.loadAllAdjs(partsOfSpeechList[posList_indices_c["adjective"]])
    print "loading existing adverbs into adverb converter..."
    advRowConverter.loadAllAdvs(partsOfSpeechList[posList_indices_c["adverb"]])
    print "loading existing verbs into verb converter..."
    verbRowConverter.loadAllVerbs(partsOfSpeechList[posList_indices_c["verb"]], lexicon_c)
    print "loading PMI_Dictionary into verb converter..."
    verbRowConverter.loadPMIDictionary()

    csv_f = openCSV("lexica/new_dinflections.csv", '\t')
    # skip the header row
    iterRows = iter(csv_f)
    next(iterRows)

    print "parsing new_dinflections.csv..."

    for row in iterRows:
        # get the rowConverter class to convert the row to the proper TDL
        rowToTDL = factory.converterFactory(row)

        # skip rows that have no ways to be converted to TDL
        if rowToTDL is None:
            continue

        rowToTDL.addToDictionary()

    '''#LHS: print out the entire adjective/noun/verb dictionary
    adjKeys = adjRowConverter.allAdjs.keys()
    for k in adjKeys:
        print(str(k) + ' -> ' + str(adjRowConverter.allAdjs[k]))
    nounKeys = nounRowConverter.allNouns.keys()
    for k in nounKeys:
        print(str(k) + ' -> ' + str(nounRowConverter.allNouns[k]))
    verbKeys = verbRowConverter.allVerbs.keys()
    for k in verbKeys:
        print(str(k) + ' -> ' + str(verbRowConverter.allVerbs[k]))
    #LHS: print out all the adverbs
    for item in advRowConverter.allAdvs:
        print(str(item))
    verbCompKeys = verbRowConverter.verbsComplements.keys()#LHS test
    for k in verbCompKeys:#LHS test
        print(str(k) + ' -> ' + str(verbRowConverter.verbsComplements[k]))#LHS test'''

    print "printing noun lexicon..."
    nounRowConverter.printAllNouns(lexicon_c, "lexica/lexicon_noun.tdl")
    #nounRowConverter.printAllNouns(lexicon_c, False, "lexica/lexicon_noun.tdl")
    #print "printing noun lexicon with punctuation..."
    #nounRowConverter.printAllNouns(lexicon_c, True, "lexica/lexicon_noun_punct.tdl")
    print "printing adjective lexicon..."
    adjRowConverter.printAllAdjs(lexicon_c, "lexica/lexicon_adj.tdl")
    #adjRowConverter.printAllAdjs(lexicon_c, False, "lexica/lexicon_adj.tdl")
    #print "printing adjective lexicon with punctuation..."
    #adjRowConverter.printAllAdjs(lexicon_c, True, "lexica/lexicon_adj_punct.tdl")
    print "printing adverb lexicon..."
    advRowConverter.printAllAdvs(lexicon_c, "lexica/lexicon_adv.tdl")
    #advRowConverter.printAllAdvs(lexicon_c, False, "lexica/lexicon_adv.tdl")
    #print "printing adverb lexicon with punctuation..."
    #advRowConverter.printAllAdvs(lexicon_c, True, "lexica/lexicon_adv_punct.tdl")
    print "printing verb lexicon..."
    verbRowConverter.printAllVerbs(lexicon_c, "lexica/lexicon_verb.tdl")
    #verbRowConverter.printAllVerbs(lexicon_c, False, "lexica/lexicon_verb.tdl")
    #print "printing verb lexicon with punctuation..."
    #verbRowConverter.printAllVerbs(lexicon_c, True, "lexica/lexicon_verb_punct.tdl")

    print "printing noun types..."
    nounRowConverter.printTypes("lexica/noun_types.txt")

    print "printing verb types..."
    verbRowConverter.printTypes("lexica/verb_types.txt")
