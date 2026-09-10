import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header
        self.drawString(40, A4[1] - 30, "COURS D'URGENCE BILINGUE FRONT OFFICE — FOCUS SHOCKDESK & GRECS")
        self.drawRightString(A4[0] - 40, A4[1] - 30, "CALVIN MINANG — S&T / QUANT DESK")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(40, A4[1] - 34, A4[0] - 40, A4[1] - 34)
        
        # Footer
        self.line(40, 35, A4[0] - 40, 35)
        self.drawString(40, 24, "CONFIDENTIEL — PRÉPARATION DESK S&T / GLOBAL MARKETS")
        self.drawRightString(A4[0] - 40, 24, f"Page {self._pageNumber} sur {page_count}")
        self.restoreState()

def create_course_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F2942'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2B6CB0'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F2942'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=5
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1A202C')
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#2C5282')
    )

    story = []
    
    # Header Banner
    story.append(Paragraph("⚡ COURS D'URGENCE BILINGUE : FRONT OFFICE & SHOCKDESK", title_style))
    story.append(Paragraph("<b>Guide Commando de Maîtrise Technique & Vocabulaire de Marché (FR / EN)</b><br/>Spécialisation : Multi-Asset Stress-Testing, Grecs, Pricing de Dérivés & Attribution de P&L", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceAfter=10))
    
    # Module 1
    story.append(Paragraph("MODULE 1 : LE PITCH CHOC DE SHOCKDESK (60 SECONDES CHRONO)", h1_style))
    
    pitch_data = [
        [Paragraph("<b>Pitch en Français (Desk Paris / Genève)</b>", body_bold), Paragraph("<b>English Trading Floor Pitch (London / International)</b>", body_bold)],
        [
            Paragraph("« J'ai développé <b>ShockDesk</b>, une plateforme quantitative en Python dédiée au <b>stress-testing multi-actifs</b> et au <b>calcul dynamique des sensibilités (Grecs)</b>. Elle simule des scénarios macro extrêmes (chocs de taux, flambée du pétrole, squeeze de liquidité) avec réévaluation non-linéaire du portefeuille, calcul de VaR/CVaR et attribution exacte du P&L (Delta, Gamma, Vega, Theta). Chez BPCE Assurances, j'ai complété cette approche par l'automatisation Bloomberg BQL et Excel VBA. »", body_style),
            Paragraph("“I engineered <b>ShockDesk</b>, a quantitative Python framework designed for <b>multi-asset portfolio stress-testing</b> and <b>real-time Greeks computation</b>. It simulates severe macro tail-events (yield curve shocks, oil spikes, liquidity crunches) using non-linear revaluation, historical & parametric VaR/CVaR, and full P&L attribution (Delta, Gamma, Vega, Theta). Backed by my experience at BPCE Assurances (Bloomberg BQL & VBA), I am immediately operational on desk analytics.”", body_style)
        ]
    ]
    
    t_pitch = Table(pitch_data, colWidths=[260, 260])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#EBF8FF')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#F7FAFC')),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor('#F0F4F8')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pitch)
    story.append(Spacer(1, 10))
    
    # Module 2
    story.append(Paragraph("MODULE 2 : LES GRECS DANS SHOCKDESK — DÉFINITION & APPLICATIONS DESK", h1_style))
    
    greeks_data = [
        [Paragraph("<b>Grecque & Ordre</b>", body_bold), Paragraph("<b>Formule & Rôle Mathématique</b>", body_bold), Paragraph("<b>Interprétation Desk & ShockDesk Engine</b>", body_bold), Paragraph("<b>Phrasé Anglais Déterminant</b>", body_bold)],
        [
            Paragraph("<b>Delta (Δ) & DV01</b><br/>(1er Ordre)", body_style),
            Paragraph("Δ = ∂V / ∂S<br/>DV01 = ∂P / ∂y (1 bp)", code_style),
            Paragraph("Sensibilité du prix au sous-jacent ou variation en $ pour 1 bp de taux. ShockDesk calcule le ratio de couverture optimal (Delta-Hedging via futures/swaps).", body_style),
            Paragraph("<i>“Our net DV01 is hedged via 10Y Bund futures to lock in the yield curve exposure.”</i>", body_style)
        ],
        [
            Paragraph("<b>Gamma (Γ) & Convexité</b><br/>(2nd Ordre)", body_style),
            Paragraph("Γ = ∂²V / ∂S²<br/>C = (1/P)(∂²P / ∂y²)", code_style),
            Paragraph("Vitesse de variation du Delta. Les positions Long Gamma gagnent du delta quand le spot monte et en perdent quand il baisse (asymétrie positive).", body_style),
            Paragraph("<i>“Long gamma positioning provides positive convexity during high-volatility rate cut cycles.”</i>", body_style)
        ],
        [
            Paragraph("<b>Vega (ν) & Vol Surface</b><br/>(1er Ordre Vol)", body_style),
            Paragraph("ν = ∂V / ∂σ", code_style),
            Paragraph("Sensibilité à 1% de volatilité implicite. ShockDesk modélise le Smile/Skew et le Risk Reversal (ex: spread 25-delta Put vs Call sur FX).", body_style),
            Paragraph("<i>“We capture the vol skew steepening across short-dated FX options.”</i>", body_style)
        ],
        [
            Paragraph("<b>Theta (θ) & Carry</b><br/>(Sensibilité Temps)", body_style),
            Paragraph("θ = ∂V / ∂t", code_style),
            Paragraph("Érosion temporelle de la valeur optionnelle. Sur un desk Taux/FX : arbitrage entre l'encaissement de portage (Carry/Roll-Down) et le coût du Theta.", body_style),
            Paragraph("<i>“Steep yield curve maximizes roll-down gains, compensating for negative theta bleed.”</i>", body_style)
        ],
        [
            Paragraph("<b>Volga & Vanna</b><br/>(2nd Ordre Vol/Spot)", body_style),
            Paragraph("Volga = ∂²V/∂σ²<br/>Vanna = ∂²V/∂S∂σ", code_style),
            Paragraph("Sensibilités croisées de second ordre indispensables au pricing des dérivés exotiques et autocalls dans ShockDesk.", body_style),
            Paragraph("<i>“Cross-gamma and vanna exposures are monitored against extreme spot-vol correlations.”</i>", body_style)
        ]
    ]
    
    t_greeks = Table(greeks_data, colWidths=[90, 110, 180, 140])
    t_greeks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F2942')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F7FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_greeks)
    story.append(Spacer(1, 10))
    
    # Module 3
    story.append(Paragraph("MODULE 3 : LES 4 SCÉNARIOS DE CHOCS MACRO SIMULÉS DANS SHOCKDESK", h1_style))
    
    shocks_data = [
        [Paragraph("<b>Scénario Macro</b>", body_bold), Paragraph("<b>Choc de Marché Injecté</b>", body_bold), Paragraph("<b>Comportement Multi-Actifs & Risques</b>", body_bold), Paragraph("<b>Formule d'Attribution P&L</b>", body_bold)],
        [
            Paragraph("<b>1. Choc Pétrolier & Stagflation</b>", body_bold),
            Paragraph("Brent +25%, Taux courts +40 bps, Actions -8%", body_style),
            Paragraph("Surperformance Commodities/Gold (GC=F), élargissement des breakevens d'inflation, baisse des multiples actions.", body_style),
            Paragraph("ΔP&L ≈ Δ_oil·ΔS_oil + DV01·Δy + Veg·Δσ", code_style)
        ],
        [
            Paragraph("<b>2. Choc de Taux / Steepener</b>", body_bold),
            Paragraph("Pentification 2s10s (+35 bps sur 10Y)", body_style),
            Paragraph("Perte sur duration longue (TLT), gain sur portage/roll-down sur la partie centrale de courbe, spread sovereign vs swaps.", body_style),
            Paragraph("ΔP&L ≈ -DV01_10Y·Δy_10Y + 0.5·C·(Δy)²", code_style)
        ],
        [
            Paragraph("<b>3. Flight to Quality / Crash FX</b>", body_bold),
            Paragraph("DXY +6%, EM FX -12%, Spreads Crédit +80 bps", body_style),
            Paragraph("Widening des Cross-Currency Basis Swaps, tension sur le collatéral Repo, explosion du risque de contrepartie (XVA).", body_style),
            Paragraph("Stress Loss = Max Drawdown(Historical VaR 99%)", code_style)
        ],
        [
            Paragraph("<b>4. Volatility Squeeze</b>", body_bold),
            Paragraph("VIX / VSTOXX +15 pts, Skew Put +4%", body_style),
            Paragraph("Asymétrie violente sur les puts OTM, débouclage de carry trades, risque de gap sur positions Short Gamma.", body_style),
            Paragraph("ΔP&L ≈ 0.5·Γ·(ΔS)² + Vega·Δσ + 0.5·Volga·(Δσ)²", code_style)
        ]
    ]
    
    t_shocks = Table(shocks_data, colWidths=[120, 110, 160, 130])
    t_shocks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F7FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_shocks)
    story.append(Spacer(1, 10))
    
    # Module 4
    story.append(Paragraph("MODULE 4 : QUESTIONS TECHNIQUES ASSASSINES EN ENTRETIEN DESK (RÉPONSES CHOC)", h1_style))
    
    qa_data = [
        [
            Paragraph("<b>Q1 (Desk FIC) : If the ECB cuts rates by 50 bps while the Fed stays hawkish, how do you position on EUR/USD and Rates?</b>", body_bold),
        ],
        [
            Paragraph("<b>Réponse Choc :</b> <i>“This monetary divergence widens the 2Y interest rate differential (SOFR vs Euribor) in favor of the USD, putting downward pressure on EUR/USD spot. On rates, we expect a bull steepening of the European curve (front-end rallying faster). Strategy: short EUR/USD via risk-reversal (long puts funded by OTM calls) to capture the skew, while entering a 2s10s steepener on EGBs.”</i>", body_style)
        ],
        [
            Paragraph("<b>Q2 (Desk Dérivés Exotiques) : What is the difference between VaR and Stress-Testing, and why does VaR fail during crises?</b>", body_bold),
        ],
        [
            Paragraph("<b>Réponse Choc :</b> <i>“VaR is a quantile-based metric assuming normal or historical return distributions within a given confidence level (e.g. 99% 1-day). It fails in crises due to fat tails, non-linear derivatives payoff breakdown, and liquidity evaporation. That is why I built ShockDesk: scenario-based stress-testing performs full revaluation without relying on Gaussian correlations, capturing true tail risk.”</i>", body_style)
        ],
        [
            Paragraph("<b>Q3 (Desk Structuration) : How does high implied volatility impact an Autocall / Reverse Convertible pricing?</b>", body_bold),
        ],
        [
            Paragraph("<b>Réponse Choc :</b> <i>“Higher implied volatility increases the value of the embedded short put option sold by the investor. This allows the structurer to offer a higher guaranteed coupon (enhanced yield) or to offer a deeper capital protection barrier for the same target coupon.”</i>", body_style)
        ]
    ]
    
    t_qa = Table(qa_data, colWidths=[520])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#EDF2F7')),
        ('BACKGROUND', (0,1), (0,1), colors.white),
        ('BACKGROUND', (0,2), (0,2), colors.HexColor('#EDF2F7')),
        ('BACKGROUND', (0,3), (0,3), colors.white),
        ('BACKGROUND', (0,4), (0,4), colors.HexColor('#EDF2F7')),
        ('BACKGROUND', (0,5), (0,5), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_qa)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    out_pdf = "candidatures-reseau-fo/COURS_URGENCE_BILINGUE_FRONT_OFFICE_SHOCKDESK.pdf"
    create_course_pdf(out_pdf)
