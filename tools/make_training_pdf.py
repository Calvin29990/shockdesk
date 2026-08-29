#!/usr/bin/env python3
"""
Générateur du Carnet d'Entraînement Progressif ShockDesk (PDF).
Utilise fpdf2 et la police DejaVuSans pour un rendu typographique propre et complet en UTF-8.
"""

import os
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "entrainement-progressif.pdf")

DEJAVU_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


class TrainingPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.set_margins(left=15, top=15, right=15)
        
        if os.path.exists(DEJAVU_REGULAR) and os.path.exists(DEJAVU_BOLD):
            self.add_font("DejaVu", "", DEJAVU_REGULAR)
            self.add_font("DejaVu", "B", DEJAVU_BOLD)
            self.font_main = "DejaVu"
        else:
            self.font_main = "Helvetica"
            
        if os.path.exists(DEJAVU_MONO):
            self.add_font("DejaVuMono", "", DEJAVU_MONO)
            self.font_mono = "DejaVuMono"
        else:
            self.font_mono = "Courier"

    def header(self):
        self.set_font(self.font_main, "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "SHOCKDESK — CARNET D'ENTRAÎNEMENT PROGRESSIF", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(0, 5, "https://shockdesk.onrender.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_draw_color(226, 232, 240)
        self.line(15, 21, 195, 21)
        self.ln(4)

    def footer(self):
        self.set_y(-14)
        self.set_font(self.font_main, "", 8)
        self.set_text_color(148, 163, 184)
        self.set_draw_color(226, 232, 240)
        self.line(15, 283, 195, 283)
        self.cell(0, 8, "ShockDesk • Lab d'Entraînement par Capture d'Écran", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(0, 8, f"Page {self.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    def page_title(self, num, title, subtitle=None):
        self.set_y(24)
        self.set_font(self.font_main, "B", 13)
        self.set_text_color(15, 23, 42)
        self.cell(0, 7, f"{num}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        if subtitle:
            self.set_font(self.font_main, "", 8.5)
            self.set_text_color(71, 85, 105)
            self.cell(0, 5, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        self.ln(2)

    def section_header(self, title):
        self.set_font(self.font_main, "B", 9.5)
        self.set_text_color(30, 41, 59)
        self.set_fill_color(241, 245, 249)
        self.cell(0, 6, f"  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", fill=True)
        self.ln(1.5)

    def card_box(self, x, y, w, h, bg_color=(248, 250, 252), border_color=(203, 213, 225)):
        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.rect(x, y, w, h, style="FD")


def generate_pdf():
    os.makedirs(DOCS_DIR, exist_ok=True)
    pdf = TrainingPDF()

    # Page 1 : Niveau 1 & 2
    pdf.add_page()
    pdf.set_y(24)
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(15, 24, 180, 22, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf.font_main, "B", 13)
    pdf.set_xy(20, 27)
    pdf.cell(170, 6, "CARNET D'ENTRAÎNEMENT INTERACTIF — SHOCKDESK", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_xy(20, 33)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(170, 5, "Protocole de progression pas à pas par modification ciblée et captures d'écran", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(50)
    pdf.section_header("NIVEAU 1 — LES RÉFLEXES DE BASE (Stratégie shock-lab-oil.py)")

    ateliers_n1 = [
        ("Atelier 1 : Leçon du Timing (TAKE_PROFIT_AT_PEAK = False)",
         "Action : Passez la ligne 11 à 'False'. Lancez avec Ctrl+Entrée.\n"
         "Ce qu'on observe : La courbe d'équité rechute après le 22 juillet. Le P&L passe de +337 k$ à quasi 0.\n"
         "Diagnostic : Le pétrole retombe à -6,5 % au stop. Sans take-profit à J+7, vous perdez tout votre gain brut."),
        
        ("Atelier 2 : Levier et Exposition (BASE_EXPOSURE = 0.40 vs 1.00)",
         "Action : Testez BASE_EXPOSURE = 0.40 puis 1.00 à la ligne 14.\n"
         "Ce qu'on observe : À 0.40, le P&L est modéré (~+160 k$) et la vol < 1,2 %. À 1.00, le P&L dépasse +400 k$.\n"
         "Diagnostic : L'exposition est votre variateur de volume sans altérer la logique du scénario."),
        
        ("Atelier 3 : Neutraliser le Miss (BOOK['GC=F'] = 0.00)",
         "Action : Mettez le poids de l'or à 0.00 à la ligne 21.\n"
         "Ce qu'on observe : La perte de -71 k$ sur l'or s'annule. Le P&L global bondit à plus de +400 k$.\n"
         "Diagnostic : Retirer un actif dont le comportement contredit la thèse assainit immédiatement le book.")
    ]

    y_pos = 58
    for i, (atitle, abody) in enumerate(ateliers_n1):
        by = y_pos + i * 36
        pdf.card_box(15, by, 180, 33, bg_color=(248, 250, 252), border_color=(203, 213, 225))
        pdf.set_xy(18, by + 2)
        pdf.set_font(pdf.font_main, "B", 8)
        pdf.set_text_color(14, 116, 144)
        pdf.cell(174, 4, atitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(18, by + 6.5)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(174, 3.8, abody)

    pdf.set_y(172)
    pdf.section_header("NIVEAU 2 — LES STRATÉGIES ALTERNATIVES")

    ateliers_n2 = [
        ("Atelier 4 : Long Strangle (long-strangle-shock.py)",
         "Action : Exécutez la stratégie sur 1 M$ de capital.\n"
         "Observation : P&L = +12 084 $ (+1,21 %). Le Call OTM compense largement le Put grâce aux +18,4 % du Brent."),
        
        ("Atelier 5 : Butterfly au Pic (butterfly-peak.py)",
         "Action : Exécutez le butterfly sur 1 M$ de capital.\n"
         "Observation : P&L = -22 365 $ (-2,24 %). Le Brent dépasse l'aile, mais la perte est rigoureusement bornée au coût de prime.")
    ]

    y_pos2 = 180
    for i, (atitle, abody) in enumerate(ateliers_n2):
        by = y_pos2 + i * 38
        pdf.card_box(15, by, 180, 35, bg_color=(255, 255, 255), border_color=(226, 232, 240))
        pdf.set_xy(18, by + 2)
        pdf.set_font(pdf.font_main, "B", 8)
        pdf.set_text_color(3, 105, 161)
        pdf.cell(174, 4, atitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(18, by + 6.5)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(174, 3.8, abody)

    # Page 2 : Niveau 3, 4 et Grille de bord
    pdf.add_page()
    pdf.page_title("2", "NIVEAUX AVANCÉS & TABLEAU DE PROGRESSION", "Atelier d'options, anticipation, boucle de revue et feuille de suivi")

    pdf.section_header("NIVEAU 3 — OPTIONS & GRECQUES")
    pdf.card_box(15, pdf.get_y(), 180, 30, bg_color=(248, 250, 252), border_color=(203, 213, 225))
    pdf.set_xy(18, pdf.get_y() + 2)
    pdf.set_font(pdf.font_main, "B", 8)
    pdf.set_text_color(14, 116, 144)
    pdf.cell(174, 4, "Atelier 7 : Onglet Options & Sensibilité Vega", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(18, pdf.get_y() + 1)
    pdf.set_font(pdf.font_main, "", 7.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(174, 3.8, 
        "Action : Dans l'onglet Options, testez un Strangle SPY 30 j avec un iv_shift de +0.10 (+10 pts d'IV).\n"
        "Observation : La prime et le profit latent augmentent instantanément grâce au Vega positif de la structure.")

    pdf.set_y(pdf.get_y() + 10)
    pdf.section_header("NIVEAU 4 — L'ANTICIPATION & LA BOUCLE DE REVUE")
    pdf.card_box(15, pdf.get_y(), 180, 32, bg_color=(255, 255, 255), border_color=(226, 232, 240))
    pdf.set_xy(18, pdf.get_y() + 2)
    pdf.set_font(pdf.font_main, "B", 8)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(174, 4, "Atelier 8 : La Commande de Revue Mensuelle (CLI revue)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(18, pdf.get_y() + 1)
    pdf.set_font(pdf.font_main, "", 7.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(174, 3.8,
        "Action : Lancez 'python -m shockdesk.cli revue --name global-macro --asof 2026-08-28'.\n"
        "Observation : Le terminal affiche le Scorecard (4/6 de signe), la proposition de révision JSON prête à l'emploi et la matrice de calibration.")

    pdf.set_y(pdf.get_y() + 10)
    pdf.section_header("TABLEAU DE PROGRESSION À VALIDER PAR CAPTURE D'ÉCRAN")

    tableau = [
        ("Atelier 1", "Timing Take-Profit", "TAKE_PROFIT_AT_PEAK = False", "P&L s'effondre"),
        ("Atelier 2", "Exposition Brute", "BASE_EXPOSURE = 0.40 / 1.00", "Gain & Vol modifiés"),
        ("Atelier 3", "Neutraliser Miss", "BOOK['GC=F'] = 0.00", "P&L dépasse +400 k$"),
        ("Atelier 4", "Long Strangle", "long-strangle-shock.py", "+12 k$ sur gamma"),
        ("Atelier 5", "Butterfly", "butterfly-peak.py", "Perte bornée à -2,24 %"),
        ("Atelier 6", "Choc Vega", "Onglet Options iv_shift", "Revalorisation du Call/Put"),
        ("Atelier 7", "Revue CLI", "shockdesk.cli revue", "Scorecard & calibration")
    ]

    y_t = pdf.get_y() + 1
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(15, y_t, 180, 6, style="F")
    pdf.set_font(pdf.font_main, "B", 7.5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(18, y_t + 1)
    pdf.cell(30, 4, "ATELIER")
    pdf.cell(45, 4, "CONCEPT")
    pdf.cell(60, 4, "PARAMÈTRE MODIFIÉ")
    pdf.cell(45, 4, "EFFET CLÉ ATTENDU", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    for idx, (at, cp, pm, ef) in enumerate(tableau):
        row_y = y_t + 6 + idx * 6.2
        bg = (248, 250, 252) if idx % 2 == 0 else (255, 255, 255)
        pdf.card_box(15, row_y, 180, 6.2, bg_color=bg, border_color=(241, 245, 249))
        pdf.set_xy(18, row_y + 1)
        pdf.set_font(pdf.font_main, "B", 7.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(30, 4, at)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.cell(45, 4, cp)
        pdf.set_font(pdf.font_mono, "", 6.8)
        pdf.set_text_color(3, 105, 161)
        pdf.cell(60, 4, pm)
        pdf.set_font(pdf.font_main, "", 7)
        pdf.set_text_color(16, 185, 129)
        pdf.cell(45, 4, ef, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(OUTPUT_PDF)
    print(f"PDF d'entraînement généré avec succès : {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
