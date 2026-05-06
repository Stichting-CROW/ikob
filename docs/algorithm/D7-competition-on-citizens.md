# D7: Voor elke zone met arbeidsplaatsen wordt bepaald in welke mate deze zone in het voordeel is of in het nadeel ten opzichte van andere zones met arbeidsplaatsen in bereikbaarheid voor inwoners (per inkomensklasse)

In woorden de ‘concurrentiekracht qua bereikbaarheid van bedrijven en instellingen in een zone voor inwoners eromheen is voor een groep is:

$$
\frac{\text{Aantal inwoners in herkomstzone}}
{\text{Aantal bereikbare arbeidsplaatsen voor de herkomstzone}} \times \text{Reistijdgewicht}
$$

Gesommeerd over alle herkomstzones

Symbolen:

_C_~gbv~ = Concurrentiekracht voor groep _g_ in bestemmingszone _b_ voor vervoerswijze(combinatie) _v_  
_C_~ibv~ = Concurrentiekracht voor inkomensklasse _i_ in bestemmingszone _b_ voor vervoerswijze(combinatie) _v_  
_G_~ghbvm~ = Gewicht van de (combinatie) van vervoerswijzen _v_ voor groep _g_ met herkomst _h_ en bestemming _b_ voor motief _m_  
_V_~gh~ = Omvang groep _g_ in herkomstzone _h_  
_A_~ib~ = Aantal arbeidsplaatsen voor inkomensklasse _i_ in bestemmingszone _b_  
_B_~ibv~ = Bereik in aantal arbeidsplaatsen voor inkomensklasse _i_ in herkomstzone _b_ voor vervoerswijze(combinatie) _v_  
_I_~ih~ = Aantal inwoners in inkomensklasse _i_ in herkomstzone _h_

Voor elk van de groepen:

$$
C_{ibv}
=
\sum_{h} \frac{I_{ih}}{B_{ihv}} \times G_{ihbvm}
$$

En voor inkomensklasse _i_ geldt:

$$
C_{ibv}
=
\sum_{g\;in\;i} C_{gbv}
$$

En de totale concurrentiekracht voor een regio:

$$
C_{irv}
=
\frac{\sum_{b\;in\;r} C_{ibv} \times A_{ib}}
     {\sum_{b\;in\;r} A_{ib}}
$$
