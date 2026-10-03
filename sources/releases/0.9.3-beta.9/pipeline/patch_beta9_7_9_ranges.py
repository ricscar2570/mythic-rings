import fitz, shutil, hashlib, os
SRC='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
BAK='/mnt/data/_beta9_before_7_9_normalization.pdf'
shutil.copy2(SRC,BAK)
doc=fitz.open(SRC)
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
patches=[]
for pi,page in enumerate(doc):
    words=page.get_text('words')
    targets=[]
    for w7 in words:
        if w7[4] != '7':
            continue
        candidates=[w for w in words if w[4].startswith('9') and abs(w[1]-w7[1])<1.6 and 0 < w[0]-w7[2] < 25]
        if not candidates:
            continue
        w9=min(candidates,key=lambda w:w[0])
        targets.append((w7,w9))
    if not targets:
        continue
    # font size / baseline from raw dict before redaction
    td=page.get_text('dict')
    specs=[]
    for w7,w9 in targets:
        cx=(w7[0]+w7[2])/2; cy=(w7[1]+w7[3])/2
        size=10.0; baseline=w7[3]-2.3
        for b in td.get('blocks',[]):
            for line in b.get('lines',[]):
                for s in line.get('spans',[]):
                    r=fitz.Rect(s['bbox'])
                    if r.contains(fitz.Point(cx,cy)):
                        size=s['size']; baseline=s['origin'][1]; break
        rect=fitz.Rect(w7[0],min(w7[1],w9[1]),w9[2],max(w7[3],w9[3]))
        suffix=w9[4][1:]
        specs.append((rect,w7[0],baseline,size,'7–9'+suffix))
        page.add_redact_annot(rect,fill=(1,1,1))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=fitz.PDF_REDACT_LINE_ART_NONE,text=fitz.PDF_REDACT_TEXT_REMOVE)
    page.insert_font(fontname='DVB7',fontfile=fontfile)
    for rect,x,baseline,size,text in specs:
        page.insert_text((x,baseline),text,fontsize=size,fontname='DVB7',color=(0.09,0.09,0.09),overlay=True)
        patches.append((pi+1,text,rect))

TMP='/mnt/data/_beta9_7_9_normalized.pdf'
doc.save(TMP,garbage=4,deflate=True,clean=True)
doc.close(); os.replace(TMP,SRC)
print('PATCHES',len(patches))
for p,t,r in patches: print(p,t,r)
with open(SRC,'rb') as f: print('SHA256',hashlib.sha256(f.read()).hexdigest())
