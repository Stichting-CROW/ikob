# D6: Voor elke buurt wordt bepaald in welke mate de buurt in het voordeel is of het nadeel ten opzichte van andere buurten in het bereiken van arbeidsplaatsen (per inkomensklasse)

In woorden de ‘concurrentiekracht qua bereikbaarheid van arbeidsplaatsen voor inwoners uit een zone' is:

$$
\frac{𝐴𝑎𝑛𝑡𝑎𝑙\;𝑎𝑟𝑏𝑒𝑖𝑑𝑠𝑝𝑙𝑎𝑎𝑡𝑠𝑒𝑛\;𝑖𝑛\;𝑏𝑒𝑠𝑡𝑒𝑚𝑚𝑖𝑛𝑔𝑠𝑧𝑜𝑛𝑒}
{𝑃𝑜𝑡𝑒𝑛𝑡𝑖𝑒\;𝑣𝑎𝑛\;𝑑𝑒\;𝑏𝑒𝑠𝑡𝑒𝑚𝑚𝑖𝑛𝑔𝑠𝑧𝑜𝑛𝑒} \times 𝑅𝑒𝑖𝑠𝑡𝑖𝑗𝑑𝑔𝑒𝑤𝑖𝑐ℎ𝑡
$$

Gesommeerd over alle bestemmingszones

Symbolen:

_C_~ghv~ = Concurrentiekracht voor groep _g_ in herkomstzone _h_ voor vervoerswijze(combinatie) _v_  
_C_~ihv~ = Concurrentiekracht voor inkomensklasse _i_ in herkomstzone _h_ voor vervoerswijze(combinatie) _v_  
_G_~ghbvm~ = Gewicht van de (combinatie) van vervoerswijzen _v_ voor groep _g_ met herkomst _h_ en bestemming _b_ voor motief _m_  
_A_~ib~ = Aantal arbeidsplaatsen voor inkomensklasse _i_ in bestemmingszone _b_  
_V_~gh~ = Omvang groep _g_ in herkomstzone _h_  
_B_~gbv~ = Bereik in aantal inwoners voor groep _g i_ in bestemmingszone _b_ voor vervoerswijze(combinatie) _v_  
_B_~ibv~ = Bereik in aantal inwoners voor inkomensklasse _i_ in bestemmingszone _b_ voor vervoerswijze(combinatie) _v_  
_I_~ih~ = Aantal inwoners in inkomensklasse _i_ in herkomstzone _h_

Voor elke groep geldt (_i_ is de inkomensklasse waar groep _g_ toe behoort):

$$
𝐶_{𝑔ℎ𝑣} = \sum_{b} \frac{𝐴_{𝑖𝑏}} {𝐵_{𝑔ℎ𝑣} } \times 𝐺_{𝑔ℎ𝑏𝑣𝑚}
$$

En voor inkomensklasse _i_ geldt:

$$
C_{ihv}
=
\frac{\sum_{g\;in\;i} C_{ghv} \times V_{gh}}
     {\sum_{g\;in\;i} V_{gh}}
$$

En de totale concurrentiekracht voor een regio:

$$
C_{irv}
=
\frac{\sum_{h\;in\;r} C_{ihv} \times I_{ih}}
     {\sum_{h\;in\;r} I_{ih}}
$$
