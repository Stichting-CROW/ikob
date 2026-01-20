# D1: Berekening ervaren reistijd

Symbolen:

_ER_~ghbv~ = Ervaren reistijd voor groep _g_ tussen herkomst _h_ en bestemming _b_ met vervoerwijze _v_  
_R_~hbv~ = “Pure” deur-tot-deur-reistijd tussen herkomst _h_ en bestemming _b_ met vervoerwijze _v_  
_PZA_~z~ = Parkeerzoektijd bij aankomst in zone _z_  
_PZV_~v~= Parkeerzoektijd bij vertrek uit zone z (in dit geval dus de tijd om de geparkeerde auto te zoeken en te bereiken)  
_VT_~ho~ = Voortransporttijd OV van herkomst _h_ naar opstaphalte _o_  
_NT_~ub~ = Natransporttijd OV van uitstapstation _u_ naar bestemming _b_  
_T_~o~ = Transfertijd op opstationstation _o_  
_T_~u~ = Transfertijd op uitstationstation _u_  
_W_ = Wachttijden vanwege overstappen  
_T_~hb,voertuig~ = Reistijd in het voertuig tussen herkomst _h_ en bestemming _b_  
_A_~hb,voertuig~ = Afstand in het voertuig tussen herkomst _h_ en bestemming _b_  
_Ktotaal_~ghbv~ = Totale kosten van herkomst _h_ naar bestemming _b_ voor groep _g_ met vervoerwijze _v_  
_Kvar_~gv~ = Variabele kosten per kilometer voor groep _g_ met vervoerwijze _v_  
_Kheffing_~gv~ = Heffing per km voor groep _g_ met vervoerwijze _v_  
_Kparkeer_~gv~ = Totale parkeerkosten per reis voor groep _g_ met vervoerwijze _v_  
_Kopstap_ = Opstaptarief (in het OV)  
_Kcordon_~gv~ = Cordonheffing voor groep _g_ met vervoerwijze _v_  
_TVOM_~i~ = Time Value of Money voor inkomensklasse _i_ (het aantal minuten extra ervaren reistijd per euro aan kosten)

De ervaren reistijd is:

$$𝐸𝑅_{𝑔ℎ𝑏𝑣} = R_{ℎ𝑏𝑣} + 𝑇𝑉𝑂𝑀_{𝑖} \times (𝐾𝑡𝑜𝑡𝑎𝑎𝑙_{𝑔ℎ𝑏𝑣})$$

Met voor de auto:

$$𝑅_{hb 𝑎𝑢𝑡𝑜} = 𝑃𝑍𝐴_{𝑧} + 𝑃𝑍𝑉_{𝑧} + 𝑇_{ℎ𝑏,𝑣𝑜𝑒𝑟𝑡𝑢𝑖𝑔}$$

$$𝐾𝑡𝑜𝑡𝑎𝑎𝑙_{𝑔ℎ𝑏𝑎𝑢𝑡𝑜} = (𝐾𝑣𝑎𝑟_{𝑔,𝑎𝑢𝑡𝑜} + 𝐾ℎ𝑒𝑓𝑓𝑖𝑛𝑔_{𝑔,𝑎𝑢𝑡𝑜}) ∗ 𝐴_{ℎ𝑏,𝑣𝑜𝑒𝑟𝑡𝑢𝑖𝑔} + 𝐾𝑝𝑎𝑟𝑘𝑒𝑒𝑟_{𝑔,𝑎𝑢𝑡𝑜} + 𝐾𝑐𝑜𝑟𝑑𝑜𝑛_{𝑔,𝑎𝑢𝑡𝑜}$$

Voor het gebruik van de auto wordt als variabele kosten €0,16/km gehanteerd. Voor deelauto’s
(groep GeenAuto) €0,30/km en €3 per uur (€0,05/minuut). Voor taxi’s (groep GeenRijbewijs)
€2,40/km en €0,40/minuut.

Voor groepen met “GratisAuto” zijn de variabele kosten nihil. De heffingen moeten wel worden
betaald.

Voor de parkeerzoektijden wordt de plaatselijke parkeerzoektijdentabel gahanteerd. Indien die er niet is, wordt deze tabel gehanteerd:

<figure markdown>
<figcaption>
Tabel 8 Parkeerzoektijden in minuten naar stedelijkheidsgraad
</figcaption>

| Stedelijkheidsgraad | Aankomstzoektijd | Vertrekzoektijd |
| ------------------- | ---------------- | --------------- |
| 1                   | 12.5             | 5               |
| 2                   | 7.5              | 2.5             |
| 3                   | 4                | 2               |
| 4                   | 0                | 0               |
| 5                   | 0                | 0               |

</figure>

Parkeerkosten zijn op dit moment alleen relevant voor de functie winkelen.

Voor het OV:

$$𝑅_{ℎ𝑏\;𝑜𝑣} = 𝑉𝑇_{ℎ𝑜} + 𝑇_{𝑜} + 𝑇_{𝑜𝑢,𝑣𝑜𝑒𝑟𝑡𝑢𝑖𝑔} + 𝑊 + 𝑁𝑇_{𝑢𝑏} + 𝑇_{𝑢}$$  
$$𝐾𝑡𝑜𝑡𝑎𝑎𝑙_{𝑔ℎ𝑏𝑜𝑣} = (𝐾𝑣𝑎𝑟_{𝑔,𝑜𝑣}) \times 𝐴_{𝑜𝑢,𝑣𝑜𝑒𝑟𝑡𝑢𝑖𝑔} + 𝐾𝑜𝑝𝑠𝑡𝑎𝑝 + 𝐾𝑝𝑎𝑟𝑘𝑒𝑒𝑟_{𝑔,𝑓𝑖𝑒𝑡𝑠}$$

Voor het OV gaat het alleen om echt pure reistijden. Dus geen penalties op wachttijden o.i.d. voor de transfertijd zijn de tijden uit de modellen gehanteerd. Als die er niet zijn, wordt 7,5 minuut transfertijd gehanteerd (tijd voor stallen fiets + speling om de trein te halen).
Voor de voertuigreistijd wordt de reistijd in het voertuig tussen opstaphalte _o_ en uitstaphalte _u_ genomen.

_Kvar_~,ov~ = €0,121

Kopstap = € 0,75

Voor groepen met “GratisOV” zijn zowel de variabele kosten als het opstaptarief nihil

Voor de (elektrische) fiets:

$$𝑅_{ℎ𝑏 𝑓𝑖𝑒𝑡𝑠} = 𝑇_{ℎ𝑏 𝑣𝑜𝑒𝑟𝑡𝑢𝑖𝑔}$$

De variabele kosten van de fiets zijn op nihil gesteld.
