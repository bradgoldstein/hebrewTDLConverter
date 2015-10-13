# converter_verb_helpers.py - helper functions for verbRowConverter
from sys import exit
from collections import defaultdict
from itertools import combinations

# returns True if the tense is infinitive; false otherwise
def infinitive(tense):
    if tense in ['5', '6']:
        return True
    return False

# returns the string of the verb's tense
def getTense(tense):
    if tense == '1':
        return "imperative"

    elif tense == '2':
        return "past"

    elif tense == '3':
        return "present"

    elif tense == '4':
        return "future"

    elif infinitive(tense):
        return "infinitive"

    # unknown tense, tenses of '-' should already have been weeded out
    print "\n*** unknown tense: %s ***" % (tense)
    exit()

# returns a tuple (person, number, gender)
def png(p, num, g, tense):
    return (person(p, tense), number(num), gender(g))

# determines the "person" of the verb (1,2,3)
def person(p, tense):
    # Map all beinoni entries to an unspecified person
    if tense == "present":
        return ""

    # person value of (3, 4) is third person
    if p in ['3', '4']:
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

# determines the "number" of the verb
def number(num):
    # number value of (-) should have been ignored
    assert num != '-'

    # number value of (1) is singular
    if num == '1':
        return "s"

    # number value of (3) is plural
    elif num == '3':
        return "p"

    #  error, unknown number
    print "\n*** unknown number: %s ***" % (num)
    exit()

# determines the "gender" of the verb - (m/f)
def gender(g):
    # gender value of (1) is masculine
    if g == '1':
        return "m"

    # gender value of (2) is feminine
    elif g == '2':
        return "f"

    # gender value of (3,-) is unspecified
    return ""

# appends the argType and ppsorts into allComplements if all of the
# prepositions are present in complements. Then removes each of the
# prepositions from complements
def addToTypesPPSORTs(prepositions, argType, ppsorts, complements, allComplements):
    if all(prep in complements for prep in prepositions):
        allComplements.append((argType, ppsorts))
        for prep in prepositions:
            complements.remove(prep)

# generates the part of a verb type after the "arg1" given a dictionary from
# numbers->[realizations]
def generateVerbType(num_realization, none_complement):
    verb_type = "" # start off with an empty argument type
    
    # generate each possible combination of the keys and append it to the argType
    keys = num_realization.keys()
    for i in range(len(keys)):
        for x in list(combinations(keys, i+1)):
            verb_type += "-1"
            for j in x:
               verb_type += str(j)
    # remove the first -1, because that is common to all types
    verb_type = verb_type[2:]

    # append groups of realizations for each number
    for key in keys:
        verb_type += "_"
        for realization in num_realization[key]:
            verb_type += realization

    if none_complement:
        verb_type = '-1' + verb_type

    return verb_type

# adds the remaining argType and ppsorts in the remaining complements
# into the allComplements list
def addRemaining(complements, allComplements, none_complement):
    # return the empty complements, all cases were already dealt with
    if not complements:
        return

    ppsorts = [] # all relevant ppsorts
    num_realization = defaultdict(list) # all complement numbers and their relevant realizations
    for comp in complements:
        # Semantic arg: 2; Syntactic realization: n
        if comp == "at":
            num_realization[2].append('n')

        # Semantic arg: 2; Syntactic realization: c
        elif comp == "clause":
            num_realization[2].append('c')

        # Semantic arg: 2; Syntactic realization: p
        # SYNSEM.LOCAL.CAT.VAL.PPSORT.DEP2-P _b_p_rel
        elif comp == "b":
            num_realization[2].append('p')
            ppsorts.append("2-P _b_p_rel")

        # Semantic arg: 3; Syntactic realization: p
        elif comp == "l":
            if 3 not in num_realization:
                num_realization[3].append('p')

        # Semantic arg: 3; Syntactic realization: p
        elif comp == "al":
            if 3 not in num_realization:
                num_realization[3].append('p')

        # Semantic arg: 5; Syntactic realization: p
        # SYNSEM.LOCAL.CAT.VAL.PPSORT.DEP5-P _ym_p_rel
        elif comp == "ym":
            num_realization[5].append('p')
            ppsorts.append("5-P _ym_p_rel")

        # Semantic arg: 5; Syntactic realization: p
        # SYNSEM.LOCAL.CAT.VAL.PPSORT.DEP5-P _m_p_rel
        elif comp == "m":
            num_realization[5].append('p')
            ppsorts.append("5-P _m_p_rel")

        # Semantic arg: 6; Syntactic realization: p
        # SYNSEM.LOCAL.CAT.VAL.PPSORT.DEP6-P _yl_p_rel
        elif comp == "yl":
            num_realization[6].append('p')
            ppsorts.append("6-P _yl_p_rel")

    allComplements.append((generateVerbType(num_realization, none_complement) , ppsorts))

