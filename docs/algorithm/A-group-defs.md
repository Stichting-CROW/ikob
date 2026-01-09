# Definitie van groepen

De groepen worden bepaald aan de hand van

1. Autobezit en bezit rijbewijs
1. Bezit forfait of auto van de zaak (variabele kosten zijn dan nihil)
1. Inkomensniveau (hoog, middelhoog, middellaag, laag)
1. Voorkeur voor een bepaalde vervoerswijze (auto, fiets, OV of neutraal)

Bij “gratis auto” is de voorkeur auto, behalve bij “gratis auto en gratis OV” waarbij de voorkeur
neutraal is.
Bij “gratis OV” is de voorkeur OV, behalve bij “gratis auto en gratis OV” waarbij de voorkeur neutraal
is.
Bij “geen auto” en “geen rijbewijs” is voorkeur auto niet mogelijk.
Dit leidt tot de volgende groepen:

1. `GratisAuto_laag`
1. `GratisAuto_middellaag`
1. `GratisAuto_middelhoog`
1. `GratisAuto_hoog`
1. `GratisAuto_GratisOV_laag`
1. `GratisAuto_GratisOV_middellaag`
1. `GratisAuto_GratisOV_middelhoog`
1. `GratisAuto_GratisOV_hoog`
1. `WelAuto_GratisOV_laag`
1. `WelAuto_GratisOV_middellaag`
1. `WelAuto_GratisOV_middelhoog`
1. `WelAuto_GratisOV_hoog`
1. `WelAuto_vkAuto_laag`
1. `WelAuto_vkAuto_middellaag`
1. `WelAuto_vkAuto_middelhoog`
1. `WelAuto_vkAuto_hoog`
1. `WelAuto_vkNeutraal_laag`
1. `WelAuto_vkNeutraal_middellaag`
1. `WelAuto_vkNeutraal_middelhoog`
1. `WelAuto_vkNeutraal_hoog`
1. `WelAuto_vkFiets_laag`
1. `WelAuto_vkFiets_middellaag`
1. `WelAuto_vkFiets_middelhoog`
1. `WelAuto_vkFiets_hoog`
1. `WelAuto_vkOV_laag`
1. `WelAuto_vkOV_middellaag`
1. `WelAuto_vkOV_middelhoog`
1. `WelAuto_vkOV_hoog`
1. `GeenAuto_GratisOV_laag`
1. `GeenAuto_GratisOV_middellaag`
1. `GeenAuto_GratisOV_middelhoog`
1. `GeenAuto_GratisOV_hoog`
1. `GeenAuto_vkNeutraal_laag`
1. `GeenAuto_vkNeutraal_middellaag`
1. `GeenAuto_vkNeutraal_middelhoog`
1. `GeenAuto_vkNeutraal_hoog`
1. `GeenAuto_vkFiets_laag`
1. `GeenAuto_vkFiets_middellaag`
1. `GeenAuto_vkFiets_middelhoog`
1. `GeenAuto_vkFiets_hoog`
1. `GeenAuto_vkOV_laag`
1. `GeenAuto_vkOV_middellaag`
1. `GeenAuto_vkOV_middelhoog`
1. `GeenAuto_vkOV_hoog`
1. `GeenRijbewijs_GratisOV_laag`
1. `GeenRijbewijs_GratisOV_middellaag`
1. `GeenRijbewijs_GratisOV_middelhoog`
1. `GeenRijbewijs_GratisOV_hoog`
1. `GeenRijbewijs_vkNeutraal_laag`
1. `GeenRijbewijs_vkNeutraal_middellaag`
1. `GeenRijbewijs_vkNeutraal_middelhoog`
1. `GeenRijbewijs_vkNeutraal_hoog`
1. `GeenRijbewijs_vkFiets_laag`
1. `GeenRijbewijs_vkFiets_middellaag`
1. `GeenRijbewijs_vkFiets_middelhoog`
1. `GeenRijbewijs_vkFiets_hoog`
1. `GeenRijbewijs_vkOV_laag`
1. `GeenRijbewijs_vkOV_middellaag`
1. `GeenRijbewijs_vkOV_middelhoog`
1. `GeenRijbewijs_vkOV_hoog`
