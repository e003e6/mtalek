import csv
import time
import json
from lekerdezes import getinfo


# csv fájl beolvasása
urls = []
with open("mtalist.csv", newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        urls.append(row[0])

print(len(urls))

# lekérdezés függvény minden url-hez

mindenadat = []

for url in urls:
    print(url)
    info = getinfo('https://'+url)

    adatok = {}
    adatok['url'] = url
    
    if info:
        for i in info:
            cim = i[0]
            data = i[1:] if len(i) > 2 else i[1]
            adatok[cim] = data
        
    print(adatok, '\n')
    mindenadat.append(adatok)
    time.sleep(0.1)
    #break


print(len(mindenadat))


# exportálás json-ba
with open("nyersdata.json", "w", encoding="utf-8") as f:
    json.dump(mindenadat, f, ensure_ascii=False, indent=4)



