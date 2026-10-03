import fitz,os,hashlib
P='/mnt/data/Mythic_Rings_Manuale_Completo_0.9.3-beta.9_BLIND-CLEAN-CANDIDATE.pdf'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
d=fitz.open(P)
fixes={
157:(fitz.Rect(44.5,386.5,372.5,416.0),"6−: una voce risponde, ma non è quella attesa o il contatto apre una via;\nil Custode compie una Mossa.",7.4),
320:(fitz.Rect(44.0,454.5,373.0,496.0),"Riduci di 1, fino a un minimo coerente con gli eventi già\navvenuti, quando i Guardiani:\n- distruggono un'infrastruttura essenziale;\n- convertono una cellula della Fratellanza;",7.5),
351:(fitz.Rect(44.0,154.0,374.0,276.0),"- Vincenzo viene sconfitto e il rituale viene stabilizzato;\n- Vincenzo accetta un'alternativa e collabora alla riscrittura;\n- i Guardiani assumono il controllo dei pilastri;\n- lo Specchio collassa e il gruppo decide che cosa salvare;\n- una fazione terza prende il Nexus, conseguenza di alleanze fallite.",7.5),
}
for pn,(rect,text,fs) in fixes.items():
    page=d[pn-1]
    page.add_redact_annot(rect,fill=(1,1,1))
    page.apply_redactions()
    page.insert_font(fontname='DVSBlock',fontfile=FONT)
    rc=page.insert_textbox(rect,text,fontname='DVSBlock',fontsize=fs,color=(0,0,0),lineheight=1.12,align=0,overlay=True)
    print(pn,'textbox rc',rc)
tmp='/mnt/data/_beta9_blockfix_tmp.pdf'
d.save(tmp,garbage=4,deflate=True,clean=True)
d.close();os.replace(tmp,P)
with open(P,'rb') as f: print('SHA',hashlib.sha256(f.read()).hexdigest())
