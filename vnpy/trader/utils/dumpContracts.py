import shelve 
f = shelve.open("ContractData.vt")
if 'data' in f:
    d = f['data']
    for key, value in d.items():
        print key, value 
        print d[key].__dict__
        # contractDict[key] = value
f.close()
