
import string
from Reaxys_API import Reaxys_API

API_URL = 'https://www.reaxys.com/reaxys/api'

ra = Reaxys_API();
ra.connect(API_URL, '', '', '', 'apitest_clark');

target_names = ["Histamine H1 receptor"]

def example_7a(ra):
  with open('example7a_output.sdf', 'w') as sdfh:
    for target_nm in target_names:
      ra.select("RX", "S", "DAT.TNAME = '" + target_nm + "'", "", "WORKER,NO_CORESULT")
      sdf = ''
      batchSize = 5 # molecules per batch
      maxMolecules = 10
      
      for i in range(1, maxMolecules, batchSize):  # int(ra.resultsize)):
        print("range from " + str(1) + " to " + str(maxMolecules))
        # print(i)
        # retrieve fact availability (FA) information using option "hitonly"
        #fa_response = ra.retrieve(ra.resultname, ["FA"], i, i+batchSize, "", "", "", "HITONLY")
        #print(fa_response)
        # sdf = fa_response + "\n"
        # sdfh.write(sdf)
        last = min(i+batchSize-1, maxMolecules)
        ide_yy_response = ra.retrieve(ra.resultname, ["IDE", "YY"], i, min(i+batchSize-1, maxMolecules), "", "", "", "HITONLY,EXPORT=true")
        # print(ide_yy_response)
        
        dataSize = len(ra.get_field_content(ide_yy_response, "IDE.XRN"))
        mol = ra.get_field_content(ide_yy_response, "YY.STR")
        xrn = ra.get_field_content(ide_yy_response, "IDE.XRN")
        bio = ra.get_field_content(ide_yy_response, "IDE.HASBIO")
        # molecules are in SDfile v2000 followed by SDfile v3000, although one can request one or the other
        for m in range(0, dataSize):
          sdf = mol[m*2] + "\n"
          sdf += "> <target>\n" + target_nm + "\n\n"
          sdf += "> <IDE.XRN>\n" + xrn[m] + "\n\n"
          # sdf += "> <IDE.COSRC>\n" + src[0] + "\n\n"
          # sdf += "> <IDE.CN>\n" + nme[0] + "\n\n"
          sdf += "> <IDE.HASBIO>\n" + bio[m] + "\n\n"
        
          sdf += ">  <COPYRIGHT>\n"
          sdf += "Copyright (C) 2017 Reed Elsevier Properties SA. All rights " + \
                  "reserved. Authorized use only. Reaxys (R) is a trademark " + \
                 "owned and protected by Reed Elsevier Properties SA and used under license.\n\n"
          sdf += "$$$$\n"
          sdfh.write(sdf)


def example_7b(ra):
  with open('example7b_output.sdf', 'w') as sdfh:

    for target_nm in target_names:
      ra.select("RX", "S", "DAT.TNAME = '" + target_nm + "'", "", "WORKER,NO_CORESULT")
      sdf = ''
      
      for i in range(1, int(ra.resultsize), 20):
        # print(i)
        # retrieve fact availability (FA) information using option "hitonly"
        fa_response = ra.retrieve(ra.resultname, ["FA"], i, i+20, "", "", "", "HITONLY")
        print(fa_response)
        # sdf = fa_response + "\n"
        # sdfh.write(sdf)
        
        ide_yy_response = ra.retrieve(ra.resultname, ["IDE", "YY"], i, i, "", "", "", "HITONLY,EXPORT=true")
        # print(ide_yy_response)
        
        if int(ra.get_facts_availability(fa_response, "PED")) > 0:
          mol = ra.get_field_content(ide_yy_response, "YY.STR")
          xrn = ra.get_field_content(ide_yy_response, "IDE.XRN")
          # src = ra.get_field_content(ide_yy_response, "IDE.COSRC")
          # nme = ra.get_field_content(ide_yy_response, "IDE.CN")
          bio = ra.get_field_content(ide_yy_response, "IDE.HASBIO")
        
          sdf = mol[0] + "\n"
          sdf += "> <target>\n" + target_nm + "\n\n"
          sdf += "> <IDE.XRN>\n" + xrn[0] + "\n\n"
          # sdf += "> <IDE.COSRC>\n" + src[0] + "\n\n"
          # sdf += "> <IDE.CN>\n" + nme[0] + "\n\n"
          sdf += "> <IDE.HASBIO>\n" + bio[0] + "\n\n"
          
          # loop over all DAT data points
          for n in range(1, int(ra.get_facts_availability(fa_response, "DAT")) + 1):
            # retrieve DAT information using option "hitonly"
            response = ra.retrieve(ra.resultname, ["DAT(" + str(n) + "," + str(n) + ")"], i, i, "", "", "", "HITONLY")
            result = ra.get_field_content(response, "DAT")
            
            # get type, value,  effect and citation number from the DAT data point
            r = ''.join(filter(lambda x:x in string.printable, result[0]))
            vt = ra.get_field_content(r, "DAT.VTYPE")
            
            if len(vt) == 0: vt = ["n/a"]
            u = ra.get_field_content(r, "DAT.UNIT")
            
            if len(u) == 0: u = ["n/a"]
            v = ra.get_field_content(r, "DAT.VALUE")
            
            if len(v) == 0: v = ["n/a"]
            px = ra.get_field_content(r, "DAT.PAURES")
            
            if len(px) == 0: px = ["n/a"]
                        
            sdf += "> <DAT.VTYPE>\n" + vt[0] + "\n\n"
            sdf += "> <DAT.UNIT>\n" + u[0] + "\n\n"
            sdf += "> <DAT.VALUE>\n" + v[0] + "\n\n"
            sdf += "> <DAT.PAURES>\n" + px[0] + "\n\n"
			    
        # the copyright must always be included
        if int(ra.get_facts_availability(fa_response, "DAT")) > 0:
          sdf += ">  <COPYRIGHT>\n"
          sdf += "Copyright (C) 2017 Reed Elsevier Properties SA. All rights " + \
                  "reserved. Authorized use only. Reaxys (R) is a trademark " + \
                  "owned and protected by Reed Elsevier Properties SA and used under license.\n\n"
          sdf += "$$$$\n"
          wcount += 1
          print("write " + str(wcount))
          sdfh.write(sdf)

          
example_7a(ra)
#example_7b(ra)
print("done")
