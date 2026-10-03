from pypdf import PdfReader, PdfWriter
import fitz, os, hashlib
BASE='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
REPL='/mnt/data/_beta9_appendices_379_384.pdf'
OUT='/mnt/data/_beta9_pypdf_final.pdf'
base=PdfReader(BASE)
rep=PdfReader(REPL)
writer=PdfWriter()
# pages 1-378 from current fully patched base
for i in range(378): writer.add_page(base.pages[i])
# clean appendices 379-384
for i in range(6): writer.add_page(rep.pages[i])
# pages 385-387 from base
for i in range(384,387): writer.add_page(base.pages[i])
writer.add_metadata({
    '/Title':'Mythic Rings - 0.9.3-beta.9 BLIND CLEAN CANDIDATE',
    '/Author':'Riccardo Scaringi',
    '/Subject':'Mythic Rings editorial clean candidate for external blind-read verification',
    '/Keywords':'Mythic Rings, beta.9, blind clean candidate, RPG'
})
# Rebuild outline deterministically
outline=[
(1,'Cover',1),(1,'Che gioco è Mythic Rings',2),(1,'Indice - Parte I-IV',3),(1,'Indice - Parte V-VI e appendici',4),(1,'Come leggere le regole',5),(1,'Spoiler, stato e blind test',6),(1,'Milano Nascosta',7),(1,'I Custodi e gli Anelli di Custodia',20),(1,'Le Quattro Casate',47),(2,'Interrogare i Morti',70),(1,'Creare il Tuo Guardiano',75),(1,'Come si gioca',96),(1,'Le Mosse Base',122),(1,'Poteri di Avalon',135),(1,'Poteri di Umbra',142),(1,'Poteri di Ife',149),(1,'Poteri di Mictlan',156),(1,'La Milano Sotterranea',163),(1,'I Dodici Quartieri di Milano',169),(1,'Le Fazioni di Milano',208),(1,'Profili operativi delle fazioni',211),(1,'20 Hook per Avventure',212),(1,'Session Zero',216),(1,'I Principi del Custode',220),(1,'Le Mosse del Custode',228),(1,'Il Doom Clock Espanso',237),(1,'Creare e Gestire Sessioni',244),(1,'Bilanciare il Combattimento',252),(1,'Scaling per 2-5 Guardiani',258),(1,'XP e Avanzamento',259),(1,'Mosse Avanzate',262),(1,'Le 12 Attività di Downtime',267),(1,'Sistema di Reputazione',276),(1,'Safety Tools',282),(1,'Il Bestiario di Milano',283),(1,'Dashboard della campagna',309),(1,'Campagna: Il Crepuscolo del Velo',310),(2,'Sessione 6: La discesa',342),(1,'Pacing delle one-shot',358),(1,'Tre One-Shot',359),(2,'Notte al Monumentale',359),(2,"Il Mercante d'Ombre",366),(2,'Sangue sotto il Duomo',372),(1,'Appendice A - Glossario essenziale',379),(1,'Appendice B - Quick Reference Giocatori',380),(1,'Appendice C - Quick Reference Custode',382),(1,'Appendice D - FAQ: casi limite',384),(1,'Appendice E - Indice essenziale',385),(1,'Appendice F - Protocollo blind',386)
]
parents={}
for level,title,page in outline:
    parent=parents.get(level-1) if level>1 else None
    item=writer.add_outline_item(title,page_number=page-1,parent=parent)
    parents[level]=item
    for k in list(parents):
        if k>level: parents.pop(k,None)
with open(OUT,'wb') as f: writer.write(f)
# quick checks
D=fitz.open(OUT); text='\n'.join(p.get_text() for p in D)
print('pages',len(D),'toc',len(D.get_toc()),'nulls',text.count(chr(0)))
for pn in [157,320,351,379,380,381,382,384]: print('page',pn,'nulls',D[pn-1].get_text().count(chr(0)))
with open(OUT,'rb') as f: print('sha',hashlib.sha256(f.read()).hexdigest())
print('size',os.path.getsize(OUT))
