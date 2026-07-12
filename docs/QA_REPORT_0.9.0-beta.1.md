# Rapporto di qualità — 0.9.0-beta.1

Prodotto: **Mythic Rings — Prima Edizione**  
Autore: **Riccardo Scaringi**  
Ramo: **develop/1.0**  
Stato: **beta editoriale per blind playtest**

## Scopo

Questo rapporto documenta i controlli interni applicati ai sorgenti e agli artefatti della versione 0.9.0-beta.1. Certifica la coerenza tecnica ed editoriale interna raggiunta dalla build; non sostituisce blind playtest umano, editing indipendente, consulenza culturale, verifica legale e validazione commerciale.

## Perimetro verificato

- 33 capitoli del manuale principale;
- specifica canonica delle regole;
- 61 poteri delle quattro Casate;
- 31 avversari generati da dati strutturati;
- campagna in otto sessioni *Il Crepuscolo del Velo*;
- tre one-shot nel manuale;
- quickstart autonomo;
- Kit del Giocatore;
- avventura autonoma *Notte al Monumentale*;
- pipeline DOCX, HTML e PDF;
- metadati, segnalibri, indice, colophon e crediti.

## Risultati della validazione editoriale

La validazione automatica non rileva errori bloccanti. Rimane un solo avviso informativo: il capitolo 12, dedicato ai dodici quartieri, supera la soglia di lunghezza prevista dal linter. L'avviso non indica contenuto mancante o malformato e non impedisce la pubblicazione della beta; segnala soltanto un possibile intervento futuro di alleggerimento o suddivisione.

Sono stati verificati e rimossi:

- placeholder dell'autore e dei playtester;
- ISBN fittizi;
- marcatori TODO/TBD;
- riferimenti esposti alle revisioni 3.x;
- definizioni concorrenti delle regole centrali;
- stat block con colonne slittate o campi mancanti;
- riferimenti rapidi e FAQ non allineati alla specifica canonica.

## Controllo visivo

Tutte le pagine dei quattro PDF sono state ispezionate mediante renderizzazione e tavole di contatto.

| Artefatto | Pagine | Esito |
|---|---:|---|
| Manuale principale | 387 | Superato |
| Quickstart | 22 | Superato |
| Kit del Giocatore | 10 | Superato |
| *Notte al Monumentale* | 11 | Superato |

Non sono stati rilevati:

- testi o box oltre i margini;
- sovrapposizioni;
- tabelle troncate;
- pagine involontariamente vuote;
- stat block spezzati in modo illeggibile;
- elementi mancanti nelle sezioni normative;
- errori di navigazione evidenti.

Sono presenti alcuni spazi bianchi dovuti a chiusure di capitolo e box mantenuti indivisibili. Sono difetti di rifinitura grafica, non problemi editoriali o funzionali, e restano fuori dal perimetro della presente revisione.

## Preflight PDF

Tutti i PDF:

- si aprono correttamente;
- non sono cifrati;
- contengono testo selezionabile;
- non risultano scansioni;
- non contengono moduli XFA;
- non generano avvisi nel preflight tecnico;
- riportano titolo e autore corretti;
- possiedono segnalibri editoriali.

Segnalibri verificati:

| Artefatto | Segnalibri |
|---|---:|
| Manuale principale | 36 |
| Quickstart | 14 |
| Kit del Giocatore | 9 |
| *Notte al Monumentale* | 8 |

## Audit DOCX e accessibilità

I DOCX di quickstart, kit e avventura non generano anomalie nell'audit automatico.

Il manuale principale genera 298 avvisi medi `table_no_header_row`. L'ispezione OOXML mostra che il documento contiene:

- 409 elementi tabella complessivi;
- 111 tabelle dati con riga di intestazione marcata;
- 298 tabelle utilizzate come contenitori di impaginazione per box, titoli di capitolo e stat block.

La coincidenza esatta tra i 298 avvisi e i 298 contenitori di impaginazione dimostra che non si tratta di 298 tabelle dati prive di intestazione. Marcare questi contenitori come tabelle con intestazione sarebbe semanticamente scorretto. L'avviso viene quindi classificato come limite noto dello strumento automatico, non come difetto bloccante. Prima di un'eventuale edizione digitale formalmente certificata accessibile resta raccomandato un audit manuale specialistico dell'ordine di lettura e della struttura del PDF/DOCX.

## Robustezza della pipeline

Sono state applicate le seguenti protezioni:

- rimozione preventiva degli artefatti PDF obsoleti;
- conversione LibreOffice in processi isolati con profili temporanei;
- timeout e terminazione dell'intero gruppo di processo in caso di blocco;
- post-processing PDF su copia temporanea;
- aggiornamento incrementale di metadati e segnalibri;
- verifica di riapertura e numero di pagine prima della sostituzione atomica dell'originale;
- lock di paginazione verificato contro le pagine effettive del PDF;
- modalità separata per rigenerare il lock dopo modifiche impaginanti;
- controllo di parità approssimativa del contenuto tra DOCX, HTML e PDF;
- preflight di tutti gli artefatti della linea di ingresso.

## Gate interni

| Gate | Stato |
|---|---|
| Regole canoniche uniche | Superato |
| Validazione automatica | Superato |
| Test canonici e audit contenuto | Superato |
| Build completa da sorgenti | Superato |
| Ispezione visiva integrale | Superato |
| Preflight PDF | Superato |
| Audit DOCX | Superato con limite noto documentato |
| Placeholder e metadati | Superato |
| Parità dei prodotti | Superato |

## Gate esterni ancora obbligatori

La versione non deve essere promossa a 1.0 commerciale finché non risultano documentati:

1. blind playtest con Custodi e gruppi indipendenti;
2. developmental editing e technical editing indipendenti;
3. copyediting e correzione bozze finali da una seconda persona;
4. lettura culturale delle tradizioni rappresentate;
5. verifica legale di nome, licenze, font, contributi e contratti;
6. verifica fiscale e dei canali di vendita;
7. crediti nominativi autorizzati dei playtester;
8. validazione di prezzo, pubblico e conversione tramite quickstart.

## Conclusione

La 0.9.0-beta.1 è una beta editoriale completa e tecnicamente controllata, adatta al blind playtest e alla revisione indipendente. Non è ancora una release commerciale 1.0 perché i gate esterni non possono essere sostituiti da controlli automatici o da una revisione interna dell'autore.
