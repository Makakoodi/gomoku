# Määrittelydokumentti

## Ohjelmointikieli
- Toteutuskieli: Python
- Hallitut kielet vertaisarviointia varten: Python, Java, Javascript, vähän C
- opinto-ohjelmani on tietojenkäsittelytiede

## Mitä algoritmeja ja tietorakenteita
- Algoritmit:
  - Minimax + alpha–beta pruning
  - naapurustopohjainen rajaus
  - lupaavimmat siirrot ensin (heuristiikkaa)
  - Heuristinen arviointi eli eri kuvioiden arviointi
- Tietorakenteet:
  - Mahdolliset siirtohistorian tallennukset listarakenteella
  - 2d lauta

## Ongelma mikä ratkaistaan
- Gomoku peli missä on tarpeeksi tehokas minimaxi algoritmi, eli tutkitaan vain tiettyjä ruutuja.

## Aika- ja tilavaativuudet
- O(b^d) eli kasvaa exponentiaalisti mutta alpha beta pruningin takia b pitäisi pysyä pienenä

## Harjoitustyön ydin
Harjoitustyön ydin on Gomoku-pelin tehokas tekoäly. Painopiste on tekoälyn suunnittelussa.

## Testaus
- Yksikkötestit: kandidaattien ylläpito, naapurustot, arviot.
- Integraatio: minimax/alpha–beta, siirtojärjestys.
- Exe/protokolla: "test_exe.py" käynnistää binäärin ja tarkastaa IO:n.

## Lähteet
- Gomocup/Piskvork-dokumentaatio
- koko internetin tieto minimaxista ja alpha–betasta