# encoding: UTF-8
import json 

'''
with open('data.json', 'w') as fp:
    fp.write(json.dumps(idict, sort_keys=True, indent=4))
'''

'''
"MHI-201705.HKFE"
sanity check for all the settings file 
'''

with open('ctaStrategy/CTA_setting.json') as fp:
    ctaset = json.load(fp)

print ctaset 

with open('dataRecorder/DR_setting.json') as fp:
    drset = json.load(fp)
print drset 


