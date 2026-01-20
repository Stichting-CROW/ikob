# D3: Van gewichten voor enkele vervoerswijzen naar gecombineerde gewichten

Symbolen:

_G_~ghbvm~ = gewicht van een verplaatsing van herkomst _h_ naar bestemming _b_ voor groep _g_ bij
vervoerswijze _v_ en motief _m_  
_GC_~ghbm~ = Gecombineerd gewicht over meerdere vervoerswijzen voor groep _g_ herkomst _h_ bestemming
_b_ en motief _m_

Voor de ene bestemming is de ene vervoerswijze het ‘best’ voor een andere bestemmingen een
andere.

Voor elke combinatie van vervoerswijzen (fiets-auto, elektrische fiets-auto, fiets-OV, elektrische fietsOV, auto-ov, fiets-auto-OV, elektrische fiets-auto-OV) geldt:

$$GC_{ghbm} = \max(v) G_{ghbvm}$$
Oftewel per herkomst-bestemmingscel neem je het maximumgewicht over de vervoerswijzen.
