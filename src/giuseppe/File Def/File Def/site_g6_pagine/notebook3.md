---
layout: default
title: "Chi salirà sul podio a Los Angeles?"
subtitle: "Machine Learning, causalità e previsioni per i Giochi Olimpici del 2028"
vega: true
scrollama: true
header_type: base
---

Le analisi precedenti hanno stabilito che PIL totale e spesa élite correlano con le medaglie olimpiche. Qui facciamo un passo più avanzato: costruiamo modelli predittivi, verifichiamo se il legame tra investimento e medaglie è causale, clusterizziamo i 218 paesi in profili olimpici e stimiamo il medagliere di Los Angeles 2028.
{: .lead}

Le domande che guidano questa analisi:

1. Quale algoritmo predice meglio le medaglie olimpiche, e di quanto batte un modello lineare semplice?
2. Il passato olimpico di un paese predice il futuro meglio dell'economia?
3. Investire nello sport **causa** più medaglie, o i paesi vincitori ricevono semplicemente più fondi?
4. Quali sono i quattro profili olimpici dei paesi del mondo, e dove si colloca l'Italia?
5. Quante medaglie vincerà ogni paese a Los Angeles 2028?

---

{% include scrollytelling.html
 data_file="scrollama_nb3"
 chart_height="460px"
 desktop_chart_height="60vh"
 sticky_top="10vh"
 desktop_steps_padding_top="5vh"
 step_gap="95vh"
 last_step_gap="5vh"
 only_active_step_visible="false"
%}

---

## Risposta alla Domanda di Ricerca

**Sì, gli investimenti in infrastrutture sportive producono medaglie olimpiche.** Le evidenze sono coerenti su più livelli di analisi, in più nazioni e in più periodi storici. Il meccanismo è documentato: investimento → strutture, tecnici e atleti → medaglie nel ciclo successivo, con un lag di 4-8 anni. Serve **continuità**: non basta un singolo ciclo di investimento, ma un programma pluriennale.

## In sintesi

- Il **Random Forest** è il modello più accurato: R² = 0.75 in cross-validation, R² = 0.86 su Tokyo 2020 (out-of-sample), MAE = 4.2 medaglie per paese, molto meglio della regressione lineare baseline (R² = 0.75).
- La variabile più predittiva non è il PIL ma le **medaglie del ciclo precedente** (46% della feature importance): i sistemi sportivi d'élite sono inerti, il passato olimpico predice il futuro meglio dell'economia.
- Il modello è più preciso per i grandi paesi (MAE ≈ 6 medaglie su 60-130) e meno per i piccoli con alta variabilità intrinseca.
- Il **Difference-in-Differences** supporta la causalità: chi aumenta i finanziamenti migliora sistematicamente i risultati rispetto a chi mantiene la spesa stabile.
- Quattro profili olimpici emergono, **Potenze assolute**, **Specializzati**, **Emergenti/Medi**, **Partecipanti**, con leve di successo radicalmente diverse.
- Per **Los Angeles 2028**: USA 100 medaglie (effetto host +15), Cina 91, Gran Bretagna 66, Francia 62, Italia 39.

### Nota metodologica

Le previsioni assumono trend economici stabili e nessun evento geopolitico straordinario. L'intervallo di confidenza 10-90% è derivato dalla dispersione delle previsioni dei 300 alberi del Random Forest, riflette l'incertezza del modello, non quella degli scenari futuri. Il modello non include la spesa élite come feature perché i dati SPLISS coprono troppo poche nazioni per essere usati nel training. L'endogeneità non è completamente risolta (servirebbe una variabile strumentale formale): il DiD riduce il problema senza eliminarlo.
