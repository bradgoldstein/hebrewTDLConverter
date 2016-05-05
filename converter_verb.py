from converter_row import *
from converter_helpers import *
from converter_verb_helpers import *
from collections import defaultdict
from tdl_regexs import *
from CSV_helpers import openCSV
from utfToTransliteration import utf8ToTransliteration

class verbRowConverter(rowConverter):

    # TODO to fix error # 21, add a lexicalPointer field into the key of the allVerbs dictionary.
    # TODO this will ensure that if two words are similar but have different pointers, they will not be merged.

    #LHS: this is done below, at addToDictionary, using
    # the new getLexicalPointer() method, which was added in converter_row.py.
    
    # TODO One problem with this is that words in the existing lexicon do not have lexical pointers associated with them,
    # TODO so it would be more difficult filter out words from dinflections.csv that already exist in the existing lexicon.
    # TODO One work around for this would be to assign all preexisting words a default lexical pointer value, and if a new
    # TODO word matches all of the key besides the pointer value, update the pointer value in the existing word.
    # a dictionary of all verbs yet seen:
    # (stem, pred, tense, control, subject_control)->
    # 	(person, number, gender, complements, [ppsorts])

    #LHS:
    # (stem, pred, tense, control, subject_control, lexicalPointer)->
    # 	(person, number, gender, complements, [ppsorts])
    allVerbs = {}
    # a dictionary of all verbs yet seen:
    # (stem, pred, tense, control, subject_control)->
    #   {arguments->([realizations], [PPSORTS])} of those arguments
    verbsComplements = {}

    #LHS (fixing bug #24):
    # Special verbs, based on preexisting special verbs from our lexicon. This is a small group, so a copy of also saved
    # separately, so that they can be queried more quickly.
    # The structure is the same as for allVerbs, but as far as the key goes, the entire structure is under "pred", there is "special_word" for "tense",
    # and both controls have an empty string, while the lexical pointer is the default one.
    specialVerbs = {}

    # for printing out all the verb types
    allTypes = set()
    @staticmethod
    def printTypes(fileName):
        fout = open(fileName, 'w')

        for t in verbRowConverter.allTypes:
            fout.write('arg1'+t)
            fout.write('\n')

        fout.close()

    # load the allVerbs given a set of tuples (garbage, tdl-entry, predicate)
    # the allVerbs set must be empty when this method is called
    @staticmethod
    def loadAllVerbs(verbTuples, lexicon):
        assert len(verbRowConverter.allVerbs) is 0

        for tup in verbTuples:
            tdl = tup[1]

            tdl = tdl.split(' ')
            # tdl[0] = name
            # tdl[1] = :=
            # tdl[2] = type
            wordType = tdl[2]
            # tdl[3] = &

            # the tdl starts with title_c(?)
            title = tdl[0].strip()
            title = title.split('_')
            stem = title[0]

            # key for if the word is special
            #specialKey = (stem, tup[1], "special_word", '', '')
            specialKey = (stem, tup[1], "special_word", '', '', DEFAULT_LEXICAL_POINTER)#LHS - add the default lexical pointer

            # assume the word is not a control word
            control = False
            # assume the word is subject control
            subject_control = True
            # if there is a _c ending, the word is a control word
            # LHS: note that for object control words, the trailing c only appears if there is a non-control counterpart (therefore, most object control cases
            # are captured in the next elif, and not here
            if 'c' in title:
                control = True
                # if the word is object-control, mark is as so
                if "obj-cntrl" in tup[1]:
                    subject_control = False

            # if there is another ending, the word is special.
            # save the entire word in the pred field
            # and mark the tense as "special"
            #LHS: additional unaccusative types have been added to the input lexicon
            elif 'r' in title or \
                 'v' in title or \
                 'sc' in title or \
                 'oc' in title or \
                 'pron' in title or \
                 'obj-cntrl' in wordType or \
                 'unacc' in wordType:
                addToLexicon(stem, lexicon)
                verbRowConverter.allVerbs.update({specialKey: [('', '', '')]})
                verbRowConverter.specialVerbs.update({specialKey: [('', '', '')]})#LHS (bug #24)
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                
                continue

            # error checking that the stem we found matches the regex
            stemCheck = stem_re.search(tup[1])
            assert stemCheck
            assert stemCheck.group(1) == stem
            # get the png for HEAD.CNCRD if it has one
            # default values
            person, number, gender = '', '', ''
            pngCheck = png_re.search(tup[1])
            if pngCheck:
                person, number, gender = getPersonNumberGender(pngCheck.group(1))

            # get the word's predicate if it has one
            pred_check = verb_pred_re.search(tup[1])
            # if there is no predicate, the word is special.
            # save the entire word in the pred field
            # and mark the tense as "special"
            if not pred_check:
                addToLexicon(stem, lexicon)
                verbRowConverter.allVerbs.update({specialKey: [('', '', '')]})
                verbRowConverter.specialVerbs.update({specialKey: [('', '', '')]})#LHS (bug #24)
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                continue

            pred = pred_check.group(1)

            # get the verbs tense
            tenseCheck = tense_re.search(wordType)
            # every word should have a tense
            assert tenseCheck
            tense = tenseCheck.group(1)
            # every word should have a valid tense
            assert tense in ["imperative", "past", "present", "future", "infinitive"]

            basicCheck = basic_re.search(wordType)
            if basicCheck:
               complement =  '_' + basicCheck.group(1)

            else:
                # get the complement of the word
                complementCheck = complement_re.search(wordType)
                assert complementCheck
                complement = complementCheck.group(1)[1:]

            if control and subject_control and complement != '2_v':
                addToLexicon(stem + '_c', lexicon)
                verbRowConverter.allVerbs.update({specialKey: [('', '', '')]})
                verbRowConverter.specialVerbs.update({specialKey: [('', '', '')]})#LHS (bug #24)
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                continue

            # if 'j' is in the complement, the word is special.
            # save the entire word in the pred field
            # and mark the tense as "special"
            if 'j' in complement:
                addToLexicon(stem, lexicon)
                verbRowConverter.allVerbs.update({specialKey: [('', '', '')]})
                verbRowConverter.specialVerbs.update({specialKey: [('', '', '')]})#LHS (bug #24)
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                continue

            # find all occurrences of ppsort values
            ppsorts_t = ppsort_re.findall(tup[1])
            ppsorts = list()
            for x in ppsorts_t:
                ppsorts.append(''.join((x[0], '-P ', x[1])))

            # (stem, pred, tense, control, subject_control)->
            # 	(person, number, gender,[complements], [ppsorts])

            #LHS - add the lexical pointer field
            # (stem, pred, tense, control, subject_control, default_lexical_pointer)->
            # 	(person, number, gender,[complements], [ppsorts])            

            #keyTup = (stem, pred, tense, control, subject_control)

            keyTup = (stem, pred, tense, control, subject_control, DEFAULT_LEXICAL_POINTER)#LHS - see above

            verbRowConverter.allVerbs.update({keyTup: [(person, number, gender)]})
            verbRowConverter.verbsComplements.update({keyTup: ([], [(complement, ppsorts)])})

    # a dictionary of all the lexical pointers to complements
    # associated with that pointer in PMI_Dictionary.txt
    # pointer->[complement_LexiconItem]
    pmi = defaultdict(list)

    # load the pmi dictionary before adding words from dinflections.csv
    # so that the file does not need to be repeatedly queried
    @staticmethod
    def loadPMIDictionary():
        pmi_f = openCSV("lexica/PMI_Dictionary.txt", '\t')

        # skip the header row
        iterRows = iter(pmi_f)
        next(iterRows)

        # get all of the complements for each lexical pointer
        for row in iterRows:
            complement = row[7]
            if complement not in ["None", "clause", "inf"]:
                complement = utf8ToTransliteration(complement)

            verbRowConverter.pmi[int(row[1])].append(complement)

    # print all the verbs from the dictionary in tdl format
    # takes as input the list of names used so far, and whether to
    # print words with punctuation in them
    @staticmethod
    #def printAllVerbs(lexicon, wantPunctuation, fileName):
    def printAllVerbs(lexicon, fileName):#LHS: no need to check for punctuation here anymore (fixed bug #27)
        fout = open(fileName, 'w')

        for key, valueList in verbRowConverter.allVerbs.iteritems():
            # if the word is a special case, just print it to the file
            if key[2] == "special_word":
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

            # merge each of the png's to make them as general as possible
            valueList = mergePNG(valueList)

            # for each of the png's, print out the .tdl entry
            for value in valueList:
                png = value[0] + value[1] + value[2]
                for tdl in verbRowConverter.rowToTDL(
                    key, png, verbRowConverter.verbsComplements[key], lexicon):
                    fout.write(tdl)
                    fout.write('\n')

        fout.close()

    # adds the row into the allVerbs dictionary
    # this function does nothing if the row is irrelevant
    def addToDictionary(self):

        # skip rows that contain irrelevant verbs
        if self.irrelevant():
            return

        r = self.row  # for readability

        # only participles have a tense of '3'
        if r[tense_c] == '3':
            assert r[pos_c] == '13'

        # find the verb's tense
        tense = getTense(r[tense_c])

        # find the png of the verb
        p,n,g = '', '', ''

        if tense != "infinitive":
            (p, n, g) = png(r[person_c], r[number_c], r[gender_c], tense)

         # make a copy of the complements so that complements are not deleted from the pmi dictionary
        complements_ref = verbRowConverter.pmi[int(r[lexicalPointer_c])]
        complements = complements_ref[:]

        typesPPSORTs = [] # a list of (type and PPSORT)'s for a specific verb

        # Find if it is a control verb; assume not
        control, subject_control = False, True
        if "inf" in complements:
            control = True

        # If None is the only complement, the word is _basic
        if "None" in complements and len(complements) == 1:
            typesPPSORTs.append(("_basic", []))
        else:
            #LHS: fixing bug #29 - verbs that only have a subject control entry but should have an intransitive alternate, should get the alternate:
            if "None" in complements and "inf" in complements and len(complements) == 2:
                typesPPSORTs.append(("_basic", []))
            # remove "inf" from the complements
            try:
               complements.remove("inf")
            except ValueError:
                pass

            # remove "None" from the complements
            if "None" in complements:
                none_complement = True
                complements.remove("None")
            else:
                none_complement = False


            # TODO I believe that many of the errors come from storing the PPSORT/complement values incorrectly
            # TODO for example, errors # 7, 8, 9, 18, 19, 20 I believe come from this incorrect storing of values.

            # attempt to add each of the exceptions into the types/PPSORTs,
            # while removing those prepositions from the list of complements

            # Exception: verb can take "m", and "l", and "al"
            #LHS: fixing issue #22 (uncovered in issue #18) - if there's a none complement alternate, include it.
            if not none_complement:
                addToTypesPPSORTs(["m", "l", "al"],
                               "5-16-156_p_p",
                               ["5-P _m_p_rel", "6-P al-l-p"],
                               complements, typesPPSORTs)
            else:
                addToTypesPPSORTs(["m", "l", "al"],
                               "-15-16-156_p_p",
                               ["5-P _m_p_rel", "6-P al-l-p"],
                               complements, typesPPSORTs)

            # Exception: verb can take both "l" and  "m"

            #addToTypesPPSORTs(["l", "m"],
            #                  "5-16-156_p_p",
            #                  ["6-P _l_p_rel"],
            #                  complements, typesPPSORTs)

            #LHS: correction - added the PPSORT of DEP5 as well, which was missing (issue #18 and therefore also #15)
            #LHS: fixing issue #22 (uncovered in issue #18) - if there's a none complement alternate, include it.
            # Exception: verb can take both "m" and  "l" but not "al"
            if not none_complement:
                addToTypesPPSORTs(["m", "l"],
                              "5-16-156_p_p",
                              ["5-P _m_p_rel", "6-P _l_p_rel"],
                              complements, typesPPSORTs)
            else:
                addToTypesPPSORTs(["m", "l"],
                              "-15-16-156_p_p",
                              ["5-P _m_p_rel", "6-P _l_p_rel"],
                              complements, typesPPSORTs)                

            #LHS: fixing issue #22 (uncovered in issue #18) - if there's a none complement alternate, include it.
            # Exception: verb can take both "al" and "m"
            if not none_complement:
                addToTypesPPSORTs(["m", "al"],
                              "5-16-156_p_p",
                              ["5-P _m_p_rel", "6-P _al_p_rel"],
                              complements, typesPPSORTs)
            else:
                addToTypesPPSORTs(["m", "al"],
                              "-15-16-156_p_p",
                              ["5-P _m_p_rel", "6-P _al_p_rel"],
                              complements, typesPPSORTs)                

            # Exception: verb can take "at" and "l" (but not "m" or "l")
            #addToTypesPPSORTs(["at", "l"],
            #                  "2-123_n_p", [],
            #                  complements, typesPPSORTs)

            #LHS: correction - 13 is also a possible combination (issue #20 and therefore also #7)
            # Exception: verb can take "at" and "l" (but not "m")
            #LHS: fixing issue #22 (uncovered in issue #18) - if there's a none complement alternate, include it.
            if not none_complement:
                addToTypesPPSORTs(["at", "l"],
                              "2-13-123_n_p", [],
                              complements, typesPPSORTs)
            else:
                addToTypesPPSORTs(["at", "l"],
                              "-12-13-123_n_p", [],
                              complements, typesPPSORTs)                

            #LHS: added a case for when "m", "ym" and "at" are all possible (issue #8)
            #LHS: fixing issue #22 (uncovered in issue #18) - if there's a none complement alternate, include it.                
            # Exception: verb can take "at", and both "m" and "ym" (but not "l" or "al")
            if not none_complement:
                addToTypesPPSORTs(["at", "m", "ym"],
                              "2-15-125_n_p",
                              ["5-P m-ym-p"],
                              complements, typesPPSORTs)
            else:
                addToTypesPPSORTs(["at", "m", "ym"],
                              "-12-15-125_n_p",
                              ["5-P m-ym-p"],
                              complements, typesPPSORTs)
            #LHS: fixing issue #22 (uncovered in issue #18) - if there's a none complement alternate, include it.
            # Exception: verb can take both "m" and  "ym" (but not "l" or "al")
            if not none_complement:
                addToTypesPPSORTs(["m", "ym"],
                              "5_p",
                              ["5-P m-ym-p"],
                              complements, typesPPSORTs)
            else:
                addToTypesPPSORTs(["m", "ym"],
                              "-15_p",
                              ["5-P m-ym-p"],
                              complements, typesPPSORTs)
                
            addRemaining(complements, typesPPSORTs, none_complement)

            
            

        # store each of the possible types for the printTypes() method
        for t_ppsort in typesPPSORTs:
            verbRowConverter.allTypes.add(t_ppsort[0])

        #LHS:
        # (stem, pred, tense, control, subject_control)->
        # 	(person, number, gender, complements, [ppsorts])
        #keyTuple = (self.getStem(), self.getPred(), tense, control, subject_control)

        #LHS: get rid of illegal punctuation in pred or stem (bug #27)
        stem = self.getStem()
        pred = self.getPred()
        (stem, pred) = replacePunct(stem, pred)

        keyTuple = (stem, pred, tense, control, subject_control, self.getLexicalPointer())
        pngTuple = (p, n, g)

        # if there is nothing with this stem, pred and type seen yet,
        # insert it into the dictionary
        valueTuple = verbRowConverter.allVerbs.get(keyTuple)

        preexistingKeyTuple = (stem, pred, tense, control, subject_control, DEFAULT_LEXICAL_POINTER)##LHS - the key is unchanged, except the lexical pointer
        preexistingValueTuple = verbRowConverter.allVerbs.get(preexistingKeyTuple)##LHS

        ##LHS fixing bug #30:
        shouldHaveControlEntry = False
        if not control and subject_control:#i.e., the input entry doesn't have a control possibility
            alternateCntrlKeyTuple = (stem, pred, tense, True, subject_control, DEFAULT_LEXICAL_POINTER)#create an entry with a subject control possibility
        elif control and subject_control:#i.e., the input entry has a subject control possibility
            alternateCntrlKeyTuple = (stem, pred, tense, False, subject_control, DEFAULT_LEXICAL_POINTER)#create an entry without a control possibility
            if verbRowConverter.allVerbs.get(alternateCntrlKeyTuple):#If this is true, that means that the input entry has a subject control possibility, whereas
                #there's a pre-existing entry that is identical but DOESN'T have a subject control possibility.
                shouldHaveControlEntry = True #We mark this case

        alternateCntrlValuetuple = verbRowConverter.allVerbs.get(alternateCntrlKeyTuple)
        
        
        if valueTuple is None:
            if preexistingValueTuple is None: #LHS - added this-subcondition. We only want the entry to be added if it doesn't already appear,
                #including if there's a similar entry in the pre-existing lexicon
                if alternateCntrlValuetuple is None:#Bug #30
                    if self.noSpecialCounterpartExists(preexistingKeyTuple):#LHS: also make sure that there's no special word entry for this STRING&PRED combination
                        verbRowConverter.allVerbs.update({keyTuple:[pngTuple]})
                elif alternateCntrlValuetuple and shouldHaveControlEntry:#i.e., it's the specific case described above, so we want it to be included as well.
                    verbRowConverter.allVerbs.update({keyTuple:[pngTuple]})

        # otherwise keep track of all the png values associated with key
        elif (person, number, gender) not in valueTuple:
            valueTuple.append(pngTuple)

        # keep track of the args and realizations separately for printing
        if not shouldHaveControlEntry:#LHS for bug #30
            verbRowConverter.verbsComplements.update({keyTuple: (complements, typesPPSORTs)})
        else:
            verbRowConverter.verbsComplements.update({keyTuple: ([], [])})#because we only want the subject control entry in this case
            #(which is captured in the True, True part of the keyTuple); As the other entry/ies for this string already pre-exist.
            


    #LHS: makes sure that there is no pre-existing special word that has the same STEM and PRED values as this candidate entry; This requires going over all
    #forty something special verbs, because of the way they are stored (with their entire structure under PRED). Fixing bug #24.
    def noSpecialCounterpartExists(self, preexistingKeyTuple):
        specialVerbsKeys = verbRowConverter.specialVerbs.keys()
        preexistingStem = preexistingKeyTuple[0]
        preexistingPred = preexistingKeyTuple[1]
        preexistingTense = preexistingKeyTuple[2]
        for k in specialVerbsKeys:
            if k[0] == preexistingStem and k[1].startswith(preexistingPred) and k[2] == 'special_word' and k[3] == '' and k[4] == '' and k[5] == '-1' and preexistingTense in k[1]:
                return False
        return True  
        

    # returns true if the row is irrelevant
    def irrelevant(self):
        r = self.row  # for readability

        # ignore all verbs that have a png value other than '-'
        if r[png_c] != '-':
            return True

        # ignore any entries that have an undefined number
        elif r[number_c] == '-':
            # only if the tense is infinitive (5) and the word starts with "l",
            # create a lexical entry but don't map this to anything.
            # For all other cases, ignore these words altogether.
            if not (infinitive(r[tense_c]) and r[transliteration_c][0] == 'l'):
                return True

        # ignore any verbs without a specified tense
        elif r[tense_c] == '-':
            return True

        # if the tense is infinitive or breinfinitive and the word does not
        # begin with 'l', ignore it
        elif infinitive(r[tense_c]) and r[transliteration_c][0] != 'l':
            return True

        # if the verb has an undefined person,
        elif r[person_c] == '-':
            # only if the tense is infinitive (5) and the word starts with "l",
            # create a lexical entry but don't map this to anything.
            # For all other cases, ignore these words altogether.
            if not (infinitive(r[tense_c]) and r[transliteration_c][0] == 'l'):
                return True

        # ignore participles with definiteness 1 or 6
        elif r[pos_c] == '13' and r[definiteness_c] in ['1', '6']:
            return True

        # ignore entries whose SuffixStatus is 1
        elif r[suffixStatus_c] == '1':
            return True

        # the verb is relevant
        else:
            return False


    # returns the tdl formatted string given key, value tuples and complement dictionary
    # in the allVerbs dictionary
    @staticmethod
    def rowToTDL(key, png, complement, lexicon):
        # since there can be several tdl's from one row, return a list
        # of the tdl formats
        tdls = []

        comps_list = complement[1]

        # LHS: fixing bug #28 - actually, dealing with control verbs should be outside of the loop, because for verbs that only have a control entry (e.g. htqeh),
        # the loop isn't entered to at all (as they have an empty list as their complement), and for verbs that have an additional entry, this is only needed once anyway.

        # object control verbs
        if key[3] and not key[4]:
            type = complement[1][0][0]
            if png == '':
                png_text = ''
            else:
                png_text = "LOCAL.CAT.HEAD.CNCRD png-" + png + ",\n     "
            verb_name = addToLexicon(replaceSpaceWithUnderscore(key[0] + '_c'), lexicon)
            tdls.append(''.join((verb_name, " := arg1", type, "_obj-cntrl_", key[2], "_le &\n",
                                     "  [ STEM < \"", breakUpWordWithComma(key[0]),  "\" >,\n",
                                     "   SYNSEM [ ", png_text,
                                     "LKEYS.KEYREL.PRED _",key[1], "_v_rel ] ].\n")))
            return tdls

        # subject control verbs
        elif key[3]:
            verb_name = addToLexicon(replaceSpaceWithUnderscore(key[0] + '_c'), lexicon)
            if png == '':
                png_text, last_bracket = "   SYNSEM.", ""
            else:
                png_text, last_bracket = "   SYNSEM [ LOCAL.CAT [ HEAD.CNCRD png-" + png + " ],\n" + "    ", " ]"
            tdls.append(''.join((verb_name, " := arg12_v_subj-cntrl_", key[2],
                                     "_le &\n  [ STEM < \"",
                                    breakUpWordWithComma(key[0]),
                                     "\" >,\n", png_text, "LKEYS.KEYREL.PRED _", key[1], "_v_rel ]", last_bracket, ".\n")))

        # ensure that invalid types are not written for pre-existing verbs with subject control
        try:
            if key[3] and key[4] and complement[1][0][0] == '2_v':
                return tdls
        except:
            pass

        if len(complement[1]) is 0:
            return tdls
            
        #LHS: fixing bug #19 (enabling more than one lexical entry per verb)
        for c in comps_list:#LHS: loop through all possible entries (complement[1] actually stores possible entries)
 
            type = c[0]
            ppsorts = c[1]            

            # get the correct syntax if there are more than 1 PPSORT's
            if len(ppsorts) > 1:
                ppsorts_text = "SYNSEM.LOCAL.CAT.VAL.PPSORT [ "
                for i, ppsort in enumerate(ppsorts):
                    if i == 0:
                        ppsorts_text = ''.join((ppsorts_text, "DEP", ppsort, ",\n"))
                    elif i == (len(ppsorts) - 1):
                        ppsorts_text = ''.join((ppsorts_text, "                                 DEP", ppsort, " ],\n"))
                    else:
                        ppsorts_text = ''.join((ppsorts_text, "                                 DEP", ppsort, ",\n"))

            # get the correct syntax if there is exactly 1 PPSORT
            elif len(ppsorts) == 1:
                ppsorts_text = ''.join(("SYNSEM.LOCAL.CAT.VAL.PPSORT.DEP", ppsorts[0], ",\n"))

            # get the correct syntax if there are no PPSORT's
            else:
                ppsorts_text = ""

            # get the correct syntax for the png value
            if png == '':
                png_text = ""
            else:
                png_text = "   SYNSEM.LOCAL.CAT.HEAD.CNCRD png-" + png + ",\n"

            # append the entire .tdl syntax
            tdls.append(''.join((addToLexicon(replaceSpaceWithUnderscore(key[0]), lexicon), " := arg1", type, "_", key[2],
                                     "_le &\n  [ STEM < \"",
                                     breakUpWordWithComma(key[0]),
                                     "\" >,\n", png_text,
                                     "   ", ppsorts_text,
                                     "   SYNSEM.LKEYS.KEYREL.PRED _", key[1], "_v_rel ].\n")))

        return tdls
