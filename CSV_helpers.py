
import csv

# returns the .csv file as a .csv reader class
def openCSV(filename, dlim):
	try:
	    fin = open(filename, 'r')
	except:
	    (type, detail) = sys.exc_info()[:2]
	    print "\n*** %s: %s: %s ***" % (filename, type, detail)
	    exit()
	
	return csv.reader(fin, delimiter = dlim)