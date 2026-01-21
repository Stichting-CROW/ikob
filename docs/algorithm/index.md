# About the IKOB algorithms

> Whilst we work on improving and generalizing IKOB, this documentation will be translated piece-by-piece into English.

De berekeningen van IKOB doorlopen de volgende stappen:

1. Vooraf vindt de definitie van de groepen plaats [(A)](./A-group-defs.md)

1. Als een apart algoritme wordt per buurt de verdeling van de bevolking over groepen gemaakt [(B)](./B-groups-per-neighborhood.md)

1. Ook wordt de verdeling van arbeidsplaatsen over de inkomensklassen bepaald [(C)](./C-workplaces-across-groups.md)

1. Berekening van de ervaren reistijd per groep vanuit de pure reistijd, de reisafstand en de (variabele) kosten per km; D1

1. Vanuit de ervaren reistijd berekening van de gewichten van bestemmingszones vanuitherkomstzones met behulp van reistijdvervalscurves – per groep; Het gewicht geeft aan in welke mate ontplooiingsmogelijkheden worden meegewogen vanuit een bestemmingszone; in eerste instantie per vervoerswijze (auto, OV met fiets als voor- en natransport, fiets, elektrische fiets) [(D2)](./D2-single-weights.md)

1. Per groep wordt voor elke combinatie van herkomsten de gewichten voor combinaties van vervoerswijzen bepaald [(D3)](./D3-combined-weights.md)

1. Voor elke buurt wordt het gewogen aantal bereikbare arbeidsplaatsen bepaald rekening houdend met de samenstelling van de bevolking en waar arbeidsplaatsen zijn voor welke inkomensgroep [(D4)](./D4-employment-opportunities.md)

1. Per gebied met arbeidsplaatsen wordt het gewogen aantal inwoners bepaald rekening houdend met de doelgroep van de arbeidsplaatsen qua inkomensklasse en de samenstelling van de buurten van herkomst [(D5)](./D5-potential-companies.md)

1. Voor elke buurt wordt bepaald in welke mate de buurt in het voordeel is of het nadeel ten opzichte van andere buurten in het bereiken van arbeidsplaatsen (per inkomensklasse) [(D6)](./D6-competition-on-jobs.md)

1. Voor elke zone met arbeidsplaatsen wordt bepaald in welke mate deze zone in het voordeel is of in het nadeel ten opzichte van andere zones met arbeidsplaatsen in bereikbaarheid voor inwoners (per inkomensklasse) [(D7)](./D7-competition-on-citizens.md)
