"""Mise en page commune des documents EburSeal (ReportLab)."""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, Image, NextPageTemplate, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.utils import ImageReader

F = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("D", "DejaVuSans.ttf"), ("DB", "DejaVuSans-Bold.ttf"),
             ("DI", "DejaVuSans-Oblique.ttf"), ("DBI", "DejaVuSans-BoldOblique.ttf"),
             ("M", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, F + f))
registerFontFamily("D", normal="D", bold="DB", italic="DI", boldItalic="DBI")

NAVY = colors.HexColor("#14325C")
ACC = colors.HexColor("#2C7DA0")
DARK = colors.HexColor("#222222")
LIGHT = colors.HexColor("#EEF4F9")
ALT = colors.HexColor("#F5F6F8")
NOTE = colors.HexColor("#FFF6DA"); NOTEB = colors.HexColor("#D9A400")
OK = colors.HexColor("#E7F4EA"); OKB = colors.HexColor("#2E8B57")
GRID = colors.HexColor("#C5CDD6")
W = 17.4  # largeur utile en cm

S = {
    "h1": ParagraphStyle("h1", fontName="DB", fontSize=15, leading=19, textColor=NAVY, spaceBefore=4, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DB", fontSize=12, leading=15, textColor=ACC, spaceBefore=9, spaceAfter=4),
    "h3": ParagraphStyle("h3", fontName="DB", fontSize=10, leading=13, textColor=DARK, spaceBefore=6, spaceAfter=3),
    "b": ParagraphStyle("b", fontName="D", fontSize=9.3, leading=12.8, textColor=DARK, spaceAfter=4, alignment=TA_JUSTIFY),
    "li": ParagraphStyle("li", fontName="D", fontSize=9.3, leading=12.6, textColor=DARK, leftIndent=13,
                         bulletIndent=3, spaceAfter=2, alignment=TA_JUSTIFY),
    "c": ParagraphStyle("c", fontName="D", fontSize=7.9, leading=10, textColor=DARK),
    "cs": ParagraphStyle("cs", fontName="D", fontSize=7.3, leading=9.2, textColor=DARK),
    "ch": ParagraphStyle("ch", fontName="DB", fontSize=8, leading=10, textColor=colors.white),
    "cb": ParagraphStyle("cb", fontName="DB", fontSize=7.9, leading=10, textColor=DARK),
    "note": ParagraphStyle("n", fontName="D", fontSize=9, leading=12, textColor=DARK),
    "cap": ParagraphStyle("cap", fontName="DI", fontSize=8, leading=10, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=6),
    "code": ParagraphStyle("code", fontName="M", fontSize=7.8, leading=10, textColor=DARK),
}


class Doc:
    def __init__(self, path, title, subtitle, version, kind):
        self.story, self.pend = [], []
        self.title, self.subtitle, self.version, self.kind = title, subtitle, version, kind
        self.doc = BaseDocTemplate(path, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                                   topMargin=1.8 * cm, bottomMargin=1.7 * cm, title=f"EburSeal — {title}",
                                   author="OUATTARA Yacouba, YEO Tanna Daouda")
        fr = Frame(self.doc.leftMargin, self.doc.bottomMargin, self.doc.width, self.doc.height, id="f")
        self.doc.addPageTemplates([PageTemplate(id="cover", frames=[fr], onPage=self._cover_bg),
                                   PageTemplate(id="body", frames=[fr], onPage=self._page)])
        self.doc.afterFlowable = self._after
        self.h1n = 0; self.h2n = 0; self.h1_break = True

    # --- en-têtes / pieds
    def _page(self, c, d):
        c.saveState()
        c.setStrokeColor(NAVY); c.setLineWidth(1)
        c.line(1.8 * cm, A4[1] - 1.25 * cm, A4[0] - 1.8 * cm, A4[1] - 1.25 * cm)
        c.setFont("DB", 7.5); c.setFillColor(NAVY)
        c.drawString(1.8 * cm, A4[1] - 1.1 * cm, "EburSeal")
        c.setFont("D", 7.5); c.setFillColor(colors.grey)
        c.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.1 * cm, f"{self.title} — v{self.version}")
        c.drawString(1.8 * cm, 1.0 * cm, "SUP'COM · CySeD · Sécurité Applicative — Atelier 2026-2027")
        c.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, f"Page {d.page}")
        c.restoreState()

    def _cover_bg(self, c, d):
        c.saveState()
        c.setFillColor(NAVY); c.rect(0, A4[1] - 9.5 * cm, A4[0], 9.5 * cm, fill=1, stroke=0)
        c.setFillColor(ACC); c.rect(0, A4[1] - 9.8 * cm, A4[0], 0.3 * cm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("DB", 30); c.drawString(2 * cm, A4[1] - 3.6 * cm, "EburSeal")
        c.setFont("D", 11.5)
        c.drawString(2 * cm, A4[1] - 4.5 * cm, "Le sceau invisible des diplômes ivoiriens")
        c.setFont("DB", 19); c.drawString(2 * cm, A4[1] - 6.6 * cm, self.title)
        c.setFont("D", 11); c.drawString(2 * cm, A4[1] - 7.5 * cm, self.subtitle)
        c.restoreState()

    def _after(self, fl):
        if isinstance(fl, Paragraph) and hasattr(fl, "_toc"):
            lvl, txt, key = fl._toc
            self.doc.canv.bookmarkPage(key)
            self.doc.canv.addOutlineEntry(txt, key, level=lvl, closed=lvl > 0)
            self.doc.notify("TOCEntry", (lvl, txt, self.doc.page, key))

    # --- primitives
    def flush(self):
        self.story.extend(self.pend); self.pend = []

    def P(self, t, s="b"):
        (self.pend if self.pend else self.story).append(Paragraph(t, S[s]))

    def H1(self, t, newpage=None):
        self.flush()
        if newpage is None: newpage = self.h1_break
        if newpage: self.story.append(PageBreak())
        self.h1n += 1; self.h2n = 0
        txt = f"{self.h1n}. {t}"
        p = Paragraph(txt, S["h1"]); p._toc = (0, txt, f"h{self.h1n}")
        self.pend.append(p)

    def H2(self, t):
        self.flush()
        self.h2n += 1
        txt = f"{self.h1n}.{self.h2n} {t}"
        p = Paragraph(txt, S["h2"]); p._toc = (1, txt, f"h{self.h1n}_{self.h2n}")
        self.pend.append(p)

    def H3(self, t):
        self.flush(); self.pend.append(Paragraph(t, S["h3"]))

    def L(self, items, style="li"):
        ps = [Paragraph(it, S[style], bulletText="•") for it in items]
        if self.pend:
            self.story.append(KeepTogether(self.pend + ps[:1])); self.pend = []; ps = ps[1:]
        self.story.extend(ps)

    def box(self, t, title="À retenir", kind="note"):
        bg, bd = (NOTE, NOTEB) if kind == "note" else (OK, OKB) if kind == "ok" else (LIGHT, ACC)
        p = Paragraph(f"<b>{title}</b> — {t}" if title else t, S["note"])
        tb = Table([[p]], colWidths=[W * cm])
        tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, bd),
                                ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        self.story.append(KeepTogether(self.pend + [Spacer(1, 2), tb, Spacer(1, 5)])); self.pend = []

    def table(self, rows, widths, first_bold=True, keep=True, small=False, header=True, spans=None):
        cst = S["cs"] if small else S["c"]
        data = []
        for i, r in enumerate(rows):
            row = []
            for j, cell in enumerate(r):
                if isinstance(cell, (Paragraph, Image)):
                    row.append(cell); continue
                st = S["ch"] if (header and i == 0) else (S["cb"] if first_bold and j == 0 else cst)
                row.append(Paragraph(str(cell), st))
            data.append(row)
        t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
        st = [("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6)]
        if header: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
        for i in range(1 if header else 0, len(rows)):
            st.append(("BACKGROUND", (0, i), (-1, i), LIGHT if i % 2 else colors.white))
        if first_bold: st.append(("BACKGROUND", (0, 1 if header else 0), (0, -1), ALT))
        for sp in (spans or []): st.append(sp)
        t.setStyle(TableStyle(st))
        if keep: self.story.append(KeepTogether(self.pend + [t, Spacer(1, 6)]))
        else:
            self.story.append(CondPageBreak(6 * cm)); self.story.extend(self.pend); self.story.append(t); self.story.append(Spacer(1, 6))
        self.pend = []

    def kv(self, pairs, w1=4.2):
        """Fiche clé/valeur (2 colonnes, sans en-tête)."""
        self.table([[f"<b>{k}</b>", v] for k, v in pairs], [w1, W - w1], first_bold=True, header=False)

    def img(self, path, width_cm, caption=None):
        ir = ImageReader(path); iw, ih = ir.getSize()
        im = Image(path, width=width_cm * cm, height=width_cm * cm * ih / iw)
        items = [im] + ([Paragraph(caption, S["cap"])] if caption else [])
        self.story.append(KeepTogether(self.pend + items)); self.pend = []

    def sp(self, h=6):
        self.flush(); self.story.append(Spacer(1, h))

    # --- page de garde + sommaire
    def cover(self, rows, history):
        self.story.append(Spacer(1, 8.6 * cm))
        t = Table([[Paragraph(f"<b>{k}</b>", S["c"]), Paragraph(v, S["c"])] for k, v in rows],
                  colWidths=[4.5 * cm, 12.9 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, GRID), ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        self.story.append(t); self.story.append(Spacer(1, 14))
        self.story.append(Paragraph("Historique des versions", S["h3"]))
        self.table([["Version", "Date", "Auteur(s)", "Modifications"]] + history, [1.8, 2.4, 4.4, 8.8])
        self.flush()
        self.story.append(NextPageTemplate("body"))
        self.story.append(PageBreak())
        self.story.append(Paragraph("Sommaire", S["h1"]))
        toc = TableOfContents()
        toc.levelStyles = [ParagraphStyle("t0", fontName="DB", fontSize=9.5, leading=13, leftIndent=0, textColor=NAVY),
                           ParagraphStyle("t1", fontName="D", fontSize=8.8, leading=11.5, leftIndent=14)]
        self.story.append(toc)

    def build(self):
        self.flush()
        self.doc.multiBuild(self.story)
