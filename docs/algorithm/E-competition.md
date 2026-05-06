# E: Berekening van concurrentie

Het is het aandeel, dat je hebt vanuit een herkomstzone in de potentie van de bestemmingszone vermenigvuldigd met het aantal arbeidsplaatsen (of algemener ontplooiingsmogelijkheden) van dei bestemmingszone. Potentie is het aantal relevante inwoners, die die bestemmingszone kunnen bereiken, gewogen met de reistijdvervalscurve.

Het gewicht van een verplaatsing binnen een zone is 1.

- De potentie van Zone A is: $10*1 + 70 * 0,5 + 20 \* 0,5=55$
- De potentie van Zone B is: $70*1 + 20 * 0,5 + 10 \* 0,5 = 85$
- De potentie van Zone C is: $20*1 + 10 * 0,5 + 70 \* 0,5 = 60$

De concurrentiekracht van Zone A in het kunnen bereiken van arbeidsplaatsen is:

$$
\frac{10 * 1}{55} + \frac{70 * 0,5}{85} + \frac{20 * 0,5}{60} = 0,76
$$

De concurrentiekracht van Zone B in het kunnen bereiken van arbeidsplaatsen is:

$$
\frac{10 * 0,5}{55} + \frac{70 * 1}{85} + \frac{20 * 0,5}{60} = 1,08
$$

De concurrentiekracht van Zone C in het kunnen bereiken van arbeidsplaatsen is:

$$
\frac{10 * 0,5}{55} + \frac{70 * 0,5}{85} + \frac{20 * 1}{60} = 0,84
$$

Dit is ook wat je er intuïtief uit wilt hebben: Zone B heeft relatief veel arbeidsplaatsen binnen bereik en Zone A het minst. Vervolgens moet je nog wegen naar het inwoneraantal per zone om het gemiddelde over de totale bevolking op 1 te krijgen:

| Zone   | Concurrentie |
| ------ | ------------ |
| Zone A | 0,931373     |
| Zone B | 1,323529     |
| Zone C | 1,029412     |

$$
$$
