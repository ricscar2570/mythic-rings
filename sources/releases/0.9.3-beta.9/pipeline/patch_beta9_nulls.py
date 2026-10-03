import fitz, os, hashlib
P='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
d=fitz.open(P)
fixes={
157:[((45.0,388.4,365.0,400.0),'6−: una voce risponde, ma non è quella attesa o il contatto apre una via; il Custode compie una Mossa.',8.0)],
320:[((44.5,464.0,220.0,476.0),"- distruggono un'infrastruttura essenziale;",8.1),((44.5,470.4,220.0,482.0),'- convertono una cellula della Fratellanza;',8.1)],
351:[((44.5,158.0,260.0,170.0),'- Vincenzo viene sconfitto e il rituale viene stabilizzato;',8.1),((44.5,164.5,270.0,176.5),"- Vincenzo accetta un'alternativa e collabora alla riscrittura;",8.1)],
}
for pn,items in fixes.items():
    page=d[pn-1]
    for rect,text,fs in items:
        r=fitz.Rect(rect)
        page.add_redact_annot(r,fill=(1,1,1))
    page.apply_redactions()
    page.insert_font(fontname='DVSFix',fontfile=FONT)
    for rect,text,fs in items:
        r=fitz.Rect(rect)
        # baseline near original baseline
        page.insert_text((r.x0+0.5,r.y0+fs+1.2),text,fontname='DVSFix',fontsize=fs,color=(0,0,0),overlay=True)
# preserve toc/meta already in doc
tmp='/mnt/data/_beta9_nullfix_tmp.pdf'
d.save(tmp,garbage=4,deflate=True,clean=True)
d.close(); os.replace(tmp,P)
with open(P,'rb') as f: print(hashlib.sha256(f.read()).hexdigest())
