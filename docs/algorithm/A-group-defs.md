---
icon: lucide/users
---

# A: Definitie van groepen

De groepen worden bepaald aan de hand van:

1. Autobezit en bezit rijbewijs
1. Bezit forfait of auto van de zaak (variabele kosten zijn dan nihil)
1. Inkomensniveau (hoog, middelhoog, middellaag, laag)
1. Voorkeur voor een bepaalde vervoerswijze (auto, fiets, OV of neutraal)

Elke groep heeft ook een voorkeursmodaliteit:

- Bij “gratis auto” is de voorkeur auto, behalve bij “gratis auto en gratis OV” waarbij de voorkeur neutraal is.
- Bij “gratis OV” is de voorkeur OV, behalve bij “gratis auto en gratis OV” waarbij de voorkeur neutraal is.
- Bij “geen auto” en “geen rijbewijs” is voorkeur auto niet mogelijk.

Dit leidt tot de volgende groepen:

| Groep                                 | Rijbewijs | Auto | Gratis <br>auto | Gratis<br> OV | Inkomen    | Voorkeur |
| ------------------------------------- | :-------: | :--: | --------------- | ------------- | ---------- | -------- |
| `GratisAuto_laag`                     |    ✔️     |  ✔️  | ✔️              |               | laag       | auto     |
| `GratisAuto_middellaag`               |    ✔️     |  ✔️  | ✔️              |               | middellaag | auto     |
| `GratisAuto_middelhoog`               |    ✔️     |  ✔️  | ✔️              |               | middelhoog | auto     |
| `GratisAuto_hoog`                     |    ✔️     |  ✔️  | ✔️              |               | hoog       | auto     |
| `GratisAuto_GratisOV_laag`            |    ✔️     |  ✔️  | ✔️              | ✔️            | laag       | neutraal |
| `GratisAuto_GratisOV_middellaag`      |    ✔️     |  ✔️  | ✔️              | ✔️            | middellaag | neutraal |
| `GratisAuto_GratisOV_middelhoog`      |    ✔️     |  ✔️  | ✔️              | ✔️            | middelhoog | neutraal |
| `GratisAuto_GratisOV_hoog`            |    ✔️     |  ✔️  | ✔️              | ✔️            | hoog       | neutraal |
| `WelAuto_GratisOV_laag`               |    ✔️     |  ✔️  |                 | ✔️            | laag       | OV       |
| `WelAuto_GratisOV_middellaag`         |    ✔️     |  ✔️  |                 | ✔️            | middellaag | OV       |
| `WelAuto_GratisOV_middelhoog`         |    ✔️     |  ✔️  |                 | ✔️            | middelhoog | OV       |
| `WelAuto_GratisOV_hoog`               |    ✔️     |  ✔️  |                 | ✔️            | hoog       | OV       |
| `WelAuto_vkAuto_laag`                 |    ✔️     |  ✔️  |                 |               | laag       | auto     |
| `WelAuto_vkAuto_middellaag`           |    ✔️     |  ✔️  |                 |               | middellaag | auto     |
| `WelAuto_vkAuto_middelhoog`           |    ✔️     |  ✔️  |                 |               | middelhoog | auto     |
| `WelAuto_vkAuto_hoog`                 |    ✔️     |  ✔️  |                 |               | hoog       | auto     |
| `WelAuto_vkNeutraal_laag`             |    ✔️     |  ✔️  |                 |               | laag       | neutraal |
| `WelAuto_vkNeutraal_middellaag`       |    ✔️     |  ✔️  |                 |               | middellaag | neutraal |
| `WelAuto_vkNeutraal_middelhoog`       |    ✔️     |  ✔️  |                 |               | middelhoog | neutraal |
| `WelAuto_vkNeutraal_hoog`             |    ✔️     |  ✔️  |                 |               | hoog       | neutraal |
| `WelAuto_vkFiets_laag`                |    ✔️     |  ✔️  |                 |               | laag       | fiets    |
| `WelAuto_vkFiets_middellaag`          |    ✔️     |  ✔️  |                 |               | middellaag | fiets    |
| `WelAuto_vkFiets_middelhoog`          |    ✔️     |  ✔️  |                 |               | middelhoog | fiets    |
| `WelAuto_vkFiets_hoog`                |    ✔️     |  ✔️  |                 |               | hoog       | fiets    |
| `WelAuto_vkOV_laag`                   |    ✔️     |  ✔️  |                 |               | laag       | OV       |
| `WelAuto_vkOV_middellaag`             |    ✔️     |  ✔️  |                 |               | middellaag | OV       |
| `WelAuto_vkOV_middelhoog`             |    ✔️     |  ✔️  |                 |               | middelhoog | OV       |
| `WelAuto_vkOV_hoog`                   |    ✔️     |  ✔️  |                 |               | hoog       | OV       |
| `GeenAuto_GratisOV_laag`              |    ✔️     |      |                 | ✔️            | laag       | OV       |
| `GeenAuto_GratisOV_middellaag`        |    ✔️     |      |                 | ✔️            | middellaag | OV       |
| `GeenAuto_GratisOV_middelhoog`        |    ✔️     |      |                 | ✔️            | middelhoog | OV       |
| `GeenAuto_GratisOV_hoog`              |    ✔️     |      |                 | ✔️            | hoog       | OV       |
| `GeenAuto_vkNeutraal_laag`            |    ✔️     |      |                 |               | laag       | neutraal |
| `GeenAuto_vkNeutraal_middellaag`      |    ✔️     |      |                 |               | middellaag | neutraal |
| `GeenAuto_vkNeutraal_middelhoog`      |    ✔️     |      |                 |               | middelhoog | neutraal |
| `GeenAuto_vkNeutraal_hoog`            |    ✔️     |      |                 |               | hoog       | neutraal |
| `GeenAuto_vkFiets_laag`               |    ✔️     |      |                 |               | laag       | fiets    |
| `GeenAuto_vkFiets_middellaag`         |    ✔️     |      |                 |               | middellaag | fiets    |
| `GeenAuto_vkFiets_middelhoog`         |    ✔️     |      |                 |               | middelhoog | fiets    |
| `GeenAuto_vkFiets_hoog`               |    ✔️     |      |                 |               | hoog       | fiets    |
| `GeenAuto_vkOV_laag`                  |    ✔️     |      |                 |               | laag       | OV       |
| `GeenAuto_vkOV_middellaag`            |    ✔️     |      |                 |               | middellaag | OV       |
| `GeenAuto_vkOV_middelhoog`            |    ✔️     |      |                 |               | middelhoog | OV       |
| `GeenAuto_vkOV_hoog`                  |    ✔️     |      |                 |               | hoog       | OV       |
| `GeenRijbewijs_GratisOV_laag`         |           |      |                 | ✔️            | laag       | OV       |
| `GeenRijbewijs_GratisOV_middellaag`   |           |      |                 | ✔️            | middellaag | OV       |
| `GeenRijbewijs_GratisOV_middelhoog`   |           |      |                 | ✔️            | middelhoog | OV       |
| `GeenRijbewijs_GratisOV_hoog`         |           |      |                 | ✔️            | hoog       | OV       |
| `GeenRijbewijs_vkNeutraal_laag`       |           |      |                 |               | laag       | neutraal |
| `GeenRijbewijs_vkNeutraal_middellaag` |           |      |                 |               | middellaag | neutraal |
| `GeenRijbewijs_vkNeutraal_middelhoog` |           |      |                 |               | middelhoog | neutraal |
| `GeenRijbewijs_vkNeutraal_hoog`       |           |      |                 |               | hoog       | neutraal |
| `GeenRijbewijs_vkFiets_laag`          |           |      |                 |               | laag       | fiets    |
| `GeenRijbewijs_vkFiets_middellaag`    |           |      |                 |               | middellaag | fiets    |
| `GeenRijbewijs_vkFiets_middelhoog`    |           |      |                 |               | middelhoog | fiets    |
| `GeenRijbewijs_vkFiets_hoog`          |           |      |                 |               | hoog       | fiets    |
| `GeenRijbewijs_vkOV_laag`             |           |      |                 |               | laag       | OV       |
| `GeenRijbewijs_vkOV_middellaag`       |           |      |                 |               | middellaag | OV       |
| `GeenRijbewijs_vkOV_middelhoog`       |           |      |                 |               | middelhoog | OV       |
| `GeenRijbewijs_vkOV_hoog`             |           |      |                 |               | hoog       | OV       |
