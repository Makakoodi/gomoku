# Viikkoraportti 3

## Mitä tein
- Testasin aluksi että botti toimii ja tekee jotain perusliikkeitä jonka jälkeen aloin implementoimaan minimax algoritmia.
- jouduin myös debuggaamaan LLM avulla miksi botti ei lähtenyt ollenkaan käyntiin ja syyksi selvisi että compilaus vaiheessa oli joku win32 import bugi(tjs??)


## Miten ohjelma on edistynyt(tai ei edistynyt)
- minimax algoritmi toimii järkevästi ja tekee hyviä liikkeitä. Tällä hetkellä alpha beta pruning on suunnitelmissa ja kokeilin jotain toteutusta asiasta mutta se rikkoo botin tällä hetkellä. Saan sen luultavasti ensi viikolle kuntoon.

## Mitä opin
- erittäin paljon minimaxin toiminnastatoteutuksesta ja alpha beta pruning esimerkeistä ja teoriasta.


## Seuraavat askeleet
1. tehostan algoritmin käyttämään alpha beta pruningia
2. evaluate funktiota voisi parantaa ettei se katsoisi vain pisintä linjaa
3. pitää tehdä testit
