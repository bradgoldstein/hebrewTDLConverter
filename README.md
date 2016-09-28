
CSVToTDLLexicalType.py - this is the main file for converting from the .csv to .tdl types.
	Run it and comment out the relevant lines from 24-32 and 53-68, depending on what part of speech you wish
	to convert.

converter_factory.py - a factory function for converting specific parts of speech depending on the part of speech
    value in dinflections.csv.

converter_row.py - implements a base class, rowConverter, that defines the methods necessary for converting each
    of the parts of speech.

converter_*pos*.py - inherits from rowConverter and implements the methods necessary for converting that specific
    part of speech using the helper methods defined in converter_*pos*_helpers.py.

converter_helpers.py - general helper methods for converting parts of speech.

CSV_helpers.py - helper methods for manipulating, reading and writing to CSV files.

getExistantEntries.py - for converting the lexicon.tdl into python for checking if entries already exist, etc.

speadsheetInfo.py - contains some data about the spreadsheet that modules can import from
	to make accessing dinflections.csv easier and more readable

tdl_regexs.py - contains regular expressions for identifying parts of entries in lexicon.tdl.

utfToTransliteration.py - contains a function for converting between the .csv file's hebrew
	formatting to the transliteration

/lexica/lexicon.tdl - the existing .tdl entries.

/lexica/lexicon_*pos*.tdl - the generated .tdl entries for the specified part of speech. 

/lexica/lexicon_*pos*.tdl - the generated .tdl entries for the specified part of speech. 

/lexica/*pos*_types.tdl - all of the types generated for the specified part of speech.

/lexica/new_dinflections.csv - the new_dinflections.xlsx saved as a .csv file. (Note: this is not uploaded to Github
    due to its size. Add it to the /lexica folder manually.)

/lexica/PMI_Dictionary.txt - the PMI_Dictionary.csv saved as a .txt file. (Note: this is not uploaded to Github
    due to its size. Add it to the /lexica folder manually.)