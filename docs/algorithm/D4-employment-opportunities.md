# D4: Van (gecombineerde) gewichten naar aantal bereikbare arbeidsplaatsen

Symbolen:

_G_~ghbvm~ = Gewicht van de (combinatie) van vervoerswijzen _v_ voor groep _g_ met herkomst _h_ en
bestemming _b_ voor motief _m_  
_A_~ib~ = Aantal arbeidsplaatsen voor inkomensklasse _i_ in bestemmingszone _z_  
_V_~gh~ = Omvang groep _g_ in herkomstzone _z_  
_I_~ih~ = Aantal inwoners in inkomensklasse _i_ in herkomstzone _h_  
_B_~ghv~ = Bereik in aantal arbeidsplaatsen voor groep _g_ in herkomstzone _h_ voor
vervoerswijze(combinatie) _v_  
_B_~ihv~ = Bereik in aantal arbeidsplaatsen voor inkomensklasse _i_ in herkomstzone _h_ voor
vervoerswijze(combinatie) _v_  
_B_~irv~ = Bereik in aantal arbeidsplaatsen voor inkomensklasse _i_ in regio _r_ voor vervoerswijze(combinatie)
_v_  
Voor elke groep, elke vervoerswijzecombinatie en elke herkomstzone geldt nu:

$$𝐵_{𝑔ℎ𝑣} = \sum_{b} 𝑉_{𝑔ℎ} \times 𝐺_{𝑔ℎ𝑏𝑣𝑚} \times 𝐴_{𝑖𝑏}$$

Waarbij _i_ de inkomensklasse is, waartoe groep _g_ behoort.  
Wanneer we het bereik van inkomensklassen willen bepalen, geldt:  
$$𝐵_{𝑖ℎ𝑣} = \sum_{g} 𝐵_{𝑔ℎ𝑣}$$

Wanneer de totale bereikbaarheid in een regio (gemeente, deelgemeente, provincie etc) _r_ moet
worden bepaald, geldt:

$$
B_{irv}
=
\frac{\sum_{h \;in\;r} B_{ihv} \times I_{ih}}
     {\sum_{h\;in\;r} I_{ih}}
$$

Ofwel het bereik van een regio wordt berekend door het bereik van alle zones in de regio op te
tellen, gewogen naar het aantal inwoners in die zones.
