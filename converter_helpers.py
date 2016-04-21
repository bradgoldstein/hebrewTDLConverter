# converter_helpers.py - helper functions for CSVToTDLLexicalType.py that
# are used across modules

from spreadsheetInfo import *

# add the name to the lexicon. If the name is already in the lexicon,
# return a '_x' at the end, and add another term into the lexicon
def addToLexicon(name, lexicon):
    # update the name in the lexicon with a value of 1
    lexicon[name] += 1

    # return the name alone if it is the only name of the kind in
    # the lexicon, otherwise return name_#ofTimesItAppears
    number = lexicon[name]
    if number is 1:
        return name
    else:
        return name + '_' + str(number)

# returns True if the stem or lemma contains (.), (') or (")
def containsPunct(stem, lemma):
    # if .' or " in the stem, return True
    if '\'' in stem or '\"' in stem or '.' in stem:
        return True

    # if .' or " in the lemma, return True
    if '\'' in lemma or '\"' in lemma or '.' in lemma:
        return True

    # no ' or " present
    else:
        return False

# LHS: replaces illegal punctuation in stem or pred (but not in the original data structure, just in the passed strings)
def replacePunct(stem, pred):
    if containsPunct(stem, pred):
        stem = stem.replace("'", '1')
        stem = stem.replace('"', '2')
        stem = stem.replace('.', '0')
        pred = pred.replace("'", '1')
        pred = pred.replace('"', '2')
        pred = pred.replace('.', '0')
    return (stem, pred)

# replaces all instances of ' ' in a string with '_'
def replaceSpaceWithUnderscore(word):
    return word.replace(' ', '_')

# replaces all instances of 'abc xyz' with 'abc", "xyz' 
def breakUpWordWithComma(word):
    return word.replace(' ', "\", \"")

# returns a tuple of (person, number, gender) while taking into account all
# combinations. For example 3m would map to (3, '', 'm') and return a blank
# number
def getPersonNumberGender(png):
    assert len(png) < 4

    # all traits (person, number and gender) are available
    if len(png) is 3:
        assert png[0] in ['1', '2', '3']
        assert png[1] in ['s', 'p']
        assert png[2] in ['m', 'f']
        return (png[0], png[1], png[2])

    # default values for each trait
    person = ''
    number = ''
    gender = ''

    # only two traits are available
    if len(png) is 2:

        # first place is person
        if png[0] in ['1', '2', '3']:
            person = png[0]

            # second place is either number of gender
            assert png[1] in ['s', 'p', 'm', 'f']
            if png[1] in ['s', 'p']: # second place is number
                number = png[1]
            else: # second place is gender
                gender = png[1]

        # first place is number and second place is gender
        else:
            assert png[0] in ['s', 'p']
            number = png[0]
            assert png[1] in ['m', 'f']
            gender = png[1]

    # only one trait is available
    elif len(png) is 1:
        assert png[0] in ['1', '2', '3', 's', 'p', 'm', 'f']

        # person is available
        if png[0] in ['1', '2', '3']:
            person = png[0]

        # number is available
        elif png[0] in ['s', 'p']:
            number = png[0]

        # gender is available
        else:
            number = png[0]

    # else size is 0, so return the defaults

    return (person, number, gender)

# returns True if the new tuple is more specific than an existing tuple
def moreSpecific(numNew, genNew, numOld, genOld):
    # return true if one of the components are more specific, while the other
    # is equivalent
    if numNew == numOld and genNew != '' and genOld == '':
        return True
    elif genNew == genOld and numNew != '' and numOld == '':
        return True
    # otherwise, the new tuple is not more specific
    else:
        return False

# returns True is the new tuple is more general than an existing tuple
def moreGeneralOrDifferent(numNew, genNew, numOld, genOld):
    # return true if one of the components are more general,
    if numNew == '' and numOld != '':
        return True
    elif genNew == '' and genOld != '':
        return True

    # return true if one of the components are different
    elif numNew != numOld:
        return True
    elif genNew != genOld:
        return True

    # otherwise, the new tuple is not more general or different
    else:
        return False

# returns a tuple of the most general combination of the numbers and genders
# eg. ('s','f') + ('p','f') = ('','f')
def mergeNumberGender(num1, gen1, num2, gen2):
    numReturn = ''
    genReturn = ''
    if num1 == num2:
        numReturn = num1
    if gen1 == gen2:
        genReturn = gen1
    return (numReturn, genReturn)

# does a proper "lexicographical" merge between existing terms in 
# the noun dictionary:
#	(1/s/f) + (1/s/m) = (1/s)
#	(2/p/f) + (2/s/f) = (2/f)
#	(1/s/m) + (1/p/m) + (1/s/f) = (1/m, 1/s)
#	etc...
# pngs is a list of tuples containing (person, number, gender, poss_person,
# poss_number, poss_gender)
def mergePNGs(pngs):
    assert len(pngs) > 0

    # if there is only 1 png, there is nothing to merge
    if len(pngs) is 1:
        return pngs

    newPNGs = []

    for png in pngs:
        # if this is the first one being looked at, there is nothing to merge
        if len(newPNGs) is 0:
            newPNGs.append(png)
            continue

        merged = False # if the png never gets merged, just add it to the list

        # for each of the already merged pngs,
        for index, mergedPNG in enumerate(newPNGs):

            # cannot merge entries with different people
            if png[0] != mergedPNG[0] or png[3] != mergedPNG[3]:
                continue

            # if the entry is a repeat, simply return the existing list
            if png[1] == mergedPNG[1] and png[2] == mergedPNG[2] and \
               png[4] == mergedPNG[4] and png[5] == mergedPNG[5]:
                merged = True
                break

            # if the entry is more specific in both possessor and png,
            # the new entry does not need to be merged, but still keep
            # searching just in case there is another png to merge it with
            if moreSpecific(png[1], png[2], mergedPNG[1], mergedPNG[2]) and \
               moreSpecific(png[4], png[5], mergedPNG[4], mergedPNG[5]):
                merged = True
                continue

            # if we get to this point, the new png is not the same, not more
            # specific and not a repeat. It must be more general and should be
            # merged with that entry
            assert moreGeneralOrDifferent(png[1], png[2], mergedPNG[1], mergedPNG[2]) or \
                   moreGeneralOrDifferent(png[4], png[5], mergedPNG[4], mergedPNG[5])

            mergedNum, mergedGen = \
                mergeNumberGender(png[1], png[2], mergedPNG[1], mergedPNG[2])
            mergedNum_poss, mergedGen_poss = \
                mergeNumberGender(png[4], png[5], mergedPNG[4], mergedPNG[5])
            newPNGs[index] = (png[0],mergedNum, mergedGen,
                          png[3], mergedNum_poss, mergedGen_poss)

            merged = True

        if not merged:
            newPNGs.append(png)

    return newPNGs

# does a proper "lexicographical" merge between existing terms in
# the noun dictionary:
#	(1/s/f) + (1/s/m) = (1/s)
#	(2/p/f) + (2/s/f) = (2/f)
#	(1/s/m) + (1/p/m) + (1/s/f) = (1/m, 1/s)
#	etc...
# pngs is a list of tuples containing (person, number, gender)
def mergePNG(pngs):
    assert len(pngs) > 0

    # if there is only 1 png, there is nothing to merge
    if len(pngs) is 1:
        return pngs

    newPNGs = []

    for png in pngs:
        # if this is the first one being looked at, there is nothing to merge
        if len(newPNGs) is 0:
            newPNGs.append(png)
            continue

        merged = False # if the png never gets merged, just add it to the list

        # for each of the already merged pngs,
        for index, mergedPNG in enumerate(newPNGs):
            # cannot merge entries with different people
            if png[0] != mergedPNG[0]:
                continue

            # if the entry is a repeat, simply return the existing list
            if png[1] == mergedPNG[1] and png[2] == mergedPNG[2]:
                merged = True
                break

            # if the entry is more specific in both possessor and png,
            # the new entry does not need to be merged, but still keep
            # searching just in case there is another png to merge it with
            if moreSpecific(png[1], png[2], mergedPNG[1], mergedPNG[2]):
                merged = True
                continue

            # if we get to this point, the new png is not the same, not more
            # specific and not a repeat. It must be more general and should be
            # merged with that entry
            assert moreGeneralOrDifferent(
                png[1], png[2], mergedPNG[1], mergedPNG[2])

            mergedNum, mergedGen = \
                mergeNumberGender(png[1], png[2], mergedPNG[1], mergedPNG[2])

            newPNGs[index] = (png[0],mergedNum, mergedGen)
            merged = True

        if not merged:
            newPNGs.append(png)

    return newPNGs
