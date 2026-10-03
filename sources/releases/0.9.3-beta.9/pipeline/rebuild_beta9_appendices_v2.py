from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, black
from reportlab.pdfbase.pdfmetrics import stringWidth
import fitz, os, hashlib

SRC='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
REPL='/mnt/data/_beta9_appendices_379_384_v2.pdf'
TMP='/mnt/data/_beta9_appendices_replaced_v2.pdf'
W,H=419.5276,595.2756

# Unicode-capable embedded fonts.
pdfmetrics.registerFont(TTFont('NS','/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NS-B','/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('NSS','/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NSS-B','/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'))

c=canvas.Canvas(REPL,pagesize=(W,H),pageCompression=1)
LEFT=44; RIGHT=375; WIDTH=RIGHT-LEFT
HEADER_COLOR=HexColor('#182536')
GRID=HexColor('#8B98A7')
HEADER_FILL=HexColor('#E8EEF4')
FOOTER=HexColor('#49515A')


def footer(page):
    c.setFillColor(FOOTER)
    c.setFont('NSS',5.4)
    c.drawString(LEFT,27,'MYTHIC RINGS 0.9.3-beta.9 | BLIND CLEAN CANDIDATE')
    c.setFont('NSS',6.8)
    c.drawCentredString(W/2,10,str(page))
    c.setFillColor(black)


def wrap(text,font,size,width):
    lines=[]
    for para in str(text).split('\n'):
        words=para.split()
        if not words:
            lines.append('')
            continue
        cur=''
        for word in words:
            test=word if not cur else cur+' '+word
            if stringWidth(test,font,size)<=width:
                cur=test
            else:
                if cur: lines.append(cur)
                cur=word
        if cur: lines.append(cur)
    return lines


def draw_lines(x,y,lines,font='NS',size=7.0,leading=8.3):
    c.setFont(font,size)
    for ln in lines:
        c.drawString(x,y,ln)
        y-=leading
    return y


def text_block(x,y,text,width,font='NS',size=7.0,leading=8.3,gap=0):
    y=draw_lines(x,y,wrap(text,font,size,width),font,size,leading)
    return y-gap


def heading(text,size=15.0,y=548):
    c.setFillColor(HEADER_COLOR)
    c.setFont('NS-B',size)
    c.drawString(LEFT,y,text)
    c.setFillColor(black)


def subheading(text,y,size=9.6):
    c.setFillColor(HEADER_COLOR)
    c.setFont('NS-B',size)
    c.drawString(LEFT,y,text)
    c.setFillColor(black)


def bullet_list(y,items,x=LEFT,width=WIDTH,size=6.65,leading=8.0,gap=4.0):
    for item in items:
        lines=wrap(item,'NS',size,width-13)
        c.setFillColor(HEADER_COLOR)
        c.circle(x+2.8,y-2.4,1.15,fill=1,stroke=0)
        c.setFillColor(black)
        y=draw_lines(x+11,y,lines,'NS',size,leading)
        y-=gap
    return y


def draw_table(x,y,col_widths,rows,header=True,font_size=6.2,row_pad=3.1):
    heights=[]
    for r_i,row in enumerate(rows):
        f='NSS-B' if header and r_i==0 else 'NSS'
        maxlines=1
        for j,cell in enumerate(row):
            maxlines=max(maxlines,len(wrap(cell,f,font_size,col_widths[j]-2*row_pad)))
        heights.append(maxlines*(font_size+1.65)+2*row_pad)
    totalw=sum(col_widths)
    cur=y
    for r_i,row in enumerate(rows):
        h=heights[r_i]
        if header and r_i==0:
            c.setFillColor(HEADER_FILL); c.rect(x,cur-h,totalw,h,fill=1,stroke=0); c.setFillColor(black)
        c.setStrokeColor(GRID); c.setLineWidth(0.35)
        c.rect(x,cur-h,totalw,h,fill=0,stroke=1)
        xx=x
        for w in col_widths[:-1]:
            xx+=w; c.line(xx,cur-h,xx,cur)
        xx=x
        f='NSS-B' if header and r_i==0 else 'NSS'
        for j,cell in enumerate(row):
            lines=wrap(cell,f,font_size,col_widths[j]-2*row_pad)
            ty=cur-row_pad-font_size
            c.setFont(f,font_size)
            for ln in lines:
                c.drawString(xx+row_pad,ty,ln); ty-=font_size+1.65
            xx+=col_widths[j]
        cur-=h
    c.setStrokeColor(black)
    return cur

# 379 - Glossario
heading('Appendice A - Glossario essenziale')
y=519
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
    # term and description as one compact paragraph; term bold on first line only is unnecessary for semantic clarity.
    text=f'{term}. {desc}'
    lines=wrap(text,'NS',6.45,WIDTH)
    y=draw_lines(LEFT,y,lines,'NS',6.45,7.35)-1.55
if y<36:
    raise RuntimeError(f'Glossary overflow y={y}')
footer(379); c.showPage()

# 380 - Quick reference giocatori 1
heading('Appendice B - Quick Reference Giocatori')
y=518
subheading('Tiro base',y); y-=13
rows=[['Totale','Esito'],['10+','Successo pieno'],['7–9','Successo con costo, scelta o efficacia ridotta'],['6−','Conseguenza; il Custode compie una Mossa']]
y=draw_table(LEFT,y,[70,261],rows,font_size=6.35); y-=14
subheading('Combattimento',y); y-=13
items=[
"Ogni round: un'Azione Principale + movimento coerente.",
"Difendere e Aiutare in combattimento consumano l'Azione Principale se ancora disponibile; Resistere no.",
"Un potere offensivo diretto usa Usare Potere; un'arma evocata già attiva usa Attaccare per i colpi successivi.",
"Escalation: round 3 +1 danno, round 4 +2, round 5+ +3; massimo una volta per Azione Principale.",
"Evocazioni: normalmente un'unità mantenuta; attaccare o usare una capacità significativa richiede la tua Azione Principale, salvo autonomia esplicita.",
]
y=bullet_list(y,items,size=6.45,leading=7.7,gap=3.5); y-=2
subheading('Danno',y); y-=12
rows=[['Tipo','Regola'],['Fisico','Armatura fisica o mistica'],['Magico','Solo Armatura mistica'],['Puro','Ignora Armatura'],['Penetrante X','Riduci Armatura di X prima del calcolo'],['Resistenza [tipo]','−2 danno dopo Armatura, minimo 1 salvo immunità']]
y=draw_table(LEFT,y,[95,236],rows,font_size=6.0); y-=8
y=text_block(LEFT,y,'Armatura non qualificata negli stat block = Armatura fisica. Modificatore totale, Caratteristica inclusa: da −3 a +4.',WIDTH,size=6.1,leading=7.35)
footer(380); c.showPage()

# 381 - Quick reference giocatori 2
heading('Risonanza',size=11.2)
y=529
items=[
"1/scena; dopo eventuale Fato e prima delle conseguenze.",
"Solo Usare Potere o Mossa Esclusiva di Casata con tiro.",
"6− diventa 7–9; 7–9 diventa 10+.",
"Il Custode offre due prezzi validi di categorie diverse. Se non può, la procedura non parte.",
"Se due prezzi validi sono stati dichiarati, l'uso è speso anche se rifiuti.",
"Accettare sostituisce la fascia originale: non applicare anche la conseguenza precedente.",
]
y=bullet_list(y,items,size=6.55,leading=7.8,gap=3.5); y-=2
rows=[['Prezzo','Effetto'],['Corpo',"Perdi 4 PF ignorando Armatura, dopo l'effetto migliorato"],['Anima','Condizione nuova o significativamente diversa'],['Legame','Conseguenza concreta su un Legame L1+ nominato'],['Mondo','Velo +1 e traccia concreta nella fiction']]
y=draw_table(LEFT,y,[80,251],rows,font_size=6.2); y-=14
subheading('Ultimo Respiro',y,size=9.8); y-=12
rows=[['Esito','Conseguenza'],['12+','1 PF, cosciente; agisci prima della fine del round'],['10–11','1 PF, incapacitato finché non ricevi cure o la scena cambia'],['7–9','1 PF, incapacitato come 10–11 + conseguenza duratura'],['6−','Muori, salvo Morte Eroica o altra regola esplicita']]
y=draw_table(LEFT,y,[75,256],rows,font_size=6.15)
footer(381); c.showPage()

# 382 - Quick Reference Custode
heading('Appendice C - Quick Reference Custode')
y=518
subheading('Procedura al tavolo',y); y-=13
items=[
"Chiedi obiettivo e metodo; se non c'è rischio interessante, non tirare.",
"Individua un solo trigger per la stessa incertezza.",
"Dichiara rischio e costo prima del tiro quando la procedura lo richiede.",
"Su 6− o conseguenza usa la fiction già stabilita: non generare una seconda attivazione completa di una minaccia che ha già speso il budget.",
"Gli indizi fondamentali non vengono negati da un singolo tiro.",
]
y=bullet_list(y,items,size=6.4,leading=7.6,gap=3.4); y-=3
subheading('Budget delle minacce',y); y-=13
y=text_block(LEFT,y,"Ogni avversario significativo o gruppo di minion gestito insieme ha normalmente una sola Azione Significativa per round. Può spenderla come conseguenza, quando una minaccia annunciata viene ignorata, oppure a fine round se ancora libera.",WIDTH,size=6.4,leading=7.6,gap=10)
subheading('Risonanza - prezzi validi',y); y-=13
items=[
"Corpo: valido finché il Guardiano è vivo e può perdere PF; può portare a Ultimo Respiro.",
"Anima: richiede un limite concreto e una via di risoluzione.",
"Legame: richiede un Legame L1+ nominato e realmente raggiungibile dalla conseguenza.",
"Mondo: richiede una traccia concreta; non è valido a Velo 12 salvo una procedura oltre la Rivelazione.",
"Offri due prezzi differenti e realmente applicabili.",
]
y=bullet_list(y,items,size=6.4,leading=7.6,gap=3.4)
footer(382); c.showPage()

# 383 - Quick Reference Custode Preparazione
heading('Quick Reference Custode - Preparazione')
y=518
subheading('Preparazione minima',y); y-=12
rows=[['Elemento','Domanda'],['Verità','Che cosa sta succedendo davvero?'],['Minaccia','Che cosa vuole e che cosa farà se nessuno interviene?'],['Indizi','Quali tre piste indipendenti conducono alla verità?'],['Pressione','Quale Clock o conseguenza rende urgente la situazione?'],['Scelte','Quali almeno due soluzioni sono realmente praticabili?'],['Ricaduta','Quale Legame, fazione o parte del Velo reagirà?']]
y=draw_table(LEFT,y,[95,236],rows,font_size=6.05); y-=14
subheading('Combattimento',y); y-=12
y=text_block(LEFT,y,'Definisci obiettivo, impulso della minaccia, via di fuga, terreno utile, budget di Azione Significativa e possibile cambio di fase. Non bilanciare soltanto sui PF.',WIDTH,size=6.35,leading=7.6,gap=6)
y=text_block(LEFT,y,"Evocazioni: normalmente una sola unità mantenuta per Guardiano. Un attacco o capacità significativa usa l'Azione Principale del Guardiano salvo autonomia esplicita; l'azione autonoma non riceve Escalation.",WIDTH,size=6.35,leading=7.6,gap=11)
subheading('Reputazione alta',y); y-=12
y=text_block(LEFT,y,'A +3/+5 la Reputazione cambia prima di tutto ciò che è possibile nella fiction. Non chiedere automaticamente Persuadere o Raggirare per privilegi già concessi dallo status; tira solo se resta un conflitto reale.',WIDTH,size=6.35,leading=7.6)
footer(383); c.showPage()

# 384 - FAQ, 2 colonne
heading('Appendice D - FAQ: soli casi limite')
COLW=158; X1=44; X2=218

def qa(x,y,q,a):
    qlines=wrap(q,'NS-B',7.15,COLW)
    y=draw_lines(x,y,qlines,'NS-B',7.15,8.25)-1.2
    alines=wrap(a,'NS',6.2,COLW)
    y=draw_lines(x,y,alines,'NS',6.2,7.25)-8.5
    return y

left_items=[
('Attaccare o Usare Potere?',"Un potere offensivo diretto usa Usare Potere. Un'arma evocata già attiva usa Attaccare per i colpi successivi. Non fare due tiri per la stessa incertezza."),
('Posso Difendere dopo avere già agito?',"No, salvo capacità che conceda una reazione. Difendere spende l'Azione Principale se ancora disponibile."),
("Resistere consuma l'azione?","No. Si attiva solo se l'effetto concede opposizione e non genera un'azione offensiva extra."),
('Come funzionano le evocazioni?',"Normalmente puoi mantenere un'unità evocata per Guardiano. Per attaccare o usare una capacità significativa spendi la tua Azione Principale, salvo autonomia esplicita."),
('I PF temporanei possono pagare costi o contare per Sangue Tenace?',"No. Assorbono danno ma non pagano costi, non aumentano i PF massimi e non modificano la soglia del 40%."),
('Confidente L2 o L3?',"Un Confidente L2+ che assiste Riprendersi concede lo speciale +1; sostituisce il normale bonus del Legame. Catarsi è L3."),
('Corruzione a 8?',"Risolvi il potere che ha raggiunto la soglia, poi avviene la trasformazione in PNG, salvo eccezione esplicita."),
]
right_items=[
('Ultimo Respiro 7–9?',"Torni a 1 PF, resti incapacitato come sul 10–11 e scegli una conseguenza duratura."),
('Rinuncia: si perde automaticamente la percezione magica?',"No. Conseguenze permanenti ulteriori devono essere concordate prima; Davide è un caso specifico."),
('Rifiutare Risonanza la conserva?',"Solo se il Custode non riesce a formulare due prezzi validi. Se i due prezzi sono stati dichiarati, l'uso della scena è speso anche se rifiuti."),
('Mondo usa una scala diversa dal Velo?',"No. Usa sempre il Velo Tracker."),
('Interrogare o Parlare con i Morti?',"Se i resti rendono già possibile il contatto, usa Interrogare senza pagare PF. Parlare apre il contatto quando altrimenti non sarebbe possibile. Mai due tiri per la stessa incertezza."),
('Armatura non qualificata?',"Negli stat block significa Armatura fisica salvo diversa specificazione."),
]
y1=510
for q,a in left_items: y1=qa(X1,y1,q,a)
y2=510
for q,a in right_items: y2=qa(X2,y2,q,a)
if min(y1,y2)<45:
    raise RuntimeError(f'FAQ overflow left={y1} right={y2}')
footer(384); c.showPage()

c.save()

# Replace pages 379-384 (1-based): indices 378..383.
src=fitz.open(SRC)
toc=src.get_toc(simple=False)
meta=src.metadata
rep=fitz.open(REPL)
for idx in range(383,377,-1):
    src.delete_page(idx)
src.insert_pdf(rep,start_at=378)
src.set_metadata(meta)
# Preserve original TOC. Add appendices/bookmark children if absent later in separate verification step.
try: src.set_toc(toc)
except Exception as e: print('TOC warning',e)
src.save(TMP,garbage=4,deflate=True,clean=True)
src.close(); rep.close()
os.replace(TMP,SRC)
with open(SRC,'rb') as f: print('SHA256',hashlib.sha256(f.read()).hexdigest())
print('SIZE',os.path.getsize(SRC))
