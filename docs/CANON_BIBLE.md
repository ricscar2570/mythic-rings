# Mythic Rings — Bibbia canonica del mondo

**Stato:** normativa per il canon d'ambientazione dalla beta 0.9.0-beta.2 / Gate G1  
**Data:** 13 agosto 2026

Questa bibbia risolve le versioni concorrenti di geografia occulta, gerarchia, cronologia e numeri. Non sostituisce `docs/CANONICAL_RULES_SPEC.md` per le regole di gioco: governa il **mondo**, mentre la specifica delle regole governa le **procedure**.

## Gerarchia delle fonti del canon d'ambientazione

1. `data/canon/*.yml` — dati canonici strutturati.
2. Questo documento — spiegazione leggibile e implicazioni.
3. Capitoli del manuale — presentazione editoriale coerente con 1 e 2.
4. Campagna, one-shot, quick reference — applicazioni; non possono ridefinire il canon.

Se una fonte di livello inferiore diverge, va corretta: non crea una variante valida.

## 1. Tempo e Milano reale

Mythic Rings usa un **presente mobile**. Nel testo si scrive *Milano, oggi* salvo date storiche o date diegetiche indispensabili. Questo evita che il manuale diventi obsoleto per effetto del calendario.

Per scala urbana, il testo distingue:

- **Comune di Milano:** circa 1,4 milioni di residenti.
- **Città Metropolitana di Milano:** circa 3,25 milioni di residenti.
- **Regione urbana più ampia:** non riceve un numero canonico e non è sinonimo di Città Metropolitana.

I valori puntuali e le date di riferimento sono registrati in `data/canon/world.yml` e documentati in `docs/research/CANON_SOURCE_NOTES.md`.

## 2. Custodi, Società del Velo e Cerchia

I **Custodi di Milano** comprendono circa **40 Guardiani attivi**, ciascuno scelto da un Anello, più circa **200 persone di supporto** appartenenti alla stessa struttura: analisti, medici, archivisti, tecnici, logistica e Consapevoli.

La **Società del Velo** è un'organizzazione distinta e alleata. Conta circa **100 operativi** Consapevoli inseriti nel mondo civile e istituzionale. I suoi operativi non sono inclusi nelle duecento persone di supporto dei Custodi.

La **Cerchia degli Anziani** ha cinque seggi: quattro rappresentanti delle Casate e una Presidenza neutrale.

### Cerchia attuale

- **Elisabetta Conti** — Presidente neutrale; ex-Avalon ritirata. Presiede, media e vota come quinto membro.
- **Eleonora Visconti** — Anziana Avalon e coordinatrice operativa; è *Prima tra Pari* sul campo, non Presidente della Cerchia.
- **Leila Ferrara** — Anziana Umbra; intelligence e sicurezza interna.
- **Kwame Asante** — Anziano Ife; mediazione e reti viventi.
- **Marisol Reyes** — Anziana Mictlan; memoria dei morti e gestione delle soglie.

**Padre Tommaso De Luca** è un Guardiano Avalon veterano e mentore, non un Anziano.  
**Valentina Riva, “La Volpe”** è un'Umbra rinnegata e mediatrice indipendente del Mercato Notturno; non è un personaggio giocatore di esempio.

## 3. Anelli e Casate

Esistono **quattro stirpi fondative di Anelli**, non quattro soli artefatti. Gli Anelli individuali sono molteplici; a Milano ne risultano attivi circa quaranta, in corrispondenza approssimativa con i Guardiani operativi.

Gli Anelli sono più antichi delle istituzioni milanesi. Nel 1224 quattro portatori fondarono il patto che diventerà l'organizzazione dei Custodi. Gli archivi moderni classificano retroattivamente quei portatori nelle quattro stirpi, ma non è necessario né canonico che chiamassero già le Casate **Avalon, Umbra, Ife e Mictlan**.

I nomi moderni delle Casate sono una convenzione istituzionale. In particolare:

- il gioco **non** afferma che tradizioni yoruba o nahua/mesoamericane derivino da Milano o dagli Anelli;
- il gioco **non** assegna a Ife o Mictlan una singola “data di arrivo” basata su una migrazione storica inventata;
- le formulazioni culturali restano soggette a sensitivity reading specialistico prima della release commerciale.

## 4. Cronologia canonica

La timeline strutturata è in `data/canon/timeline.yml`. I punti irrinunciabili sono:

- **1224:** fondazione del patto dei Custodi in un periodo di conflitto politico e crescente tensione imperiale; non “Milano devastata dalle guerre di Federico II”.
- **1348:** crisi del Velo durante la peste e formalizzazione di protocolli funerari/di contenimento.
- **1386:** in parallelo all'avvio storico del cantiere del Duomo, evento occulto dello Specchio del Velo e Patto del Nexus.
- **1503:** Grande Scisma degli Ouroboros, evento interamente fittizio.
- **XIX–XX secolo:** consolidamento progressivo della nomenclatura moderna delle Casate negli archivi.
- **1943:** brecce durante i bombardamenti e violazione del Patto del Nexus da parte di Gervasio, evento occulto fittizio.
- **1992:** Marisol Reyes arriva a Milano seguendo il proprio Anello; questo non equivale all'“arrivo della Casata Mictlan”.
- **2003:** crisi Arianna. Elisabetta partecipa alla decisione originaria e perde un braccio; Eleonora partecipa alla copertura successiva.
- **oggi:** circa quaranta Guardiani e Anelli attivi.

## 5. Le cinque Linee Ley

Le Linee sono geografia **occulta e fittizia**, ma i percorsi rispettano la geografia relativa della città abbastanza da poter essere ricostruiti senza interpretazioni concorrenti.

| ID | Linea | Direzione | Percorso canonico | Affinità |
|---|---|---|---|---|
| MR-LEY-001 | Alba | Nord-est | Sesto San Giovanni → Loreto → Porta Venezia → San Babila → Duomo | Avalon |
| MR-LEY-002 | Ombra | Sud-ovest | Navigli → Darsena → Porta Ticinese → Colonne di San Lorenzo → Duomo | Umbra |
| MR-LEY-003 | Vita | Nord-ovest | Parco Sempione → Castello Sforzesco → Cairoli → Duomo | Ife |
| MR-LEY-004 | Morti | Nord | Cimitero Monumentale → Porta Garibaldi → Brera → Duomo | Mictlan |
| MR-LEY-005 | Fato | Sud-est | Porta Romana → Crocetta → Duomo | nessuna |

### Politica meccanica

Le Linee e i Nexus **non concedono +1/-1 generici**. Cambiano prima di tutto la fiction:

- rendono disponibile un accesso;
- aumentano o riducono scala/portata/durata quando il testo della mossa lo permette;
- fanno emergere informazioni o segnali;
- cambiano posizione e rischio;
- rendono possibile una procedura che altrove richiederebbe preparazione.

Il tiro, il costo di potere, la guarigione, l'Armatura, lo Stress e la Corruzione restano quelli delle rispettive fonti normative.

## 6. Nexus

Il **Nexus del Duomo (MR-LOC-001)** è la convergenza delle cinque Linee, territorio neutrale e sede dei rituali di scala maggiore.

I cinque Nexus Secondari canonici sono:

- **MR-LOC-002 — Giardini di Porta Venezia**, Linea dell'Alba.
- **MR-LOC-003 — Darsena**, Linea dell'Ombra.
- **MR-LOC-004 — Castello Sforzesco / Parco Sempione**, Linea della Vita.
- **MR-LOC-005 — Cimitero Monumentale**, Linea dei Morti.
- **MR-LOC-006 — Porta Romana / Crocetta**, Linea del Fato.

Ogni nodo ha funzione, custodia, rischio, beneficio e segnale sensoriale in `data/canon/occult_geography.yml`. I benefici sono fictionali e non persistono automaticamente nella sessione successiva.

## 7. Invarianti del canon

Una modifica futura che contraddice uno di questi punti richiede una decisione registrata:

1. Milano reale e riconoscibile è il luogo centrale del gioco.
2. Gli Anelli sono molteplici ma appartengono a quattro stirpi.
3. Risonanza e prezzo rendono l'Anello il centro del sistema.
4. Le quattro Casate sono istituzioni contemporanee costruite su stirpi più antiche, non prove di un'origine comune delle culture reali evocate.
5. Il Velo produce conseguenze condivise sulla città.
6. La Cerchia ha cinque seggi e ruoli distinti.
7. Linee e Nexus non devono diventare una seconda economia di bonus numerici.
