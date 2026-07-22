---
layout: default
title: "Più ricchi, più medaglie?"
subtitle: "PIL, popolazione e sviluppo umano: quali fattori spiegano il successo alle Olimpiadi estive?"
vega: true
scrollama: true
header_type: base
---

Esploriamo il dataset olimpico per capire se e quanto lo sviluppo economico di un paese spiega le medaglie vinte alle Olimpiadi estive. Le domande che guidano questa analisi sono tre:

1. Quali indicatori socioeconomici correlano di più con il successo olimpico?
2. La relazione tra ricchezza e medaglie è stabile nel tempo o cambia con gli eventi geopolitici?
3. Quali paesi emergono se guardiamo le medaglie in modo proporzionale alla popolazione?
{: .lead}

I dati provengono dal dataset **dataset_indicatori_definitivo.csv**, 3.368 osservazioni, una per ogni combinazione paese-edizione olimpica estiva dal 1964 al 2020, arricchite con 29 indicatori World Bank. Il dataset copre **218 paesi unici** in **15 edizioni olimpiche** e include solo le Olimpiadi estive. Prima di qualsiasi analisi, abbiamo risolto un bug strutturale nel dataset originale (226 righe con dati scissi) e verificato l'integrità di ogni osservazione.

---

{% include scrollytelling.html
 data_file="scrollama_nb1"
 chart_height="420px"
 desktop_chart_height="55vh"
 sticky_top="15vh"
 desktop_steps_padding_top="5vh"
 step_gap="95vh"
 last_step_gap="5vh"
 only_active_step_visible="false"
%}

---

## In sintesi

- Il **PIL totale** (non pro capite) è il predittore socioeconomico più forte delle medaglie olimpiche (r = 0.58): conta la massa di risorse del sistema-paese, non la ricchezza individuale.
- La **popolazione** emerge come secondo predittore significativo (r = 0.44): un grande bacino demografico offre più atleti da selezionare.
- La relazione PIL-medaglie è **stabile nel tempo**, con l'eccezione dei boicottaggi del 1980 e del 1984 che distorcono artificialmente il segnale.
- Normalizzando per la popolazione, emergono paesi **piccoli e specializzati**, Giamaica, Cuba, Ungheria, con un'efficienza olimpica molto superiore alle grandi potenze assolute.
- Il PIL spiega il 33% circa della varianza delle medaglie, una parte rilevante, ma lascia aperta la domanda più importante: **quanto contano gli investimenti diretti nello sport élite?**

### Nota metodologica

Le correlazioni sono calcolate sul sottoinsieme dei paesi vincitori (medaglie > 0) per evitare che la massa di zeri distorca i coefficienti di Pearson. Le variabili economiche sono in scala logaritmica per gestire la forte asimmetria delle distribuzioni (PIL e popolazione variano di ordini di grandezza tra i paesi del campione). I boicottaggi del 1980 e 1984 non sono stati esclusi dall'analisi ma sono evidenziati come anomalie geopolitiche.
