
from converter_row import *
import converter_noun_helpers as noun

class nounRowConverter(rowConverter):
    # TODO to fix error # 21, add a lexicalPointer field into the key of the allNouns dictionary.#LHS: this is done below, at addToDictionary, using
    # the new getLexicalPointer() method, which was added in converter_row.py.
    # TODO this will ensure that if two words are similar but have different pointers, they will not be merged.
    # TODO One problem with this is that words in the existing lexicon do not have lexical pointers associated with them,
    # TODO so it would be more difficult to filter out words from dinflections.csv that already exist in the existing lexicon.
    # TODO One work around for this would be to assign all preexisting words a default lexical pointer value, and if a new
    # TODO word matches all of the key besides the pointer value, update the pointer value in the existing word.

    #LHS: I did something similar below, in addToDictionary, where something will be added only if it's not already there, but I also added
    #that it won't be added if an entry that is almost identical (but with a lexical pointer of '-1') is already there. As pre-existing
    #lexical entries get a default lexical pointer of -1 (I added this to loadAllNouns()), this takes care of the redundant entries problem.

    # a dictionary of all nouns yet seen:
    # 	(stem, predicate, noun-type, definiteness)->
    # 		[(person, number, gender, possessor-person, possessor-number, possessor-gender)]
    # this is to ensure that words that are identical in everything except
    # gender or number are merged

    #LHS:
    # 	(stem, predicate, noun-type, definiteness, lexiconPointer)->
    # 		[(person, number, gender, possessor-person, possessor-number, possessor-gender)]
    
    allNouns = {}

##########################
# for printing out all the noun types
    allTypes = set()
    @staticmethod
    def printTypes(fileName):
        fout = open(fileName, 'w')

        for t in nounRowConverter.allTypes:
            fout.write(t)
            fout.write('\n')

        fout.close()
#############################		

    # load the allNouns dictionary given a set of tuples (stem, type, predicate)
    # the allNouns dictionary must be empty when this method is called
    @staticmethod
    def loadAllNouns(nounTuples):#LHS: CSVToTDLLexicalType calls this method;
        #LHS: nounTuples starts out as a list that contains a set of tuples (stem, type, predicate) of all the preexisting nouns
        assert len(nounRowConverter.allNouns) is 0

        for tup in nounTuples:
            nounType = tup[1]

            # default values for each noun
            definiteness = ""
            png = ""
            possPng = ""

            # special word
            if tup[0] == "special_word":
                #nounRowConverter.allNouns.update({(tup[0],tup[1], 0, 0):[0]})
                nounRowConverter.allNouns.update({(tup[0],tup[1], 0, 0, DEFAULT_LEXICAL_POINTER):[0]})#LHS: added default lexical pointer
                continue

            # proper noun
            if "-proper-noun-lex" in nounType:
                n_type = "proper"
                png = nounType.partition('-')[0]

            # possessive noun
            elif "poss-cmn-" in nounType:
                n_type = "poss-cmn"
                png = nounType.split('-')[2]
                possPng = nounType.split('-')[3]

            # pronoun
            elif "nom-pron-" in nounType:
                n_type = "nom-pron"
                png = nounType.split('-')[2]

            # common noun
            elif "-cmn-" in nounType:
                n_type = "cmn"
                definiteness = nounType.partition('-')[0] + '-'
                png = nounType.split('-')[2]

            # construct state noun
            elif "cs-" in nounType:
                n_type = "cs"
                png = nounType.split('-')[1]

            # special nouns have entire name saved in the definiteness field
            else:
                n_type = "special"
                definiteness = nounType

            person, number, gender = getPersonNumberGender(png)
            poss_person, poss_number, poss_gender = getPersonNumberGender(possPng)

            #nounRowConverter.allNouns.update({(tup[0],tup[2], n_type, definiteness): \
            #LHS: set a default lexical pointer for all nouns from the pre-existing lexicon
            nounRowConverter.allNouns.update({(tup[0],tup[2], n_type, definiteness, DEFAULT_LEXICAL_POINTER): \
                [(person, number, gender, poss_person, poss_number, poss_gender)]})

    # print all the nouns from the dictionary in tdl format
    # takes as input the list of names used so far, and whether to
    # print words with punctuation in them
    @staticmethod
    #def printAllNouns(lexicon, wantPunctuation, fileName):
    def printAllNouns(lexicon, fileName):#LHS: no need to check for punctuation here anymore 
        fout = open(fileName, 'w')

        for key, valueList in nounRowConverter.allNouns.iteritems():
            # if the word is a special case, just print it to the file
            if key[0] == "special_word":
                #if not wantPunctuation:#LHS: not needed anymore
                    #fout.write(key[1])
                    #fout.write('\n')
                fout.write(key[1])
                fout.write('\n')
                continue


            '''# if there is punctuation when we don't want it or vice-versa,
            # don't count it
            has_punct = containsPunct(key[0], key[1])
            if not wantPunctuation and has_punct or wantPunctuation and not has_punct:
                continue'''#LHS: no longer needed

            # merge each of the pngs to make them as general as possible
            valueList = mergePNGs(valueList)

            for value in valueList:
                fout.write(nounRowConverter.rowToTDL(key, value, lexicon))
                fout.write('\n')

        fout.close()

    # adds the row into the allNouns dictionary
    # this function does nothing if the row is irrelevant
    def addToDictionary(self):
        # skip rows that contain irrelevant nouns
        if self.irrelevant():
            return

        r = self.row  # for readability


    #LHS:
    # 	(stem, predicate, noun-type, definiteness, lexiconPointer)->
    # 		[(person, number, gender, possessor-person, possessor-number, possessor-gender)]
    
        # get all the information about the row
        (definiteness, nounType) = noun.definitenessNounType(int(r[pos_c]), \
                        r[suffixStatus_c], r[png_c], r[definiteness_c])
        #keyTuple = (self.getStem(), self.getPred(), nounType, definiteness)

        #LHS: get rid of illegal punctuation
        stem = self.getStem()
        pred = self.getPred()
        (stem, pred) = replacePunct(stem, pred)
        
        #LHS:
        keyTuple = (stem, pred, nounType, definiteness, self.getLexicalPointer())
        (person, number, gender) = noun.png(r[person_c], r[number_c], r[gender_c])
        (poss_person, poss_number, poss_gender) = noun.possessorPNG(r[png_c])
        pngData = (person, number, gender, poss_person, poss_number, poss_gender)

        # if there is nothing with this stem, pred and type seen yet,
        # insert it into the dictionary
        valueTuple = nounRowConverter.allNouns.get(keyTuple)
        
        preexistingKeyTuple = (stem, pred, nounType, definiteness, DEFAULT_LEXICAL_POINTER)##LHS - the key is unchanged, except the lexical pointer
        preexistingValueTuple = nounRowConverter.allNouns.get(preexistingKeyTuple)##LHS

        #LHS: if printing is needed for debugging: 
        #if preexistingValueTuple is not None:
        #    print(str(preexistingKeyTuple) + ' -> ' + str(preexistingValueTuple) )
   
        if valueTuple is None:
            if preexistingValueTuple is None:#LHS - added this-subcondition. We only want the entry to be added if it doesn't already appear,
                #including if there's a similar entry in the pre-existing lexicon
                nounRowConverter.allNouns.update({keyTuple: [pngData]})
        # otherwise keep track of all the png values associated with
        # this stem, pred and type
        elif pngData not in valueTuple:
                valueTuple.append(pngData)

    # returns true if the row is irrelevant
    def irrelevant(self):
        # skip all rows that are both proper nouns and definite
        if self.row[pos_c] == '10' and self.row[definiteness_c] in ['1','4','5']:
            return True

        # skip all pronouns that aren't interesting
        elif noun.irrelevantPronoun(self.row[transliteration_c], int(self.row[pos_c])):
            return True

        # the noun is relevant
        else:
            return False

    # returns the tdl formatted string given key and value tuples
    # in the allNouns dictionary
    @staticmethod
    def rowToTDL(key, value, lexicon):
        # proper nouns have a different type ordering, so check if the noun is
        # proper and return the propen noun ordering
        if key[2] == "proper": # proper noun
            tdlType = ''.join((value[0],value[1],value[2],'-',key[2], "-noun-lex"))

        elif key[2] == "special": # special case
            tdlType = key[3]

        else: # all other nouns
            tdlType = ''.join((
                key[3],
                key[2],'-',
                value[0],value[1],value[2]))

            # print the end of the tdl value depending on if there's a possessor
            if value[3] == '' and value[4] == '' and value[5] == '':
                tdlType += "-noun-lex"
            else:
                tdlType = ''.join ((tdlType,'-',
                    value[3],value[4],value[5],
                    "-noun-lex"))

        nounRowConverter.allTypes.add(tdlType)

        # return the tdl format
        return ''.join((addToLexicon(replaceSpaceWithUnderscore(key[0]), lexicon), " := ",
            tdlType, " &\n  [ STEM < \"",
            breakUpWordWithComma(key[0]),
            "\" >,\n   SYNSEM.LKEYS.KEYREL.PRED _",
            key[1],
            "_n_rel ].\n"))
