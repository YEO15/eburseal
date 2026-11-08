"""Mise en page commune des documents EburSeal (ReportLab).

Style aligné sur le modèle de rapport d'atelier SUP'COM : page de garde officielle
(armoiries + logo), cadre de page, police Times (Liberation Serif, métriquement
identique à Times New Roman) en 12 pt, titres noirs, tableaux à en-tête gris.
"""
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, Image, NextPageTemplate, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.utils import ImageReader

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
ASSETS = HERE / "assets"

# --- Polices : Liberation Serif (= Times New Roman) ; DejaVu pour les symboles ✔ ✘ et le code
for n, f in [("D", "LiberationSerif-Regular.ttf"), ("DB", "LiberationSerif-Bold.ttf"),
             ("DI", "LiberationSerif-Italic.ttf"), ("DBI", "LiberationSerif-BoldItalic.ttf"),
             ("SYM", "DejaVuSans.ttf"), ("M", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, str(FONTS / f)))
registerFontFamily("D", normal="D", bold="DB", italic="DI", boldItalic="DBI")

# --- Palette sobre (noir / gris), seul le titre de garde reprend le bleu du modèle
BLACK = colors.black
DARK = colors.HexColor("#1A1A1A")
GREY = colors.HexColor("#595959")
HEAD = colors.HexColor("#D9D9D9")     # en-tête de tableau
ALT = colors.HexColor("#F2F2F2")      # 1re colonne / encadrés
GRID = colors.HexColor("#808080")
FRAME = colors.HexColor("#1F2A44")    # cadre de page (modèle)
TITLE = colors.HexColor("#1F4E79")    # titre de la page de garde (modèle)
W = 17.4  # largeur utile en cm

BODY = 12
S = {
    "h1": ParagraphStyle("h1", fontName="DB", fontSize=16, leading=20, textColor=BLACK, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DB", fontSize=13.5, leading=17, textColor=BLACK, spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName="DB", fontSize=12, leading=15, textColor=BLACK, spaceBefore=7, spaceAfter=3),
    "b": ParagraphStyle("b", fontName="D", fontSize=BODY, leading=15.5, textColor=DARK, spaceAfter=5, alignment=TA_JUSTIFY),
    "li": ParagraphStyle("li", fontName="D", fontSize=BODY, leading=15, textColor=DARK, leftIndent=16,
                         bulletIndent=4, spaceAfter=2.5, alignment=TA_JUSTIFY),
    "c": ParagraphStyle("c", fontName="D", fontSize=10, leading=12.2, textColor=DARK),
    "cs": ParagraphStyle("cs", fontName="D", fontSize=9.3, leading=11.2, textColor=DARK),
    "ch": ParagraphStyle("ch", fontName="DB", fontSize=10, leading=12.2, textColor=BLACK),
    "cb": ParagraphStyle("cb", fontName="DB", fontSize=10, leading=12.2, textColor=DARK),
    "note": ParagraphStyle("n", fontName="D", fontSize=11.5, leading=14.5, textColor=DARK, alignment=TA_JUSTIFY),
    "cap": ParagraphStyle("cap", fontName="DBI", fontSize=10, leading=12, textColor=DARK, alignment=TA_CENTER,
                          spaceBefore=3, spaceAfter=8),
    "code": ParagraphStyle("code", fontName="M", fontSize=9, leading=11, textColor=DARK),
    # page de garde
    "gc": ParagraphStyle("gc", fontName="D", fontSize=10, leading=12.5, textColor=BLACK, alignment=TA_CENTER),
    "gl": ParagraphStyle("gl", fontName="D", fontSize=10, leading=12.5, textColor=BLACK, alignment=TA_LEFT),
    "gr": ParagraphStyle("gr", fontName="D", fontSize=10, leading=12.5, textColor=BLACK, alignment=2),
    "gkind": ParagraphStyle("gk", fontName="DB", fontSize=24, leading=29, textColor=TITLE, alignment=TA_CENTER),
    "gbox": ParagraphStyle("gb", fontName="DB", fontSize=16, leading=20, textColor=BLACK, alignment=TA_CENTER),
    "gsub": ParagraphStyle("gs", fontName="DI", fontSize=12.5, leading=16, textColor=BLACK, alignment=TA_CENTER),
    "ginfo": ParagraphStyle("gi", fontName="D", fontSize=12, leading=18, textColor=BLACK, alignment=TA_CENTER),
    "gh": ParagraphStyle("gh", fontName="DB", fontSize=13.5, leading=17, textColor=BLACK),
    "gn": ParagraphStyle("gn", fontName="DB", fontSize=12, leading=16, textColor=BLACK),
}


def fx(t):
    """Bascule les symboles absents de la police Times vers DejaVu."""
    t = str(t)
    for ch in ("✔", "✘"):
        t = t.replace(ch, f'<font name="SYM">{ch}</font>')
    return t


class Doc:
    def __init__(self, path, title, subtitle, version, kind):
        self.story, self.pend = [], []
        self.title, self.subtitle, self.version, self.kind = title, subtitle, version, kind
        self.doc = BaseDocTemplate(path, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                                   topMargin=2.0 * cm, bottomMargin=2.0 * cm, title=f"EburSeal — {title}",
                                   author="OUATTARA Yacouba, YEO Tanna Daouda")
        fr = Frame(self.doc.leftMargin, self.doc.bottomMargin, self.doc.width, self.doc.height, id="f")
        self.doc.addPageTemplates([PageTemplate(id="cover", frames=[fr], onPage=self._cover_bg),
                                   PageTemplate(id="body", frames=[fr], onPage=self._page)])
        self.doc.afterFlowable = self._after
        self.h1n = 0; self.h2n = 0; self.h1_break = True

    # --- cadre, en-têtes, pieds de page
    def _frame(self, c):
        c.setStrokeColor(FRAME); c.setLineWidth(2.2)
        c.rect(1.0 * cm, 1.0 * cm, A4[0] - 2.0 * cm, A4[1] - 2.0 * cm, stroke=1, fill=0)

    def _page(self, c, d):
        c.saveState()
        self._frame(c)
        c.setFont("D", 8.5); c.setFillColor(GREY)
        c.drawRightString(A4[0] - 1.6 * cm, A4[1] - 1.5 * cm, f"EburSeal — {self.title} — v{self.version}")
        c.drawCentredString(A4[0] / 2, 1.35 * cm,
                            f"SUP'COM — INDP3 CySeD — Sécurité Applicative — page {d.page}")
        c.restoreState()

    def _cover_bg(self, c, d):
        c.saveState(); self._frame(c); c.restoreState()

    def _after(self, fl):
        if isinstance(fl, Paragraph) and hasattr(fl, "_toc"):
            lvl, txt, key = fl._toc
            self.doc.canv.bookmarkPage(key)
            self.doc.canv.addOutlineEntry(txt, key, level=lvl, closed=lvl > 0)
            self.doc.notify("TOCEntry", (lvl, txt, self.doc.page, key))

    # --- primitives
    def flush(self):
        self.story.extend(self.pend); self.pend = []

    def _flush_unless_headings(self):
        """Garde un titre attaché au titre suivant (pas de titre orphelin en bas de page)."""
        if not all(getattr(p, "_heading", False) for p in self.pend):
            self.flush()

    def P(self, t, s="b"):
        (self.pend if self.pend else self.story).append(Paragraph(fx(t), S[s]))

    def H1(self, t, newpage=None):
        self.flush()
        if newpage is None: newpage = self.h1_break
        if newpage: self.story.append(PageBreak())
        self.h1n += 1; self.h2n = 0
        txt = f"{self.h1n}. {t}"
        p = Paragraph(txt, S["h1"]); p._toc = (0, txt, f"h{self.h1n}"); p._heading = True
        self.pend.append(p)

    def H2(self, t):
        self._flush_unless_headings()
        self.h2n += 1
        txt = f"{self.h1n}.{self.h2n} {t}"
        p = Paragraph(txt, S["h2"]); p._toc = (1, txt, f"h{self.h1n}_{self.h2n}"); p._heading = True
        self.pend.append(p)

    def H3(self, t):
        self._flush_unless_headings()
        p = Paragraph(fx(t), S["h3"]); p._heading = True
        self.pend.append(p)

    def L(self, items, style="li"):
        ps = [Paragraph(fx(it), S[style], bulletText="•") for it in items]
        if self.pend:
            self.story.append(KeepTogether(self.pend + ps[:1])); self.pend = []; ps = ps[1:]
        self.story.extend(ps)

    def box(self, t, title="À retenir", kind="note"):
        p = Paragraph(fx(f"<b>{title} :</b> {t}" if title else t), S["note"])
        tb = Table([[p]], colWidths=[W * cm])
        tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ALT), ("LINEBEFORE", (0, 0), (0, -1), 3, DARK),
                                ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                                ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        self.story.append(KeepTogether(self.pend + [Spacer(1, 3), tb, Spacer(1, 7)])); self.pend = []

    def table(self, rows, widths, first_bold=True, keep=True, small=False, header=True, spans=None):
        cst = S["cs"] if small else S["c"]
        data = []
        for i, r in enumerate(rows):
            row = []
            for j, cell in enumerate(r):
                if isinstance(cell, (Paragraph, Image)):
                    row.append(cell); continue
                st = S["ch"] if (header and i == 0) else (S["cb"] if first_bold and j == 0 else cst)
                row.append(Paragraph(fx(cell), st))
            data.append(row)
        t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
        st = [("GRID", (0, 0), (-1, -1), 0.5, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
        if header: st.append(("BACKGROUND", (0, 0), (-1, 0), HEAD))
        for sp in (spans or []): st.append(sp)
        t.setStyle(TableStyle(st))
        if keep: self.story.append(KeepTogether(self.pend + [t, Spacer(1, 8)]))
        else:
            self.story.append(CondPageBreak(6 * cm)); self.story.extend(self.pend); self.story.append(t); self.story.append(Spacer(1, 8))
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

    # --- page de garde (modèle SUP'COM) + fiche du document + sommaire
    def cover(self, rows, history):
        arm = Image(str(ASSETS / "armoiries-tunisie.png"), width=2.6 * cm, height=2.6 * cm * 174 / 160)
        logo = Image(str(ASSETS / "logo-supcom.png"), width=6.2 * cm, height=6.2 * cm * 288 / 694)
        top = Table([[Paragraph("République Tunisienne", S["gl"]),
                      Paragraph("Ministère de l'Enseignement Supérieur et de la Recherche Scientifique<br/>"
                                "École Supérieure des Communications de Tunis (SUP'COM)", S["gr"])],
                     [arm, logo]], colWidths=[6.0 * cm, 11.4 * cm])
        top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 1), (1, 1), "RIGHT"),
                                 ("ALIGN", (0, 1), (0, 1), "LEFT"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        self.story += [top, Spacer(1, 3.0 * cm), Paragraph(self.title.upper(), S["gkind"]), Spacer(1, 12)]

        box = Table([[Paragraph("EburSeal — Le sceau invisible des diplômes ivoiriens", S["gbox"])],
                     [Paragraph(self.subtitle, S["gsub"])]], colWidths=[13.5 * cm])
        box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, TITLE), ("TOPPADDING", (0, 0), (-1, -1), 7),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
        self.story += [box, Spacer(1, 18)]
        self.story.append(Paragraph(
            "Module : Sécurité Applicative — Atelier (application PWA/SPA)<br/>"
            "Année universitaire : 2026-2027<br/>"
            "Classe : INDP3 Cybersecurity and Defense (CySeD)<br/>"
            f"Version {self.version}", S["ginfo"]))
        self.story.append(Spacer(1, 3.2 * cm))
        sig = Table([[Paragraph("<u>Réalisé par :</u>", S["gh"]), Paragraph("<u>Encadré par :</u>", S["gh"])],
                     [Paragraph("OUATTARA Yacouba<br/>YEO Tanna Daouda", S["gn"]),
                      Paragraph("Dr. Ing. Mohamed-Becha KAÂNICHE", S["gn"])]],
                    colWidths=[9.2 * cm, 8.2 * cm])
        sig.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 1), (-1, 1), 8),
                                 ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        self.story.append(sig)

        # page 2 : fiche du document, historique, sommaire
        self.story.append(NextPageTemplate("body"))
        self.story.append(PageBreak())
        self.story.append(Paragraph("Fiche du document", S["h3"]))
        self.table([[f"<b>{k}</b>", v] for k, v in rows], [4.5, 12.9], first_bold=True, header=False)
        self.story.append(Paragraph("Historique des versions", S["h3"]))
        self.table([["Version", "Date", "Auteur(s)", "Modifications"]] + history, [1.8, 2.4, 4.4, 8.8])
        self.flush()
        self.story.append(PageBreak())
        self.story.append(Paragraph("Sommaire", S["h1"]))
        toc = TableOfContents()
        toc.levelStyles = [ParagraphStyle("t0", fontName="DB", fontSize=12, leading=17, leftIndent=0, textColor=BLACK),
                           ParagraphStyle("t1", fontName="D", fontSize=11, leading=14.5, leftIndent=16, textColor=DARK)]
        toc.dotsMinLevel = 0
        self.story.append(toc)

    def build(self):
        self.flush()
        self.doc.multiBuild(self.story)
