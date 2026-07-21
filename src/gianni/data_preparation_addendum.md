## Un bug nascosto: le righe fittizie da cambio di bandiera olimpica

Il dataset comune descritto sopra unisce, per ogni riga *paese × edizione*, il medagliere con gli indicatori socio-economici del paese in quel periodo. Questa unione, fatta per nome paese su tutta la serie storica 1964–2020, si è rivelata corretta per la stragrande maggioranza delle nazioni — ma ha generato un problema sistematico per tutti i paesi che, nel tempo, hanno cambiato identità olimpica: si sono divisi, uniti, o hanno gareggiato sotto una sigla diversa dalla propria.

**Come si è scoperto il problema.** Durante un controllo dei duplicati sul dataset, sono emerse due righe per la stessa combinazione *codice NOC × anno* in corrispondenza di Russia 1992 e Russia 2020: una con gli indicatori socio-economici popolati e 0 medaglie, l'altra con gli indicatori nulli e le medaglie reali. La causa: nel 1992 la Russia gareggiò come parte della Squadra Unificata (EUN, le 12 ex repubbliche sovietiche), e nel 2020 come ROC (Russian Olympic Committee, per la squalifica della Russia dal doping di stato) — due sigle diverse dalla Federazione Russa vera e propria. Il merge per nome paese aveva agganciato gli indicatori economici alla "Russia" su tutta la serie storica, indipendentemente da quale identità olimpica fosse effettivamente in gara quell'anno, creando così una riga fittizia parallela a quella corretta.

**La correzione.** Il problema è stato risolto costruendo una mappatura esplicita tra codice NOC (usato dal CIO per identificare le delegazioni sportive) e codice ISO (usato dagli indicatori World Bank) — i due standard, nati per scopi diversi, non coincidono sempre per le stesse entità storiche.

**Un audit più esteso.** Verificando lo stesso meccanismo su tutte le nazioni storicamente divise, unite o nate nel periodo 1964–2020, lo stesso tipo di riga fittizia è emerso anche per:

- **Germania**: 6 righe fittizie (1968–1988, periodo della divisione tra Germania Ovest e Germania Est)
- **Cecoslovacchia → Cechia e Slovacchia**: 16 righe fittizie (1964–1992, prima che le due repubbliche esistessero come Comitati Olimpici indipendenti)
- **Jugoslavia → Bosnia-Erzegovina, Croazia, Macedonia del Nord, Montenegro, Slovenia, Serbia**: 46 righe fittizie (1964–1992)
- **Serbia e Montenegro → Serbia e Montenegro separate**: 6 righe fittizie (1996–2004)

In tutti questi casi il pattern era identico: una riga a zero medaglie, con indicatori economici popolati, per un'entità che in quell'anno non esisteva ancora come Comitato Olimpico indipendente — duplicata rispetto alla riga reale della federazione che allora esisteva davvero (URSS, Cecoslovacchia, Jugoslavia). In totale, oltre alle correzioni su Germania e Russia, sono state rimosse **68 righe fittizie aggiuntive**.

**Un problema diverso: codici incoerenti nel tempo.** Due nazioni — Trinidad and Tobago ed Egitto — non presentavano righe duplicate, ma un codice NOC che cambiava a metà della serie storica (per esempio Egitto: UAR fino al 1968, poi EGY dal 1972). Non essendoci sovrapposizione di anni non si trattava di un duplicato da rimuovere, ma di una serie storica "spezzata" in due tronconi con codici diversi — un problema comunque rilevante per le analisi che usano lo storico recente di un paese (come le feature di lag), risolto unificando i due codici in uno solo.

## Verifica finale

Dopo tutte le correzioni, il dataset è stato controllato sistematicamente per:

- **Nomi doppi sotto lo stesso codice NOC**: nessuno residuo
- **Righe fittizie a zero medaglie per le entità storiche corrette**: nessuna residua, per tutti i casi elencati sopra
- **Duplicati sulla coppia codice NOC + anno**: zero
- **Somma totale delle medaglie**: invariata rispetto alla versione precedente alla correzione — a conferma che nessuna medaglia reale è stata toccata, solo righe fittizie e codici incoerenti

Il dataset finale (`dataset_indicatori_definitivo_5.csv`) parte da 3.058 righe grezze e arriva a **2.619 osservazioni valide** dopo la pulizia dei valori mancanti (interpolazione limitata a 3 anni di gap + imputazione con mediana per nazione + eliminazione delle sole righe prive dei pilastri fondamentali PIL, popolazione e punteggio medaglie) — l'**85,7%** del dataset di partenza, una quota di conservazione più alta rispetto alle versioni precedenti, proprio perché la base di partenza era già più pulita.

**Nota per chi riusa questo dataset:** il lavoro di correzione è documentato passo per passo, con il codice e la verifica di ogni singola riga rimossa, nel notebook `per_dataset_new.ipynb`.
