# encoding: UTF-8
import json 

onedict= {} 
onedict['state']= 'FLAT' 
onedict['orders']= ['LONG' , 'LADD1'] 
onedict['LONG']  = ['date1', 2008, 1] 
onedict['LADD1'] = ['date3', 2030, 1] 
onedict['stoploss'] = 2009
onedict['multiple'] = 10
onedict['atr'] = 20 

idict = {} 
idict['rb1710'] = onedict 
idict['ru1709'] = onedict 

with open('data.json', 'w') as fp:
    fp.write(json.dumps(idict, sort_keys=True, indent=4))


with open('data.json') as fp:
    pos = json.load(fp)


print pos['rb1710'] 

