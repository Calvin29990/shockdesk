import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

pdf_path = "candidatures-reseau-fo/DOSSIER_DE_REPRISE_CHASSE_FO_CALVIN_MINANG.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0f172a"))
        self.drawString(40, 810, "CALVIN MINANG — DOSSIER DE PASSATION & AUDIT RÉSEAU GLOBAL")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(555, 810, "Septembre 2026 | Confidentiel")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(40, 802, 555, 802)
        
        # Footer
        self.line(40, 45, 555, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(40, 32, "Opérations : Calvin (Front Office Janv 2027) | Yasmine (Alternance M2) | Aldrin (Génie Industriel)")
        self.drawRightString(555, 32, f"Page {self._pageNumber} / {page_count}")
        self.restoreState()

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    leftMargin=40,
    rightMargin=40,
    topMargin=50,
    bottomMargin=55
)

styles = getSampleStyleSheet()
primary = colors.HexColor("#0f172a")
accent = colors.HexColor("#1e3a8a")
success = colors.HexColor("#065f46")
warning = colors.HexColor("#92400e")
danger = colors.HexColor("#991b1b")

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=primary,
    spaceAfter=6
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#475569"),
    spaceAfter=12
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=16,
    textColor=accent,
    spaceBefore=10,
    spaceAfter=6
)

h2_style = ParagraphStyle(
    'SectionH2',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#1e293b"),
    spaceBefore=6,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'DocBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor("#1e293b")
)

bold_body = ParagraphStyle(
    'DocBodyBold',
    parent=body_style,
    fontName='Helvetica-Bold'
)

callout_style = ParagraphStyle(
    'CalloutText',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12,
    textColor=colors.HexColor("#0f172a")
)

story = []

story.append(Paragraph("DOSSIER DE PASSATION & AUDIT GLOBAL DU RÉSEAU", title_style))
story.append(Paragraph("<b>Candidat</b> : Calvin Minang — SKEMA Business School (PGE & Double Diplôme MSc Corporate Financial Management / CFM)<br/><b>Opérations actives</b> : Calvin FO Janvier 2027 | Yasmine Touil (Alternance M2) | Vianney-Aldrin Minang (Génie Industriel)", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

# Section 1
story.append(Paragraph("1. PROFIL OFFICIEL & CADRE DU CANDIDAT (CALVIN MINANG)", h1_style))
prof_text = """
<b>• Formation :</b> Master 2 Finance @ <b>SKEMA Business School</b> (Programme Grande École + Double Diplôme MSc Corporate Financial Management - CFM, 2022-2026). Classe Prépa IPESUP ECE (2021-2022), Bac S Spé Maths.<br/>
<b>• Certifications :</b> Candidat FRM (GARP), AMF en cours, Certifications QuantInsti (Python, ML & Options for Trading), Citi Forage Markets.<br/>
<b>• Expérience Clé :</b> BPCE Assurances — Reporting multi-actifs (FX, Taux, Actions, Indices), Bloomberg BQL, Excel/VBA.<br/>
<b>• Projets Desk :</b> ShockLab (Stress-testing ML/Python), CalvinX Market Terminal, Options Pricing & Greeks (BSM/VBA).<br/>
<b>• Statut Actuel FO :</b> En pause temporaire pendant la finalisation de sa préparation technique avec masterclass.
"""
story.append(Paragraph(prof_text, body_style))
story.append(Spacer(1, 8))

# Section 2
story.append(Paragraph("2. AUDIT VISUEL À 100% DU RÉSEAU 1ER DEGRÉ CALVIN (PROUVE PAR CAPTURE)", h1_style))
story.append(Paragraph("<b>A. Top 14 Grands Patrons, MD & Desk Heads FO (100% Vierges Vérifiés) :</b>", h2_style))

top_heads_data = [
    [Paragraph("<b>Nom & Prénom</b>", bold_body), Paragraph("<b>Titre & Institution</b>", bold_body), Paragraph("<b>Périmètre / Métier</b>", bold_body)],
    [Paragraph("Raoul Salomon", body_style), Paragraph("CEO France Barclays & Co-Head Markets Europe", body_style), Paragraph("Global Markets Direction", body_style)],
    [Paragraph("Herve Alfon", body_style), Paragraph("CEO Marex SA & Co-Head Capital Markets EMEA", body_style), Paragraph("Fixed Income & FX Courtage", body_style)],
    [Paragraph("Francois Blanc", body_style), Paragraph("Executive Director, IRS Cross-market Trading (Natixis)", body_style), Paragraph("IRS & Rates Pricing", body_style)],
    [Paragraph("Sylvie Soundaravelou", body_style), Paragraph("Head of Financial Markets Trading @ TotalEnergies", body_style), Paragraph("Trésorerie FO FX / Rates", body_style)],
    [Paragraph("Rosnan Chotard", body_style), Paragraph("Head Cross-Asset Structuring @ TP ICAP", body_style), Paragraph("Structuration Cross-Asset", body_style)],
    [Paragraph("Tristan Yonace", body_style), Paragraph("Executive Director @ Morgan Stanley", body_style), Paragraph("Derivatives Risk & Clearing", body_style)],
    [Paragraph("Michael Hart, CFA", body_style), Paragraph("Executive Director – Credit Sales @ Morgan Stanley", body_style), Paragraph("Vente Crédit Londres", body_style)],
    [Paragraph("Veronique Sabbah", body_style), Paragraph("Head EMEA Sales - Equity Derivatives @ HSBC", body_style), Paragraph("Direction Vente EQD EMEA", body_style)],
    [Paragraph("Olivier Moser", body_style), Paragraph("Sales Manager @ Barclays Private Bank Monaco", body_style), Paragraph("Wealth & Markets Monaco", body_style)],
    [Paragraph("Florent Thy-tine", body_style), Paragraph("Head Equity Research @ TP ICAP", body_style), Paragraph("Recherche Actions & Dérivés", body_style)],
    [Paragraph("Márcio MARTINS", body_style), Paragraph("Chief Financial Officer @ CMB Monaco", body_style), Paragraph("CFO & Trésorerie Monaco", body_style)],
    [Paragraph("Romain Ciarlet", body_style), Paragraph("Vice-Chairman & CEO @ Fondation Prince Albert II", body_style), Paragraph("Décideur Monaco", body_style)],
    [Paragraph("Hervé Samour-Cachian", body_style), Paragraph("CIO / Dir. Gestions Multi-Assets @ APICIL", body_style), Paragraph("Multi-Asset PM", body_style)],
    [Paragraph("Yann LE HER", body_style), Paragraph("Président 23IS (Ex-Head EQD Americas HSBC)", body_style), Paragraph("Family Office & Dérivés", body_style)],
]
t_heads = Table(top_heads_data, colWidths=[110, 240, 165])
t_heads.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
]))
story.append(t_heads)
story.append(Spacer(1, 8))

# Section 3
story.append(Paragraph("3. PISTES CHAUDES & RECOMMANDATIONS DIRECTES DISPONIBLES", h1_style))
pistes_text = """
<b>1. Brahim Louati (LCL SDM) :</b> Recommandation directe et email fourni par <b>Ali Megarni</b> (Deutsche Bank) : <code>brahim.louati@lcl-sdm.fr</code>.<br/>
<b>2. Yannick Leite Velho, CFA (Arrowpoint) :</b> Global Macro PM ayant formellement demandé le CV de Calvin.<br/>
<b>3. Florence Oudin (FinStart) :</b> Référence professionnelle senior formellement accordée pour les process de recrutement.<br/>
<b>4. Échéances Octobre 2026 (Janvier 2027) :</b> Manon Giorgi, Matthieu Mugler (CA IDF), Nicolas Ruiz (BNP CIB), Maxime Fontaine (Decathlon SE).
"""
story.append(Paragraph(pistes_text, body_style))
story.append(Spacer(1, 8))

# Section 4
story.append(Paragraph("4. DOSSIER YASMINE TOUIL — ALTERNANCE M2 ARCHITECTURE / DESIGN", h1_style))
yas_text = """
<b>• Objectif :</b> Alternance Master 2 Architecture d'intérieur / Scénographie / Retail Luxe (Région Auvergne-Rhône-Alpes & Paris).<br/>
<b>• Stratégie :</b> Double recommandation Calvin Minang & Marc-Aurèle Lerno (Crédit Agricole CIB) sans Yasmine en copie.<br/>
<b>• Packs Prêts :</b> Vague 1 (50 agences Lyon intra-muros archivée) | Vague 2 (50 nouvelles agences réparties par villes : Annecy, Chambéry, Grenoble, Saint-Étienne, Grand Lyon, Scéno/Retail).<br/>
<b>• Fichier maître :</b> <code>candidatures-reseau-fo/dossier-yasmine-touil/PACK_VAGUE_2_50_MAILS_VILLE_PAR_VILLE_YASMINE.md</code>.
"""
story.append(Paragraph(yas_text, body_style))
story.append(Spacer(1, 8))

# Section 5
story.append(Paragraph("5. DOSSIER VIANNEY-ALDRIN MINANG — CDI JUNIOR GÉNIE INDUSTRIEL", h1_style))
ald_text = """
<b>• Objectif :</b> CDI Junior Mobilité Europe (France, Luxembourg, Belgique) avec sponsoring visa (ANEF, AST, Permis Unique).<br/>
<b>• Contact direct :</b> <code>via.minang@gmail.com</code> | Tél : <b>+33 7 52 97 58 09</b> / <b>+241 62 20 81 40</b>.<br/>
<b>• Packs Prêts :</b> 20 emails recruteurs spécialisés génie industriel avec sources + guide légal des visas.
"""
story.append(Paragraph(ald_text, body_style))

doc.build(story, canvasmaker=NumberedCanvas)
print("PDF generated successfully:", pdf_path)
