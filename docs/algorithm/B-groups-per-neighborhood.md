# B: Verdeling groepen over buurten

Gebruikte symbolen:

_s_ = Stedelijkheidsgraad  
_S_~z~ = Stedelijkheidsgraad van zone _z_  
_i_ = Inkomensklasse _i_  
_z_ = zone _z_  
_v_ = vervoerswijze  
_h_ = huishouden  
_AZ~si~_ = Autobezit naar stedelijkheidsgraad _s_ en inkomensklasse _i_  
_AZ~z~_ = Totaal Autobezit per zone _z_  
_AZ~iz~_ = Totaal Autobezit per zone _z_ per inkomensklasse _i_  
_GA~si~_ = Geen Autobezit, wel rijbewijs naar stedelijkheidsgraad _s_ en inkomensklasse _i_  
_GA~z~_ = Geen Autobezit, wel rijbewijs per zone _z_  
_GA~iz~_ = Geen Autobezit, wel rijbewijs per zone _z_ per inkomensklasse _i_  
_GR~si~_ = Geen rijbewijs naar stedelijkheidsgraad _s_ en inkomensklasse _i_  
_GR~z~_ = Geen rijbewijs per zone _z_  
_GR~iz~_ = Geen rijbewijs per zone _z_ per inkomensklasse _i_  
_GrA~i~_ = Gratis Autobezitpercentage per inkomensklasse _i_  
_GrA~iz~_ = Gratis Autobezit naar inkomensklasse _i_ in zone _z_  
_WA~iz~_ = Autobezit (niet-gratis) naar inkomensklasse _i_ in zone _z_  
_GrOV~si~_ = Gratis OV naar stedelijkheidsgraad _s_  
_GrOV~z~_ = Gratis OV per zone _z_  
_VK~vs~_ = Voorkeur voor vervoerswijze _v_ naar stedelijkheidsgraad _s_  
_VK~vz~_ = Voorkeur voor vervoerswijze _v_ per zone _z_  
_P~iz~_ = Percentage aandeel inkomensklasse _i_ per zone _z_  
_AA~hz~_ = Aantal auto’s per huishouden in zone _z_

## Stap 1: Bepaling autobezit

Allereerst wordt het auto- en rijbewijsbezit aan de hand van stedelijkheidsgraad en inkomensklasse
bepaald (bron: CBS):

<figure markdown>
<figcaption>
Tabel 1: Percentage autobezit naar stedelijkheidsgraad en inkomensklasse (bron: CBS)
</figcaption>

| Stedelijkheidsgraad | Laag | Middellaag | Middelhoog | Hoog |
| ------------------- | ---- | ---------- | ---------- | ---- |
| 1                   | 33   | 59         | 78         | 94   |
| 2                   | 49   | 74         | 91         | 97   |
| 3                   | 60   | 80         | 94         | 97   |
| 4                   | 66   | 84         | 95         | 98   |
| 5                   | 70   | 86         | 96         | 97   |

</figure>

<figure markdown>
<figcaption>Tabel 2: Percentage personen zonder auto met rijbewijs naar inkomensklasse en stedelijkheidsgraad (bron: CBS)</figcaption>

| Stedelijkheidsgraad | Laag | Middellaag | Middelhoog | Hoog |
| ------------------- | ---- | ---------- | ---------- | ---- |
| 1                   | 29   | 20         | 14         | 4    |
| 2                   | 21   | 12         | 5          | 2    |
| 3                   | 15   | 8          | 3          | 1    |
| 4                   | 12   | 6          | 2          | 0    |
| 5                   | 10   | 5          | 2          | 1    |

</figure>

<figure markdown>
<figcaption>Tabel 3: Percentage zonder rijbewijs naar stedelijkheidsgraad en inkomensklasse (bron: CBS)</figcaption>

| Stedelijkheidsgraad | Laag | Middellaag | Middelhoog | Hoog |
| ------------------- | ---- | ---------- | ---------- | ---- |
| 1                   | 38   | 21         | 9          | 2    |
| 2                   | 29   | 14         | 4          | 1    |
| 3                   | 25   | 12         | 3          | 2    |
| 4                   | 22   | 10         | 2          | 2    |
| 5                   | 20   | 9          | 2          | 2    |

</figure>

Alleerst worden de percentages van inkomensklassen P~iz~ en de Stedelijkheidsgraad S~z~ uit de CBS Wijk-
en Buurtgegevens afgeleid.

Aan de hand hiervan wordt het “theoretisch” autobezit berekend:

$$AZ_{z,theor} = \sum_{i} AZ_{st} P_{iz}$$

En net zo het theoretisch bezit met rijbewijs zonder auto:

$$GA_{z,theor} = \sum_{i} GA_{si} P_{iz}$$

En zonder Rijbewijs:

$$GR_{z,theor} = \sum_{i} GR_{si} P_{iz}$$

Nu is het voor veel zones zo, dat het aantal auto’s per huishouden volgens de CBS Wijk- en buurtgegevens groter is dan 1.
Maar er zijn ook zone’s waar het werkelijk aantal auto’s per huishouden kleiner is dan het theoretisch Autobezit.
Daar zullen huishoudens met 2 of meer auto’s vrijwel niet voorkomen. Dus als:

$$AA_{hz} < AZ_{z,theor}$$

Dan is:

$$AZ_{z} = AA_{hz}$$

In alle andere gevallen geldt:

$$AZ_{z} = AZ_{z,theor}$$

Het autobezit per zone per inkomensklasse is dan:

$$AZ_{iz} = \frac{AA_{hz}}{AZ_{z,theor}} \times AZ_{iz,theor}$$

Maar als het aantal huishoudens met een auto lager is dan je op grond van de algemene statistieken zou verwachten, betekent dat ook dat het aantal huishoudens zonder auto en/of rijbewijs hoger is.
Dit aantal wordt als volgt gecorrigeerd:

$$GA_{iz} = \frac{1 - AA_{hz}}{1 - AZ_{z,theor}} \times GA_{iz,theor}$$

en

$$GR_{iz} = \frac{1 - AA_{hz}}{1 - AZ_{z,theor}} \times GR_{iz,theor}$$

## Stap 2: Bepaling Gratis Auto en Gratis OV-bezit

In totaal zijn (bron Vereniging Zakelijke Rijders, VZR) 12% van de auto’s een auto van de zaak.
Per inkomensklasse is het percentage auto’s van de zaak:

<figure markdown>
<figcaption>
Tabel 4 Percentage auto's van de zaak per inkomensklasse (bron: VZR)
</figcaption>

| Inkomensklasse | Perc auto vd zaak |
| -------------- | ----------------- |
| Hoog           | 27.5%             |
| Middelhoog     | 17.5%             |
| Middellaag     | 2.0%              |
| Laag           | 0.0%              |

</figure>

Derhalve is dus
$$GrA_{iz} = GrA_i \times AZ_{iz}$$
En daarmee de “niet-gratis” auto’s:
$$WA_{iz} = AZ_{iz} - GrA_{iz}$$

Per stedelijkheidsgraad is het percentage mensen met gratis OV (schatting):

<figure markdown>
<figcaption>
Tabel 5 Percentage mensen met gratis OV naar stedelijkheidsgraad (schatting aan de hand van gegevens van NS)
</figcaption>

| Stedelijkheidsgraad | Perc gratis OV |
| ------------------- | -------------- |
| 1                   | 4.0%           |
| 2                   | 2.5%           |
| 3                   | 1.0%           |
| 4                   | 0%             |
| 5                   | 0%             |

</figure>

Voor alle groepen wordt dan het percentage van gratis OV toegewezen naar aanleiding van de
stedelijkheidsgraad en het resterende gedeelte verdeeld over de andere onderdelen.

## Stap 3: Bepaling voorkeuren

<figure markdown>
<figcaption>
Tabel 6 Voorkeuren vervoerswijzen per stedelijkheidsgraad (bron: OVIN en enquête gemeente Amsterdam),percentages
</figcaption>

| Stedelijkheidsgraad | Auto | Neutraal | Fiets | OV  |
| ------------------- | ---- | -------- | ----- | --- |
| 1                   | 25   | 25       | 30    | 20  |
| 2                   | 35   | 25       | 30    | 10  |
| 3                   | 50   | 20       | 25    | 5   |
| 4                   | 70   | 10       | 15    | 5   |
| 5                   | 85   | 5        | 10    | 0   |

</figure>

<figure markdown>
<figcaption>
Tabel 7 Voorkeuren vervoerswijze (percentage) voor hen die geen auto bezitten. Bron : OVIN en enquête gemeente Amsterdam
</figcaption>

| Stedelijkheidsgraad | Neutraal | Fiets | OV  |
| ------------------- | -------- | ----- | --- |
| 1                   | 33       | 40    | 27  |
| 2                   | 38       | 46    | 15  |
| 3                   | 40       | 50    | 10  |
| 4                   | 33       | 50    | 17  |
| 5                   | 33       | 67    | 0   |

</figure>

Voor een zone z met stedelijkheidsgraad s is dan voor vervoerswijze v:

$$VK_{vz} = VK_{vs}$$

## Variant: “Kunstmatig autobezit”

In bepaalde beleidsvarianten wil men bv door lagere parkeernormen het autobezit beperken. De
effectiviteit daarvan kan in beeld gebracht worden door een file “Kunstmatig autobezit” toe te
voegen, waarin voor de betreffende zones het beoogde autobezit wordt neergezet.

In dat geval wordt dus: $AA_z = KA_{hz}$, waarbij $KA_{hz}$ staat voor het Kunstmatig Autobezit per
huishouden.
