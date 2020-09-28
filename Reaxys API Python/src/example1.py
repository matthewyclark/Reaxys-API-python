
from Reaxys_API import Reaxys_API
from timeit import default_timer as timer


API_URL = 'https://www.reaxys.com/reaxys/api'
CALLER_ID = 'apitest_clark'

ra = Reaxys_API().connect(API_URL, CALLER_ID);

batchSize = 1000 # maximum molecules per batch, 1000  is the optimal value
    
target_names = ["Histamine H1 receptor"]

def example_7a(ra):
    start = timer()
    with open('example7a_output.sdf', 'w') as sdfh:

    # value less than max for testing.
        maxMolecules = 7000 # maximum molecules, up to ra.resultsize
        counter = 0
        for target_nm in target_names:
            # this line queries the RX database for substances querying by target name.
            ra.select("RX", "S", "DAT.TNAME = '" + target_nm + "'", "")
            sdf = ''
            numResults = int(ra.resultsize)
      
            # index starts at 1, not 0
            for first in range(1, min(maxMolecules, numResults), batchSize):  # int(ra.resultsize)):
                # the Reaxys arrays start at 1, so the last molecule is first+batch - 1
                last = min(first + batchSize - 1, maxMolecules)  # last molecule
 
                # retrieve molecule indentification "IDE" and structure "YY" from the result set
                ide_yy_response = ra.retrieve(ra.resultname, ["IDE", "YY"], first, last)
        
                mol = ra.get_field_content(ide_yy_response, "YY.STR")
                xrn = ra.get_field_content(ide_yy_response, "IDE.XRN")
                bio = ra.get_field_content(ide_yy_response, "IDE.HASBIO")
                dataSize = len(mol)
        
                for m in range(0, dataSize):
                    sdf = mol[m] + "\n"
                    sdf += "> <target>\n" + target_nm + "\n\n"
                    sdf += "> <IDE.XRN>\n" + xrn[m] + "\n\n"
                    sdf += "> <IDE.HASBIO>\n" + bio[m] + "\n\n"
        
                    sdf += ">  <COPYRIGHT>\n"
                    sdf += "Copyright (C) 2017 Reed Elsevier Properties SA. All rights " + \
                    "reserved. Authorized use only. Reaxys (R) is a trademark " + \
                    "owned and protected by Reed Elsevier Properties SA and used under license.\n\n"
                    sdf += "$$$$\n"
                    counter += 1
                    sdfh.write(sdf)

    elapsed = timer() - start
    print ("batch size %i time %.2fs  %d molecules at %.2f molecules/second" % ( batchSize, elapsed, counter, maxMolecules/elapsed))

          
example_7a(ra)

