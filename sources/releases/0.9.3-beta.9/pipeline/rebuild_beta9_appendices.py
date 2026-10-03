from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, black
from reportlab.pdfbase.pdfmetrics import stringWidth
import fitz, os, hashlib

SRC='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
REPL='/mnt/data/_beta9_appendices_379_384.pdf'
TMP='/mnt/data/_beta9_appendices_replaced.pdf'
W,H=419.5276,595.2756

pdfmetrics.registerFont(TTFont('DVS','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('DVS-B','/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVSS','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVSS-B','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

c=canvas.Canvas(REPL,pagesize=(W,H))

LEFT=44; RIGHT=375

def footer(page):
    c.setFillColor(HexColor('#30343b'))
    c.setFont('DVS',5.6)
    c.drawString(LEFT,28,'MYTHIC RINGS | BLIND CLEAN CANDIDATE')
    c.setFont('DVS',7.2)
    c.drawCentredString(W/2,10,str(page))
    c.setFillColor(black)

def wrap(text,font,size,width):
    out=[]
    for para in str(text).split('\n'):
        words=para.split()
        if not words:
            out.append(''); continue
        cur=''
        for word in words:
            test=word if not cur else cur+' '+word
            if stringWidth(test,font,size)<=width:
                cur=test
            else:
                if cur: out.append(cur)
                cur=word
        if cur: out.append(cur)
    return out

def text_block(x,y,text,width,font='DVS',size=7.2,leading=8.8,gap=0):
    c.setFont(font,size)
    for ln in wrap(text,font,size,width):
        c.drawString(x,y,ln)
        y-=leading
    return y-gap

def heading(text,page,sub=False):
    c.setFont('DVS-B', 15.5 if not sub else 11.0)
    c.drawString(LEFT,548 if not sub else 515,text)

def draw_table(x,y,width,col_widths,rows,header=True,font_size=6.4,row_pad=3.3):
    # calculate row heights then draw
    heights=[]
    for r_i,row in enumerate(rows):
        f='DVSS-B' if header and r_i==0 else 'DVSS'
        sz=font_size
        maxlines=1
        for j,cell in enumerate(row):
            lines=wrap(cell,f,sz,col_widths[j]-2*row_pad)
            maxlines=max(maxlines,len(lines))
        heights.append(maxlines*(sz+1.7)+2*row_pad)
    cur=y
    totalw=sum(col_widths)
    for r_i,row in enumerate(rows):
        h=heights[r_i]
        if header and r_i==0:
            c.setFillColor(HexColor('#E5EDF3')); c.rect(x,cur-h,totalw,h,fill=1,stroke=0); c.setFillColor(black)
        # grid
        c.setStrokeColor(HexColor('#76879A')); c.setLineWidth(0.35)
        c.rect(x,cur-h,totalw,h,fill=0,stroke=1)
        xx=x
        for w in col_widths[:-1]:
            xx+=w; c.line(xx,cur-h,xx,cur)
        # cells
        xx=x
        f='DVSS-B' if header and r_i==0 else 'DVSS'
        sz=font_size
        c.setFont(f,sz)
        for j,cell in enumerate(row):
            lines=wrap(cell,f,sz,col_widths[j]-2*row_pad)
            ty=cur-row_pad-sz
            for ln in lines:
                c.drawString(xx+row_pad,ty,ln); ty-=sz+1.7
            xx+=col_widths[j]
        cur-=h
    return cur

# PAGE 379 - Glossary
heading('Appendice A - Glossario essenziale',379)
y=518
entries=[
("Ancora dell'Anello.","Legame L1+ designato alla creazione. Non concede bonus aggiuntivi; può sostituire un prezzo Anima della Risonanza con Legame una volta per sessione secondo la procedura completa."),
("Azione Principale.","Azione significativa disponibile a ogni Guardiano una volta per round. Attaccare, poteri, cure, Aiutare/Difendere in combattimento e comandi significativi alle evocazioni la consumano."),
("Armatura.","Riduce il danno pertinente; usa la migliore fonte, non la somma indiscriminata. Equipaggiamento max 3, totale ordinario max 4, boss max 2. Negli stat block, Armatura non qualificata significa Armatura fisica."),
("Casata.","Tradizione soprannaturale dell'Anello: Avalon, Umbra, Ife o Mictlan."),
("Condizione.","Ostacolo persistente con effetto fictionale/meccanico e via di rimozione dichiarata."),
("Corruzione.","Risorsa Umbra 0–8. A 6–7 aumenta i costi; a 8, dopo la risoluzione del potere che raggiunge la soglia, avviene la trasformazione salvo eccezione esplicita."),
("Custode.","Partecipante che presenta il mondo, interpreta PNG e minacce e applica le Mosse senza tirare dadi."),
("Danno puro.","Danno che ignora Armatura."),
("Doom Clock.","Tracciato dell'avanzamento di una minaccia o crisi."),
("Escalation.","Bonus al danno dei Guardiani negli scontri lunghi: +1 al round 3, +2 al round 4, +3 dal round 5; una sola volta per Azione Principale."),
("Fato.","Risorsa personale: 2 per sessione, max 2; 1 punto ritira un solo d6 dopo il tiro e prima delle conseguenze."),
("Legame.","Relazione significativa con Tipo e Livello 0–3. Bonus +1 a L1, +2 a L2–L3 quando persona e Tipo sono direttamente pertinenti."),
("LS.","Livello di Sfida: indicatore orientativo della pressione prodotta da una minaccia."),
("Mossa.","Procedura attivata da un trigger nella fiction."),
("PF temporanei.","Riserva separata che assorbe danno prima dei PF reali; non paga costi, non aumenta PF massimi, non modifica soglie e non si somma."),
("Rinuncia.","Procedura volontaria e consensuale che spezza il legame operativo con l'Anello; ulteriori conseguenze permanenti devono essere concordate prima."),
("Risonanza.","Una volta per scena può migliorare 6− in 7–9 o 7–9 in 10+ su Usare Potere o Mossa Esclusiva con tiro, pagando un prezzo Corpo/Anima/Legame/Mondo."),
("Sangue Tenace.","Passivo Mictlan 1/scena che può convertire parte di un costo in PF in Stress quando il pagamento porterebbe sotto il 40% dei PF massimi, secondo i limiti del potere."),
("Stress.","Risorsa 0–10; a 8–9 aumenta i costi in Stress, a 10 il sovraccarico produce Burnout."),
("Ultimo Respiro.","Tiro 2d6 senza bonus a 0 PF."),
("Velo Tracker.","Scala globale 0–12 della persistenza delle prove pubbliche del soprannaturale."),
]
c.setFont('DVS',7.0)
for term,desc in entries:
    full=term+' '+desc
    lines=wrap(full,'DVS',7.0,331)
    # make term bold manually first line if possible by drawing term then remainder
    # easiest: first line regular to preserve compactness; heading-like term still explicit via punctuation
    for ln in lines:
        c.drawString(LEFT,y,ln); y-=8.2
    y-=2.0
footer(379); c.showPage()

# PAGE 380 - Player quick ref 1
heading('Appendice B - Quick Reference Giocatori',380)
y=518
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Tiro base'); y-=12
rows=[['Totale','Esito'],['10+','Successo pieno'],['7–9','Successo con costo, scelta o efficacia ridotta'],['6−','Conseguenza; il Custode compie una Mossa']]
y=draw_table(LEFT,y,331,[70,261],rows,font_size=6.6); y-=15
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Combattimento'); y-=13
bullets=[
"Ogni round: un'Azione Principale + movimento coerente.",
"Difendere e Aiutare in combattimento consumano l'Azione Principale se ancora disponibile; Resistere no.",
"Un potere offensivo diretto usa Usare Potere; un'arma evocata già attiva usa Attaccare per i colpi successivi.",
"Escalation: round 3 +1 danno, round 4 +2, round 5+ +3; massimo una volta per Azione Principale.",
"Evocazioni: normalmente un'unità mantenuta; attaccare o usare una capacità significativa richiede la tua Azione Principale, salvo autonomia esplicita.",
]
for b in bullets:
    y=text_block(LEFT,y,'- '+b,331,size=6.6,leading=8.0,gap=4)
y-=4
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Danno'); y-=12
rows=[['Tipo','Regola'],['Fisico','Armatura fisica o mistica'],['Magico','Solo Armatura mistica'],['Puro','Ignora Armatura'],['Penetrante X','Riduci Armatura di X prima del calcolo'],['Resistenza [tipo]','-2 danno dopo Armatura, minimo 1 salvo immunità']]
y=draw_table(LEFT,y,331,[95,236],rows,font_size=6.2); y-=8
y=text_block(LEFT,y,'Armatura non qualificata negli stat block = Armatura fisica. Modificatore totale, Caratteristica inclusa: da -3 a +4.',331,size=6.3,leading=7.7)
footer(380); c.showPage()

# PAGE 381 - Player quick ref 2
c.setFont('DVS-B',11.0); c.drawString(LEFT,548,'Risonanza')
y=529
bullets=[
"1/scena; dopo eventuale Fato e prima delle conseguenze.",
"Solo Usare Potere o Mossa Esclusiva di Casata con tiro.",
"6− diventa 7–9; 7–9 diventa 10+.",
"Il Custode offre due prezzi validi di categorie diverse. Se non può, la procedura non parte.",
"Se due prezzi validi sono stati dichiarati, l'uso è speso anche se rifiuti.",
"Accettare sostituisce la fascia originale: non applicare anche la conseguenza precedente.",
]
for b in bullets:
    y=text_block(LEFT,y,'- '+b,331,size=6.7,leading=8.0,gap=4)
y-=2
rows=[['Prezzo','Effetto'],['Corpo',"Perdi 4 PF ignorando Armatura, dopo l'effetto migliorato"],['Anima','Condizione nuova o significativamente diversa'],['Legame','Conseguenza concreta su un Legame L1+ nominato'],['Mondo','Velo +1 e traccia concreta nella fiction']]
y=draw_table(LEFT,y,331,[80,251],rows,font_size=6.4); y-=15
c.setFont('DVS-B',10.0); c.drawString(LEFT,y,'Ultimo Respiro'); y-=12
rows=[['Esito','Conseguenza'],['12+','1 PF, cosciente; agisci prima della fine del round'],['10–11','1 PF, incapacitato finché non ricevi cure o la scena cambia'],['7–9','1 PF, incapacitato come 10–11 + conseguenza duratura'],['6−','Muori, salvo Morte Eroica o altra regola esplicita']]
y=draw_table(LEFT,y,331,[75,256],rows,font_size=6.3)
footer(381); c.showPage()

# PAGE 382 - GM quick ref
heading('Appendice C - Quick Reference Custode',382)
y=518
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Procedura al tavolo'); y-=13
bullets=[
"Chiedi obiettivo e metodo; se non c'è rischio interessante, non tirare.",
"Individua un solo trigger per la stessa incertezza.",
"Dichiara rischio e costo prima del tiro quando la procedura lo richiede.",
"Su 6− o conseguenza usa la fiction già stabilita: non generare una seconda attivazione completa di una minaccia che ha già speso il budget.",
"Gli indizi fondamentali non vengono negati da un singolo tiro.",
]
for b in bullets: y=text_block(LEFT,y,'- '+b,331,size=6.6,leading=8.0,gap=4)
y-=4
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Budget delle minacce'); y-=13
y=text_block(LEFT,y,"Ogni avversario significativo o gruppo di minion gestito insieme ha normalmente una sola Azione Significativa per round. Può spenderla come conseguenza, quando una minaccia annunciata viene ignorata, oppure a fine round se ancora libera.",331,size=6.6,leading=8.0,gap=10)
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Risonanza - prezzi validi'); y-=13
bullets=[
"Corpo: valido finché il Guardiano è vivo e può perdere PF; può portare a Ultimo Respiro.",
"Anima: richiede un limite concreto e una via di risoluzione.",
"Legame: richiede un Legame L1+ nominato e realmente raggiungibile dalla conseguenza.",
"Mondo: richiede una traccia concreta; non è valido a Velo 12 salvo una procedura oltre la Rivelazione.",
"Offri due prezzi differenti e realmente applicabili.",
]
for b in bullets: y=text_block(LEFT,y,'- '+b,331,size=6.6,leading=8.0,gap=4)
footer(382); c.showPage()

# PAGE 383 - GM prep
c.setFont('DVS-B',15.5); c.drawString(LEFT,548,'Quick Reference Custode - Preparazione')
y=518
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Preparazione minima'); y-=12
rows=[['Elemento','Domanda'],['Verità','Che cosa sta succedendo davvero?'],['Minaccia','Che cosa vuole e che cosa farà se nessuno interviene?'],['Indizi','Quali tre piste indipendenti conducono alla verità?'],['Pressione','Quale Clock o conseguenza rende urgente la situazione?'],['Scelte','Quali almeno due soluzioni sono realmente praticabili?'],['Ricaduta','Quale Legame, fazione o parte del Velo reagirà?']]
y=draw_table(LEFT,y,331,[95,236],rows,font_size=6.2); y-=15
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Combattimento'); y-=12
y=text_block(LEFT,y,'Definisci obiettivo, impulso della minaccia, via di fuga, terreno utile, budget di Azione Significativa e possibile cambio di fase. Non bilanciare soltanto sui PF.',331,size=6.5,leading=7.9,gap=7)
y=text_block(LEFT,y,"Evocazioni: normalmente una sola unità mantenuta per Guardiano. Un attacco o capacità significativa usa l'Azione Principale del Guardiano salvo autonomia esplicita; l'azione autonoma non riceve Escalation.",331,size=6.5,leading=7.9,gap=12)
c.setFont('DVS-B',9.5); c.drawString(LEFT,y,'Reputazione alta'); y-=12
y=text_block(LEFT,y,'A +3/+5 la Reputazione cambia prima di tutto ciò che è possibile nella fiction. Non chiedere automaticamente Persuadere o Raggirare per privilegi già concessi dallo status; tira solo se resta un conflitto reale.',331,size=6.5,leading=7.9)
footer(383); c.showPage()

# PAGE 384 - FAQ two columns
heading('Appendice D - FAQ: soli casi limite',384)
COLW=158; X1=44; X2=218

def qa(x,y,q,a):
    c.setFont('DVS-B',7.7)
    for ln in wrap(q,'DVS-B',7.7,COLW): c.drawString(x,y,ln); y-=9.0
    y-=1.5
    c.setFont('DVS',6.6)
    for ln in wrap(a,'DVS',6.6,COLW): c.drawString(x,y,ln); y-=7.7
    return y-10
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
footer(384); c.showPage()

c.save()

# Replace pages 379-384 (1-based), i.e. indices 378..383
src=fitz.open(SRC)
toc=src.get_toc(simple=False)
meta=src.metadata
rep=fitz.open(REPL)
for idx in range(383,377,-1):
    src.delete_page(idx)
src.insert_pdf(rep, start_at=378)
src.set_metadata(meta)
try:
    src.set_toc(toc)
except Exception as e:
    print('TOC reset warning',e)
src.save(TMP,garbage=4,deflate=True,clean=True)
src.close(); rep.close()
os.replace(TMP,SRC)
with open(SRC,'rb') as f: print('SHA256',hashlib.sha256(f.read()).hexdigest())
print('SIZE',os.path.getsize(SRC))
