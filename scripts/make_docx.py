"""Build docs/working-paper.docx from docs/working-paper.md.

Usage: python scripts/make_docx.py [paper.md] [out.docx]   (defaults: docs/working-paper.md, docs/working-paper.docx)
Needs pandoc and python-docx. Pandoc converts the markdown (figures embedded, alt text kept); the script then sets
Times New Roman, US Letter, 1-inch margins, the DRAFT//PRE-DECISIONAL header and footer with page numbers,
column-width figures, and plain tables. The paper's own marking lines are dropped because the header and footer carry it.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor


def postprocess(src, dst):
    d=Document(src)
    class _S:
        def __init__(s,d): s.m={x.name.lower():x for x in d.styles}
        def __getitem__(s,k): return s.m[k.lower()]
    ST=_S(d)
    FONT="Times New Roman"
    def setfont(st,size=None,bold=None,color=None):
        st.font.name=FONT
        rpr=st.element.get_or_add_rPr(); rf=rpr.find(qn('w:rFonts'))
        if rf is None: rf=OxmlElement('w:rFonts'); rpr.append(rf)
        for a in ('w:ascii','w:hAnsi','w:cs','w:eastAsia'): rf.set(qn(a),FONT)
        for a in ('w:asciiTheme','w:hAnsiTheme','w:cstheme','w:eastAsiaTheme'):
            if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
        if size: st.font.size=Pt(size)
        if bold is not None: st.font.bold=bold
        if color is not None: st.font.color.rgb=color
    navy=RGBColor(0x0B,0x2A,0x5B)
    for st in d.styles:
        if st.type in (1,2):
            try: setfont(st)
            except Exception: pass
    for n,s in (('Title',20),('Heading 1',15),('Heading 2',12.5),('Heading 3',11.5)):
        setfont(ST[n],s,True,navy)
    for n in ('Normal','Body Text','First Paragraph','Compact','Block Text'):
        if n.lower() in ST.m:
            setfont(ST[n],11)
            ST[n].paragraph_format.space_after=Pt(6)
    for n in ('Image Caption','Captioned Figure'):
        if n.lower() in ST.m: setfont(ST[n],9.5)
    sec=d.sections[0]
    sec.page_width=Inches(8.5); sec.page_height=Inches(11)
    for m in ('left_margin','right_margin'): setattr(sec,m,Inches(1))
    sec.top_margin=sec.bottom_margin=Inches(1)
    def mark(par):
        par.alignment=WD_ALIGN_PARAGRAPH.CENTER
        r=par.add_run("DRAFT//PRE-DECISIONAL"); r.bold=True; r.font.size=Pt(11); r.font.name=FONT; r.font.color.rgb=navy
    sec.header.is_linked_to_previous=False
    mark(sec.header.paragraphs[0])
    fp=sec.footer.paragraphs[0]; mark(fp)
    p2=sec.footer.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p2.add_run("Page "); r.font.size=Pt(10); r.font.name=FONT
    r=p2.add_run()
    for t,txt in (('begin',None),(None,' PAGE '),('end',None)):
        if t:
            e=OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'),t)
        else:
            e=OxmlElement('w:instrText'); e.set(qn('xml:space'),'preserve'); e.text=txt
        r._r.append(e)
    r.font.size=Pt(10); r.font.name=FONT
    # images: fit column width
    maxw=Inches(6.5)
    for s in d.inline_shapes:
        if s.width>maxw:
            ratio=maxw/s.width; s.width=maxw; s.height=int(s.height*ratio)
    # tables
    for t in d.tables:
        t.style=t.style
        tblPr=t._tbl.tblPr
        b=OxmlElement('w:tblBorders')
        for e in ('top','bottom','insideH'):
            x=OxmlElement(f'w:{e}'); x.set(qn('w:val'),'single'); x.set(qn('w:sz'),'4'); x.set(qn('w:color'),'8A8D91'); b.append(x)
        tblPr.append(b)
        for i,row in enumerate(t.rows):
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_after=Pt(2)
                    for r in p.runs:
                        r.font.size=Pt(9.5); r.font.name=FONT
                        if i==0: r.bold=True
                if i==0:
                    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
                    sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),'E6EBF5'); tcPr.append(sh)
    for p in d.paragraphs:
        if p.text.startswith('Figure ') and p.runs and p.runs[0].bold: p.paragraph_format.keep_with_next=True
    d.core_properties.title="Estimating Auction Revenue for 20 Megahertz at 1675–1695 MHz"
    d.core_properties.author="Nick (with AI assistance)"
    d.save(dst)



def main():
    md = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/working-paper.md")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/working-paper.docx")
    lines = md.read_text(encoding="utf-8").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    body = "\n".join(lines[2:-1])                     # drop the marking line, blank line, and closing marking line
    with tempfile.TemporaryDirectory() as td:
        src, raw = Path(td) / "paper.md", Path(td) / "raw.docx"
        src.write_text(body, encoding="utf-8")
        subprocess.run(["pandoc", str(src), "-f", "markdown-implicit_figures", "-t", "docx",
                        f"--resource-path={md.parent}", "-o", str(raw)], check=True)
        postprocess(str(raw), str(out))
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
