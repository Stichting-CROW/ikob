# D5: Van (gecombineerde) gewichten naar aantal inwoners dat bedrijven en instellingen kan bereiken

Symbolen:

_G_~ghbvm~ = Gewicht van de (combinatie) van vervoerswijzen _v_ voor groep _g_ met herkomst _h_ en bestemming _b_ voor motief _m_  
_A_~ib~ = Aantal arbeidsplaatsen voor inkomensklasse _i_ in bestemmingszone  
_I_~gh~ =Aantal inwoners in groep _g_ in herkomstzone _h_  
_I_~ih~ = Aantal inwoners in inkomensklasse _i_ in herkomstzone _h_  
_B_~gbv~ = Bereik in aantal inwoners voor groep _g_ in bestemmingszone _b_ voor vervoerswijze(combinatie) _v_  
_B_~ibv~ = Bereik in aantal inwoners voor inkomensklasse _i_ in bestemmingszone _b_ voor
vervoerswijze(combinatie) _v_  
_B_~irv~ = Bereik in aantal inwoners voor inkomensklasse _i_ voor bedrijven in regio _r_ voor
vervoerswijze(combinatie) _v_

Voor elke groep, elke vervoerswijzecombinatie en elke bestemmingszone geldt nu:  
$$𝐵_{𝑔𝑏𝑣} = \sum_{h} 𝐼_{𝑔ℎ} \times 𝐺_{𝑔ℎ𝑏𝑣𝑚}$$

Waarbij _i_ de inkomensklasse is, waartoe groep _g_ behoort.  
Wanneer we het bereik van inkomensklassen willen bepalen, geldt:  
$$𝐵_{𝑖𝑏𝑣} = \sum_{g} 𝐵_{𝑔𝑏𝑣}$$  
Wanneer de totale bereikbaarheid in een regio (gemeente, deelgemeente, provincie etc) _r_ moet
worden bepaald, geldt:

$$
B_{irv}=
\frac{\sum_{b \;in\; r} B_{ibv} \times A_{ib}}
     {\sum_{b \;in\; r} A_{ib}}
$$

Ofwel het totale bereik van bedrijven een regio wordt berekend door het bereik van alle zones in de regio op te tellen, gewogen naar het aantal arbeidsplaatsen in die zones.
