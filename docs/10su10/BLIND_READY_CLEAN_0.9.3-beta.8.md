# Mythic Rings — Blind Ready Clean 0.9.3-beta.8

**Data:** 2026-10-03  
**Stato:** freeze editoriale pre-blind, successore di beta.7  
**Manuale:** `Mythic_Rings_Manuale_Completo_0.9.3-beta.8_BLIND-READY-CLEAN.pdf`  
**SHA-256 manuale:** `d80c2a18f0da36e65405c7066b4bb5e38d012d23fa6f89c04f68c46853512fcb`  
**Pagine:** 387  
**Blind Test Pack:** `Mythic_Rings_BLIND_TEST_PACK_0.9.3-beta.8.zip`  
**SHA-256 pack:** `74c298a86f743fc84725dfcd404f6b467cf89a8db3637be6095c7544e86dd7f4`

## Motivo della beta.8

La verifica differenziale della beta.5 aveva dimostrato che il sistema era blind-ready ma il PDF concreto conservava residui editoriali capaci di falsare i test. La beta.7 ne chiudeva la maggior parte; il controllo finale audit→beta.7 ha ancora rilevato:

- frammento duplicato di **Interrogare i Morti**;
- titoli/procedure di **Confine dei Morti**, **Animare i Caduti** e **Maremoto dei Morti** non ancora composti correttamente;
- duplicazione della sezione **Rispetta i limiti del sistema** nella Guida del Custode;
- incoerenza fra pacing e durata dichiarata di **Sangue sotto il Duomo**;
- fasce numeriche ancora miste.

## Correzioni beta.8

- eliminato il frammento duplicato sopra *Presagio*;
- ricostruiti come blocchi integri Confine dei Morti, Animare i Caduti e Maremoto dei Morti;
- ricostruita la sezione dei limiti del Custode senza caratteri nulli o doppioni;
- *Sangue sotto il Duomo*: 5–6 ore completo, 4–5 ore convention cut;
- fasce e intervalli numerici normalizzati ricostruendo soltanto i blocchi interessati, senza sostituzioni globali fragili;
- nessuna modifica a costi, danni, PF, Risonanza, scaling, progressione o potenza delle Casate.

## QA

- preflight PASS: 387 pagine, PDF apribile e non cifrato;
- 44 voci outline;
- tutte le 387 pagine renderizzate con successo;
- zero residui testuali delle principali corruzioni audit;
- nessun `7 9`, `7-9`, `10-11`, `6-`, `0-8`, `0-10` residuo nelle fasce/range normalizzati;
- Blind Test Pack rigenerato direttamente dalla beta.8;
- tutti i file del pack verificati con SHA256SUMS;
- documenti organizer rigenerati nativamente per beta.8.

## Freeze

**Beta.8 è l’unica build da distribuire ai gruppi blind.** Beta.6 e beta.7 sono superseded.

Da qui in avanti, modifiche a costi, danni, PF, Risonanza, scaling, poteri o durata degli scontri devono derivare dai dati umani del blind.
