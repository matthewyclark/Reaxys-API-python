#
#
from Reaxys_API import Reaxys_API
import random
from timeit import default_timer as timer

API_URL = 'https://www.reaxys.com/reaxys/api'
CALLER_ID = 'apitest_clark'


#
# get a set of molecules as SDF files based on a query
#
def test1():
    
    print("test1")
    start = timer()
    reaxys = Reaxys_API().connect(API_URL, CALLER_ID);
    query = "DAT.TNAME = 'GSK3'"
    reaxys.select("RX", "S", query)
    numResults = reaxys.resultsize
    batchSize = 1000 # optimal batch size
    maxMolecules = random.randrange(1, 5000)
    print("query %s - number of results %d" % (query, numResults))
    
    moleculeCounter = 0
    for first in range(1, min(maxMolecules, numResults), batchSize):  # int(ra.resultsize)):
    # the Reaxys arrays start at 1, so the last molecule is first+batch - 1
        last = min(first + batchSize - 1, maxMolecules)  # last molecule
 
        # retrieve molecule identification "IDE" and structure "YY" from the result set
        ide_yy_response = reaxys.retrieve(reaxys.resultname, ["IDE", "YY"], first, last)
        
        mol = reaxys.get_field_content(ide_yy_response, "YY.STR")
        xrn = reaxys.get_field_content(ide_yy_response, "IDE.XRN")
        bio = reaxys.get_field_content(ide_yy_response, "IDE.HASBIO")
        dataSize = len(mol)
        print("retrieving batch of %d molecules" % dataSize)
        for m in range(0, dataSize):
            sdf = mol[m] + "\n"
            sdf += "> <QUERY>\n" + query + "\n\n"
            sdf += "> <IDE.XRN>\n" + xrn[m] + "\n\n"
            sdf += "> <IDE.HASBIO>\n" + bio[m] + "\n\n"
            sdf += "$$$$\n"
            moleculeCounter += 1
    
    print('example \n' + sdf)
    assert moleculeCounter == maxMolecules
    print("** total %d molecules out of desired %d" % (moleculeCounter, maxMolecules))
    elapsed = timer() - start
    print ("batch size %i time %.2fs  %d molecules at %.2f molecules/second" % 
    (batchSize, elapsed, moleculeCounter, maxMolecules/elapsed))

    reaxys.disconnect()


test1();
