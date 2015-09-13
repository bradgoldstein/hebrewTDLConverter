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
    # TODO One problem with this is that words in the existing lexicon do not have lexical pointers associated with them,
    # TODO so it would be more difficult filter out words from dinflections.csv that already exist in the existing lexicon.
    # TODO One work around for this would be to assign all preexisting words a default lexical pointer value, and if a new
    # TODO word matches all of the key besides the pointer value, update the pointer value in the existing word.
    # a dictionary of all verbs yet seen:
    # (stem, pred, tense, control, subject_control)->
    # 	(person, number, gender, complements, [ppsorts])
    allVerbs = {}
    # a dictionary of all verbs yet seen:
    # (stem, pred, tense, control, subject_control)->
    #   {arguments->([realizations], [PPSORTS])} of those arguments
    verbsComplements = {}

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
            specialKey = (stem, tup[1], "special_word", '', '')

            # assume the word is not a control word
            control = False
            # assume the word is subject control
            subject_control = True
            # if there is a _c ending, the word is a control word
            if 'c' in title:
                control = True
                # if the word is object-control, mark is as so
                if "obj-cntrl" in tup[1]:
                    subject_control = False

            # if there is another ending, the word is special.
            # save the entire word in the pred field
            # and mark the tense as "special"
            elif 'r' in title or \
                 'v' in title or \
                 'sc' in title or \
                 'oc' in title or \
                 'pron' in title or \
                 'obj-cntrl' in wordType or \
                 'unacc_past' in wordType:
                addToLexicon(stem, lexicon)
                verbRowConverter.allVerbs.update({specialKey: [('', '', '')]})
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
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                continue

            pred = pred_check.group(1)

            # get the verbs tense
            tenseCheck = tense_re.search(wordType)
            # every word should have a tense
            assert tenseCheck
            tense = tenseCheck.group(1)
            # every word should have a valid tense
            assert tense in ["imperitive", "past", "present", "future", "infinitive"]

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
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                continue

            # if 'j' is in the complement, the word is special.
            # save the entire word in the pred field
            # and mark the tense as "special"
            if 'j' in complement:
                addToLexicon(stem, lexicon)
                verbRowConverter.allVerbs.update({specialKey: [('', '', '')]})
                verbRowConverter.verbsComplements.update({specialKey: ({})})
                continue

            # find all occurrences of ppsort values
            ppsorts_t = ppsort_re.findall(tup[1])
            ppsorts = list()
            for x in ppsorts_t:
                ppsorts.append(''.join((x[0], '-P ', x[1])))

            # (stem, pred, tense, control, subject_control)->
            # 	(person, number, gender,[complements], [ppsorts])
            keyTup = (stem, pred, tense, control, subject_control)

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

    # print all the nouns from the dictionary in tdl format
    # takes as input the list of names used so far, and whether to
    # print words with punctuation in them
    @staticmethod
    def printAllVerbs(lexicon, wantPunctuation, fileName):
        fout = open(fileName, 'w')

        for key, valueList in verbRowConverter.allVerbs.iteritems():
            # if the word is a special case, just print it to the file
            if key[2] == "special_word":
                if not wantPunctuation:
                    fout.write(key[1])
                    fout.write('\n')
                continue

            # if there is punctuation when we don't want it or vice-versa,
            # don't count it
            has_punct = containsPunct(key[0], key[1])
            if not wantPunctuation and has_punct or wantPunctuation and not has_punct:
                continue

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
            addToTypesPPSORTs(["m", "l", "al"],
                               "5-16-156_p_p",
                               ["5-P _m_p_rel", "6-P al-l-p"],
                               complements, typesPPSORTs)

            # Exception: verb can take both "l" and  "m"
            addToTypesPPSORTs(["l", "m"],
                              "5-16-156_p_p",
                              ["6-P _l_p_rel"],
                              complements, typesPPSORTs)

            # Exception: verb can take both "al" and "m"
            addToTypesPPSORTs(["al", "m"],
                              "5-16-156_p_p",
                              ["5-P _m_p_rel", "6-P _al_p_rel"],
                              complements, typesPPSORTs)

            # Exception: verb can take "at" and "l" (but not "m" or "l")
            addToTypesPPSORTs(["at", "l"],
                              "2-123_n_p", [],
                              complements, typesPPSORTs)

            # Exception: verb can take both "m" and  "ym" (but not "l" or "al")
            addToTypesPPSORTs(["m", "ym"],
                              "5_p",
                              ["5-P m-ym-p"],
                              complements, typesPPSORTs)

            addRemaining(complements, typesPPSORTs, none_complement)

        # store each of the possible types for the printTypes() method
        for t_ppsort in typesPPSORTs:
            verbRowConverter.allTypes.add(t_ppsort[0])

        keyTuple = (self.getStem(), self.getPred(), tense, control, subject_control)
        pngTuple = (p, n, g)

        # if there is nothing with this stem, pred and type seen yet,
        # insert it into the dictionary
        valueTuple = verbRowConverter.allVerbs.get(keyTuple)
        if valueTuple is None:
            verbRowConverter.allVerbs.update({keyTuple:[pngTuple]})

        # otherwise keep track of all the png values associated with key
        elif (person, number, gender) not in valueTuple:
            valueTuple.append(pngTuple)

        # keep track of the args and realizations separately for printing
        verbRowConverter.verbsComplements.update({keyTuple: (complements, typesPPSORTs)})

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

        # the noun is relevant
        else:
            return False

    # returns the tdl formatted string given key, value tuples and complement dictionary
    # in the allNouns dictionary
    @staticmethod
    def rowToTDL(key, png, complement, lexicon):

        # since there can be several tdl's from one row, return a list
        # of the tdl formats
        tdls = []

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

        # if there are no complements, all TDL values have been found.
        if len(complement[1]) is 0:
            return tdls

        type = complement[1][0][0]
        ppsorts = complement[1][0][1]

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
