from bs4 import BeautifulSoup
import requests


def tag_formalo(tag) -> list: 
    return [tag.get_text(strip=True) for tag in tag.contents if tag.get_text(strip=True)]


def szovegkereso(tag) -> bool:
    szavak = ['phd', 'kandidátus']
    text = tag.get_text(strip=True).lower()
    return any(szo in text for szo in szavak)


def ppprint(adatok: list):
    for a in adatok:
        print(f'{a[0]}:')
        
        if len(a[1:]) == 1:
            print(a[1])
        else:
            for i in a[1:]:
                print(i)
        print()
        #print(f'{a[0]}: \n\t{a[1] if len(a[1:]) == 1 else a[1:]} \n')


def getinfo(url: str) -> list:
    html = requests.get(url)

    # lekérdezés ellenőrzése
    if html.status_code != 200:
        print('hibás lekérdezés!')
        return

    soup = BeautifulSoup(html.text, 'lxml')
    mbox = soup.find_all('div', class_='member_box') 

    # oldal struktúra ellenőrzése
    if len(mbox) == 1:
        mbox = mbox[0]
    elif len(mbox) == 0:
        print('Az oldal hibás!')
        return
    else: 
        print('Az oldalon több ember van!')
        return

    # adatok kiszedése

    # ellenőrzni kell, hogy még létezik e az ember az adatbázisban:
    if mbox.div.get_text(strip=True) == 'Nincs a keresési feltételeknek megfelelő személy.':
        print('nincsen ilyen személy')
        return 
    
    nev = mbox.div.h3.text
    kepurl = mbox.div.img.get('src')
    mtmturl = mbox.find('a').get('href') if mbox.find('a') else None

    adatok = [['nev', nev], ['kepurl', kepurl], ['mtmturl', mtmturl]]

    adatsorok = mbox.find('div', class_='lists').find_all(['p', 'ul'])

    for i, adat in enumerate(adatsorok):
        # három lehetőség van: 1. ez egy adatsor, 2. ez egy címor amit egy felsorolás követ, 3. ez egy felsorolás

        adatlista = tag_formalo(adat)
        
        # a phd cimkét külön kezeljük 
        # (a html-en mint címsor jelenkik meg pedig nem az)
        if adat.name == 'p' and adat.find("span") and len(adatlista)==1 and szovegkereso(adatsorok[i-1]):
            # p tag és azon belül span tag-ban van a szöveg, egy elemből áll és az előző elem tartalmazza a phd-szót
            
            phdcimke = adat.get_text(strip=True)
            adatok[-1].append(phdcimke)
            continue

        # ha ez egy adatsor (címsor és tartalom egy tag alatt)
        if adat.name == 'p' and len(adatlista) > 1:
            # adatsor ha több elemből áll (cím és tartalom)

            if adatlista[0] == 'Publikációk': # publikációk elem nem kell (már fent el lett mentve)
                continue
                
            adatok.append(adatlista)
            continue
    
        # ha ez egy felsorolás
        if adat.name == 'ul':
            
            # ellenőrzini kell hogy a felsorolás üres-e
            if adat.find("li") is None:
                continue

            cim = adatsorok[i-1].get_text(strip=True) # a cím ez előző p-tag
            adatlista.insert(0, cim)
            adatok.append(adatlista)

    return adatok



if __name__ == "__main__":

	# három teszt url
	urls = ['https://mta.hu/koztestuleti_tagok?PersonId=11887', 'https://mta.hu/koztestuleti_tagok?PersonId=21670', 'https://mta.hu/koztestuleti_tagok?PersonId=7609']

	# webscrape
	info = getinfo(urls[0]) # első url lekérdezése

	ppprint(info)

	"""
	output:

		nev:
		Bagdy György

		kepurl:
		https://aat.mta.hu/aat/FileData/Get/2900

		mtmturl:
		https://m2.mtmt.hu/gui2/?type=authors&mode=browse&sel=10001318

		Született:
		1955.07.31.

		MTA doktora:
		1999

		az orvostudomány kandidátusa:
		1992

		Szakterület:
		Neuropszichofarmakológia, gyógyszertan, idegtudomány, biológiai pszichiátria, neuroendokrinológia
		Orvosi Tudományok Osztálya

		Foglalkozás:
		igazgató, tanszékvezető egyetemi tanár

		Kutatási téma:
		A szerotonin és receptorainak funkciója és farmakológiája a központi idegrendszerben
		A szorongás és a depresszió genomikája és neurobiológiája
		Az alvás szabályozása és farmakológiája
		Az Ecstasy neuronkárosító hatása

		Szervezeti tagságok:
		Elméleti Orvostudományi Bizottság (szavazati jogú tag)
		Gyógyszerésztudományi Osztályközi Állandó Bizottság (szavazati jogú tag)
		III. sz. Doktori Bizottság (szavazati jogú tag)
		Magyar Élettani Társaság
		Magyar Felsőoktatási Akkreditációs Bizottság Orvos-, Gyógyszerész- és Egészségügyi Szakbizottság
		Magyar Gyógyszerésztudományi Társaság
		Magyar Kísérletes és Klinikai Farmakológiai Társaság (vezetőségi tag)
		Magyar Személyre Szabott Medicina Társaság
		OTKA Élettudományi Kollégium Klinikai Orvostudományi Zsűri
		Academia Europaea
		Collegium Internationale Neuropsychopharmacologicum
		European College of Neuropsychopharmacology
		European Neuropsychopharmacology (szerkesztőbizottsági tag)
		International Society of Psychoneuroendocrinology
		Serotonin Club
		The International Journal of Neuropsychopharmacology
		Neuropsychopharmacologia Hungarica (szerkesztőbizottsági tag)

		Szerkesztői tevékenységek:
		Neuropsychopharmacologia Hungarica, Szerkesztőbizottság
		International Journal of Neuropsychopharmacology, Szerkesztőbizottság
		European Journal of Neuropsychopharmacology, Szerkesztőbizottság

		Díjak:
		Széchenyi-díj:2022
		Issekutz Díj:2014
		Akadémiai Díj (Magyar Tudományos Akadémia Elnöksége):2012
		Huzella Tivadar-emlékérem és jutalomdíj:2010
		Kiváló PhD Oktató:2009
		Egészségügyi Miniszter Elismerő Oklevele (egészségügyi miniszter):1998

		Elérhetőségek:
		Semmelweis EgyetemGyógyszerésztudományi KarGyógyszerhatástani Intézet1089 Budapest, Nagyvárad tér 4.MagyarországTel.: +36 1 4591495Fax: +36 1 2104411Email:bag13638@iif.hu

	"""
