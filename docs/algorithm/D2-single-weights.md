# D2: Van ervaren reistijd naar berekening van gewichten

Symbolen:

_ER_~ghbv~ = Ervaren reistijd voor groep _g_ tussen herkomst _h_ en bestemming _b_ met vervoerwijze _v_  
_RTV_~pvm~ = De reistijdvervalscurvefunctie bij voorkeur (preference) _p_ en vervoerswijze _v_ en motief _m_  
α,ω,w = constanten in de reistijdvervalscurve (afhankelijk van vervoerwijze, voorkeur en motief)  
_G_~ghbvm~= gewicht van een verplaatsing van herkomst _h_ naar bestemming _b_ voor groep _g_ bij
vervoerswijze _v_ en motief _m_  
De algemene formule is:  
$$𝐺_{𝑔ℎ𝑏𝑣𝑚} =𝑅𝑇𝑉_{𝑝𝑣𝑚} (𝐸𝑅_{𝑔ℎ𝑏𝑣})$$

Daarbij heeft de reistijdvervalscurve de volgende format:

$$
RTV_{pvm} = w \times \left(\frac{1}{1 + e^{\alpha \cdot (-\omega + t_{erv})}}\right)
$$

Met _ω_ = het omslagpunt (waar de verplaatsingen nog voor de helft meetellen)  
_α_= de steilte van de curve (tussen de 0,1 en 0,25 is realistisch)  
_w_= de weging van de waarde  
_𝑡_~𝑒𝑟𝑣~ = de ervaren reistijd

<figure markdown>
<figcaption>
Tabel 9 – Waarden van de constanten in de reistijdvervalscurve voor het motief woon-werk
</figcaption>

| Voorkeur | Vervoerwijze      | α     | ω   | W    |
| -------- | ----------------- | ----- | --- | ---- |
| Auto     | Auto              | 0.125 | 50  | 1    |
|          | OV                | 0.125 | 30  | 0.95 |
|          | Fiets             | 0.225 | 25  | 1    |
|          | Elektrische fiets | 0.175 | 35  | 1    |
| Neutraal | Auto              | 0.125 | 45  | 1    |
|          | OV                | 0.125 | 45  | 1    |
|          | Fiets             | 0.225 | 25  | 1    |
|          | Elektrische fiets | 0.175 | 35  | 1    |
| OV       | Auto              | 0.125 | 45  | 0.95 |
|          | OV                | 0.125 | 60  | 1    |
|          | Fiets             | 0.225 | 25  | 1    |
|          | Elektrische fiets | 0.175 | 35  | 1    |
| Fiets    | Auto              | 0.125 | 45  | 0.75 |
|          | OV                | 0.125 | 45  | 1    |
|          | Fiets             | 0.175 | 35  | 1    |
|          | Elektrische fiets | 0.125 | 50  | 1    |

</figure>

<figure markdown>
<figcaption>
Tabel 10 Waarden van de constanten in de reistijdvervalscurve voor het motief winkel dagelijks, zorg
</figcaption>

| Voorkeur | Vervoerwijze      | α     | ω   | W    |
| -------- | ----------------- | ----- | --- | ---- |
| Auto     | Auto              | 0.225 | 10  | 1    |
|          | OV                | 0.225 | 10  | 0.95 |
|          | Fiets             | 0.225 | 10  | 1    |
|          | Elektrische fiets | 0.225 | 12  | 1    |
| Neutraal | Auto              | 0.225 | 10  | 1    |
|          | OV                | 0.225 | 10  | 1    |
|          | Fiets             | 0.225 | 10  | 1    |
|          | Elektrische fiets | 0.225 | 12  | 1    |
| OV       | Auto              | 0.225 | 10  | 0.95 |
|          | OV                | 0.175 | 10  | 1    |
|          | Fiets             | 0.225 | 10  | 1    |
|          | Elektrische fiets | 0.225 | 12  | 1    |
| Fiets    | Auto              | 0.225 | 10  | 0.75 |
|          | OV                | 0.225 | 10  | 1    |
|          | Fiets             | 0.225 | 10  | 1    |
|          | Elektrische fiets | 0.225 | 15  | 1    |

</figure>

<figure markdown>
<figcaption>
Tabel 11 Waarden van de constanten in de reistijdvervalscurve voor het motief winkel niet-dagelijks, onderwijs
</figcaption>

| Voorkeur | Vervoerwijze      | α     | ω   | W    |
| -------- | ----------------- | ----- | --- | ---- |
| Auto     | Auto              | 0.225 | 20  | 1    |
|          | OV                | 0.225 | 20  | 0.95 |
|          | Fiets             | 0.225 | 15  | 1    |
|          | Elektrische fiets | 0.225 | 20  | 1    |
| Neutraal | Auto              | 0.225 | 20  | 1    |
|          | OV                | 0.225 | 20  | 1    |
|          | Fiets             | 0.225 | 15  | 1    |
|          | Elektrische fiets | 0.225 | 20  | 1    |
| OV       | Auto              | 0.225 | 20  | 0.95 |
|          | OV                | 0.175 | 20  | 1    |
|          | Fiets             | 0.225 | 15  | 1    |
|          | Elektrische fiets | 0.225 | 20  | 1    |
| Fiets    | Auto              | 0.225 | 20  | 0.75 |
|          | OV                | 0.225 | 20  | 1    |
|          | Fiets             | 0.225 | 20  | 1    |
|          | Elektrische fiets | 0.225 | 25  | 1    |

</figure>
