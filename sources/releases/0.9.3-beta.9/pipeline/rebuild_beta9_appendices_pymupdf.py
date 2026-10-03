import fitz, os, hashlib
from pathlib import Path

SRC = '/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
REPL = '/mnt/data/_beta9_appendices_379_384_pymupdf.pdf'
TMP = '/mnt/data/_beta9_appendices_merged_pymupdf.pdf'
W,H = 419.5276, 595.2756
LEFT, RIGHT = 44, 375
WIDTH = RIGHT-LEFT

FONT_FILES={
    'DVS':'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    'DVS-B':'/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
    'DVSS':'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'DVSS-B':'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
}
MEASURE={k:fitz.Font(fontfile=v) for k,v in FONT_FILES.items()}
COLORS={
    'header':(24/255,37/255,54/255),
    'grid':(139/255,152/255,167/255),
    'fill':(232/255,238/255,244/255),
    'footer':(73/255,81/255,90/255),
    'black':(0,0,0),
}

def setup(page):
    for name,path in FONT_FILES.items():
        page.insert_font(fontname=name,fontfile=path)

def text_width(text,font,size):
    return MEASURE[font].text_length(text,fontsize=size)

def wrap(text,font,size,width):
    out=[]
    for para in str(text).split('\n'):
        words=para.split()
        if not words:
            out.append(''); continue
        cur=''
        for word in words:
            test=word if not cur else cur+' '+word
            if text_width(test,font,size)<=width:
                cur=test
            else:
                if cur: out.append(cur)
                cur=word
        if cur: out.append(cur)
    return out

def put_line(page,x,y,text,font='DVS',size=7,color=None):
    page.insert_text((x,y),text,fontsize=size,fontname=font,color=color or COLORS['black'],overlay=True)

def put_lines(page,x,y,lines,font='DVS',size=7,leading=8.3,color=None):
    for ln in lines:
        put_line(page,x,y,ln,font,size,color); y+=leading
    return y

def text_block(page,x,y,text,width,font='DVS',size=7,leading=8.3,gap=0):
    return put_lines(page,x,y,wrap(text,font,size,width),font,size,leading)+gap

def heading(page,text,size=15,y=48):
    put_line(page,LEFT,y,text,'DVS-B',size,COLORS['header'])

def subheading(page,text,y,size=9.6):
    put_line(page,LEFT,y,text,'DVS-B',size,COLORS['header'])

def footer(page,num):
    put_line(page,LEFT,568,'MYTHIC RINGS 0.9.3-beta.9 | BLIND CLEAN CANDIDATE','DVSS',5.4,COLORS['footer'])
    # centered page number
    s=str(num); w=text_width(s,'DVSS',6.8)
    put_line(page,(W-w)/2,585,s,'DVSS',6.8,COLORS['footer'])

def bullet_list(page,y,items,x=LEFT,width=WIDTH,size=6.55,leading=7.8,gap=3.5):
    for item in items:
        lines=wrap(item,'DVS',size,width-14)
        page.draw_circle((x+3,y-2.4),1.05,color=COLORS['header'],fill=COLORS['header'],overlay=True)
        y=put_lines(page,x+11,y,lines,'DVS',size,leading)+gap
    return y

def draw_table(page,x,y,col_widths,rows,header=True,font_size=6.15,row_pad=3.0):
    heights=[]
    all_lines=[]
    for ri,row in enumerate(rows):
        f='DVSS-B' if header and ri==0 else 'DVSS'
        rowlines=[]; maxlines=1
        for j,cell in enumerate(row):
            ls=wrap(cell,f,font_size,col_widths[j]-2*row_pad)
            rowlines.append(ls); maxlines=max(maxlines,len(ls))
        all_lines.append(rowlines)
        heights.append(maxlines*(font_size+1.6)+2*row_pad)
    total=sum(col_widths)
    cur=y
    for ri,row in enumerate(rows):
        h=heights[ri]
        if header and ri==0:
            page.draw_rect(fitz.Rect(x,cur,x+total,cur+h),color=None,fill=COLORS['fill'],overlay=True)
        page.draw_rect(fitz.Rect(x,cur,x+total,cur+h),color=COLORS['grid'],width=.35,overlay=True)
        xx=x
        for w in col_widths[:-1]:
            xx+=w; page.draw_line((xx,cur),(xx,cur+h),color=COLORS['grid'],width=.35,overlay=True)
        f='DVSS-B' if header and ri==0 else 'DVSS'
        xx=x
        for j,ls in enumerate(all_lines[ri]):
            ty=cur+row_pad+font_size
            for ln in ls:
                put_line(page,xx+row_pad,ty,ln,f,font_size); ty+=font_size+1.6
            xx+=col_widths[j]
        cur+=h
    return cur

# build replacement PDF
out=fitz.open()
for _ in range(6): out.new_page(width=W,height=H)
for p in out: setup(p)

# 379
p=out[0]; heading(p,'Appendice A - Glossario essenziale'); y=72
entries=[
("Ancora dell'Anello", "Legame L1+ designato alla creazione. Non concede bonus aggiuntivi; può sostituire un prezzo Anima della Risonanza con Legame una volta per sessione secondo la procedura completa."),
("Azione Principale", "Azione significativa disponibile a ogni Guardiano una volta per round. Attaccare, poteri, cure, Aiutare/Difendere in combattimento e comandi significativi alle evocazioni la consumano."),
("Armatura", "Riduce il danno pertinente; usa la migliore fonte, non la somma indiscriminata. Equipaggiamento max 3, totale ordinario max 4, boss max 2. Negli stat block, Armatura non qualificata significa Armatura fisica."),
("Casata", "Tradizione soprannaturale dell'Anello: Avalon, Umbra, Ife o Mictlan."),
("Condizione", "Ostacolo persistente con effetto fictionale/meccanico e via di rimozione dichiarata."),
("Corruzione", "Risorsa Umbra 0–8. A 6–7 aumenta i costi; a 8, dopo la risoluzione del potere che raggiunge la soglia, avviene la trasformazione salvo eccezione esplicita."),
("Custode", "Partecipante che presenta il mondo, interpreta PNG e minacce e applica le Mosse senza tirare dadi."),
("Danno puro", "Danno che ignora Armatura."),
("Doom Clock", "Tracciato dell'avanzamento di una minaccia o crisi."),
("Escalation", "Bonus al danno dei Guardiani negli scontri lunghi: +1 al round 3, +2 al round 4, +3 dal round 5; una sola volta per Azione Principale."),
("Fato", "Risorsa personale: 2 per sessione, max 2; 1 punto ritira un solo d6 dopo il tiro e prima delle conseguenze."),
("Legame", "Relazione significativa con Tipo e Livello 0–3. Bonus +1 a L1, +2 a L2–L3 quando persona e Tipo sono direttamente pertinenti."),
("LS", "Livello di Sfida: indicatore orientativo della pressione prodotta da una minaccia."),
("Mossa", "Procedura attivata da un trigger nella fiction."),
("PF temporanei", "Riserva separata che assorbe danno prima dei PF reali; non paga costi, non aumenta PF massimi, non modifica soglie e non si somma."),
("Rinuncia", "Procedura volontaria e consensuale che spezza il legame operativo con l'Anello; ulteriori conseguenze permanenti devono essere concordate prima."),
("Risonanza", "Una volta per scena può migliorare 6− in 7–9 o 7–9 in 10+ su Usare Potere o Mossa Esclusiva con tiro, pagando un prezzo Corpo/Anima/Legame/Mondo."),
("Sangue Tenace", "Passivo Mictlan 1/scena che può convertire parte di un costo in PF in Stress quando il pagamento porterebbe sotto il 40% dei PF massimi, secondo i limiti del potere."),
("Stress", "Risorsa 0–10; a 8–9 aumenta i costi in Stress, a 10 il sovraccarico produce Burnout."),
("Ultimo Respiro", "Tiro 2d6 senza bonus a 0 PF."),
("Velo Tracker", "Scala globale 0–12 della persistenza delle prove pubbliche del soprannaturale."),
]
for term,desc in entries:
    y=text_block(p,LEFT,y,f'{term}. {desc}',WIDTH,'DVS',6.35,7.25,1.4)
if y>553: raise RuntimeError(f'379 overflow {y}')
footer(p,379)

# 380
p=out[1]; heading(p,'Appendice B - Quick Reference Giocatori'); y=76
subheading(p,'Tiro base',y); y+=10
rows=[['Totale','Esito'],['10+','Successo pieno'],['7–9','Successo con costo, scelta o efficacia ridotta'],['6−','Conseguenza; il Custode compie una Mossa']]
y=draw_table(p,LEFT,y,[70,261],rows,font_size=6.25); y+=12
subheading(p,'Combattimento',y); y+=12
y=bullet_list(p,y,[
"Ogni round: un'Azione Principale + movimento coerente.",
"Difendere e Aiutare in combattimento consumano l'Azione Principale se ancora disponibile; Resistere no.",
"Un potere offensivo diretto usa Usare Potere; un'arma evocata già attiva usa Attaccare per i colpi successivi.",
"Escalation: round 3 +1 danno, round 4 +2, round 5+ +3; massimo una volta per Azione Principale.",
"Evocazioni: normalmente un'unità mantenuta; attaccare o usare una capacità significativa richiede la tua Azione Principale, salvo autonomia esplicita.",
],size=6.35,leading=7.55,gap=3.2); y+=2
subheading(p,'Danno',y); y+=11
rows=[['Tipo','Regola'],['Fisico','Armatura fisica o mistica'],['Magico','Solo Armatura mistica'],['Puro','Ignora Armatura'],['Penetrante X','Riduci Armatura di X prima del calcolo'],['Resistenza [tipo]','−2 danno dopo Armatura, minimo 1 salvo immunità']]
y=draw_table(p,LEFT,y,[95,236],rows,font_size=5.95); y+=7
y=text_block(p,LEFT,y,'Armatura non qualificata negli stat block = Armatura fisica. Modificatore totale, Caratteristica inclusa: da −3 a +4.',WIDTH,'DVS',6.0,7.2)
footer(p,380)

# 381
p=out[2]; heading(p,'Risonanza',size=11.2); y=70
y=bullet_list(p,y,[
"1/scena; dopo eventuale Fato e prima delle conseguenze.",
"Solo Usare Potere o Mossa Esclusiva di Casata con tiro.",
"6− diventa 7–9; 7–9 diventa 10+.",
"Il Custode offre due prezzi validi di categorie diverse. Se non può, la procedura non parte.",
"Se due prezzi validi sono stati dichiarati, l'uso è speso anche se rifiuti.",
"Accettare sostituisce la fascia originale: non applicare anche la conseguenza precedente.",
],size=6.45,leading=7.65,gap=3.1); y+=2
rows=[['Prezzo','Effetto'],['Corpo',"Perdi 4 PF ignorando Armatura, dopo l'effetto migliorato"],['Anima','Condizione nuova o significativamente diversa'],['Legame','Conseguenza concreta su un Legame L1+ nominato'],['Mondo','Velo +1 e traccia concreta nella fiction']]
y=draw_table(p,LEFT,y,[80,251],rows,font_size=6.05); y+=13
subheading(p,'Ultimo Respiro',y,size=9.8); y+=10
rows=[['Esito','Conseguenza'],['12+','1 PF, cosciente; agisci prima della fine del round'],['10–11','1 PF, incapacitato finché non ricevi cure o la scena cambia'],['7–9','1 PF, incapacitato come 10–11 + conseguenza duratura'],['6−','Muori, salvo Morte Eroica o altra regola esplicita']]
y=draw_table(p,LEFT,y,[75,256],rows,font_size=6.0)
footer(p,381)

# 382
p=out[3]; heading(p,'Appendice C - Quick Reference Custode'); y=76
subheading(p,'Procedura al tavolo',y); y+=12
y=bullet_list(p,y,[
"Chiedi obiettivo e metodo; se non c'è rischio interessante, non tirare.",
"Individua un solo trigger per la stessa incertezza.",
"Dichiara rischio e costo prima del tiro quando la procedura lo richiede.",
"Su 6− o conseguenza usa la fiction già stabilita: non generare una seconda attivazione completa di una minaccia che ha già speso il budget.",
"Gli indizi fondamentali non vengono negati da un singolo tiro.",
],size=6.3,leading=7.45,gap=3.2); y+=3
subheading(p,'Budget delle minacce',y); y+=12
y=text_block(p,LEFT,y,"Ogni avversario significativo o gruppo di minion gestito insieme ha normalmente una sola Azione Significativa per round. Può spenderla come conseguenza, quando una minaccia annunciata viene ignorata, oppure a fine round se ancora libera.",WIDTH,'DVS',6.3,7.5,9)
subheading(p,'Risonanza - prezzi validi',y); y+=12
y=bullet_list(p,y,[
"Corpo: valido finché il Guardiano è vivo e può perdere PF; può portare a Ultimo Respiro.",
"Anima: richiede un limite concreto e una via di risoluzione.",
"Legame: richiede un Legame L1+ nominato e realmente raggiungibile dalla conseguenza.",
"Mondo: richiede una traccia concreta; non è valido a Velo 12 salvo una procedura oltre la Rivelazione.",
"Offri due prezzi differenti e realmente applicabili.",
],size=6.3,leading=7.45,gap=3.2)
footer(p,382)

# 383
p=out[4]; heading(p,'Quick Reference Custode - Preparazione'); y=76
subheading(p,'Preparazione minima',y); y+=10
rows=[['Elemento','Domanda'],['Verità','Che cosa sta succedendo davvero?'],['Minaccia','Che cosa vuole e che cosa farà se nessuno interviene?'],['Indizi','Quali tre piste indipendenti conducono alla verità?'],['Pressione','Quale Clock o conseguenza rende urgente la situazione?'],['Scelte','Quali almeno due soluzioni sono realmente praticabili?'],['Ricaduta','Quale Legame, fazione o parte del Velo reagirà?']]
y=draw_table(p,LEFT,y,[95,236],rows,font_size=5.95); y+=13
subheading(p,'Combattimento',y); y+=10
y=text_block(p,LEFT,y,'Definisci obiettivo, impulso della minaccia, via di fuga, terreno utile, budget di Azione Significativa e possibile cambio di fase. Non bilanciare soltanto sui PF.',WIDTH,'DVS',6.25,7.45,5)
y=text_block(p,LEFT,y,"Evocazioni: normalmente una sola unità mantenuta per Guardiano. Un attacco o capacità significativa usa l'Azione Principale del Guardiano salvo autonomia esplicita; l'azione autonoma non riceve Escalation.",WIDTH,'DVS',6.25,7.45,10)
subheading(p,'Reputazione alta',y); y+=10
y=text_block(p,LEFT,y,'A +3/+5 la Reputazione cambia prima di tutto ciò che è possibile nella fiction. Non chiedere automaticamente Persuadere o Raggirare per privilegi già concessi dallo status; tira solo se resta un conflitto reale.',WIDTH,'DVS',6.25,7.45)
footer(p,383)

# 384 FAQ
p=out[5]; heading(p,'Appendice D - FAQ: soli casi limite'); COLW=158; X1=44; X2=218

def qa(page,x,y,q,a):
    y=put_lines(page,x,y,wrap(q,'DVS-B',7.05,COLW),'DVS-B',7.05,8.15)+1
    y=put_lines(page,x,y,wrap(a,'DVS',6.1,COLW),'DVS',6.1,7.15)+8.0
    return y
left=[
('Attaccare o Usare Potere?',"Un potere offensivo diretto usa Usare Potere. Un'arma evocata già attiva usa Attaccare per i colpi successivi. Non fare due tiri per la stessa incertezza."),
('Posso Difendere dopo avere già agito?',"No, salvo capacità che conceda una reazione. Difendere spende l'Azione Principale se ancora disponibile."),
("Resistere consuma l'azione?","No. Si attiva solo se l'effetto concede opposizione e non genera un'azione offensiva extra."),
('Come funzionano le evocazioni?',"Normalmente puoi mantenere un'unità evocata per Guardiano. Per attaccare o usare una capacità significativa spendi la tua Azione Principale, salvo autonomia esplicita."),
('I PF temporanei possono pagare costi o contare per Sangue Tenace?',"No. Assorbono danno ma non pagano costi, non aumentano i PF massimi e non modificano la soglia del 40%."),
('Confidente L2 o L3?',"Un Confidente L2+ che assiste Riprendersi concede lo speciale +1; sostituisce il normale bonus del Legame. Catarsi è L3."),
('Corruzione a 8?',"Risolvi il potere che ha raggiunto la soglia, poi avviene la trasformazione in PNG, salvo eccezione esplicita."),
]
right=[
('Ultimo Respiro 7–9?',"Torni a 1 PF, resti incapacitato come sul 10–11 e scegli una conseguenza duratura."),
('Rinuncia: si perde automaticamente la percezione magica?',"No. Conseguenze permanenti ulteriori devono essere concordate prima; Davide è un caso specifico."),
('Rifiutare Risonanza la conserva?',"Solo se il Custode non riesce a formulare due prezzi validi. Se i due prezzi sono stati dichiarati, l'uso della scena è speso anche se rifiuti."),
('Mondo usa una scala diversa dal Velo?',"No. Usa sempre il Velo Tracker."),
('Interrogare o Parlare con i Morti?',"Se i resti rendono già possibile il contatto, usa Interrogare senza pagare PF. Parlare apre il contatto quando altrimenti non sarebbe possibile. Mai due tiri per la stessa incertezza."),
('Armatura non qualificata?',"Negli stat block significa Armatura fisica salvo diversa specificazione."),
]
y1=70
for q,a in left: y1=qa(p,X1,y1,q,a)
y2=70
for q,a in right: y2=qa(p,X2,y2,q,a)
if max(y1,y2)>548: raise RuntimeError((y1,y2))
footer(p,384)

out.set_metadata({'title':'Mythic Rings beta.9 Appendici A-D Unicode','author':'Riccardo Scaringi'})
out.save(REPL,garbage=4,deflate=True,clean=True)
out.close()

src=fitz.open(SRC)
rep=fitz.open(REPL)
toc=src.get_toc(simple=False)
meta=src.metadata
for idx in range(383,377,-1): src.delete_page(idx)
src.insert_pdf(rep,start_at=378)
src.set_metadata(meta)
try: src.set_toc(toc)
except Exception as e: print('TOC warning',e)
src.save(TMP,garbage=4,deflate=True,clean=True)
src.close(); rep.close()
os.replace(TMP,SRC)
with open(SRC,'rb') as f: print('SHA256',hashlib.sha256(f.read()).hexdigest())
print('SIZE',os.path.getsize(SRC))
