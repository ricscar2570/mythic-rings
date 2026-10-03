import fitz, os, hashlib
P='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
REPL='/mnt/data/_beta9_appendices_379_384.pdf'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
# Work on current normalized base
D=fitz.open(P); meta=D.metadata; toc=D.get_toc()
# Replace 379-384 from clean ReportLab source
R=fitz.open(REPL)
for idx in range(383,377,-1): D.delete_page(idx)
D.insert_pdf(R,start_at=378)
R.close()
# Restore metadata/toc
D.set_metadata(meta)
try: D.set_toc(toc)
except Exception as e: print('toc warn',e)
# Fix page 320 bottom block
pg=D[319]
r=fitz.Rect(44.0,454.5,373.0,496.5)
pg.add_redact_annot(r,fill=(1,1,1)); pg.apply_redactions(); pg.insert_font(fontname='DVSStable',fontfile=FONT)
text="Riduci di 1, fino a un minimo coerente con gli eventi già\navvenuti, quando i Guardiani:\n- distruggono un'infrastruttura essenziale;\n- convertono una cellula della Fratellanza;"
print('p320',pg.insert_textbox(r,text,fontname='DVSStable',fontsize=7.5,lineheight=1.12,color=(0,0,0),overlay=True))
# Fix page 351 conclusion list
pg=D[350]
r=fitz.Rect(44.0,154.0,374.0,276.0)
pg.add_redact_annot(r,fill=(1,1,1)); pg.apply_redactions(); pg.insert_font(fontname='DVSStable2',fontfile=FONT)
text="- Vincenzo viene sconfitto e il rituale viene stabilizzato;\n- Vincenzo accetta un'alternativa e collabora alla riscrittura;\n- i Guardiani assumono il controllo dei pilastri;\n- lo Specchio collassa e il gruppo decide che cosa salvare;\n- una fazione terza prende il Nexus, conseguenza di alleanze fallite."
print('p351',pg.insert_textbox(r,text,fontname='DVSStable2',fontsize=7.5,lineheight=1.12,color=(0,0,0),overlay=True))
# Rebuild useful bookmarks (49 total) before save
base=D.get_toc()
names={x[1] for x in base}; new=[]
for item in base:
    new.append(item); title=item[1]
    if title=='Le Quattro Casate' and 'Interrogare i Morti' not in names: new.append([2,'Interrogare i Morti',70])
    if title=='Campagna: Il Crepuscolo del Velo' and 'Sessione 6: La discesa' not in names: new.append([2,'Sessione 6: La discesa',342])
    if title=='Tre One-Shot' and 'Notte al Monumentale' not in names:
        new += [[2,'Notte al Monumentale',359],[2,"Il Mercante d'Ombre",366],[2,'Sangue sotto il Duomo',372]]
D.set_toc(new)
# Ensure metadata
m=D.metadata; m['title']='Mythic Rings - 0.9.3-beta.9 BLIND CLEAN CANDIDATE'; m['author']='Riccardo Scaringi'; m['subject']='Mythic Rings editorial clean candidate for external blind-read verification'; m['keywords']='Mythic Rings, beta.9, blind clean candidate, RPG'; D.set_metadata(m)
TMP='/mnt/data/_beta9_stable_tmp.pdf'
D.save(TMP,garbage=4,deflate=True,clean=False)
D.close(); os.replace(TMP,P)
with open(P,'rb') as f: print('SHA',hashlib.sha256(f.read()).hexdigest())
print('SIZE',os.path.getsize(P))
# verify nulls quickly
D=fitz.open(P); tt='\n'.join(p.get_text() for p in D); print('NULLS',tt.count(chr(0)),'TOC',len(D.get_toc()),'PAGES',len(D))
for pn in [320,351,380,381,382,384]:
 t=D[pn-1].get_text(); print('PAGE',pn,'nulls',t.count(chr(0)))
