import json, os, sys

zipCode = json.loads(open('zipcode.json').read())

zipCodeDict = {}

for myZipInfo in zipCode:
    try:
        #zipCodeDict.update({'08820': {'City':'Edison','State':'NJ'}})
        zipCodeDict.update({myZipInfo['Zipcode'] : {'City':myZipInfo['City'], 'State':myZipInfo['State'], 'Lattitude':myZipInfo['Lat'], 'Longitude':myZipInfo['Long'], 'Xaxis':myZipInfo['Xaxis'],'Yaxis':myZipInfo['Yaxis'], 'Zaxis':myZipInfo['Zaxis'], 'EstimatedPopulation':myZipInfo['EstimatedPopulation'] , 'TotalWages':myZipInfo['TotalWages'], 'Notes':myZipInfo['Notes']}})
        #print(myZipInfo['Zipcode'])
    except:
        print(myZipInfo)

with open('zipcode_final.json', 'w') as f:
    ## need indent and each ket 
     json.dump(zipCodeDict, f, sort_keys = True, indent = 4, ensure_ascii = False)

